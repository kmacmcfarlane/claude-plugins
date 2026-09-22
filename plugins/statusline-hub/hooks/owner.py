"""Ownership of the `statusLine` settings entry, for the hub. Stdlib only.

Used by the SessionStart hook (session_start.py: first-run install, takeover,
self-heal) and by the install-statusline-hub skill's script (explicit install,
remove, replace). Both write settings only through write_settings().

- Own entry: a command running .../plugins/data/statusline-hub-<marketplace>/
  current-hooks/hub.py - the update-stable path this plugin's SessionStart
  symlink keeps current.
- The statusline footer's own entry (.../plugins/data/statusline-<marketplace>/
  current-hooks/statusline.py, as an earlier version of the statusline plugin
  installed it; or the same under the claude-kit- or context-guard- data dir,
  where older copies of that footer lived): taken over only once the
  statusline plugin has registered itself as a hub display hook (a trusted
  hooks.d/statusline.json of kind display), so the footer keeps drawing - see
  session_start.py.
- Anything else is foreign: never modified without the user's explicit consent
  (the installer's --replace, or its --wrap).

Wrap mode (the installer's --wrap, only ever on the user's word, and only
for the user settings file - registry.wrap_applies): the hub's entry
replaces a foreign one, and the foreign entry is kept in the hub's
wrap record, <config>/statusline-hub/wrap.json (registry.read_wrap: private,
0600, the trust rules of a hook manifest, since the hub runs it). The hub's
entry keeps the foreign entry's other keys (padding, say) and swaps only the
command. Each render runs the kept command, unparsed, through /bin/sh as
Claude Code would, and shows its output (hub.py). --unwrap puts the kept
entry back - its value's original text, spliced in place, so the file is
byte-for-byte as it was when nothing else changed; at the least, the entry
and its command string are exactly the same.

The settings write started as the statusline plugin's own; since that plugin
draws as a hub display hook it writes no settings, and this is the only copy.
It changes only the `statusLine` key: the file is resolved through symlinks
(a dotfiles link stays a link), read afresh at write time, changed, and
written to a temp file in the same dir with the original mode, then
os.replace()d - never truncated in place. The new text splices just that
key's member into the original text (splice_key), so a hand-formatted file
keeps every other byte; when a splice is not provably right it falls back to
re-serialising the whole file in its own layout (dumps_like). Nothing is
written when nothing changes, and a read-only file is refused unless the
caller has the user's consent to write it. Messages name paths only, never
setting values. `sensor` is this plugin's tee module, which carries the
sensor helpers (base_dir, _load, _is_v, _mkstemp).

The marker, <plugin data>/owner.json (the statusline plugin's earlier
versions kept one of the same shape in their own data dir, which the
takeover reads):
  {"v": 1, "state": "installed" | "removed" | "yielded" | "deferred" | "blocked"
                    | "wrapping" | "unwrapped",
   "settings": "<abs path>", "command": "<our command>", "at": <epoch s>}
- installed: the entry in `settings` is ours; SessionStart restores it when a
  stale session's settings write drops it.
- removed: the user ran --remove (or had removed the statusline footer from
  that file before the hub arrived); nothing re-adds it until they install
  again.
- yielded: something else replaced our entry; left alone for good.
- deferred: a statusLine was already set on first run; never overwritten.
- blocked: the settings file could not be used (not valid JSON, read-only,
  unwritable, or a project file git does not ignore); said once, retried
  quietly every session. Extra fields: "reason", and "resume" - the state
  whose work is retried ("installed" or "wrapping" or "unwrapped" for a
  heal, "new" for a first run).
- wrapping: the entry in `settings` is ours, running the wrapped entry the
  wrap record keeps; SessionStart restores it when a stale session's write
  drops it or puts the wrapped entry back, and yields to anything else.
- unwrapped: the user ran --unwrap; SessionStart puts the kept entry back
  if a stale session's write restores ours, and otherwise does nothing.
(An older hub version reads the last two as "hands off".)
The marker stores only our own command and a path; the wrapped entry lives
in the wrap record alone.
"""
import json, os, re, stat, time

import registry
import tee as sensor

PLUGIN = "statusline-hub"
SCRIPT = "hub.py"
STATUSLINE = "statusline"

# Data dirs the statusline footer's own entry has run from: the statusline
# plugin's, and those of the plugins that shipped the footer before it.
FOOTER_HOMES = (STATUSLINE, "context-guard", "claude-kit")

_SHAPE = r'\s*python3\s+"?(?:[^"\\]|\\.)*/plugins/data/{}-[^/"]+/current-hooks/{}"?\s*'
OWN_RE = re.compile(_SHAPE.format(re.escape(PLUGIN), re.escape(SCRIPT)))
STATUSLINE_RE = re.compile(_SHAPE.format(
    "(?:" + "|".join(map(re.escape, FOOTER_HOMES)) + ")", re.escape("statusline.py")))

MARKER = "owner.json"
MARKER_V = 1


class SettingsError(Exception):
    """A settings file that exists but is not a readable JSON object.
    `path` names it; `reason` is "invalid", "read-only" or "unwritable"."""
    reason = "invalid"

    def __init__(self, msg, path=None):
        super().__init__(msg)
        self.path = path


class Changed(Exception):
    """The statusLine entry changed on disk between the caller's check and
    the write (write_settings `expect`); nothing was written."""


def hooks_dir():
    return os.path.dirname(os.path.abspath(__file__))


def plugin_root():
    return os.path.dirname(hooks_dir())


def data_root():
    return os.path.join(sensor.base_dir(), "plugins", "data")


def data_name(plugin_id):
    """The data-dir name Claude Code gives a plugin id (`<name>@<marketplace>`):
    every character outside [A-Za-z0-9_-] replaced by "-", so
    statusline-hub@my.mkt -> statusline-hub-my-mkt. The one rule every data-dir
    name here comes from."""
    return re.sub(r"[^A-Za-z0-9_-]", "-", plugin_id)


def data_dir(script_path=None, scan=True):
    """This plugin's persistent data dir, first match of:
    1. $CLAUDE_PLUGIN_DATA (set for hooks; not in the Bash tool's environment);
    2. the harness's install record: the `statusline-hub@<mkt>` entry of
       <config>/plugins/installed_plugins.json whose installPath holds the
       code running now (script_path) names it, <data>/<id> with Claude
       Code's id rule (installed_by_record);
    3. the name derived from the plugin cache path this code runs from
       (plugins/cache/<mkt>/statusline-hub/ -> the id statusline-hub@<mkt>,
       named by data_name);
    4. with `scan`, the first <config>/plugins/data/statusline-hub-* dir -
       a guess when the plugin came from several marketplaces, so last. A
       dir whose current-hooks link leads somewhere without SCRIPT is not
       this plugin's and is never taken.
    None when none of those applies."""
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    if d:
        return d
    here = os.path.abspath(script_path or __file__)
    base = data_root()
    d = installed_by_record(here)
    if d:
        return d
    m = re.search(r"/plugins/cache/([^/]+)/" + re.escape(PLUGIN) + "/", here)
    if m:
        return os.path.join(base, data_name(f"{PLUGIN}@{m.group(1)}"))
    try:
        for name in (sorted(os.listdir(base)) if scan else ()):
            d = os.path.join(base, name)
            hooks = os.path.join(d, "current-hooks")
            if name.startswith(PLUGIN + "-") and os.path.isdir(d) and (
                    not os.path.lexists(hooks) or
                    os.path.isfile(os.path.join(hooks, SCRIPT))):
                return d
    except OSError:
        pass
    return None


def installed_by_record(path):
    """The data dir of the `statusline-hub@<mkt>` install whose installPath
    (in <config>/plugins/installed_plugins.json, `plugins` -> key -> list of
    records) contains `path`, or None. The dir is <config>/plugins/data/ and
    the key's data_name (Claude Code's own rule, so statusline-hub@mkt ->
    statusline-hub-mkt).
    Reads key names and install paths only. Never raises."""
    try:
        rec = os.path.join(sensor.base_dir(), "plugins", "installed_plugins.json")
        if not stat.S_ISREG(os.stat(rec).st_mode):      # a FIFO would hang the hook
            return None
        with open(rec, encoding="utf-8") as f:
            recs = json.load(f).get("plugins")
        here = os.path.realpath(path)
        for key, entries in (recs.items() if isinstance(recs, dict) else ()):
            if not (isinstance(key, str) and key.startswith(PLUGIN + "@")):
                continue
            for e in (entries if isinstance(entries, list) else ()):
                ip = e.get("installPath") if isinstance(e, dict) else None
                if not (isinstance(ip, str) and ip):
                    continue
                root = os.path.realpath(ip)
                if here == root or here.startswith(root.rstrip(os.sep) + os.sep):
                    return os.path.join(data_root(), data_name(key))
    except Exception:
        pass
    return None


_SH_SPECIAL = re.compile(r'([\\"$`])')


def _parse(text, path):
    """A settings file's text as a dict: empty (or whitespace only) is {}.
    Raises SettingsError otherwise."""
    if not text.strip():
        return {}
    try:
        d = json.loads(text)
    except ValueError as e:
        raise SettingsError(f"{path} is not readable JSON", path) from e
    if not isinstance(d, dict):
        raise SettingsError(f"{path} is not a JSON object", path)
    return d


def _read_text(path):
    """The file's text exactly (line endings kept), or None when missing."""
    try:
        with open(path, encoding="utf-8", newline="") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as e:
        raise SettingsError(f"{path} is not readable JSON", path) from e


def read_settings(path):
    """The settings object at path ({} when the file does not exist or is
    empty). Raises SettingsError when it is anything but a JSON object."""
    text = _read_text(path)
    return {} if text is None else _parse(text, path)


def _default_mode():
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def atomic_write_text(path, text, mode=None, force_mode=False):
    """Write text to path's real target via a same-dir temp file and
    os.replace. Keeps the existing file's mode (else `mode`, else the umask
    default; with `force_mode`, always `mode`). On any failure the original
    is untouched and the temp removed; the error propagates."""
    real = os.path.realpath(path)
    d = os.path.dirname(real)
    os.makedirs(d, exist_ok=True)
    try:
        if force_mode:
            raise FileNotFoundError
        mode = os.stat(real).st_mode & 0o7777
    except FileNotFoundError:
        mode = _default_mode() if mode is None else mode
    fd, tmp = sensor._mkstemp(d, "." + os.path.basename(real) + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, real)
        tmp = None
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def atomic_write_json(path, data, mode=None, force_mode=False):
    atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", mode,
                      force_mode)


_INDENT = re.compile(r'\n([ \t]+)"')
_ESCAPED = re.compile(r"\\u[0-9a-fA-F]{4}")


def _layout(original):
    """json.dumps keywords for the layout of `original`: the same indent unit
    (spaces or a tab), one-line when it was one line, \\u escapes when it
    used them for non-ASCII. Two-space indent when there is no original."""
    kw = {"ensure_ascii": False, "indent": 2}
    if original and original.strip():
        m = _INDENT.search(original)
        if m:
            kw["indent"] = m.group(1)
        elif "\n" not in original.strip() and original.strip() != "{}":
            kw["indent"] = None
            kw["separators"] = (", ", ": ") if '": ' in original else (",", ":")
        if original.isascii() and _ESCAPED.search(original):
            kw["ensure_ascii"] = True
    return kw


def dumps_like(data, original):
    """data serialised in the layout of `original` (the file's previous text,
    see _layout), with a final newline when it had one. For a file written by
    json.dumps / JSON.stringify with an indent - what Claude Code writes -
    only the changed key's lines differ; a hand-formatted file with mixed
    layouts is re-indented throughout, which is why write_settings splices
    first. With no original, two-space indent and a final newline."""
    end = "\n"
    if original and original.strip():
        end = "\n" if original.endswith("\n") else ""
    return json.dumps(data, **_layout(original)) + end


_WS = " \t\r\n"
_MISSING = object()


def _skip_ws(s, i):
    while s[i] in _WS:
        i += 1
    return i


def _end_of_string(s, i):
    """Index just past the JSON string starting at s[i] == '"'."""
    i += 1
    while s[i] != '"':
        i += 2 if s[i] == "\\" else 1
    return i + 1


def _end_of_value(s, i):
    """Index just past the JSON value starting at s[i] (no leading space)."""
    if s[i] == '"':
        return _end_of_string(s, i)
    if s[i] in "{[":
        depth = 0
        while True:
            c = s[i]
            if c == '"':
                i = _end_of_string(s, i)
                continue
            if c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
    j = i
    while j < len(s) and s[j] not in ",}]" + _WS:
        j += 1
    if j == i:
        raise ValueError("no value")
    return j


def _members(s):
    """The top-level object's members as (key, key_start, key_end,
    value_start, value_end) spans. Raises on anything it cannot follow."""
    i = _skip_ws(s, 0)
    if s[i] != "{":
        raise ValueError("not an object")
    i = _skip_ws(s, i + 1)
    out = []
    if s[i] == "}":
        return out
    while True:
        ks = i
        ke = _end_of_string(s, ks)
        i = _skip_ws(s, ke)
        if s[i] != ":":
            raise ValueError("no colon")
        vs = _skip_ws(s, i + 1)
        ve = _end_of_value(s, vs)
        out.append((json.loads(s[ks:ke]), ks, ke, vs, ve))
        i = _skip_ws(s, ve)
        if s[i] == "}":
            return out
        if s[i] != ",":
            raise ValueError("no comma")
        i = _skip_ws(s, i + 1)


def _lead(s, i):
    """The whitespace that starts the line holding s[i], or None when
    something other than whitespace precedes s[i] on that line."""
    start = s.rfind("\n", 0, i) + 1
    lead = s[start:i]
    return lead if lead.strip(" \t") == "" else None


def splice_key(original, key, value=_MISSING):
    """`original` (a settings file's text) with only the top-level member
    `key` set to `value` - replaced in place, or appended after the last
    member - or, with no `value`, deleted. Every other byte is kept, so a
    hand-formatted file (mixed indents, one-line nested objects) is not
    re-indented. The new member is laid out like its
    neighbours: the key line's indent, the file's indent unit, its key
    separator. Returns None whenever that cannot be done safely - an empty
    object, the key's only member deleted, the key repeated, text it cannot
    follow; the caller then falls back to dumps_like."""
    try:
        members = _members(original)
        hits = [m for m in members if m[0] == key]
        if len(hits) > 1 or not members:
            return None
        kw = _layout(original)
        rendered = None
        if value is not _MISSING:
            rendered = json.dumps(value, **kw)
        if hits:
            _, ks, _, vs, ve = hits[0]
            if rendered is not None:
                lead = _lead(original, ks)
                if lead:
                    rendered = rendered.replace("\n", "\n" + lead)
                return original[:vs] + rendered + original[ve:]
            n = members.index(hits[0])
            if len(members) == 1:
                return None
            if n == 0:
                return original[:ks] + original[members[1][1]:]
            return original[:members[n - 1][4]] + original[ve:]
        if rendered is None:
            return original
        last = members[-1]
        lead = _lead(original, last[1])
        if len(members) > 1:
            sep = original[members[-2][4]:last[1]]
        elif lead is not None:
            sep = ",\n" + lead
        else:
            sep = (kw.get("separators") or (", ", ": "))[0]
        colon = original[last[2]:last[3]]
        if colon not in (":", ": "):
            colon = ": " if kw.get("indent") is not None else \
                (kw.get("separators") or (", ", ": "))[1]
        if lead:
            rendered = rendered.replace("\n", "\n" + lead)
        member = sep + json.dumps(key, ensure_ascii=kw["ensure_ascii"]) + colon + rendered
        return original[:last[4]] + member + original[last[4]:]
    except (ValueError, IndexError, TypeError):
        return None


def _splice_settings(original, data):
    """The splice for writing `data` over `original`, when the two differ in
    exactly one top-level key and every other key keeps its place; checked by
    parsing the result back. None when that does not hold."""
    try:
        old = json.loads(original)
    except ValueError:
        return None
    if not isinstance(old, dict) or not isinstance(data, dict):
        return None
    changed = [k for k in dict.fromkeys(list(old) + list(data))
               if old.get(k, _MISSING) != data.get(k, _MISSING)]
    if len(changed) != 1:
        return None
    key = changed[0]
    if [k for k in old if k != key] != [k for k in data if k != key]:
        return None
    text = splice_key(original, key, data.get(key, _MISSING))
    if text is None:
        return None
    try:
        back = json.loads(text)
    except ValueError:
        return None
    if back != data or list(back) != list(data):
        return None
    return text


def _splice_raw(original, data, raw):
    """`original` with the statusLine member's value text replaced by `raw`
    verbatim - how unwrap puts an entry back exactly as it was written -
    when that member is there once and the result parses to `data` with
    the key order kept. None otherwise."""
    try:
        if json.loads(raw) != data.get("statusLine", _MISSING):
            return None
        hits = [m for m in _members(original) if m[0] == "statusLine"]
        if len(hits) != 1:
            return None
        _, _, _, vs, ve = hits[0]
        text = original[:vs] + raw + original[ve:]
        back = json.loads(text)
        if back != data or list(back) != list(data):
            return None
        return text
    except (ValueError, IndexError, TypeError):
        return None


def statusline_raw(path):
    """(the statusLine value, its text as written in the file) for the
    settings file at path - the text with CRLF read as LF, None when it
    cannot be isolated. (None, None) when the file or the key is missing.
    Raises SettingsError as read_settings does."""
    text = _read_text(os.path.realpath(path))
    if text is None:
        return None, None
    entry = _parse(text, path).get("statusLine")
    if entry is None:
        return None, None
    base = text.replace("\r\n", "\n") if _crlf(text) else text
    try:
        hits = [m for m in _members(base) if m[0] == "statusLine"]
        if len(hits) == 1:
            raw = base[hits[0][3]:hits[0][4]]
            if json.loads(raw) == entry:
                return entry, raw
    except (ValueError, IndexError, TypeError):
        pass
    return entry, None


class ReadOnly(SettingsError):
    """A settings file the user cannot write (mode 0444, say)."""
    reason = "read-only"


def _crlf(text):
    """Whether text uses CRLF line endings throughout."""
    return "\r\n" in text and text.count("\n") == text.count("\r\n")


def write_settings(path, entry, allow_read_only=False, expect=None, expect_entry=_MISSING,
                   raw=None):
    """Set the statusLine key of the settings file at path (through a
    symlink) to `entry`, or delete it when `entry` is None. Returns whether
    it wrote.

    It never writes a settings object the caller read earlier: it reads the
    file now, changes only statusLine in that fresh value, and replaces the
    file atomically - so a change another process made to any other key
    since the caller looked is kept. The window left is the few
    milliseconds between this read and the replace. `expect`, when given,
    is the set of classify() kinds the fresh statusLine may have; anything
    else raises Changed, writing nothing. `expect_entry`, when given, is the
    exact statusLine value (None: absent) the file must still hold, else
    Changed.

    Text: when only statusLine changes, only that member's text changes
    (_splice_settings); else the whole file is re-serialised in its layout
    (dumps_like). `raw`, the entry's own text (statusline_raw), is spliced
    in verbatim when the key is there to splice it into. CRLF line endings
    are kept. An empty file counts as {}.
    Raises SettingsError, writing nothing, when the file is not a JSON
    object, and ReadOnly when the user may not write it - replacing it would
    still succeed in a writable dir, overriding a deliberate read-only -
    unless `allow_read_only` (the user's explicit consent, never assumed)."""
    real = os.path.realpath(path)
    original = _read_text(real)
    current = {} if original is None else _parse(original, path)
    if expect is not None and classify(current.get("statusLine")) not in expect:
        raise Changed(f"the statusLine in {path} changed meanwhile")
    if expect_entry is not _MISSING and current.get("statusLine") != expect_entry:
        raise Changed(f"the statusLine in {path} changed meanwhile")
    data = dict(current)
    if entry is None:
        data.pop("statusLine", None)
    else:
        data["statusLine"] = entry
    if data == current and list(data) == list(current):
        return False
    if original is not None and not allow_read_only and not os.access(real, os.W_OK):
        raise ReadOnly(f"{path} is read-only", path)
    crlf = original is not None and _crlf(original)
    base = original.replace("\r\n", "\n") if crlf else original
    text = None
    if raw is not None and entry is not None and base and base.strip():
        text = _splice_raw(base, data, raw)
    if text is None and base and base.strip():
        text = _splice_settings(base, data)
    if text is None:
        text = dumps_like(data, base)
    atomic_write_text(path, text.replace("\n", "\r\n") if crlf else text)
    return True


def enabled_in(settings):
    """Whether a settings object enables this plugin (an `enabledPlugins` key
    `statusline-hub@<marketplace>` set to true). Reads key names only."""
    ep = settings.get("enabledPlugins") if isinstance(settings, dict) else None
    return isinstance(ep, dict) and any(
        isinstance(k, str) and k.startswith(PLUGIN + "@") and v is True
        for k, v in ep.items())


def read_marker(data):
    d = sensor._load(os.path.join(data, MARKER)) if data else None
    return d if sensor._is_v(d, MARKER_V) else None


def write_marker(data, state, settings, command, **extra):
    """Record `state` for `settings`; `extra` adds fields (a blocked state's
    reason and the state it resumes)."""
    atomic_write_json(os.path.join(data, MARKER),
                      dict({"v": MARKER_V, "state": state,
                            "settings": os.path.abspath(settings), "command": command,
                            "at": time.time()}, **extra), mode=0o600)


def wrap_entry(inner, data):
    """The hub's entry that wraps `inner`: inner's keys, in inner's order,
    with only the command swapped for ours."""
    e = dict(inner)
    e["command"] = command_for(data)
    return e


def write_wrap(settings, entry, raw, running):
    """Write the wrap record (registry.read_wrap) atomically, 0600, in the
    private hub dir; raises SettingsError when that dir fails the trust
    rules, so nothing is kept where the hub would refuse to run it."""
    registry.mkdirs_private(registry.hub_dir())
    why = registry.hub_problem()
    if why:
        raise SettingsError(f"{registry.hub_dir()} is {why}", registry.hub_dir())
    atomic_write_json(registry.wrap_path(),
                      {"v": registry.WRAP_V, "settings": os.path.abspath(settings),
                       "entry": entry, "raw": raw, "running": running,
                       "at": time.time()}, mode=0o600, force_mode=True)


def set_running(rec, running):
    """Rewrite the wrap record `rec` (read_wrap's) with `running`."""
    write_wrap(rec["settings"], rec["entry"], rec["raw"], running)


def drop_wrap():
    """Delete the wrap record. Never raises."""
    try:
        os.unlink(registry.wrap_path())
    except OSError:
        pass


def _same_path(a, b):
    try:
        return os.path.realpath(a) == os.path.realpath(b)
    except Exception:
        return False


def ensure_hooks_symlink(data):
    """Create <data>/current-hooks -> this plugin's hooks dir, as the
    SessionStart hook does (ln -sfn), for a session that started before the
    plugin loaded. Leaves a link that already resolves alone."""
    link = os.path.join(data, "current-hooks")
    if os.path.isdir(link):
        return
    os.makedirs(data, exist_ok=True)
    tmp = link + ".tmp"
    try:
        if os.path.lexists(tmp):
            os.remove(tmp)
        os.symlink(hooks_dir(), tmp)
        os.replace(tmp, link)  # atomic; also replaces a dangling link
    except OSError:
        pass



def command_for(data):
    """`python3 "<data>/current-hooks/hub.py"`: the path in shell double
    quotes (\\, ", $ and ` escaped), kept as UTF-8."""
    path = os.path.join(data, "current-hooks", SCRIPT)
    return 'python3 "' + _SH_SPECIAL.sub(r"\\\1", path) + '"'


def classify(entry):
    """'absent', 'own', 'statusline' (the statusline footer's own entry,
    from the statusline plugin or an older copy - FOOTER_HOMES) or 'foreign'
    for a statusLine value."""
    if entry is None:
        return "absent"
    cmd = entry.get("command") if isinstance(entry, dict) else None
    if not isinstance(cmd, str):
        return "foreign"
    if OWN_RE.fullmatch(cmd):
        return "own"
    if STATUSLINE_RE.fullmatch(cmd):
        return "statusline"
    return "foreign"


def enabled_for(settings, plugin):
    """Whether a settings object enables `plugin` (an `enabledPlugins` key
    `<plugin>@<marketplace>` set to true). Reads key names only."""
    ep = settings.get("enabledPlugins") if isinstance(settings, dict) else None
    return isinstance(ep, dict) and any(
        isinstance(k, str) and k.startswith(plugin + "@") and v is True
        for k, v in ep.items())


def statusline_markers(own=None):
    """The statusline plugin's owner.json markers, read-only: one entry per
    statusline data dir under <config>/plugins/data/ - the marker dict, or
    None when that dir has none (its first run has not happened, or it lost
    it). A dir counts when it holds current-hooks/statusline.py or a marker
    whose command is the statusline's; this plugin's own data dir (`own`)
    never does. Never raises."""
    out = []
    base = data_root()
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return out
    for name in names:
        if not name.startswith(STATUSLINE + "-"):
            continue
        d = os.path.join(base, name)
        if own and _same_path(d, own):
            continue
        try:
            m = read_marker(d)
            cmd = m.get("command") if m else None
            if (isinstance(cmd, str) and STATUSLINE_RE.fullmatch(cmd)) or \
                    os.path.isfile(os.path.join(d, "current-hooks", "statusline.py")):
                out.append(m)
        except Exception:
            continue
    return out
