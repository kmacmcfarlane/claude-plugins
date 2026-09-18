#!/usr/bin/env python3
"""Install, move, or remove the status line, idempotently.

    install_statusline.py [--user|--project|--local|--settings PATH] [--remove] [--force]

Writes `statusLine` pointing at the update-stable plugin-data path
(<config>/plugins/data/statusline-<marketplace>/current-hooks/statusline.py),
resolved to an ABSOLUTE path at install time: the status line docs do not
promise env expansion in the command, so none is relied on. The plugin's
SessionStart hook keeps that symlink current; if it does not exist yet (a
session started before the plugin loaded), this script creates it the same way.

--user     the user settings file, <config>/settings.json  (default)
--project  .claude/settings.json in the current directory - shared with the
           team, and the command is an absolute path on THIS machine
--local    .claude/settings.local.json in the current directory (per user)
--remove   delete the entry this plugin installed from the chosen scope
--force    replace or remove a statusLine that some other tool installed

Exit codes: 0 done (or nothing to do), 1 error (nothing written),
3 a different statusLine is present and --force was not given (nothing written).
"""
import argparse, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "hooks"))
import owner  # noqa: E402
import sensor  # noqa: E402

STALE_WARNING = (
    "Note: sessions already running hold their own copy of the settings; a "
    "settings change made from one of them (a /plugin toggle, a model or effort "
    "change) can drop this entry. If the status line disappears, run this again.")


def settings_path(a):
    if a.settings:
        return a.settings
    if a.project:
        return os.path.join(".claude", "settings.json")
    if a.local:
        return os.path.join(".claude", "settings.local.json")
    return os.path.join(sensor.base_dir(), "settings.json")


def remove(path, force):
    d = owner.read_settings(path)
    kind = owner.classify(d.get("statusLine"))
    data = owner.data_dir(__file__)
    if kind == "foreign" and not force:
        print(f"the statusLine in {path} was not installed by this plugin; left "
              f"unchanged. Re-run with --force to remove it anyway.")
        return 3
    if kind != "absent":
        d.pop("statusLine", None)
        owner.atomic_write_json(path, d)
    owner.retire_predecessor_markers(only_settings=path)
    if data and os.path.isdir(data):
        m = owner.read_marker(data)
        if m is None or owner._same_path(m.get("settings") or "", path):
            owner.write_marker(data, "removed", path, owner.command_for(data))
    print(f"removed statusLine from {path}" if kind != "absent"
          else f"no statusLine in {path}")
    return 0


def install(path, force, project):
    d = owner.read_settings(path)
    data = owner.data_dir(__file__)
    if not data:
        print("the plugin's data dir was not found and could not be derived from "
              "this script's path - is the statusline plugin installed?", file=sys.stderr)
        return 1
    owner.ensure_hooks_symlink(data)
    script = os.path.join(data, "current-hooks", "statusline.py")
    if not os.path.exists(script):
        print(f"{script} is missing - the current-hooks link could not be created; "
              f"start one session with the plugin enabled, then run this again",
              file=sys.stderr)
        return 1
    kind = owner.classify(d.get("statusLine"))
    if kind == "foreign" and not force:
        print(f"{path} already has a different statusLine; left unchanged. "
              f"Re-run with --force to replace it.")
        return 3
    cmd = owner.command_for(data)
    d["statusLine"] = {"type": "command", "command": cmd}
    owner.atomic_write_json(path, d)
    owner.write_marker(data, "installed", path, cmd)
    owner.retire_predecessor_markers()
    verb = {"absent": "installed", "own": "updated"}.get(kind, "replaced")
    print(f"{verb} statusLine in {path}\n  -> {script}")
    print("It shows from the next session.")
    if project:
        print("WARNING: .claude/settings.json is shared with everyone who uses this "
              "repo, and the command above is an absolute path on this machine; do "
              "not commit it. Teammates should install the plugin and run this "
              "skill themselves (or use --local).")
    print(STALE_WARNING)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Install or remove the status line.")
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--user", action="store_true")
    scope.add_argument("--project", action="store_true")
    scope.add_argument("--local", action="store_true")
    scope.add_argument("--settings", help="explicit settings file path")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    path = settings_path(a)
    try:
        if a.remove:
            return remove(path, a.force)
        return install(path, a.force, a.project)
    except owner.SettingsError as e:
        print(f"{e}; left unchanged - fix the file, then run this again.", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"could not finish writing {path}: {e.strerror or e}; the settings file is either "
              f"unchanged or fully updated, never partly written.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
