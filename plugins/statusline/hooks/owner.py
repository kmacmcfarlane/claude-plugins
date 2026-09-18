"""Ownership of the `statusLine` settings entry. Stdlib only.

Used by the install-statusline skill's script (explicit install and remove) and
by the SessionStart hook, session_start.py (first-run install, takeover,
self-heal). Both write settings only through write_settings().

- Own entry: a command running .../plugins/data/statusline-<marketplace>/
  current-hooks/statusline.py - the update-stable path this plugin's
  SessionStart symlink keeps current.
- Predecessor entry: the same shape under an earlier plugin's data dir
  (PREDECESSORS). It is replaced without asking - recognised by its command
  path alone, marker or not; its install markers (`statusline-installed.json`
  in those data dirs) are retired, so an older self-heal that acts on them
  goes inert.
- Anything else is foreign: never modified without the user's explicit consent
  (the installer's --replace).

Settings writes change only the `statusLine` key: the file is resolved through
symlinks (a dotfiles link stays a link), read, changed, and written to a temp
file in the same dir with the original mode, then os.replace()d - never
truncated in place. The new text splices just that key's member into the
original text (splice_key), so a hand-formatted file keeps every other byte;
when a splice is not provably right it falls back to re-serialising the whole
file in its own layout (dumps_like). Nothing is written when nothing changes,
and a read-only file is refused unless the caller has the user's consent to
write it. Messages name paths only, never setting values.

The own marker, <plugin data>/owner.json:
  {"v": 1, "state": "installed" | "removed" | "yielded" | "deferred",
   "settings": "<abs path>", "command": "<our command>", "at": <epoch s>}
- installed: the entry in `settings` is ours; SessionStart restores it when a
  stale session's settings write drops it, and repoints a predecessor entry.
- removed: the user ran --remove; nothing re-adds it until they install again.
- yielded: something else replaced our entry; left alone for good.
- deferred: a statusLine was already set on first run; never overwritten.
It stores only our own command and a path.
"""
import json, os, re, time

import sensor

PLUGIN = "statusline"
# Plugins that shipped this status line before (takeover fingerprints).
PREDECESSORS = ("claude-kit", "context-guard")
MARKER = "owner.json"
PREDECESSOR_MARKER = "statusline-installed.json"
MARKER_V = 1

_SHAPE = r'\s*python3\s+"?[^"]*/plugins/data/(?:{})-[^/"]+/current-hooks/statusline\.py"?\s*'
OWN_RE = re.compile(_SHAPE.format(re.escape(PLUGIN)))
PREDECESSOR_RE = re.compile(_SHAPE.format("|".join(map(re.escape, PREDECESSORS))))


class SettingsError(Exception):
    """A settings file that exists but is not a readable JSON object."""


def hooks_dir():
    return os.path.dirname(os.path.abspath(__file__))


def plugin_root():
    return os.path.dirname(hooks_dir())


def data_root():
    return os.path.join(sensor.base_dir(), "plugins", "data")


def data_dir(script_path=None, scan=True):
    """This plugin's persistent data dir: $CLAUDE_PLUGIN_DATA, else (with
    `scan`) the first <config>/plugins/data/statusline-* dir, else the name
    derived from the plugin cache path this code runs from
    (plugins/cache/<mkt>/statusline/). None when none of those applies."""
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    if d:
        return d
    base = data_root()
    try:
        for name in (sorted(os.listdir(base)) if scan else ()):
            if name.startswith(PLUGIN + "-") and os.path.isdir(os.path.join(base, name)):
                return os.path.join(base, name)
    except OSError:
        pass
    m = re.search(r"/plugins/cache/([^/]+)/" + re.escape(PLUGIN) + "/",
                  os.path.abspath(script_path or __file__))
    if m:
        return os.path.join(base, f"{PLUGIN}-{m.group(1)}")
    return None


def command_for(data):
    return "python3 " + json.dumps(os.path.join(data, "current-hooks", "statusline.py"))


def classify(entry):
    """'absent', 'own', 'predecessor' or 'foreign' for a statusLine value."""
    if entry is None:
        return "absent"
    cmd = entry.get("command") if isinstance(entry, dict) else None
    if not isinstance(cmd, str):
        return "foreign"
    if OWN_RE.fullmatch(cmd):
        return "own"
    if PREDECESSOR_RE.fullmatch(cmd):
        return "predecessor"
    return "foreign"


def read_settings(path):
    """The settings object at path ({} when the file does not exist). Raises
    SettingsError when it exists but is not a JSON object."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise SettingsError(f"{path} is not readable JSON") from e
    if not isinstance(d, dict):
        raise SettingsError(f"{path} is not a JSON object")
    return d


def _default_mode():
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def atomic_write_text(path, text, mode=None):
    """Write text to path's real target via a same-dir temp file and
    os.replace. Keeps the existing file's mode (else `mode`, else the umask
    default). On any failure the original is untouched and the temp removed;
    the error propagates."""
    real = os.path.realpath(path)
    d = os.path.dirname(real)
    os.makedirs(d, exist_ok=True)
    try:
        mode = os.stat(real).st_mode & 0o7777
    except FileNotFoundError:
        mode = _default_mode() if mode is None else mode
    fd, tmp = sensor._mkstemp(d, "." + os.path.basename(real) + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
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


def atomic_write_json(path, data, mode=None):
    atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", mode)


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


class ReadOnly(SettingsError):
    """A settings file the user cannot write (mode 0444, say)."""


def write_settings(path, data, allow_read_only=False):
    """Replace the settings file at path (through a symlink) with `data`,
    keeping its mode and its text: when only one top-level key changes, only
    that member's text changes (_splice_settings), else the whole file is
    re-serialised in its layout (dumps_like). A no-op when `data` equals what
    is there; returns whether it wrote. Raises ReadOnly, writing nothing, when
    the file exists but the user may not write it - replacing it would still
    succeed in a writable dir, and that would override a deliberate read-only
    - unless `allow_read_only` (the user's explicit consent, never assumed)."""
    real = os.path.realpath(path)
    try:
        with open(real, encoding="utf-8") as f:
            original = f.read()
    except FileNotFoundError:
        original = None
    text = None
    if original is not None:
        try:
            if json.loads(original) == data:
                return False
        except ValueError:
            pass
        if not allow_read_only and not os.access(real, os.W_OK):
            raise ReadOnly(f"{path} is read-only")
        text = _splice_settings(original, data)
    atomic_write_text(path, text if text is not None else dumps_like(data, original))
    return True


def enabled_in(settings):
    """Whether a settings object enables this plugin (an `enabledPlugins` key
    `statusline@<marketplace>` set to true). Reads key names only."""
    ep = settings.get("enabledPlugins") if isinstance(settings, dict) else None
    return isinstance(ep, dict) and any(
        isinstance(k, str) and k.startswith(PLUGIN + "@") and v is True
        for k, v in ep.items())


def read_marker(data):
    d = sensor._load(os.path.join(data, MARKER)) if data else None
    return d if sensor._is_v(d, MARKER_V) else None


def write_marker(data, state, settings, command):
    atomic_write_json(os.path.join(data, MARKER),
                      {"v": MARKER_V, "state": state,
                       "settings": os.path.abspath(settings), "command": command,
                       "at": time.time()}, mode=0o600)


def predecessor_markers():
    """Install markers left in earlier plugins' data dirs."""
    out = []
    base = data_root()
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return out
    for name in names:
        if any(name.startswith(p + "-") for p in PREDECESSORS):
            m = os.path.join(base, name, PREDECESSOR_MARKER)
            if os.path.isfile(m):
                out.append(m)
    return out


def _same_path(a, b):
    try:
        return os.path.realpath(a) == os.path.realpath(b)
    except Exception:
        return False


def retire_predecessor_markers(only_settings=None):
    """Delete predecessor install markers (all, or only those naming
    `only_settings`). Returns how many were removed. Never raises."""
    n = 0
    for m in predecessor_markers():
        try:
            if only_settings is not None:
                rec = sensor._load(m) or {}
                if not isinstance(rec.get("settings"), str) or \
                        not _same_path(rec["settings"], only_settings):
                    continue
            os.remove(m)
            n += 1
        except Exception:
            continue
    return n


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
