"""The hub's hook registry, its config, hook health and display-text hygiene.

Stdlib only; nothing here raises to its caller. The contract these functions
enforce is skills/statusline-hub/references/hook-contract.md; read that first.

Layout, all under ${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/ (the hub dir):

    hooks.d/<name>.json   one manifest per hook, written by the plugin that owns
                          the hook from its own SessionStart (atomic replace)
    config.json           the user's order / disabled / separator / health window
    cache/<name>/<sid>.json  a display hook's last good text, per session
    log/<name>.log        a hook's stderr, capped

Trust: a manifest executes code, so it counts only when every one of these
holds, and is otherwise skipped (never run, never an error on the line):
- the hub dir and hooks.d are real directories (not symlinks), owned by this
  user, writable by nobody else (no group or other write bit);
- the manifest is a regular file (opened without following a symlink),
  owned by this user, writable by nobody else, at most MANIFEST_MAX bytes,
  touched within STALE_DAYS (a plugin refreshes its manifest every session
  start, so an uninstalled plugin's hook fades out, then is pruned) - unless
  it says "pinned": true, which a hand-written manifest may;
- the hub dir does not lie inside the session's project tree, unless that
  project is the home directory or above it; nor inside a git work tree (a
  `.git` in the config dir or any directory above it, up to but not
  including the home directory), unless it is the default ~/.claude - so a
  config dir relocated into a cloned repository never supplies hooks, even
  when Claude Code was started in a subdirectory or the payload names no dir;
- its fields validate (see parse()).
"""
import datetime, errno, json, math, os, re, shlex, stat, time, unicodedata

import tee

HUB = "statusline-hub"
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
KINDS = ("display", "record")
MANIFEST_MAX = 16384        # bytes; a manifest is a few hundred
MANIFESTS_MAX = 32          # manifests read at most, in name order
STALE_DAYS = 14             # a manifest not refreshed this long is ignored, then pruned
# (default, max) timeout per kind, in ms. A display hook runs on the render
# path, inside Claude Code's 300 ms debounce; a record hook runs detached.
TIMEOUTS = {"display": (150, 250), "record": (1000, 10000)}
TIMEOUT_MIN_MS = 10
ARGV_MAX = 64
ARG_MAX = 4096
CONFIG_MAX = 16384
HEALTH_MAX = 4096
HEALTH_IGNORE_S = 86400     # a health file untouched this long is stale: shows nothing
HEALTH_STALE_MIN = 15       # default N: no last_ok within N minutes of its latest write
HEALTH_STALE_MAX = 7 * 1440
SEPARATOR = "  "
SEPARATOR_MAX = 8
VISIBLE_MAX = 300           # printable characters kept from one hook's line
ORDER_MAX = 64


def hub_dir():
    return os.path.join(tee.base_dir(), HUB)


def hooks_dir():
    return os.path.join(hub_dir(), "hooks.d")


def config_path():
    return os.path.join(hub_dir(), "config.json")


def cache_dir():
    return os.path.join(hub_dir(), "cache")


def log_dir():
    return os.path.join(hub_dir(), "log")


def run_dir():
    return os.path.join(hub_dir(), "run")


def mkdirs_private(path):
    """Create `path` and any missing parents below the config dir, each 0700.
    Returns whether `path` is a directory afterwards; False, creating nothing
    further, at a component that is a symlink. Never raises."""
    try:
        base = os.path.abspath(tee.base_dir())
        path = os.path.abspath(path)
        if not path.startswith(base.rstrip(os.sep) + os.sep):
            return False
        parts = os.path.relpath(path, base).split(os.sep)
        cur = base
        for p in parts:
            cur = os.path.join(cur, p)
            try:
                os.mkdir(cur, 0o700)
            except FileExistsError:
                if os.path.islink(cur):
                    return False
        return os.path.isdir(path)
    except Exception:
        return False


def private_dir_problem(path):
    """None when `path` is a real directory owned by this user and writable by
    no one else; else a short reason."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unreadable"
    if stat.S_ISLNK(st.st_mode):
        return "a symlink"
    if not stat.S_ISDIR(st.st_mode):
        return "not a directory"
    if st.st_uid != os.geteuid():
        return "not owned by you"
    if st.st_mode & 0o022:
        return "group- or other-writable"
    return None


def _inside(path, root):
    root = root.rstrip(os.sep) or os.sep
    return path == root or path.startswith(root + os.sep)


def in_project(project_dirs):
    """Whether the hub dir lies inside one of the session's project dirs (a
    home directory, or a dir above it, does not count as a project tree)."""
    try:
        hub = os.path.realpath(hub_dir())
        home = os.path.realpath(os.path.expanduser("~"))
        for d in project_dirs:
            if not isinstance(d, str) or not d or "\0" in d:
                continue
            proj = os.path.realpath(d)
            if _inside(home, proj):
                continue
            if _inside(hub, proj):
                return True
    except Exception:
        return True  # cannot tell: no hooks, rather than a project's hooks
    return False


def in_git_tree():
    """Whether the config dir lies inside a git work tree: a `.git` (dir or
    file) in it or in any directory above it, stopping below the home
    directory (a home kept in git does not count). The default ~/.claude is
    exempt, since a repository cannot relocate it (a dotfiles repo there is
    the user's own). Fails closed."""
    try:
        cfg = os.path.realpath(tee.base_dir())
        home = os.path.realpath(os.path.expanduser("~"))
        if cfg == os.path.realpath(os.path.join(home, ".claude")):
            return False
        d = cfg
        while d != home:
            if os.path.lexists(os.path.join(d, ".git")):
                return True
            parent = os.path.dirname(d)
            if parent == d:
                return False
            d = parent
        return False
    except Exception:
        return True


def _read_capped(path, cap, follow=False):
    """(bytes, stat) of a regular file at path, read without following a final
    symlink (unless `follow`) and without blocking on a FIFO; None when it is
    not a regular file or is over `cap` bytes. Raises OSError."""
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
    if not follow:
        flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > cap:
            return None, st
        chunks, n = [], 0
        while n <= cap:
            b = os.read(fd, cap + 1 - n)
            if not b:
                break
            chunks.append(b)
            n += len(b)
        if n > cap:
            return None, st
        return b"".join(chunks), st
    finally:
        os.close(fd)


def _int(x):
    return x if type(x) is int else None


def _argv(command, shell):
    """The argv to exec for a manifest's command, or None when it is invalid.

    - a JSON array of strings: exec'd as is (the preferred form);
    - a string: split by POSIX shell-word rules (shlex) and exec'd - no shell
      runs, so no expansion, globbing, redirection or `;`;
    - only with `"shell": true`, a string runs as `/bin/sh -c <string>`.
    The program (argv[0]) is a bare name looked up on PATH or an absolute
    path; a relative path with a slash never counts (hooks run with the hub
    dir as their working directory, never the project's)."""
    if shell is True:
        if not isinstance(command, str) or not command.strip() or "\0" in command \
                or len(command) > ARG_MAX:
            return None
        return ["/bin/sh", "-c", command]
    if isinstance(command, str):
        if len(command) > ARG_MAX * 4:
            return None
        try:
            argv = shlex.split(command)
        except ValueError:
            return None
    elif isinstance(command, list):
        argv = command
    else:
        return None
    if not 1 <= len(argv) <= ARGV_MAX:
        return None
    for a in argv:
        if not isinstance(a, str) or "\0" in a or len(a) > ARG_MAX:
            return None
    prog = argv[0]
    if not prog or ("/" in prog and not os.path.isabs(prog)):
        return None
    return list(argv)


def _health_path(p):
    """The resolved health path when it is absolute and inside the config
    dir, else None."""
    try:
        if not isinstance(p, str) or not p or "\0" in p or not os.path.isabs(p):
            return None
        base = os.path.realpath(tee.base_dir())
        real = os.path.realpath(p)
        return real if real != base and _inside(real, base) else None
    except Exception:
        return None


def parse(name, raw):
    """A validated hook dict from a manifest's bytes, or (None, reason).

    Fields: name (must equal the file name), kind ("display" | "record"),
    command (see _argv), shell (optional bool, default false), timeout_ms
    (optional int, clamped to the kind's range), health_path (optional),
    order (optional int hint), pinned (optional bool: exempt from the
    staleness rule), v (optional, must be 1). Other keys are
    ignored, so a newer manifest stays readable."""
    try:
        d = json.loads(raw.decode("utf-8"))
    except Exception:
        return None, "not JSON"
    if not isinstance(d, dict):
        return None, "not a JSON object"
    if "v" in d and _int(d.get("v")) != 1:
        return None, "unknown version"
    if d.get("name") != name:
        return None, "name does not match the file name"
    kind = d.get("kind")
    if kind not in KINDS:
        return None, "kind is not display or record"
    shell = d.get("shell", False)
    if not isinstance(shell, bool):
        return None, "shell is not true or false"
    pinned = d.get("pinned", False)
    if not isinstance(pinned, bool):
        return None, "pinned is not true or false"
    argv = _argv(d.get("command"), shell)
    if argv is None:
        return None, "command is not valid"
    default, top = TIMEOUTS[kind]
    t = _int(d.get("timeout_ms"))
    t = default if t is None or t <= 0 else min(max(t, TIMEOUT_MIN_MS), top)
    hook = {"name": name, "kind": kind, "argv": argv, "timeout_ms": t,
            "order": _int(d.get("order")) or 0, "health_path": None, "pinned": pinned}
    if d.get("health_path") is not None:
        hook["health_path"] = _health_path(d.get("health_path"))
    return hook, None


def scan(now=None, project_dirs=()):
    """([trusted hooks], [(name or file, reason)]) for every manifest in
    hooks.d, in name order, before config is applied. Never raises."""
    hooks, problems = [], []
    try:
        now = time.time() if now is None else now
        for d in (hub_dir(), hooks_dir()):
            why = private_dir_problem(d)
            if why:
                if why != "missing":
                    problems.append((d, why))
                return hooks, problems
        if in_project(project_dirs):
            problems.append((hub_dir(), "inside the project tree"))
            return hooks, problems
        if in_git_tree():
            problems.append((hub_dir(), "inside a git work tree"))
            return hooks, problems
        names = sorted(n for n in os.listdir(hooks_dir()) if n.endswith(".json")
                       and not n.startswith("."))
        for fn in names[:MANIFESTS_MAX]:
            name = fn[:-5]
            if not NAME_RE.fullmatch(name):
                problems.append((fn, "file name is not a hook name"))
                continue
            try:
                raw, st = _read_capped(os.path.join(hooks_dir(), fn), MANIFEST_MAX)
            except OSError as e:
                problems.append((name, "a symlink" if e.errno == errno.ELOOP
                                 else "unreadable"))
                continue
            if raw is None:
                problems.append((name, "not a regular file, or too large"))
                continue
            if st.st_uid != os.geteuid():
                problems.append((name, "not owned by you"))
                continue
            if st.st_mode & 0o022:
                problems.append((name, "group- or other-writable"))
                continue
            hook, why = parse(name, raw)
            if hook is None:
                problems.append((name, why))
                continue
            if not hook["pinned"] and now - st.st_mtime > STALE_DAYS * 86400:
                problems.append((name, f"not refreshed for {STALE_DAYS} days"))
                continue
            hooks.append(hook)
        for fn in names[MANIFESTS_MAX:]:
            problems.append((fn, f"over {MANIFESTS_MAX} manifests"))
    except Exception:
        pass
    return hooks, problems


def config():
    """The user's config.json, validated: {"order": [names], "disabled":
    set(names), "separator": str, "health_stale_min": int}. Defaults for
    anything missing or malformed; never raises."""
    out = {"order": [], "disabled": set(), "separator": SEPARATOR,
           "health_stale_min": HEALTH_STALE_MIN}
    try:
        raw, _ = _read_capped(config_path(), CONFIG_MAX, follow=True)
        d = json.loads(raw.decode("utf-8")) if raw is not None else None
    except Exception:
        return out
    if not isinstance(d, dict):
        return out
    for key in ("order", "disabled"):
        v = d.get(key)
        if isinstance(v, list):
            names = [n for n in v[:ORDER_MAX] if isinstance(n, str) and NAME_RE.fullmatch(n)]
            out[key] = names if key == "order" else set(names)
    sep = d.get("separator")
    if isinstance(sep, str):
        sep = "".join(c for c in _ESCAPE.sub("", sep)
                      if unicodedata.category(c) not in ("Zl", "Zp")
                      and unicodedata.category(c)[0] != "C")
        out["separator"] = sep[:SEPARATOR_MAX]
    n = _int(d.get("health_stale_min"))
    if n is not None and n > 0:
        out["health_stale_min"] = min(n, HEALTH_STALE_MAX)
    return out


def arrange(hooks, cfg):
    """Enabled hooks in display order: the user's `order` first, then the rest
    by their `order` hint, then name."""
    rank = {n: i for i, n in enumerate(cfg["order"])}
    live = [h for h in hooks if h["name"] not in cfg["disabled"]]
    return sorted(live, key=lambda h: (rank.get(h["name"], len(rank)), h["order"], h["name"]))


def load(now=None, project_dirs=(), cfg=None):
    """The enabled, trusted hooks in display order. Never raises."""
    try:
        cfg = config() if cfg is None else cfg
        return arrange(scan(now, project_dirs)[0], cfg)
    except Exception:
        return []


def find(name, now=None):
    """The trusted manifest `name` as a hook dict (config not applied), or
    None."""
    for h in scan(now)[0]:
        if h["name"] == name:
            return h
    return None


# -- health ------------------------------------------------------------------

def _stamp(x):
    """An epoch-seconds time from a number or an ISO-8601 string, or None."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x) if math.isfinite(x) and x > 0 else None
    if isinstance(x, str) and 0 < len(x) <= 64:
        try:
            t = datetime.datetime.fromisoformat(x)
            if t.tzinfo is None:
                t = t.replace(tzinfo=datetime.timezone.utc)
            return t.timestamp()
        except Exception:
            return None
    return None


def health(path, now=None, stale_min=HEALTH_STALE_MIN):
    """"warn" when the health file at `path` says the hook's last run errored,
    or that it has had no last_ok within `stale_min` minutes of the file's
    latest write; None otherwise - and None for a file that is missing, not
    regular, over HEALTH_MAX, untouched for HEALTH_IGNORE_S, malformed, or
    that shows no run yet. One capped read; never raises."""
    try:
        if not path:
            return None
        now = time.time() if now is None else now
        raw, st = _read_capped(path, HEALTH_MAX)
        if raw is None or now - st.st_mtime > HEALTH_IGNORE_S:
            return None
        d = json.loads(raw.decode("utf-8"))
        if not isinstance(d, dict):
            return None
        runs = d.get("runs")
        if type(runs) is int and runs <= 0:
            return None
        ok, err = _stamp(d.get("last_ok")), _stamp(d.get("last_error"))
        if ok is None and err is None:
            return None
        if err is not None and (ok is None or err >= ok):
            return "warn"
        if ok is not None and st.st_mtime - ok > stale_min * 60:
            return "warn"
        return None
    except Exception:
        return None


# -- display text ------------------------------------------------------------

_SGR = re.compile(r"\x1b\[[0-9;:]{0,48}m")
# Any other escape sequence: CSI, OSC / DCS / SOS / PM / APC strings (to BEL or
# ST), or a lone two-character escape.
_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]?|[\]PX^_][^\x07\x1b]*(?:\x07|\x1b\\)?|.)?",
                     re.S)
ZWJ = "\u200d"
RESET = "\x1b[0m"


def sanitise(text):
    """One line of hook output made safe to print: only the first line; SGR
    colour sequences (ESC [ digits m) kept, every other escape sequence (cursor
    moves, window titles, hyperlinks, clears) dropped; other control
    characters (C0, DEL, C1) dropped, a tab becoming a space; Unicode format
    characters (bidi overrides, zero-width padding; category Cf, except a
    joiner), the Unicode line and paragraph separators (Zl, Zp) and lone surrogates dropped; at most VISIBLE_MAX printable
    characters; ends with a colour reset when it used colour, so nothing
    bleeds into the next hook's text. Returns "" for a non-string. Never
    raises."""
    if not isinstance(text, str):
        return ""
    try:
        text = text.split("\n", 1)[0].replace("\t", " ")
        out, i, n, seen, sgr = [], 0, len(text), 0, False
        while i < n and seen < VISIBLE_MAX:
            ch = text[i]
            if ch == "\x1b":
                m = _SGR.match(text, i)
                if m:
                    out.append(m.group())
                    sgr = True
                    i = m.end()
                    continue
                m = _ESCAPE.match(text, i)
                i = m.end() if m and m.end() > i else i + 1
                continue
            i += 1
            cat = unicodedata.category(ch)
            if cat in ("Cc", "Cs", "Zl", "Zp") or (cat == "Cf" and ch != ZWJ):
                continue
            out.append(ch)
            seen += 1
        s = "".join(out).rstrip()
        if not _SGR.sub("", s).strip():
            return ""
        return s + RESET if sgr else s
    except Exception:
        return ""
