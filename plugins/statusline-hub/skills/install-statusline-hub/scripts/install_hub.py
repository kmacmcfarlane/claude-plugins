#!/usr/bin/env python3
"""Put the hub in the statusLine slot, move it, or take it out, idempotently.

    install_hub.py [--user|--project|--local|--settings PATH] [--remove]
                   [--replace] [--write-read-only]
    install_hub.py --status

Writes `statusLine` pointing at the update-stable plugin-data path
(<config>/plugins/data/statusline-hub-<marketplace>/current-hooks/hub.py),
resolved to an ABSOLUTE path now. The plugin's SessionStart hook keeps that
symlink current; if it does not exist yet, this script creates it the same way.

The SessionStart hook already takes a free slot on the first session, so this
script is for another scope, removal, or replacing a status line some other
tool installed.

--user     the user settings file, <config>/settings.json  (default)
--project  .claude/settings.json in the current directory - shared with the
           team, and the command is an absolute path on THIS machine
--local    .claude/settings.local.json in the current directory (per user)
--remove   delete the hub's entry from the chosen scope
--replace  consent to replace or remove a statusLine some other tool installed
           (the statusline plugin's own entry counts, until that plugin draws
           as a hub display hook: replacing it then would drop the footer)
--write-read-only
           consent to write a settings file that is read-only (its mode is kept)
--status   print the hook registry (each hook, or why it is skipped) and exit

Exit codes: 0 done (or nothing to do); 1 error (nothing written); 2 usage
error (nothing written); 3 a different statusLine is present and --replace
was not given (nothing written); 4 the settings file is read-only and
--write-read-only was not given (nothing written).
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
HOOKS = os.path.join(ROOT, "hooks")
sys.path.insert(0, HOOKS)
import owner  # noqa: E402
import registry  # noqa: E402

STALE_WARNING = (
    "Note: sessions already running hold their own copy of the settings; a "
    "settings change made from one of them (a /plugin toggle, a model or effort "
    "change) can drop this entry. If the status line disappears, run this again.")


def ours():
    """The statusLine kinds changeable without --replace."""
    h = registry.find("statusline")
    return {"absent", "own"} | ({"statusline"} if h and h["kind"] == "display" else set())


def settings_path(a):
    if a.settings:
        return a.settings
    if a.project:
        return os.path.join(".claude", "settings.json")
    if a.local:
        return os.path.join(".claude", "settings.local.json")
    return os.path.join(owner.sensor.base_dir(), "settings.json")


def remove(path, replace, read_only):
    d = owner.read_settings(path)
    kind = owner.classify(d.get("statusLine"))
    data = owner.data_dir(__file__)
    if kind not in ("absent", "own") and not replace:
        print(f"the statusLine in {path} was not installed by the hub; left "
              f"unchanged. Re-run with --replace to remove it anyway.")
        return 3
    if kind != "absent":
        owner.write_settings(path, None, read_only,
                             expect=None if replace else {"absent", "own"})
    if data and os.path.isdir(data):
        m = owner.read_marker(data)
        if m is None or owner._same_path(m.get("settings") or "", path):
            owner.write_marker(data, "removed", path, owner.command_for(data))
    print(f"removed statusLine from {path}" if kind != "absent"
          else f"no statusLine in {path}")
    return 0


def install(path, replace, read_only, project):
    d = owner.read_settings(path)
    data = owner.data_dir(__file__)
    if not data:
        print("the plugin's data dir was not found and could not be derived from "
              "this script's path - is the statusline-hub plugin installed?",
              file=sys.stderr)
        return 1
    owner.ensure_hooks_symlink(data)
    script = os.path.join(data, "current-hooks", owner.SCRIPT)
    if not os.path.exists(script):
        print(f"{script} is missing - the current-hooks link could not be created; "
              f"start one session with the plugin enabled, then run this again",
              file=sys.stderr)
        return 1
    kind = owner.classify(d.get("statusLine"))
    allowed = ours()
    if kind not in allowed and not replace:
        what = ("the statusline plugin's footer, which does not draw as a hub hook yet; "
                "replacing it drops the footer" if kind == "statusline"
                else "a different statusLine")
        print(f"{path} already has {what}; left unchanged. Re-run with --replace to "
              f"replace it.")
        return 3
    cmd = owner.command_for(data)
    owner.write_settings(path, {"type": "command", "command": cmd}, read_only,
                         expect=None if replace else allowed)
    owner.write_marker(data, "installed", path, cmd)
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
    ap = argparse.ArgumentParser(description="Put the hub in the status-line slot.",
                                 allow_abbrev=False)
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--user", action="store_true")
    scope.add_argument("--project", action="store_true")
    scope.add_argument("--local", action="store_true")
    scope.add_argument("--settings", help="explicit settings file path")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--replace", action="store_true",
                    help="consent to replace or remove a statusLine another tool installed")
    ap.add_argument("--write-read-only", action="store_true",
                    help="consent to write a read-only settings file")
    ap.add_argument("--status", action="store_true", help="print the hook registry")
    a = ap.parse_args()
    if a.status:
        return subprocess.call([sys.executable, os.path.join(HOOKS, "hub.py"), "--status"],
                               stdin=subprocess.DEVNULL)
    path = settings_path(a)
    try:
        if a.remove:
            return remove(path, a.replace, a.write_read_only)
        return install(path, a.replace, a.write_read_only, a.project)
    except owner.Changed as e:
        print(f"{e}; left unchanged - run this again.", file=sys.stderr)
        return 1
    except owner.ReadOnly as e:
        print(f"{e}; left unchanged. Make it writable, or re-run with "
              f"--write-read-only to write it anyway.", file=sys.stderr)
        return 4
    except owner.SettingsError as e:
        print(f"{e}; left unchanged - fix the file, then run this again.", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"could not finish writing {path}: {e.strerror or e}; the settings file is "
              f"either unchanged or fully updated, never partly written.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
