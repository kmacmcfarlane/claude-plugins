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
    only while it cannot be sure no statusline install exists: once Claude
    Code's install records name the hub and no statusline@ key, nothing will
    register, and the entry is handled as an older copy, below);
  - holds anything else: yield - state `yielded`, said once, never fought.
- wrapping (the user ran /install-statusline-hub --wrap) - the marked file:
  - holds ours: nothing;
  - lost its statusLine, or holds the wrapped entry again (a stale
    session's settings write, from before the wrap): put the wrapping
    entry back - the consent was given, and --unwrap is how it is taken
    back;
  - holds anything else: yield - state `yielded`, said once; the wrapped
    entry stays in the wrap record (not run), so --unwrap --replace can
    still put it back.
  A wrap record that is gone (deleted by hand) ends the wrap: state
  `installed`, said once.
- unwrapped (the user ran --unwrap): when a stale session's write puts
  the hub's entry back, put the kept entry back again; otherwise nothing.
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
     makes the state `deferred`, said once, never overwritten: the one line
     asks whether the user wants it wrapped (what --wrap would do, and how
     to accept; only for the user settings file - a project's command is
     never offered, since the hub would run a repository's command), and
     points at embed mode and at replacing it. A lost marker with the hub's
     entry and a wrap record is adopted as `wrapping` only when the record
     is running; one the user had unwrapped gets their entry put back. The hub
     never wraps on its own (operator decision 40: ask once). The statusline footer's entry there (the statusline
     plugin's, or an older copy's) is handled as in (a), except that once the
     install records surely hold no statusline install it is an older copy
     (below). An empty slot the
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
- an older copy: the footer's entry (owner.FOOTER_HOMES: the statusline
  plugin's own, or context-guard's or claude-kit's older copy) in the slot,
  and the install records naming the hub and no statusline install, so no
  footer will register. The hub never yields to it for good. When the
  copy draws nothing - its plugin gone (no <plugin>@ install record and
  its current-hooks/statusline.py not resolving), or its plugin recorded
  with current-hooks resolving to a directory without statusline.py - the
  hub takes the slot, said once. A dangling link alone is not that: an
  update leaves one until that plugin's own SessionStart re-links it, so a
  recorded plugin whose link dangles means wait. A copy that still
  resolves draws: said once (stamped in footer-copy-notice.json in the data
  dir) that installing statusline lets the hub take over, then looked at
  again quietly each session, so a later statusline install is still taken
  over. Records it cannot read, or that do not name the hub: it cannot
  tell, so nothing.

A settings file it must use but cannot - not valid JSON, read-only,
unwritable, a project settings.local.json git does not ignore - makes the
state `blocked`, said once with the fix; later sessions retry quietly. So
does a project settings file git tracks (a team-shared .claude/settings.json,
where the old installer's --project put a footer entry): taking over the
footer's entry there would commit the hub's absolute path on this machine,
so the hub refuses and leaves the file as it is. A heal is refused there
too: a committed footer entry git brings back is not replaced, and a git
revert that drops the hub's entry is not fought (an entry the user put
there with the installer's --project is put back only by running it
again). A git that times out answering means wait for the next session.
The user settings file is never refused for being tracked (a dotfiles
repo is the user's own).

Then the prune pass (housekeeping.py): sensor records untouched for 30
days (the hub's tee writes them too), dead hooks.d manifests, stale last-good
cache and logs, segment files no render will show again, orphaned temp
files. It also creates the hub's hooks.d (0700)
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
    invalid, read-only, unwritable, not-ignored, tracked."""

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


def _git_tracks(path):
    """True when git tracks the file at `path` (it is in the index of the
    work tree that holds it). No git, or not a repo, means False; a
    timeout raises Wait, so nothing is written until a session can tell."""
    try:
        r = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(path)),
                            "ls-files", "--error-unmatch", "--", os.path.basename(path)],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=GIT_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise Wait()
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return r.returncode == 0


def _guard_local(owner, p, proj):
    """Refuse to put the hub's machine-specific entry where git would share
    it: a project settings.local.json git does not ignore, or any settings
    file other than the user's that git tracks. Tracked is checked first,
    so a force-added settings.local.json is named as tracked."""
    user = os.path.join(owner.sensor.base_dir(), "settings.json")
    if not owner._same_path(p, user) and _git_tracks(p):
        raise Blocked(p, "tracked")
    if proj and os.path.basename(p) == "settings.local.json" and _git_would_track(proj, p):
        raise Blocked(p, "not-ignored")


def _scope(marker):
    """The marker fields to carry into the next one it is replaced by: the
    `scope` the installer records for a project's shared settings file
    (--project, or --settings naming one)."""
    s = marker.get("scope") if marker else None
    return {"scope": s} if s == "project" else {}


def _put(owner, data, path, expect, keep=None):
    """Set our entry in the settings file at path (only if its statusLine is
    still one of `expect`) and record the install, keeping the fields
    `keep` holds (see _scope)."""
    try:
        owner.write_settings(path, {"type": "command", "command": owner.command_for(data)},
                             expect=expect)
    except owner.SettingsError as e:
        raise Blocked(path, e.reason)
    except owner.Changed:
        raise
    except OSError:
        raise Blocked(path, "unwritable")
    owner.write_marker(data, "installed", path, owner.command_for(data), **(keep or {}))


def _replace_hint(owner, path):
    return f"run /install-statusline-hub{_flag(owner, path)} and answer yes to replace it."


def _write(owner, path, entry, **kw):
    """owner.write_settings, with a settings file it cannot use as Blocked.
    Changed propagates."""
    try:
        return owner.write_settings(path, entry, **kw)
    except owner.SettingsError as e:
        raise Blocked(path, e.reason)
    except OSError:
        raise Blocked(path, "unwritable")


def _wrap_offer(owner, p):
    """Decision 40: the one-line question a first run asks when the slot
    holds another tool's statusLine. Wrap mode is user scope only
    (registry.wrap_applies): a project file's command is never offered,
    since the hub would run a repository's command."""
    import registry
    if not owner._same_path(p, registry.user_settings()):
        return (f"your settings already define a statusLine ({p}); left alone. It is a "
                f"project's, so the hub does not offer to wrap it (it would run that "
                f"repository's command). To feed the sensor record from it, see "
                f"/statusline-hub; to have the hub own the slot instead, "
                f"{_replace_hint(owner, p)}")
    flag = _flag(owner, p)
    return (f"your settings already define a statusLine ({p}); left alone. The hub can "
            f"wrap it if you want: it keeps drawing as now, run by the hub on each "
            f"render, so the tools that read the sensor record see this session's "
            f"context and plan usage, and hub display hooks draw beside it. To accept, "
            f"run /install-statusline-hub{flag} --wrap (--unwrap puts it back exactly). "
            f"Or feed the sensor from it yourself (/statusline-hub), or to have the hub "
            f"own the slot instead, {_replace_hint(owner, p)}")


def heal_wrap(owner, data, marker, state):
    """SessionStart for the states `wrapping` and `unwrapped` (module doc)."""
    import registry
    path = marker.get("settings")
    if not isinstance(path, str) or not os.path.isfile(path):
        return None
    rec, why = registry.read_wrap()
    if rec is None or not owner._same_path(rec["settings"], path):
        if why not in (None, "missing"):
            return None  # refused by the trust rules: --status says why; nothing moves
        if state == "unwrapped":
            owner.write_marker(data, "deferred", path, owner.command_for(data))
            return None
        owner.write_marker(data, "installed", path, owner.command_for(data))
        return (f"the status line the hub wrapped in {path} is no longer on record, so "
                f"the hub draws only its display hooks there. To use your own again, "
                f"set it, or /install-statusline-hub{_flag(owner, path)} --remove.")
    cur = _read(owner, path).get("statusLine")
    kind = owner.classify(cur)
    if state == "unwrapped":
        if kind != "own":
            return None
        _write(owner, path, rec["entry"], expect_entry=cur, raw=rec["raw"])
        return (f"put your own status line back in {path} (an older session's settings "
                f"write had restored the hub's entry after --unwrap).")
    if kind == "own":
        if not rec["running"]:
            owner.set_running(rec, True)
        return None
    if kind == "absent" or cur == rec["entry"]:
        if not _script_ready(owner, data):
            return None
        _write(owner, path, owner.wrap_entry(rec["entry"], data), expect_entry=cur)
        if not rec["running"]:
            owner.set_running(rec, True)
        what = ("dropped it" if kind == "absent" else
                "put back the entry from before the wrap")
        return (f"restored the wrapped status line in {path} (an older session's "
                f"settings write had {what}; /install-statusline-hub{_flag(owner, path)} "
                f"--unwrap puts your own back for good).")
    owner.set_running(rec, False)
    owner.write_marker(data, "yielded", path, owner.command_for(data))
    return (f"the statusLine in {path} was changed by something else; left alone, and "
            f"the hub no longer runs the status line it wrapped there. To put that one "
            f"back, run /install-statusline-hub{_flag(owner, path)} --unwrap and answer "
            f"yes to replace the current one.")


def statusline_hooked():
    """Whether the statusline plugin has registered itself as a hub display
    hook (a trusted, fresh hooks.d/statusline.json of kind display)."""
    import registry
    h = registry.find("statusline")
    return bool(h and h["kind"] == "display")


def _from_statusline(owner, data, path, proj, entry):
    """Take over the statusline footer's entry `entry` in `path` once the
    footer is a hub hook; with statusline surely uninstalled, an older copy
    (_older_copy); else Wait."""
    if statusline_hooked():
        if not _script_ready(owner, data):
            raise Wait()
        _guard_local(owner, path, proj)
        _put(owner, data, path, {"statusline"})
        return (f"took over the status line slot in {path}; the statusline footer now "
                f"draws through the hub, as one of its display hooks.")
    if not _statusline_uninstalled(owner):
        raise Wait()  # installed (or unknown): it may yet register
    return _older_copy(owner, data, path, proj, entry, "took over")


COPY_NOTICE = "footer-copy-notice.json"


def _install_hint(owner):
    """The statusline plugin's install command, from the marketplace Claude
    Code records this hub under (the kit's own when it records none)."""
    mkt = next((k.split("@", 1)[1] for k in (_install_records(owner) or {})
                if isinstance(k, str) and k.startswith(owner.PLUGIN + "@")
                and k.split("@", 1)[1]), "kmacmcfarlane")
    return f"/plugin install {owner.STATUSLINE}@{mkt}"


def _copy_name(owner, home):
    """What the footer entry in the slot is, for a message."""
    if home == owner.STATUSLINE:
        return "the statusline footer's entry, from the statusline plugin"
    return f"an older copy of the statusline footer, from the {home} plugin"


def _footer_hint(owner):
    """The first-run line's pointer at the footer: enable the statusline
    plugin when Claude Code records it installed, else its install command."""
    if _has(_install_records(owner) or {}, owner.STATUSLINE):
        return "enable the statusline plugin for its footer"
    return f"the statusline plugin draws a footer there: {_install_hint(owner)}"


def _older_copy(owner, data, path, proj, entry, verb, keep=None):
    """The slot in `path` holds an older copy of the statusline footer
    (`entry`, from one of owner.FOOTER_HOMES) and the install records surely
    hold no statusline install, so no footer will ever register: the hub
    never yields to it for good.
    - The copy draws nothing: its plugin is gone (no <plugin>@ install
      record, and its current-hooks/statusline.py does not resolve), or its
      plugin is recorded and current-hooks resolves to a directory that no
      longer holds statusline.py (a version that dropped the copy). The hub
      takes the slot.
    - The copy still resolves: it draws; said once (a stamp in the data dir,
      per settings file and entry) that installing statusline lets the hub
      take over; then the hub looks again each session, quietly.
    - Its plugin is recorded and current-hooks dangles or is absent (an
      update leaves a dangling link until that plugin's own SessionStart
      re-links it): Wait."""
    copy = owner.footer_copy(entry)
    recs = _install_records(owner)
    if copy is None or recs is None:
        raise Wait()
    home, script = copy
    if os.path.isfile(script):
        return _copy_notice(owner, data, path, entry, home)
    if _has(recs, home) and not os.path.isdir(os.path.dirname(script)):
        raise Wait()  # mid-update: the link dangles until its plugin re-links it
    if not _script_ready(owner, data):
        raise Wait()
    _guard_local(owner, path, proj)
    _put(owner, data, path, {"statusline"}, keep)
    gone = ("whose version no longer ships it" if _has(recs, home) else
            "which is no longer installed")
    return (f"{verb} the status line slot in {path}: it ran {_copy_name(owner, home)}, "
            f"{gone}, so it drew nothing. From your next session "
            f"the hub records each render for the tools that read it and draws its "
            f"registered display hooks; for the footer, install the statusline plugin: "
            f"{_install_hint(owner)}. Undo: /install-statusline-hub{_flag(owner, path)} "
            f"--remove")


def _copy_notice(owner, data, path, entry, home):
    """Say once that installing statusline lets the hub take over a live
    older copy; None when said already, or when the stamp cannot be kept
    (a notice it cannot record is withheld, so it never repeats)."""
    stamp = os.path.join(data, COPY_NOTICE)
    key = {"v": 1, "settings": os.path.abspath(path), "command": entry.get("command")}
    said = owner.sensor._load(stamp)
    if isinstance(said, dict) and all(said.get(k) == v for k, v in key.items()):
        raise Wait()
    try:
        owner.atomic_write_json(stamp, key, mode=0o600)
    except OSError:
        raise Wait()
    return (f"the status line in {path} runs {_copy_name(owner, home)}; left alone "
            f"while it draws. Install the statusline plugin ({_install_hint(owner)}) "
            f"and the hub takes over the slot, drawing the footer as one of its display "
            f"hooks.")


def heal(owner, data, marker):
    path = marker.get("settings")
    if not isinstance(path, str) or not os.path.isfile(path):
        return None
    cur = _read(owner, path).get("statusLine")
    kind = owner.classify(cur)
    if kind == "own":
        return None
    if kind == "statusline":
        if statusline_hooked() and _script_ready(owner, data):
            _guard_local(owner, path, None)
            _put(owner, data, path, {"statusline"}, _scope(marker))
            return (f"restored the status line in {path} (an older session's settings "
                    f"write had put the footer's earlier entry back; it draws through "
                    f"the hub).")
        if not _statusline_uninstalled(owner):
            raise Wait()  # installed (or unknown): it may yet register
        return _older_copy(owner, data, path, None, cur, "took back", _scope(marker))
    if kind != "absent":
        owner.write_marker(data, "yielded", path, owner.command_for(data))
        return (f"the statusLine in {path} was changed by something else; left "
                f"alone. To have the hub own it again, {_replace_hint(owner, path)}")
    if not _script_ready(owner, data):
        return None
    _guard_local(owner, path, None)
    _put(owner, data, path, {"absent"}, _scope(marker))
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
            return _from_statusline(owner, data, path, proj, d.get("statusLine")), True
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


def _install_records(owner):
    """The `plugins` object of <config>/plugins/installed_plugins.json, the
    installs Claude Code records, or None when it cannot be read or is not
    an object. Callers read key names and install paths only."""
    try:
        rec = os.path.join(owner.sensor.base_dir(), "plugins", "installed_plugins.json")
        if not stat.S_ISREG(os.stat(rec).st_mode):      # a FIFO would hang the hook
            return None
        with open(rec, encoding="utf-8") as f:
            recs = json.load(f).get("plugins")
        return recs if isinstance(recs, dict) else None
    except Exception:
        return None


def _has(recs, plugin):
    return any(isinstance(k, str) and k.startswith(plugin + "@") for k in recs)


def _statusline_uninstalled(owner):
    """Whether the install records surely say the statusline plugin is not
    installed: they describe this install (a statusline-hub@ key) and hold
    no statusline@ key at all, whatever its value. Anything else - records
    unreadable, of an unknown shape, or not naming the hub (loaded with
    --plugin-dir, say) - is False: the hub cannot tell, and yielding is for
    good."""
    recs = _install_records(owner)
    return recs is not None and _has(recs, owner.PLUGIN) and not _has(recs, owner.STATUSLINE)


def _statusline_installs_only_hooks(owner):
    """Whether Claude Code records at least one statusline@ install and none
    of them ships hooks/owner.py - every installed version registers as a hub
    hook and never installs its own entry. False when the records cannot be
    read."""
    try:
        recs = _install_records(owner) or {}
        paths = [e.get("installPath") for k, v in recs.items()
                 if isinstance(k, str) and k.startswith(owner.STATUSLINE + "@")
                 for e in (v if isinstance(v, list) else ()) if isinstance(e, dict)]
        return bool(paths) and all(
            isinstance(p, str) and p and os.path.isdir(os.path.join(p, "hooks")) and
            not os.path.lexists(os.path.join(p, "hooks", "owner.py")) for p in paths)
    except Exception:
        return False


def _statusline_enabled(owner, files):
    """Whether the statusline plugin is enabled in one of `files` (False
    when one cannot be read)."""
    try:
        return any(owner.enabled_for(owner.read_settings(p), owner.STATUSLINE)
                   for p in files)
    except owner.SettingsError:
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
        cur = _read(owner, p).get("statusLine")
        kind = owner.classify(cur)
        if kind == "foreign":
            owner.write_marker(data, "deferred", path, owner.command_for(data))
            return _wrap_offer(owner, p)
        if kind == "own":  # installed before, its owner.json lost: adopt it
            import registry
            rec, _ = registry.read_wrap()
            if rec and owner._same_path(rec["settings"], p) and rec["running"]:
                owner.write_marker(data, "wrapping", p, owner.command_for(data))
            elif rec and owner._same_path(rec["settings"], p):
                # the user had unwrapped (or it yielded); ours is back only by a
                # stale session's write: undo that, never re-run the wrap
                _write(owner, p, rec["entry"], expect_entry=_read(owner, p).get("statusLine"),
                       raw=rec["raw"])
                owner.write_marker(data, "unwrapped", p, owner.command_for(data))
                return (f"put your own status line back in {p} (an older session's "
                        f"settings write had restored the hub's entry after --unwrap).")
            else:
                owner.write_marker(data, "installed", p, owner.command_for(data))
            return None
        if kind == "statusline":
            return _from_statusline(owner, data, p, proj, cur)
    if _statusline_removed(owner, data, path):
        owner.write_marker(data, "removed", path, owner.command_for(data))
        return (f"the statusline footer was removed from {path} earlier, so the hub "
                f"leaves that status line slot empty. To turn it on: "
                f"/install-statusline-hub{_flag(owner, path)}")
    if _statusline_pending(owner, data, compete):
        raise Wait()
    if not _script_ready(owner, data):
        return None
    _guard_local(owner, path, proj)
    _put(owner, data, path, {"absent"})
    what = ("the statusline footer, and any other display hooks registered"
            if statusline_hooked() or (_statusline_installs_only_hooks(owner) and
                                       _statusline_enabled(owner, compete)) else
            f"its registered display hooks (a blank line until one registers; "
            f"{_footer_hint(owner)})")
    return (f"status line slot taken in {path}: from your next session the hub records "
            f"each render for the tools that read it and draws {what}. Undo: "
            f"/install-statusline-hub{_flag(owner, path)} --remove")


def _blocked_message(owner, path, reason, verb, project=False):
    """The once-only line for a Blocked. `project`: the marker it resumes was
    set by an explicit /install-statusline-hub --project."""
    retry = "start a new session"
    if reason == "tracked" and project:
        return (f"{path} is tracked by git, so the hub does not write its entry there on "
                f"its own (it is an absolute path on this machine); left as it is, not "
                f"{verb}. To put it back there, run /install-statusline-hub --project "
                f"again; or /install-statusline-hub --local for this machine only.")
    if reason == "tracked":
        # A project's local settings outrank its shared ones, which outrank the
        # user's (documented: https://code.claude.com/docs/en/settings), so the
        # fix that wins over the team's file is --local.
        return (f"{path} is tracked by git, and the status line entry is an absolute "
                f"path on this machine; left as it is, not {verb} there. To have the "
                f"hub own the slot in this project, run /install-statusline-hub --local "
                f"(a git-ignored .claude/settings.local.json, which outranks the shared "
                f"file), and remove any dead statusLine entry from the team's shared "
                f"file.")
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
        elif state in ("installed", "wrapping", "unwrapped"):
            resume = state
        else:
            return None  # removed, yielded, deferred - or unreadable: hands off
    else:
        resume = "new"
    try:
        if resume == "installed":
            return heal(owner, data, marker)
        if resume in ("wrapping", "unwrapped"):
            return heal_wrap(owner, data, marker, resume)
        return first_run(owner, data, _project_dir(inp))
    except (owner.Changed, Wait):
        return None  # changed under us, or the statusline plugin's turn: next session
    except Blocked as b:
        if marker and marker.get("state") == "blocked":
            return None  # said once already; retried quietly
        try:
            owner.write_marker(data, "blocked", b.path, owner.command_for(data),
                               reason=b.reason, resume=resume, **_scope(marker))
        except Exception:
            return None
        return _blocked_message(owner, b.path, b.reason,
                                "installed" if resume == "new" else "restored",
                                project=bool(_scope(marker)))


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
