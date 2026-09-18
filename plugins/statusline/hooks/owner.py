"""Ownership of the `statusLine` settings entry. Stdlib only.

Used by the install-statusline skill's script (explicit install and remove).

- Own entry: a command running .../plugins/data/statusline-<marketplace>/
  current-hooks/statusline.py - the update-stable path this plugin's
  SessionStart symlink keeps current.
- Predecessor entry: the same shape under an earlier plugin's data dir
  (PREDECESSORS). It is replaced without asking; its install markers
  (`statusline-installed.json` in those data dirs) are retired, so an older
  self-heal that acts on them goes inert.
- Anything else is foreign: never modified without an explicit force.

Settings writes change only the `statusLine` key: the file is resolved through
symlinks (a dotfiles link stays a link), read, changed, written to a temp file
in the same dir with the original mode, then os.replace()d - never truncated in
place. Messages name paths only, never setting values.

The own marker, <plugin data>/owner.json:
  {"v": 1, "state": "installed" | "removed", "settings": "<abs path>",
   "command": "<our command>", "at": <epoch s>}
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


def data_dir(script_path=None):
    """This plugin's persistent data dir: $CLAUDE_PLUGIN_DATA, else the first
    <config>/plugins/data/statusline-* dir, else the name derived from the
    plugin cache path this code runs from (plugins/cache/<mkt>/statusline/).
    None when none of those applies."""
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    if d:
        return d
    base = data_root()
    try:
        for name in sorted(os.listdir(base)):
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


def atomic_write_json(path, data, mode=None):
    """Write data to path's real target via a same-dir temp file and
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
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        os.chmod(tmp, mode)
        os.replace(tmp, real)
        tmp = None
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


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
