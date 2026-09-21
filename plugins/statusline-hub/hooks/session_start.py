#!/usr/bin/env python3
"""SessionStart: keep the hub in the statusLine slot where it belongs, then prune.

Stdlib only. Never raises, never exits non-zero, and prints exactly one JSON
object: {} or {"systemMessage": "statusline-hub: <one line>"} (the slot's
message and the refusal notice below, when both fire, share it). Settings are
written only through owner.write_settings (only the statusLine key, atomic, a
read-only file refused), and never over an entry some other tool installed.

Ported from the statusline plugin's session_start.py, from before that
plugin handed the slot to the hub; the states in <data>/owner.json are the
same (see owner.py):

- installed - the marked settings file:
  - lost its statusLine (a stale session's settings write dropped it): put
    ours back;
  - holds ours: nothing;
  - holds the statusline footer's own entry (a stale session wrote back the
    settings it read before the takeover): repoint it at the hub, as the
    takeover (a) does, once the footer is registered as a hub display hook
    (until then it still draws the footer: look again next session - but
    only while Claude Code records a statusline install; with none, nothing
    will register, and the hub yields to that entry as to any other);
  - holds anything else: yield - state `yielded`, said once, never fought.
- removed, yielded, deferred (or an owner.json it cannot read): nothing.
- blocked: the work it resumes (a heal, or a first run) is retried quietly.
- no owner.json (first run):
  a. takeover from the statusline plugin - a settings file its owner.json
     (written by the versions that still owned the slot) marks `installed`
     still holds its entry. The hub repoints that entry at itself only once
     the statusline plugin has registered itself as a hub display hook (a
     trusted hooks.d/statusline.json of kind display), so the footer keeps
     drawing through the hub. Until then (the statusline plugin's hook runs
     alongside this one, so on the first session after an upgrade its
     manifest may not be there yet; or a version that predates its hook
     mode) the hub leaves the slot alone, writes no marker and says
     nothing: it looks again next session. The statusline plugin itself
     writes no settings, so the slot moves once and never back.
  b. first-run install - into the scope where this plugin is enabled (user
     settings, else a project's git-ignored .claude/settings.local.json), when
     none of the competing files sets a statusLine. One set by another tool
     makes the state `deferred`, said once (with the embed-mode pointer),
     never overwritten. The statusline footer's entry there (the statusline
     plugin's, or an older copy's) is handled as in (a). An empty slot the
     user emptied by removing the statusline footer (its marker says
     `removed` for that file) stays empty: state `removed`, said once. And
     while the statusline plugin is enabled there but not yet registered as
     a hook (no marker, or one saying installed or blocked: a version that
     may still install itself), the hub waits the same way rather than race
     it for an empty slot - unless every statusline install Claude Code
     records (<config>/plugins/installed_plugins.json) is a version without
     hooks/owner.py, which could not install itself: then nothing is
     coming, and the hub takes the slot on the first session.
  The entry is written only once the current-hooks link resolves.

A settings file it must use but cannot - not valid JSON, read-only,
unwritable, a project settings.local.json git does not ignore - makes the
state `blocked`, said once with the fix; later sessions retry quietly.

Then the prune pass (housekeeping.py): sensor records untouched for 30
days (the hub's tee writes them too), dead hooks.d manifests, stale last-good
cache and logs, orphaned temp files. It also creates the hub's hooks.d (0700)
so a plugin registering a hook finds it private.

Finally the refusal notice: when manifests sit in hooks.d but the registry
refuses every one of them for a reason that lies with the directory, not the
manifest - the config dir inside a git work tree, or the hub dir or hooks.d a
symlink, someone else's, or writable by others - the hub says so once, naming
the directory and the reason (a stamp in its data dir remembers the reason;
it clears when the refusal does, so a new refusal is said again). Without
it such a machine would show no hooks and say nothing, since the renders
cannot speak and --status is only read on request.
"""
import json, os, stat, subprocess, sys

PREFIX = "statusline-hub: "
GIT_TIMEOUT_S = 2


class Blocked(Exception):
    """A settings file that must be used and cannot be: `reason` is one of
    invalid, read-only, unwritable, not-ignored."""

    def __init__(self, path, reason):
        super().__init__(path)
        self.path, self.reason = path, reason


class Wait(Exception):
    """Leave the slot to the statusline plugin for now; look again next
    session (no marker, no message)."""


def _project_dir(inp):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or inp.get("cwd")
    return d if isinstance(d, str) and d else None


def _script_ready(owner, data):
    owner.ensure_hooks_symlink(data)
    return os.path.isfile(os.path.join(data, "current-hooks", owner.SCRIPT))


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


def _guard_local(p, proj):
    if proj and os.path.basename(p) == "settings.local.json" and _git_would_track(proj, p):
        raise Blocked(p, "not-ignored")


def _put(owner, data, path, expect):
    """Set our entry in the settings file at path (only if its statusLine is
    still one of `expect`) and record the install."""
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


def _replace_hint(owner, path):
    return f"run /install-statusline-hub{_flag(owner, path)} and answer yes to replace it."


def statusline_hooked():
    """Whether the statusline plugin has registered itself as a hub display
    hook (a trusted, fresh hooks.d/statusline.json of kind display)."""
    import registry
    h = registry.find("statusline")
    return bool(h and h["kind"] == "display")


def _from_statusline(owner, data, path, proj):
    """Take over the statusline plugin's entry in `path`, or Wait."""
    if not statusline_hooked() or not _script_ready(owner, data):
        raise Wait()
    _guard_local(path, proj)
    _put(owner, data, path, {"statusline"})
    return (f"took over the status line slot in {path}; the statusline footer now "
            f"draws through the hub, as one of its display hooks.")


def heal(owner, data, marker):
    path = marker.get("settings")
    if not isinstance(path, str) or not os.path.isfile(path):
        return None
    kind = owner.classify(_read(owner, path).get("statusLine"))
    if kind == "own":
        return None
    if kind == "statusline":
        if statusline_hooked() and _script_ready(owner, data):
            _put(owner, data, path, {"statusline"})
            return (f"restored the status line in {path} (an older session's settings "
                    f"write had put the footer's earlier entry back; it draws through "
                    f"the hub).")
        if _statusline_install_paths(owner) != []:
            raise Wait()  # installed (or unknown): it may yet register
        # no statusline install recorded: nothing will register; yield below
    if kind != "absent":
        owner.write_marker(data, "yielded", path, owner.command_for(data))
        return (f"the statusLine in {path} was changed by something else; left "
                f"alone. To have the hub own it again, {_replace_hint(owner, path)}")
    if not _script_ready(owner, data):
        return None
    _put(owner, data, path, {"absent"})
    return (f"restored the status line in {path} (an older session's settings "
            f"write had dropped it; /install-statusline-hub{_flag(owner, path)} --remove "
            f"turns it off).")


def _takeover(owner, data, proj):
    """(message, done): repoint a settings file the statusline plugin's
    marker says it installed into, when it still holds its entry."""
    seen = set()
    for m in owner.statusline_markers(own=data):
        if not m or m.get("state") != "installed" or not isinstance(m.get("settings"), str):
            continue
        path = m["settings"]
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        try:
            d = owner.read_settings(path)
        except owner.SettingsError:
            continue
        if owner.classify(d.get("statusLine")) == "statusline":
            return _from_statusline(owner, data, path, proj), True
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
        return None
    try:
        on = owner.enabled_in(owner.read_settings(shared)) or \
            owner.enabled_in(owner.read_settings(local))
    except owner.SettingsError:
        return None
    return (local, [user, shared, local], proj) if on else None


def _statusline_install_paths(owner):
    """The install paths of every statusline@ install Claude Code records
    (<config>/plugins/installed_plugins.json; [] when it records none), or
    None when the records cannot be read. Key names and install paths only."""
    try:
        rec = os.path.join(owner.sensor.base_dir(), "plugins", "installed_plugins.json")
        if not stat.S_ISREG(os.stat(rec).st_mode):      # a FIFO would hang the hook
            return None
        with open(rec, encoding="utf-8") as f:
            recs = json.load(f).get("plugins")
        return [e.get("installPath") for k, v in recs.items()
                if isinstance(k, str) and k.startswith("statusline@")
                for e in (v if isinstance(v, list) else ()) if isinstance(e, dict)]
    except Exception:
        return None


def _statusline_installs_only_hooks(owner):
    """Whether Claude Code records at least one statusline@ install and none
    of them ships hooks/owner.py - every installed version registers as a hub
    hook and never installs its own entry. False when the records cannot be
    read."""
    try:
        paths = _statusline_install_paths(owner)
        return bool(paths) and all(
            isinstance(p, str) and p and os.path.isdir(os.path.join(p, "hooks")) and
            not os.path.lexists(os.path.join(p, "hooks", "owner.py")) for p in paths)
    except Exception:
        return False


def _statusline_pending(owner, data, files):
    """Whether the statusline plugin is enabled in one of `files` and may yet
    install its own entry (no marker, or installed / blocked, and an
    installed version that can)."""
    if statusline_hooked() or _statusline_installs_only_hooks(owner):
        return False
    try:
        if not any(owner.enabled_for(owner.read_settings(p), owner.STATUSLINE)
                   for p in files):
            return False
    except owner.SettingsError:
        return True
    markers = owner.statusline_markers(own=data)
    return not markers or any(m is None or m.get("state") in ("installed", "blocked")
                              for m in markers)


def _statusline_removed(owner, data, path):
    """Whether a statusline plugin marker says the user removed the footer
    from the settings file at `path`."""
    return any(m and m.get("state") == "removed" and isinstance(m.get("settings"), str)
               and owner._same_path(m["settings"], path)
               for m in owner.statusline_markers(own=data))


def first_run(owner, data, proj):
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    msg, done = _takeover(owner, data, proj)
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
            return (f"your settings already define a statusLine ({p}); left alone. To "
                    f"feed the sensor record from it, see /statusline-hub; to have the "
                    f"hub own the slot instead, {_replace_hint(owner, path)}")
        if kind == "own":  # installed before, its owner.json lost: adopt it
            owner.write_marker(data, "installed", p, owner.command_for(data))
            return None
        if kind == "statusline":
            return _from_statusline(owner, data, p, proj)
    if _statusline_removed(owner, data, path):
        owner.write_marker(data, "removed", path, owner.command_for(data))
        return (f"the statusline footer was removed from {path} earlier, so the hub "
                f"leaves that status line slot empty. To turn it on: "
                f"/install-statusline-hub{_flag(owner, path)}")
    if _statusline_pending(owner, data, compete):
        raise Wait()
    if not _script_ready(owner, data):
        return None
    _guard_local(path, proj)
    _put(owner, data, path, {"absent"})
    what = ("the statusline footer, and any other display hooks registered"
            if statusline_hooked() or _statusline_installs_only_hooks(owner) else
            "its registered display hooks (a blank line until one registers)")
    return (f"status line slot taken in {path}: from your next session the hub records "
            f"each render for the tools that read it and draws {what}. Undo: "
            f"/install-statusline-hub{_flag(owner, path)} --remove")


def _blocked_message(owner, path, reason, verb):
    retry = "start a new session"
    if reason == "not-ignored":
        return (f"{path} is not git-ignored, and the status line entry is an absolute "
                f"path on this machine; not installed there. Add "
                f".claude/settings.local.json to .gitignore, then {retry}, or run "
                f"/install-statusline-hub to install it in your user settings.")
    what = {"invalid": "is not valid JSON", "read-only": "is read-only",
            "unwritable": "could not be written"}.get(reason, "could not be used")
    fix = {"invalid": "Fix it", "read-only": "Make it writable",
           "unwritable": "Check its folder's permissions"}.get(reason, "Fix it")
    return (f"{path} {what}; status line not {verb}. {fix}, then {retry}, or run "
            f"/install-statusline-hub{_flag(owner, path)}.")


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
    except (owner.Changed, Wait):
        return None  # changed under us, or the statusline plugin's turn: next session
    except Blocked as b:
        if marker and marker.get("state") == "blocked":
            return None  # said once already; retried quietly
        try:
            owner.write_marker(data, "blocked", b.path, owner.command_for(data),
                               reason=b.reason, resume=resume)
        except Exception:
            return None
        return _blocked_message(owner, b.path, b.reason,
                                "restored" if resume == "installed" else "installed")


NOTICE = "refusal-notice.json"
# The registry's reasons about a directory itself (registry.private_dir_problem),
# which the fix "a real directory of yours that only you can write" answers.
DIR_REASONS = ("a symlink", "not a directory", "not owned by you", "group- or other-writable")


def refusal():
    """(directory, reason) when the registry refuses every manifest for a
    reason that lies with a directory and at least one manifest is there to
    refuse; else None."""
    import registry
    _, problems = registry.scan()
    dirs = {os.path.abspath(registry.hub_dir()), os.path.abspath(registry.hooks_dir())}
    hit = next(((d, why) for d, why in problems if os.path.abspath(d) in dirs), None)
    if not hit:
        return None
    try:
        names = [n for n in os.listdir(registry.hooks_dir())
                 if n.endswith(".json") and not n.startswith(".")]
    except OSError:
        names = []
    return hit if names else None


def refusal_notice(data):
    """The one-line refusal notice, once per reason (see the module doc), or
    None. A notice it cannot record is withheld, so it never repeats every
    session. Never raises."""
    try:
        if not data:
            return None
        import owner, registry
        stamp = os.path.join(data, NOTICE)
        hit = refusal()
        if not hit:
            if os.path.lexists(stamp):
                os.unlink(stamp)
            return None
        d, why = hit
        said = owner.sensor._load(stamp)
        if isinstance(said, dict) and said.get("dir") == d and said.get("why") == why:
            return None
        owner.atomic_write_json(stamp, {"v": 1, "dir": d, "why": why}, mode=0o600)
        if why == "inside a git work tree":
            fix = (f"the config dir {owner.sensor.base_dir()} is inside a git work tree, "
                   f"where a cloned repository could plant hooks. Keep CLAUDE_CONFIG_DIR "
                   f"outside any repository (the default ~/.claude is exempt)")
        elif why in DIR_REASONS:
            fix = f"{d} is {why}; it must be a real directory of yours that only you can write"
        else:   # a reason this text does not know: named as the registry gives it
            fix = f"{d} is refused ({why})"
        return (f"the hooks registered in {registry.hooks_dir()} are not run: {fix}. "
                f"/install-statusline-hub --status lists them.")
    except Exception:
        return None


def housekeeping(inp):
    import housekeeping as H, owner, registry
    registry.mkdirs_private(registry.hooks_dir())
    H.prune(keep=inp.get("session_id"))
    H.prune_hub()
    data = owner.data_dir(__file__, scan=False)
    if data:
        H.prune_tmp(data)


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
            housekeeping(inp)
        except Exception:
            pass
        try:
            import owner
            note = refusal_notice(owner.data_dir(__file__, scan=False))
        except Exception:
            note = None
        if note:
            msg = f"{msg} {note}" if msg else note
    except BaseException:
        msg = None
    try:
        print(json.dumps({"systemMessage": PREFIX + msg} if msg else {}))
    except BaseException:
        pass


if __name__ == "__main__":
    main()
