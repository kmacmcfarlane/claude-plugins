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
- blocked: the work it resumes (a heal, or a first run) is retried quietly.
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
  never points at a missing script. A project's settings.local.json is
  written only when git ignores it (or it is not in a git repo, or git
  cannot tell): the entry is an absolute path on this machine and must never
  land in a tracked file. When git does not ignore it, nothing is installed.

A settings file it must use but cannot - not valid JSON, read-only,
unwritable, or that not-ignored settings.local.json - makes the state
`blocked` (with the reason and the work to resume) and is said once, naming
the file and the fix; later sessions retry quietly.

Finally sensor.prune(): sensor records older than 30 days and orphaned temp
files, at most once a day; plus orphaned temp files in the data dir.

One install, per machine: owner.json names one settings file, so a plugin
enabled only per project gets the automatic install in the first such project
and /install-statusline --local in the others.
"""
import json, os, subprocess, sys

PREFIX = "statusline: "
GIT_TIMEOUT_S = 2


class Blocked(Exception):
    """A settings file that must be used and cannot be: `reason` is one of
    invalid, read-only, unwritable, not-ignored."""

    def __init__(self, path, reason):
        super().__init__(path)
        self.path, self.reason = path, reason


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
    """The installer's scope flag for a settings file, for a hint."""
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    if owner._same_path(path, user):
        return ""
    name = os.path.basename(path)
    if os.path.basename(os.path.dirname(os.path.abspath(path))) == ".claude" and \
            name in ("settings.json", "settings.local.json"):
        return " --local" if name == "settings.local.json" else " --project"
    return " --settings " + json.dumps(path)


def _read(owner, path):
    try:
        return owner.read_settings(path)
    except owner.SettingsError:
        raise Blocked(path, "invalid")


def _git_would_track(proj, path):
    """True when `path` is inside a git work tree and git does not ignore it.
    Bounded, fail-open: no git, a timeout, or not a repo all mean False."""
    try:
        r = subprocess.run(["git", "-C", proj, "check-ignore", "-q", path],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return r.returncode == 1


def _put(owner, data, path, expect):
    """Set our entry in the settings file at path (only if its statusLine is
    still one of `expect`), record the install, retire predecessor markers."""
    try:
        owner.write_settings(path, {"type": "command", "command": owner.command_for(data)},
                             expect=expect)
    except owner.SettingsError as e:
        raise Blocked(path, e.reason)
    except owner.Changed:
        raise
    except OSError:
        raise Blocked(path, "unwritable")
    owner.write_marker(data, "installed", path, owner.command_for(data))
    owner.retire_predecessor_markers()


def _replace_hint(owner, path):
    return f"run /install-statusline{_flag(owner, path)} and answer yes to replace it."


def heal(owner, data, marker):
    path = marker.get("settings")
    if not isinstance(path, str) or not os.path.isfile(path):
        return None
    kind = owner.classify(_read(owner, path).get("statusLine"))
    if kind == "own":
        return None
    if kind == "foreign":
        owner.write_marker(data, "yielded", path, owner.command_for(data))
        return (f"the statusLine in {path} was changed by something else; left "
                f"alone. To use this one again, {_replace_hint(owner, path)}")
    if not _script_ready(owner, data):
        return None
    _put(owner, data, path, {kind})
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
            continue  # user settings get their say in _target
        if owner.classify(d.get("statusLine")) == "predecessor":
            if not _script_ready(owner, data):
                return None, True
            _put(owner, data, path, {"predecessor"})
            return f"took over an existing status line setting in {path}.", True
    return None, False


def _target(owner, user, proj):
    """(settings file to install into, the files whose statusLine would
    compete with it, the project dir when it is a project's local file), or
    None."""
    if owner.enabled_in(_read(owner, user)):
        return user, [user], None
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
        return None  # cannot tell whether it is enabled here
    return (local, [user, shared, local], proj) if on else None


def _guard_local(p, proj):
    if proj and os.path.basename(p) == "settings.local.json" and _git_would_track(proj, p):
        raise Blocked(p, "not-ignored")


def first_run(owner, data, proj):
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    msg, done = _takeover(owner, data, user)
    if done:
        return msg
    target = _target(owner, user, proj)
    if target is None:
        return None
    path, compete, proj = target
    for p in compete:
        kind = owner.classify(_read(owner, p).get("statusLine"))
        if kind == "foreign":
            owner.write_marker(data, "deferred", path, owner.command_for(data))
            return (f"your settings already define a statusLine ({p}); left alone. "
                    f"To use this one instead, {_replace_hint(owner, path)}")
        if kind == "own":  # installed before, its owner.json lost: adopt it
            owner.write_marker(data, "installed", p, owner.command_for(data))
            return None
        if kind == "predecessor":
            if not _script_ready(owner, data):
                return None
            _guard_local(p, proj)
            _put(owner, data, p, {"predecessor"})
            return f"took over an existing status line setting in {p}."
    if not _script_ready(owner, data):
        return None
    _guard_local(path, proj)
    _put(owner, data, path, {"absent"})
    return (f"status line installed in {path}; it shows from your next session. "
            f"Undo: /install-statusline{_flag(owner, path)} --remove")


def _blocked_message(owner, path, reason, verb):
    retry = "start a new session"
    if reason == "not-ignored":
        return (f"{path} is not git-ignored, and the status line entry is an absolute "
                f"path on this machine; not installed there. Add "
                f".claude/settings.local.json to .gitignore, then {retry}, or run "
                f"/install-statusline to install it in your user settings.")
    what = {"invalid": "is not valid JSON", "read-only": "is read-only",
            "unwritable": "could not be written"}.get(reason, "could not be used")
    fix = {"invalid": "Fix it", "read-only": "Make it writable",
           "unwritable": "Check its folder's permissions"}.get(reason, "Fix it")
    return (f"{path} {what}; status line not {verb}. {fix}, then {retry}, or run "
            f"/install-statusline{_flag(owner, path)}.")


def run(inp):
    import owner
    data = owner.data_dir(__file__, scan=False)
    if not data:
        return None
    marker = None
    if os.path.lexists(os.path.join(data, owner.MARKER)):
        marker = owner.read_marker(data)
        state = marker.get("state") if marker else None
        if state == "blocked":
            resume = marker.get("resume")
        elif state == "installed":
            resume = "installed"
        else:
            return None  # removed, yielded, deferred - or unreadable: hands off
    else:
        resume = "new"
    try:
        if resume == "installed":
            return heal(owner, data, marker)
        return first_run(owner, data, _project_dir(inp))
    except owner.Changed:
        return None  # changed under us: look again next session
    except Blocked as b:
        if marker and marker.get("state") == "blocked":
            return None  # said once already; retried quietly
        try:
            owner.write_marker(data, "blocked", b.path, owner.command_for(data),
                               reason=b.reason, resume=resume)
        except Exception:
            return None  # cannot record it: stay quiet rather than repeat
        return _blocked_message(owner, b.path, b.reason,
                                "restored" if resume == "installed" else "installed")


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
