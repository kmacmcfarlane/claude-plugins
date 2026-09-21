#!/usr/bin/env python3
"""SessionStart: register the footer as a statusline-hub display hook, then prune.

Stdlib only. Never raises, never exits non-zero, and prints exactly one JSON
object, always {}: this hook has nothing to say.

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

Then sensor.prune(): sensor records older than 30 days and orphaned temp
files, at most once a day; plus orphaned temp files in the data dir an
earlier version wrote its marker into.
"""
import json, os, sys

HOOKS = os.path.dirname(os.path.abspath(__file__))
HUB = "statusline-hub"
NAME = "statusline"
TIMEOUT_MS = 250   # the hub's maximum for a display hook; it shares a 250 ms budget


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


def main():
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
        try:
            sensor.prune(keep=inp.get("session_id"))
            data = os.environ.get("CLAUDE_PLUGIN_DATA")
            if data:
                sensor.prune_tmp(data)
        except Exception:
            pass
    except BaseException:
        pass
    try:
        print(json.dumps({}))
    except BaseException:
        pass


if __name__ == "__main__":
    main()
