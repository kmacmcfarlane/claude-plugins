#!/usr/bin/env python3
"""Put the hub in the statusLine slot, move it, or take it out, idempotently.

    install_hub.py [--user|--project|--local|--settings PATH] [--remove]
                   [--replace] [--write-read-only]
    install_hub.py [--user|--project|--local|--settings PATH] --wrap
                   [--write-read-only]
    install_hub.py [--user|--project|--local|--settings PATH] --unwrap
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
--remove   delete the hub's entry from the chosen scope (where the hub wraps
           a status line, that is --unwrap: the wrapped entry goes back)
--wrap     the user's consent to wrap the statusLine another tool set in the
           user settings file (user scope only: a project's command would run
           in every other project's sessions, and a repository could supply
           it): the hub takes the slot and runs that command on every render,
           showing its output, after writing the sensor record. The entry is
           kept in the hub's private wrap record, never printed. Run --unwrap
           before uninstalling the plugin; after an uninstall, reinstall it
           and run --unwrap, which reads the record the uninstall left.
--unwrap   put the wrapped entry back exactly as it was (the scope defaults
           to the file it was wrapped in); with --replace, even over a
           statusLine something else set since
--replace  consent to replace or remove a statusLine some other tool installed
           (the statusline plugin's own entry counts, until that plugin draws
           as a hub display hook: replacing it then would drop the footer)
--write-read-only
           consent to write a settings file that is read-only (its mode is kept)
--status   print the hook registry (each hook, or why it is skipped), the
           segment drop dir (each every-session segment, or why a file is
           skipped) and the wrap state, and exit

Exit codes: 0 done (or nothing to do); 1 error (nothing written); 2 usage
error (nothing written); 3 a different statusLine is present and --replace
was not given (nothing written); 4 the settings file is read-only and
--write-read-only was not given (nothing written). Nothing prints a setting's
value: messages name files and keys only.
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
HOOKS = os.path.join(ROOT, "hooks")
sys.path.insert(0, HOOKS)
import owner  # noqa: E402
import registry  # noqa: E402

_ANY = owner._MISSING  # write_settings: no expected entry

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


def active_wrap():
    """The wrap record when the hub is running a wrapped entry, else None."""
    rec, _ = registry.read_wrap()
    return rec if rec and rec["running"] else None


def forget_kept(path):
    """After a plain install or replace: drop a wrap record kept for an entry
    the hub no longer runs, saying so when it was not put back."""
    rec, _ = registry.read_wrap()
    if rec and not rec["running"]:
        try:
            cur = owner.read_settings(rec["settings"]).get("statusLine")
        except owner.SettingsError:
            cur = None
        owner.drop_wrap()
        if cur != rec["entry"]:
            print(f"(the status line the hub had wrapped in {rec['settings']} is no "
                  f"longer kept)")


def wrap(path, read_only):
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
    if not owner._same_path(path, registry.user_settings()):
        print(f"the hub wraps only the statusLine in your user settings "
              f"({registry.user_settings()}), never a project's: a project's command would "
              f"run in every other project's sessions too. {path} left unchanged.")
        return 1
    m = owner.read_marker(data)
    if m and m.get("state") in ("installed", "blocked", "wrapping") and \
            isinstance(m.get("settings"), str) and not owner._same_path(m["settings"], path):
        print(f"the hub's own entry is in {m['settings']}, and it keeps one entry; wrapping "
              f"here would stop it restoring that one. Run --remove with that scope first. "
              f"{path} left unchanged.")
        return 1
    rec = active_wrap()
    entry, raw = owner.statusline_raw(path)
    kind = owner.classify(entry)
    if rec and owner._same_path(rec["settings"], path) and kind == "own":
        print(f"the hub already wraps the statusLine in {path}; nothing to do.")
        return 0
    if rec:
        print(f"the hub already wraps the statusLine in {rec['settings']}; it wraps one "
              f"at a time. Run --unwrap first.")
        return 1
    if kind == "absent":
        print(f"no statusLine in {path} to wrap; run this without --wrap to install the "
              f"hub there.")
        return 1
    if kind == "own":
        print(f"the statusLine in {path} is the hub already; nothing to wrap.")
        return 1
    if kind == "statusline":
        print(f"the statusLine in {path} is the statusline footer, which draws through "
              f"the hub as a display hook; run this without --wrap instead.")
        return 1
    cmd = entry.get("command") if isinstance(entry, dict) else None
    if not isinstance(cmd, str) or not cmd.strip() or "\0" in cmd:
        print(f"the statusLine in {path} has no command the hub could run; left "
              f"unchanged.")
        return 1
    why = registry.hub_problem()
    if why and why != "missing":
        print(f"{registry.hub_dir()} is {why}, so the hub would refuse to run a wrapped "
              f"command kept there; left unchanged. It must be a real directory of yours "
              f"that only you can write, outside any git repository.", file=sys.stderr)
        return 1
    old_marker = owner.read_marker(data)
    try:
        with open(registry.wrap_path(), "rb") as f:
            old_rec = f.read()
    except OSError:
        old_rec = None
    try:
        owner.write_wrap(path, entry, raw, True)
        owner.write_marker(data, "wrapping", path, owner.command_for(data))
        owner.write_settings(path, owner.wrap_entry(entry, data), read_only,
                             expect_entry=entry)
    except BaseException:
        if old_rec is None:
            owner.drop_wrap()
        else:
            owner.atomic_write_text(registry.wrap_path(), old_rec.decode("utf-8", "replace"),
                                    0o600, force_mode=True)
        mp = os.path.join(data, owner.MARKER)
        if old_marker is None:
            try:
                os.unlink(mp)
            except OSError:
                pass
        else:
            owner.atomic_write_json(mp, old_marker, mode=0o600)
        raise
    print(f"wrapped the statusLine in {path}: the hub now owns the slot and runs your "
          f"command on every render, after writing the sensor record, and shows its "
          f"output first, then any hub display hooks.\n  -> {script}")
    print("It shows from the next session. --unwrap puts your entry back exactly as it "
          "was. A hub display hook you do not want beside it goes under `disabled` in "
          f"{registry.config_path()}.")
    print("Run --unwrap before uninstalling statusline-hub: until then your settings run "
          "the hub, and your own entry is kept only in "
          f"{registry.wrap_path()}. If it was uninstalled first, reinstall it and run "
          "--unwrap.")
    print(STALE_WARNING)
    return 0


def unwrap(path, replace, read_only):
    """Put the wrapped entry back. `path` None: the file it was wrapped in."""
    rec, why = registry.read_wrap()
    if rec is None:
        print("the hub is not wrapping a status line." + (
            "" if why == "missing" else
            f" (its wrap record {registry.wrap_path()} is skipped: {why}.)"))
        return 1
    path = path or rec["settings"]
    if not owner._same_path(path, rec["settings"]):
        print(f"the hub wrapped the statusLine in {rec['settings']}, not {path}; run "
              f"--unwrap without a scope to put it back there.")
        return 1
    data = owner.data_dir(__file__)
    cur = owner.read_settings(path).get("statusLine")
    if cur == rec["entry"]:
        verb = "is already"
    else:
        kind = owner.classify(cur)
        if kind not in ("own", "absent") and not replace:
            print(f"the statusLine in {path} is no longer the hub's; left unchanged. "
                  f"Re-run with --replace to put the wrapped one back over it.")
            return 3
        owner.write_settings(path, rec["entry"], read_only,
                             expect=None if replace else {"own", "absent"},
                             expect_entry=_ANY if replace else cur, raw=rec["raw"])
        verb = "is back in"
    owner.set_running(rec, False)
    if data and os.path.isdir(data):
        owner.write_marker(data, "unwrapped", path, owner.command_for(data))
    print(f"unwrapped: your own statusLine {verb} {path}, exactly as it was.")
    print("It shows from the next session. A session started before this one may write "
          "the hub's entry back; the next session start then puts yours back again.")
    return 0


def remove(path, replace, read_only):
    rec = active_wrap()
    if rec and owner._same_path(rec["settings"], path):
        return unwrap(path, replace, read_only)
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
    rec = active_wrap()
    if rec:
        if owner._same_path(rec["settings"], path) and kind == "own":
            print(f"the hub already owns the statusLine in {path}, running the status "
                  f"line it wrapped there; --unwrap puts that one back.")
            return 0
        print(f"the hub wraps the statusLine in {rec['settings']}; run --unwrap first, "
              f"so that entry is not lost.")
        return 1
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
    forget_kept(path)
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
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--remove", action="store_true")
    mode.add_argument("--wrap", action="store_true",
                      help="consent to wrap the statusLine another tool set")
    mode.add_argument("--unwrap", action="store_true",
                      help="put the wrapped statusLine back exactly")
    ap.add_argument("--replace", action="store_true",
                    help="consent to replace or remove a statusLine another tool installed")
    ap.add_argument("--write-read-only", action="store_true",
                    help="consent to write a read-only settings file")
    ap.add_argument("--status", action="store_true", help="print the hook registry, the segments and the wrap state")
    a = ap.parse_args()
    if a.status:
        return subprocess.call([sys.executable, os.path.join(HOOKS, "hub.py"), "--status"],
                               stdin=subprocess.DEVNULL)
    if a.wrap and a.replace:
        ap.error("--wrap keeps the status line it finds; it takes no --replace")
    path = settings_path(a)
    try:
        if a.unwrap:
            scoped = a.user or a.project or a.local or a.settings
            return unwrap(path if scoped else None, a.replace, a.write_read_only)
        if a.wrap:
            return wrap(path, a.write_read_only)
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
