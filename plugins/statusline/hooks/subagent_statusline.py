#!/usr/bin/env python3
"""Sub-agent rows: each agent's context fill, in Claude Code's agent panel.

Claude Code runs this as the `subagentStatusLine` command (the plugin's own
settings.json ships it as a default; see How it is enabled below). On each
tick of the agent panel (first run 300 ms after a sub-agent appears, then
every 5 s, killed at 5 s) it gets one JSON object on stdin: the base hook
fields (`session_id`, `transcript_path` - the MAIN session's - and `cwd`),
`columns` (the usable row width) and `tasks`, one entry per visible
sub-agent row, each with `id`, `name`, `type`, `status`, `description`,
`label`, `model`, `contextWindowSize` and `tokenCount` among others. For each
row it can draw, it prints one line `{"id": ..., "content": ...}`; a row it
prints nothing for keeps Claude Code's default rendering.

A row reads `name · 43% 86k/200k · description`, the fill coloured like the
footer's gauge (green, yellow, red by tokens left, over the default
thresholds for that window size).

Depth. Exact when the agent's sidechain transcript can be read:
<transcript stem>/subagents/agent-<id>.jsonl, the stem being the main
transcript path without `.jsonl` (the task `id` of a local agent is its
agentId, which names that file); an agent a workflow started lives one
directory further down, subagents/workflows/<run id>/agent-<id>.jsonl, and
is looked for there when the direct path is missing. The depth is the sum of input_tokens,
cache_read_input_tokens and cache_creation_input_tokens on the last line that
carries a `usage`, reset by a compact_boundary: the same arithmetic a gate
applies to the main transcript. It lives here in full: a plugin never
reaches into another plugin's files.

The read is incremental. A per-session cache,
${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/subagents/<session>.json, keeps
per agent the byte offset of the last complete line read, the depth as of
there, and the file's device, inode and the TAIL_CHECK bytes before the
offset. A file whose identity and tail still match is read from that offset
only; anything else is read from 0. A final line without its newline is left
for the next tick. At most BUDGET bytes are read per tick across all rows
(plus the rest of one line, so every tick advances), so latency stays
bounded whatever the transcripts weigh; the rows with the least left to read
go first, and a file not read to its end within the budget shows the
approximate figure this tick and continues from where it stopped on the
next. A line longer than LINE_MAX (a huge tool result) is streamed in
chunks and never parsed whole: a string-aware scanner follows its structure
only as far as message.usage, skips every other value without keeping it,
and counts the same fields the whole-line parse would. The cache keeps up to
CACHE_MAX agents, the rows visible this tick first.

Approximate, marked `~`: when there is no readable sidechain yet, no usage
line in it yet (a new agent, or one just compacted), or the budget ran out
before its end, the row shows the payload's tokenCount over
contextWindowSize. Claude Code's tokenCount adds the agent's cumulative
output to its last input, so it overstates depth, more the longer the agent
runs. A row with neither figure is left to the default rendering.

In-process teammates. Claude Code 2.1.278 gives this command only local
agent tasks (not the main session, not fork workers), so teammate rows never
reach it; a task whose sidechain is missing would fall back to the payload
figure anyway.

How it is enabled: plugins/statusline/settings.json names this file through
the plugin-data `current-hooks` link that the SessionStart hook keeps on this
version's hooks dir (Claude Code does not expand plugin path variables in a
plugin's settings.json). A plugin's settings are the lowest layer, so a
`subagentStatusLine` the user sets in any settings file wins over it; this
plugin never writes one.

Text from the payload (name, description) is shown on one line: whitespace
and control characters collapse to one space, format characters are
dropped, and the row is cut to `columns` terminal columns (0 columns: no
rows). Never raises;
malformed input prints nothing, so every row keeps its default.
"""
import json, os, re, sys, time, unicodedata

HOOKS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HOOKS)
import sensor as S

BUDGET = 8 << 20          # bytes read from sidechain transcripts per tick, all rows together
TAIL_CHECK = 64           # bytes before a cached offset that must still match
CACHE_V = 1
CACHE_MAX = 64            # agents kept in one session's cache
TASKS_MAX = 64            # rows drawn per tick at most
LINE_MAX = 1 << 20        # a longer line is streamed in chunks of this size, never parsed whole
TOKEN_MAX = 4096          # a longer key or scalar on a long line: not worth parsing
DEPTH_MAX = 512           # deeper nesting on a long line: treated as unparseable
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}")
_UNSAFE = re.compile(r"[\s\x00-\x1f\x7f-\x9f]+")
SEP = " · "
USAGE_KEYS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def cache_dir():
    return os.path.join(S.base_dir(), "statusline", "subagents")


def cache_path(session_id):
    return os.path.join(cache_dir(), S.safe_sid(session_id) + ".json")


def prune(keep=None, now=None, days=S.PRUNE_DAYS):
    """Delete session caches not modified for `days` (keep's, the current
    session's, excepted) and orphaned temp files; SessionStart runs it.
    Regular files only, never through a symlinked dir. Returns how many
    went. Never raises."""
    n = 0
    try:
        now = time.time() if now is None else now
        d = cache_dir()
        if os.path.islink(d) or not os.path.isdir(d):
            return 0
        keep_name = S.safe_sid(keep) + ".json" if keep else None
        n = S.prune_tmp(d, now)
        with os.scandir(d) as it:
            for e in it:
                try:
                    if not e.name.endswith(".json") or e.name == keep_name or \
                            not e.is_file(follow_symlinks=False):
                        continue
                    if now - e.stat(follow_symlinks=False).st_mtime > days * 86400:
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
    except Exception:
        pass
    return n


def num(v):
    """`v` as a non-negative int, or None (bool, text, NaN and friends)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    try:
        v = int(v)
    except (ValueError, OverflowError):
        return None
    return v if v >= 0 else None


def sidechain(transcript_path, session_id, agent_id):
    """The agent's sidechain transcript path, or None: an id that is not a
    safe token, or no such file under the main transcript's stem (or, when
    the stem is not the session id, under <dir>/<session id>)."""
    if not isinstance(agent_id, str) or not _SAFE_ID.fullmatch(agent_id):
        return None
    if not isinstance(transcript_path, str) or not transcript_path:
        return None
    name = "agent-" + agent_id + ".jsonl"
    stems = [os.path.splitext(transcript_path)[0]]
    if isinstance(session_id, str) and _SAFE_ID.fullmatch(session_id):
        alt = os.path.join(os.path.dirname(transcript_path), session_id)
        if alt != stems[0]:
            stems.append(alt)
    for stem in stems:
        p = os.path.join(stem, "subagents", name)
        if os.path.isfile(p):
            return p
    import glob       # a workflow's agents: subagents/workflows/<run id>/agent-<id>.jsonl
    for stem in stems:
        base = glob.escape(os.path.join(stem, "subagents"))
        for pat in (("workflows", "*"), ("*",)):
            hits = sorted(glob.glob(os.path.join(base, *pat, glob.escape(name))))
            if hits:
                return hits[0]
    return None


def _usage_total(line):
    """The input-side token sum of this line's message.usage, or 0."""
    try:
        obj = json.loads(line.decode("utf-8", "replace"))
    except Exception:
        return 0
    msg = obj.get("message") if isinstance(obj, dict) else None
    u = msg.get("usage") if isinstance(msg, dict) else None
    if not isinstance(u, dict):
        return 0
    t = 0
    for k in USAGE_KEYS:
        v = num(u.get(k))
        t += v or 0
    return t


_WS = re.compile(rb"[ \t\r\n]*")
# The rest of a string, up to its closing quote, an escape cut by the chunk
# end, or a raw control character (which makes the line invalid JSON).
_STR = re.compile(rb'[^"\\\x00-\x1f]*(?:\\[\s\S][^"\\\x00-\x1f]*)*')
# Inside a value nothing is counted from: everything but brackets and
# whole strings, in one C-speed match.
_SKIP = re.compile(rb'(?:[^"{}\[\]]+|"[^"\\\x00-\x1f]*(?:\\[\s\S][^"\\\x00-\x1f]*)*")*')
_SCALAR = re.compile(rb"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
                     rb"|true|false|null|NaN|-?Infinity")
_SCALAR_PART = re.compile(rb"[-+.0-9A-Za-z]+")
_UKEYS = frozenset(USAGE_KEYS)


class _UsageScan:
    """The input-side token sum of a line's message.usage, fed in chunks:
    the result _usage_total would give the whole line, without holding it.
    Only the root object, its "message" object and that object's "usage"
    object are followed key by key; every other value is skipped as a run
    of strings and brackets. Duplicate keys keep the last value, as
    json.loads does; a line that is not one JSON object gives 0, except
    that bad grammar inside a skipped value (a missing comma or colon
    there) goes unnoticed."""

    def __init__(self):
        # Per open container: [tag, key, what comes next]. Only a followed
        # object (tag set) checks its grammar: "k0" a key or "}", "k" a
        # key, ":" the colon, "v" a value, "," a comma or "}".
        self.stack = []
        self.fields = None      # message.usage's fields so far, or None: not an object
        self.pend = b""         # a key or scalar cut by the chunk end
        self.in_str = False
        self.key = None         # the key string being read, or None: not a key
        self.closed = self.bad = False

    def total(self):
        if self.bad or not self.closed or self.in_str or self.pend or \
                not isinstance(self.fields, dict):
            return 0
        t = 0
        for v in self.fields.values():
            t += num(v) or 0
        return t

    def _value(self, kind, tok=None):
        """A value starts in the current container ("{", "[", "s", or a
        scalar with its token); returns the tag for a container it opens."""
        if not self.stack:
            return "root" if kind == "{" else None
        tag, key = self.stack[-1][0], self.stack[-1][1]
        if tag == "root" and key == "message":
            self.fields = None
            return "msg" if kind == "{" else None
        if tag == "msg" and key == "usage":
            self.fields = {} if kind == "{" else None
            return "usage" if kind == "{" else None
        if tag == "usage" and key in _UKEYS:
            v = None
            if tok is not None:
                try:
                    v = json.loads(tok)
                except Exception:
                    self.bad = True
            self.fields[key] = v
        return None

    def _expect(self, top):
        """True when a value may start here in a followed container (or at
        the root), and marks it taken; False in a skipped container."""
        if top is None:
            return True
        if top[0] is None:
            return False
        if top[2] != "v":
            self.bad = True
            return False
        top[2] = ","
        return True

    def feed(self, data):
        buf = self.pend + data if self.pend else data
        self.pend = b""
        i, n = 0, len(buf)
        while i < n and not self.bad:
            if self.in_str:
                j = _STR.match(buf, i).end()
                if self.key is not None and len(self.key) <= TOKEN_MAX:
                    self.key += buf[i:min(j, i + TOKEN_MAX + 1 - len(self.key))]
                if j >= n:
                    return
                if buf[j] == 0x5C:           # an escape cut by the chunk end
                    self.pend = buf[j:]
                    return
                if buf[j] != 0x22:           # a raw control character
                    self.bad = True
                    return
                self.in_str, i = False, j + 1
                if self.key is not None:
                    try:           # too long to be a name that counts
                        k = None if len(self.key) > TOKEN_MAX else \
                            json.loads(b'"' + self.key + b'"')
                    except Exception:
                        k = None
                    self.stack[-1][1], self.stack[-1][2], self.key = k, ":", None
                continue
            top = self.stack[-1] if self.stack else None
            if top is not None and top[0] is None:
                i = _SKIP.match(buf, i).end()
            else:
                i = _WS.match(buf, i).end()
            if i >= n:
                return
            c = buf[i:i + 1]
            if self.closed:
                self.bad = True
            elif c == b'"':
                self.in_str = True
                if top is not None and top[0] is not None and top[2] in ("k0", "k"):
                    self.key = b""
                elif self._expect(top):
                    self._value("s")
                i += 1
            elif c in (b"{", b"["):
                tag = self._value(c.decode()) if self._expect(top) else None
                if len(self.stack) >= DEPTH_MAX:
                    self.bad = True
                self.stack.append([tag, None, "k0"])
                i += 1
            elif c in (b"}", b"]"):
                if top is None or top[0] is not None and (c == b"]" or top[2] not in ("k0", ",")):
                    self.bad = True
                else:
                    self.stack.pop()
                    self.closed = not self.stack
                i += 1
            elif c in (b",", b":"):   # (an untracked container's are skipped)
                if top is None or top[2] != c.decode():
                    self.bad = True
                else:
                    top[2] = "k" if c == b"," else "v"
                i += 1
            else:
                if _SCALAR_PART.fullmatch(buf, i):
                    # the chunk may end inside it: finish it with the next
                    if n - i > TOKEN_MAX:
                        self.bad = True
                    self.pend = buf[i:]
                    return
                m = _SCALAR.match(buf, i)
                if not m:
                    self.bad = True
                    return
                if self._expect(top):
                    self._value("v", m.group())
                i = m.end()
                if top is None:
                    self.closed = True


def _long_line(fh, first):
    """(length, depth or 0, boundary) of a line longer than LINE_MAX whose
    first LINE_MAX bytes are `first`, read on in chunks so memory stays
    bounded; None for the length when the file ends before its newline."""
    n, u = len(first), _UsageScan()
    u.feed(first)
    boundary = b'"compact_boundary"' in first[:4096]
    while True:
        chunk = fh.readline(LINE_MAX)
        if not chunk:
            return None, None, False
        n += len(chunk)
        u.feed(chunk)
        if chunk.endswith(b"\n"):
            return n, u.total(), boundary


def scan(path, ent, budget):
    """(entry, done, bytes read): `ent` (a cache entry, or None) advanced
    over `path`. `done` is True when every complete line was read within
    `budget` bytes. An entry is {dev, ino, off, cur, tail}: `cur` the depth
    as of `off`, 0 when no usage line has been read since the start or the
    last compact_boundary."""
    with open(path, "rb") as fh:
        st = os.fstat(fh.fileno())
        off, cur = 0, 0
        if isinstance(ent, dict) and ent.get("dev") == st.st_dev and \
                ent.get("ino") == st.st_ino and isinstance(ent.get("off"), int) and \
                0 < ent["off"] <= st.st_size and isinstance(ent.get("cur"), int):
            k = min(TAIL_CHECK, ent["off"])
            fh.seek(ent["off"] - k)
            if fh.read(k).hex() == ent.get("tail"):
                off, cur = ent["off"], ent["cur"]
        fh.seek(off)
        read, done = 0, True
        while True:
            if read >= budget:
                done = off >= st.st_size
                break
            line = fh.readline(LINE_MAX)
            if not line:
                break
            if not line.endswith(b"\n"):
                if len(line) < LINE_MAX:
                    break                   # incomplete: read again next tick
                # One line is always read, however long, so every tick
                # advances; past LINE_MAX it is streamed, not parsed.
                n, t, boundary = _long_line(fh, line)
                if n is None:
                    break
                read += n
                off += n
                if boundary:
                    cur = 0
                elif t:
                    cur = t
                continue
            if read + len(line) > budget and read > 0:
                done = False
                break
            read += len(line)
            off += len(line)
            if b'"compact_boundary"' in line:
                cur = 0
                continue
            if b'"usage"' in line:
                t = _usage_total(line)
                if t:
                    cur = t
        tail = b""
        if off:
            k = min(TAIL_CHECK, off)
            fh.seek(off - k)
            tail = fh.read(k)
    return ({"dev": st.st_dev, "ino": st.st_ino, "off": off, "cur": cur,
             "tail": tail.hex()}, done, read)


def load_cache(session_id):
    try:
        with open(cache_path(session_id), encoding="utf-8") as f:
            raw = f.read(S.READ_MAX + 1)
        if len(raw) > S.READ_MAX:
            return {}
        d = json.loads(raw)
        if isinstance(d, dict) and d.get("v") == CACHE_V and isinstance(d.get("agents"), dict):
            return d["agents"]
    except Exception:
        pass
    return {}


def save_cache(session_id, agents):
    """Replace the session's cache atomically. Never raises."""
    tmp = None
    try:
        d = cache_dir()
        S._mkdir_private(d)
        fd, tmp = S._mkstemp(d, "." + S.safe_sid(session_id) + ".")
        with os.fdopen(fd, "w") as f:
            json.dump({"v": CACHE_V, "agents": agents}, f, separators=(",", ":"))
        os.replace(tmp, cache_path(session_id))
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def depths(payload):
    """{task id: exact depth} for the rows whose sidechain was read to its
    end and holds a usage line; updates the session's cache as it goes."""
    sid = payload.get("session_id")
    tp = payload.get("transcript_path")
    tasks = payload.get("tasks")
    if not isinstance(sid, str) or not sid or not isinstance(tasks, list):
        return {}
    old = load_cache(sid)
    rows = []
    for t in tasks[:TASKS_MAX]:
        tid = t.get("id") if isinstance(t, dict) else None
        if not isinstance(tid, str):
            continue
        try:
            path = sidechain(tp, sid, tid)
            st = os.stat(path) if path else None
        except Exception:
            path = st = None
        if not path:
            continue
        ent = old.get(tid)
        seen = ent.get("off") if isinstance(ent, dict) and ent.get("ino") == st.st_ino \
            and isinstance(ent.get("off"), int) and ent["off"] <= st.st_size else 0
        rows.append((st.st_size - seen, tid, path))
    # Least left to read first: the rows that can be exact this tick are,
    # and one agent catching up on a long transcript cannot starve the rest.
    rows.sort(key=lambda r: r[0])
    new, out, left = {}, {}, BUDGET
    for _todo, tid, path in rows:
        ent, done = old.get(tid), False
        if left > 0:
            try:
                ent, done, n = scan(path, ent, left)
                left -= n
            except Exception:
                ent = None
        if isinstance(ent, dict):
            new[tid] = ent
            if done and ent.get("cur"):
                out[tid] = ent["cur"]
    for tid, ent in old.items():    # rows not visible this tick keep their place
        if len(new) >= CACHE_MAX:
            break
        new.setdefault(tid, ent)
    if len(new) > CACHE_MAX:
        new = dict(list(new.items())[:CACHE_MAX])
    if new != old:
        save_cache(sid, new)
    return out


def one_line(s):
    """`s` on one printable line, or "" for a non-string: runs of whitespace
    and C0/C1 controls (ESC included) become one space, format and surrogate
    characters go."""
    if not isinstance(s, str):
        return ""
    s = "".join(ch for ch in s[:4096]
                if unicodedata.category(ch) not in ("Cf", "Cs"))
    return _UNSAFE.sub(" ", s).strip()


def width(ch):
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def fit(s, cols):
    """`s` cut to at most `cols` terminal columns, ending in an ellipsis
    when cut."""
    ws = [width(ch) for ch in s]
    if sum(ws) <= cols:
        return s
    if cols < 1:
        return ""
    used = cut = 0
    for i, w in enumerate(ws):
        if used + w > cols - 1:
            break
        used, cut = used + w, i + 1
    return s[:cut].rstrip() + "…"


def k(n):
    return f"{n // 1000}k" if n >= 1000 else str(n)


def fill(tokens, window, approx):
    """(plain text, coloured text) of the fill segment."""
    m = "~" if approx else ""
    if not window:
        text = f"{m}{k(tokens)}"
        return text, text
    pct = min(tokens * 100 // window, 100)
    text = f"{m}{pct}% {m}{k(tokens)}/{k(window)}"
    th = S.thresholds(window)
    left = max(window - tokens, 0)
    color = ("\033[32m" if left > th["due"] else
             "\033[33m" if left > th["hard"] else "\033[31m")
    return text, f"{color}{text}\033[0m"


def row(task, exact, cols):
    """The row body for one task, or None to keep Claude Code's default."""
    window = num(task.get("contextWindowSize")) or 0
    if exact:
        tokens, approx = exact, False
    else:
        tokens, approx = num(task.get("tokenCount")), True
        if not tokens:
            return None
    plain, colored = fill(tokens, window, approx)
    name = one_line(task.get("name"))
    desc = one_line(task.get("description")) or one_line(task.get("label"))
    head_plain = (name + SEP if name else "") + plain
    head = (name + SEP if name else "") + colored
    room = cols - sum(width(ch) for ch in head_plain)
    if room < 1:
        if name:        # too narrow for the name too: the fill alone
            return colored if sum(width(ch) for ch in plain) <= cols else None
        return colored if room == 0 else None
    if desc and room > len(SEP) + 1:
        return head + SEP + fit(desc, room - len(SEP))
    return head


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(d, dict) or not isinstance(d.get("tasks"), list):
        return
    cols = num(d.get("columns"))
    if cols is None:
        cols = 80       # absent: a common width; 0 is no room, so no rows

    try:
        exact = depths(d)
    except Exception:
        exact = {}
    lines = []
    for t in d["tasks"][:TASKS_MAX]:
        if not isinstance(t, dict) or not isinstance(t.get("id"), str):
            continue
        try:
            body = row(t, exact.get(t["id"]), cols)
        except Exception:
            body = None
        if body is not None:
            lines.append(json.dumps({"id": t["id"], "content": body}))
    if lines:
        print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:   # rows keep their default rendering; never a traceback
        pass
