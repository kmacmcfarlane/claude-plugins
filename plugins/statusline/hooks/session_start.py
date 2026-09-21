#!/usr/bin/env python3
"""SessionStart: register the footer as a statusline-hub display hook, then prune.

Stdlib only. Never raises, never exits non-zero, and prints exactly one JSON
object: {}, or {"systemMessage": "statusline: <one line>"} for the one
notice below.

The footer draws through the statusline-hub plugin, which owns the
`statusLine` settings entry. This plugin writes no settings at all. Each
session it (re)writes its hook manifest,
${CLAUDE_CONFIG_DIR:-~/.claude}/statusline-hub/hooks.d/statusline.json -
kind display, the exec-form command `python3 <this hooks dir>/statusline.py
--segment` - as the hub's hook contract asks (the statusline-hub skill's
references/hook-contract.md): missing directories made 0700 (never through a
symlink), the file written to a private temp file in hooks.d and os.replace()d
onto the name, so a render never reads half a manifest. Rewriting it every
session keeps its path on the plugin version installed now and refreshes the
mtime the hub reads as liveness: once this plugin is disabled or uninstalled
nothing refreshes it, and the hub ignores it, then prunes it, 14 days on.

The hub's own SessionStart takes the slot once this manifest exists: a free
one, or one an earlier version of this plugin installed (its owner.json in
this plugin's data dir still says so; nothing here touches that marker, the
hub reads it). Until then an entry an earlier version installed keeps
running statusline.py directly, which still draws the footer and writes the
sensor record. So the upgrade hands the slot over once, from that entry to
the hub, with the footer drawing on both sides of it; nothing here ever
writes it back.

The hub missing: this plugin depends on statusline-hub, but `/plugin update`
of a version that predates the dependency does not install it (Claude Code
bug #88663), and without the hub nothing runs the footer once the entry an
earlier version installed is gone. So when Claude Code's install records
(<config>/plugins/installed_plugins.json) can be read and hold no
statusline-hub@ key, no settings file the hub's own first run reads (user
settings, the project's .claude/settings.json and settings.local.json)
enables a statusline-hub@ key, and no hub data dir has a live current-hooks
link, it says so once, naming the command that fixes it. A stamp in this
plugin's data dir remembers it (no data dir: not said, so never said every
session); it clears once the hub is there, so a later loss is said again.
Only key names are read, never values; anything it cannot read counts as
the hub being there.

Then sensor.prune(): sensor records older than 30 days and orphaned temp
files, at most once a day; plus orphaned temp files in the data dir an
earlier version wrote its marker into.
"""
import json, os, re, stat, sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
HUB = "statusline-hub"
NAME = "statusline"
TIMEOUT_MS = 250   # the hub's maximum for a display hook; it shares a 250 ms budget
PREFIX = "statusline: "
MARKETPLACE = "kmacmcfarlane"   # the default, when no install record names ours
HUB_NOTICE = "hub-missing-notice.json"


def hub_hooks_dir(sensor):
    return os.path.join(sensor.base_dir(), HUB, "hooks.d")


def manifest():
    """The hook manifest (hook contract v1, kind display)."""
    return {"v": 1, "name": NAME, "kind": "display",
            "command": ["python3", os.path.join(HOOKS, "statusline.py"), "--segment"],
            "timeout_ms": TIMEOUT_MS, "order": 0}


def _mkdirs_private(base, path):
    """Create `path` and its missing parents below `base`, each 0700. False,
    creating nothing further, at a component that is a symlink or not a
    directory."""
    base = os.path.abspath(base)
    path = os.path.abspath(path)
    if not path.startswith(base.rstrip(os.sep) + os.sep):
        return False
    cur = base
    for part in os.path.relpath(path, base).split(os.sep):
        cur = os.path.join(cur, part)
        try:
            os.mkdir(cur, 0o700)
        except FileExistsError:
            if os.path.islink(cur) or not os.path.isdir(cur):
                return False
    return True


def register(sensor):
    """Write hooks.d/statusline.json atomically. Returns whether it did.
    Never raises."""
    tmp = None
    try:
        d = hub_hooks_dir(sensor)
        if not _mkdirs_private(sensor.base_dir(), d):
            return False
        fd, tmp = sensor._mkstemp(d, "." + NAME + ".json.")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest(), f)
        os.replace(tmp, os.path.join(d, NAME + ".json"))
        tmp = None
        return True
    except Exception:
        return False
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _install_keys(sensor):
    """{key: [installPath, ...]} of <config>/plugins/installed_plugins.json's
    `plugins`, or None when that cannot be read. Never raises."""
    try:
        rec = os.path.join(sensor.base_dir(), "plugins", "installed_plugins.json")
        if not stat.S_ISREG(os.stat(rec).st_mode):      # a FIFO would hang the hook
            return None
        with open(rec, encoding="utf-8") as f:
            recs = json.load(f).get("plugins")
        if not isinstance(recs, dict):
            return None
        return {k: [e.get("installPath") for e in (v if isinstance(v, list) else ())
                    if isinstance(e, dict) and isinstance(e.get("installPath"), str)]
                for k, v in recs.items() if isinstance(k, str)}
    except Exception:
        return None


def _enables_hub(path):
    """True when the settings file at path enables a statusline-hub@ key,
    False when it does not (or does not exist), None when it cannot be read.
    Key names only."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return False
    except Exception:
        return None
    if not text.strip():
        return False
    try:
        d = json.loads(text)
    except ValueError:
        return None
    ep = d.get("enabledPlugins") if isinstance(d, dict) else None
    return isinstance(ep, dict) and any(
        isinstance(k, str) and k.startswith(HUB + "@") and v is True for k, v in ep.items())


def _hub_data_live(sensor):
    base = os.path.join(sensor.base_dir(), "plugins", "data")
    try:
        names = os.listdir(base)
    except OSError:
        return False
    return any(n.startswith(HUB + "-") and
               os.path.isfile(os.path.join(base, n, "current-hooks", "hub.py"))
               for n in names)


def hub_missing(sensor, proj):
    """Whether statusline-hub is certainly absent (see the module doc)."""
    keys = _install_keys(sensor)
    if keys is None or any(k.startswith(HUB + "@") for k in keys):
        return False
    files = [os.path.join(sensor.base_dir(), "settings.json")]
    if proj:
        files += [os.path.join(proj, ".claude", "settings.json"),
                  os.path.join(proj, ".claude", "settings.local.json")]
    for p in files:
        if _enables_hub(p) is not False:
            return False
    return not _hub_data_live(sensor)


def _marketplace(sensor):
    """The marketplace this plugin was installed from: the statusline@ install
    record whose installPath holds this code, else the default."""
    here = os.path.realpath(HOOKS)
    for key, paths in (_install_keys(sensor) or {}).items():
        if not key.startswith(NAME + "@"):
            continue
        for ip in paths:
            root = os.path.realpath(ip)
            if here == root or here.startswith(root.rstrip(os.sep) + os.sep):
                mkt = key.split("@", 1)[1]
                if re.fullmatch(r"[A-Za-z0-9._-]+", mkt):
                    return mkt
    return MARKETPLACE


def hub_notice(sensor, data, proj):
    """The one-line hub-missing notice, once (see the module doc), or None.
    A notice it cannot stamp is withheld. Never raises."""
    try:
        if not data:
            return None
        stamp = os.path.join(data, HUB_NOTICE)
        if not hub_missing(sensor, proj):
            if os.path.lexists(stamp):
                os.unlink(stamp)
            return None
        if os.path.lexists(stamp):
            return None
        os.makedirs(data, mode=0o700, exist_ok=True)
        fd = os.open(stamp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"v": 1}, f)
        mkt = _marketplace(sensor)
        rec = os.path.join(sensor.base_dir(), "plugins", "installed_plugins.json")
        return (f"the footer draws through the {HUB} plugin, which is not installed "
                f"(no {HUB}@ record in {rec}; `/plugin update` does not add a new "
                f"dependency). Run /plugin install {NAME}@{mkt} again, or "
                f"/plugin install {HUB}@{mkt}, then start a new session.")
    except Exception:
        return None


def _project_dir(inp):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or inp.get("cwd")
    return d if isinstance(d, str) and d else None


def main():
    msg = None
    try:
        sys.path.insert(0, HOOKS)
        try:
            inp = json.loads(sys.stdin.read() or "{}")
        except Exception:
            inp = {}
        if not isinstance(inp, dict):
            inp = {}
        import sensor
        register(sensor)
        msg = hub_notice(sensor, os.environ.get("CLAUDE_PLUGIN_DATA"), _project_dir(inp))
        try:
            sensor.prune(keep=inp.get("session_id"))
            data = os.environ.get("CLAUDE_PLUGIN_DATA")
            if data:
                sensor.prune_tmp(data)
        except Exception:
            pass
    except BaseException:
        msg = None
    try:
        print(json.dumps({"systemMessage": PREFIX + msg} if msg else {}))
    except BaseException:
        pass


if __name__ == "__main__":
    main()
