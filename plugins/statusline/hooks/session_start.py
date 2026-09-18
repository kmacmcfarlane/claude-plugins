#!/usr/bin/env python3
"""SessionStart: keep the statusLine settings entry in place, then prune.

Stdlib only. Never raises, never exits non-zero, and prints exactly one JSON
object: {} or {"systemMessage": "statusline: <one line>"}. It writes settings
only through owner.write_settings (only the statusLine key, atomic, a
read-only file refused) and never touches an entry some other tool installed.

The data dir is $CLAUDE_PLUGIN_DATA, else the one derived from the plugin cache
path this file runs from; with neither, only the prune runs. Then, by the
state in <data>/owner.json (see owner.py):

- installed - the marked settings file:
  - lost its statusLine (a stale session's settings write dropped it): put
    ours back;
  - holds an earlier copy of this status line (a predecessor's path, put back
    by an older self-heal): repoint it at ours;
  - holds ours: nothing;
  - holds something else: yield - state `yielded`, said once, never fought.
- removed, yielded, deferred (or an owner.json it cannot read): nothing.
- no owner.json (first run, or an upgrade):
  a. takeover - the first of the settings files named by predecessor markers,
     then user settings, whose statusLine is an earlier copy of this status
     line (recognised by its command path; no marker needed) is repointed;
  b. first-run install - into the scope where the plugin is enabled: user
     settings when user settings enable it, else, when only the project's
     .claude/settings.json or .claude/settings.local.json enables it, the
     per-user, git-ignored .claude/settings.local.json. Only when none of the
     files that would compete (user; plus project and local for a project
     install) sets a statusLine - one set by some other tool makes the state
     `deferred`, said once, never overwritten. Enabled nowhere it can see:
     nothing.
  The entry is written only once the current-hooks link resolves, so it
  never points at a missing script.

Finally sensor.prune(): sensor records older than 30 days and orphaned temp
files, at most once a day; plus orphaned temp files in the data dir.

One install, per machine: owner.json names one settings file, so a plugin
enabled only per project gets the automatic install in the first such project
and /install-statusline --local in the others.
"""
import json, os, sys

PREFIX = "statusline: "


def _project_dir(inp):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or inp.get("cwd")
    return d if isinstance(d, str) and d else None


def _script_ready(owner, data):
    """Make the current-hooks link if it is missing, then whether the script
    it leads to exists. The symlink hook runs alongside this one, so a False
    here only means: try again next session."""
    owner.ensure_hooks_symlink(data)
    return os.path.isfile(os.path.join(data, "current-hooks", "statusline.py"))


def _flag(owner, path):
    """The installer's scope flag for a settings file, for an undo hint."""
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    if owner._same_path(path, user):
        return ""
    name = os.path.basename(path)
    if os.path.basename(os.path.dirname(os.path.abspath(path))) == ".claude" and \
            name in ("settings.json", "settings.local.json"):
        return " --local" if name == "settings.local.json" else " --project"
    return " --settings " + json.dumps(path)


def _entry(owner, data):
    return {"type": "command", "command": owner.command_for(data)}


def _put(owner, data, path, settings):
    """Write our entry into `settings` (the parsed file at path), record the
    install, retire predecessor markers."""
    settings["statusLine"] = _entry(owner, data)
    owner.write_settings(path, settings)
    owner.write_marker(data, "installed", path, owner.command_for(data))
    owner.retire_predecessor_markers()


def heal(owner, data, marker):
    path = marker.get("settings")
    if not isinstance(path, str) or not os.path.isfile(path):
        return None
    d = owner.read_settings(path)
    kind = owner.classify(d.get("statusLine"))
    if kind == "own":
        return None
    if kind == "foreign":
        owner.write_marker(data, "yielded", path, owner.command_for(data))
        return (f"the statusLine in {path} was changed by something else; left "
                f"alone. /install-statusline{_flag(owner, path)} --replace takes it back.")
    if not _script_ready(owner, data):
        return None
    _put(owner, data, path, d)
    if kind == "absent":
        return (f"restored the status line in {path} (an older session's settings "
                f"write had dropped it; /install-statusline{_flag(owner, path)} --remove "
                f"turns it off).")
    return f"took over an existing status line setting in {path}."


def _takeover(owner, data, user):
    seen, cands = set(), []
    for m in owner.predecessor_markers():
        rec = owner.sensor._load(m) or {}
        if isinstance(rec.get("settings"), str):
            cands.append(rec["settings"])
    cands.append(user)
    for path in cands:
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        try:
            d = owner.read_settings(path)
        except owner.SettingsError:
            continue
        if owner.classify(d.get("statusLine")) == "predecessor":
            if not _script_ready(owner, data):
                return None, True
            _put(owner, data, path, d)
            return f"took over an existing status line setting in {path}.", True
    return None, False


def _target(owner, user, proj):
    """(settings file to install into, the files whose statusLine would
    compete with it, the scope flag for the undo hint), or None."""
    if owner.enabled_in(owner.read_settings(user)):
        return user, [user], ""
    if not proj:
        return None
    shared = os.path.join(proj, ".claude", "settings.json")
    local = os.path.join(proj, ".claude", "settings.local.json")
    if os.path.realpath(shared) == os.path.realpath(user):
        return None  # the "project" is the config dir's parent: user scope
    try:
        on = owner.enabled_in(owner.read_settings(shared)) or \
            owner.enabled_in(owner.read_settings(local))
    except owner.SettingsError:
        return None
    return (local, [user, shared, local], " --local") if on else None


def first_run(owner, data, proj):
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    msg, done = _takeover(owner, data, user)
    if done:
        return msg
    target = _target(owner, user, proj)
    if target is None:
        return None
    path, compete, flag = target
    for p in compete:
        d = owner.read_settings(p)
        kind = owner.classify(d.get("statusLine"))
        if kind == "foreign":
            owner.write_marker(data, "deferred", path, owner.command_for(data))
            return (f"your settings already define a statusLine ({p}); left alone. "
                    f"/install-statusline{flag} --replace replaces it.")
        if kind == "own":  # installed before, its owner.json lost: adopt it
            owner.write_marker(data, "installed", p, owner.command_for(data))
            return None
        if kind == "predecessor":
            if not _script_ready(owner, data):
                return None
            _put(owner, data, p, d)
            return f"took over an existing status line setting in {p}."
    if not _script_ready(owner, data):
        return None
    _put(owner, data, path, owner.read_settings(path))
    return (f"status line installed in {path}; it shows from your next session. "
            f"Undo: /install-statusline{flag} --remove")


def run(inp):
    import owner
    data = owner.data_dir(__file__, scan=False)
    if not data:
        return None
    if os.path.lexists(os.path.join(data, owner.MARKER)):
        marker = owner.read_marker(data)
        if marker is None or marker.get("state") != "installed":
            return None  # removed, yielded, deferred - or unreadable: hands off
        return heal(owner, data, marker)
    return first_run(owner, data, _project_dir(inp))


def main():
    msg = None
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            inp = json.loads(sys.stdin.read() or "{}")
        except Exception:
            inp = {}
        if not isinstance(inp, dict):
            inp = {}
        try:
            msg = run(inp)
        except Exception:
            msg = None
        try:
            import owner, sensor
            sensor.prune(keep=inp.get("session_id"))
            data = owner.data_dir(__file__, scan=False)
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
