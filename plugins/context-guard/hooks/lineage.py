#!/usr/bin/env python3
"""SessionEnd(clear) + PostToolUse(Read): the links that make a rehydration
manifest (HANDOFF.md) a session's own memory when another session wrote it.
rehydrate.py applies the rule (is_ours); this hook records two of its inputs.

SessionEnd, reason "clear": /clear ends the old session under its own id,
then regenerates the id and runs SessionStart(clear) in the SAME Claude Code
process. So the ending session leaves `cleared` = {sid, lineage, manifest,
at} on the process record _proc-<key> (lib_context.proc_key; no verified
process, no record, no link), and rehydrate.link_clear pops it. `manifest`
pins the version on disk now - of this session's OWN manifest, its store file
if it has one, else the legacy repo file (rehydrate.own_manifest) - only when
it was the ending session's own (lib_context.owned_version with that session's
state), else None: a manifest a third session overwrote is never handed to the
successor.

PostToolUse, tool Read: a whole-file Read (no offset, no limit) of a manifest
(by a path named HANDOFF.md) whose frontmatter says `mode: handoff` records
`manifest_adopted` = {owner, sha, at, sid?} - that version, and only that one,
is then this session's. The path is another session's store manifest
(lib_context.manifest_sid decides that, and its session directory is recorded
as `sid`: the address) or, during the migration window, the legacy repo
manifest, by realpath (no `sid`: the pin seals that file). A session never
adopts its OWN store file - it is already ours by path. A `continue` or
`landed` manifest is never adopted; a partial Read, `cat` or `grep` looks
without adopting. Skipped inside a subagent (`agent_id` present), whose Read is
not the main session's.

The same PostToolUse(Read) also follows a rehydrated manifest's "Read in
full" list through (read_list.mark_read): a whole-file Read of a listed path,
by realpath, marks it read; context_warn.py names the unread ones once.

The version is lib_context.manifest_sha of the raw text, the same function
rehydrate.py uses. Never blocks, never raises: prints {} and exits 0.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import read_list

MANIFEST_NAME = L.MANIFEST_NAME


def _rehydrate():
    import rehydrate  # lazily: only a manifest-shaped event pays for it
    return rehydrate


def session_end(inp):
    if inp.get("reason") != "clear":
        return
    sid = inp.get("session_id")
    if not isinstance(sid, str) or not sid:
        return
    key = L.proc_key()
    if not key:
        return
    R = _rehydrate()
    st = L.load_state(sid)
    pin = None
    # Store-else-legacy, the same resolution every other pin site uses: this
    # session's own manifest when it has one, else the legacy repo file it is
    # still writing. A site that resolved differently from the site that reads
    # its pin would leave every linked /clear with a foreign header.
    path, text = R.own_manifest(sid, inp.get("cwd") or os.getcwd())
    if path:
        v = R.manifest_version(text)
        if L.owned_version(st, sid, v):
            pin = {"owner": v["owner"], "sha": v["sha"]}
    rec = {"sid": sid, "lineage": L.lineage_of(st), "manifest": pin,
           "at": time.time()}
    L.update_state(L.PROC_PREFIX + key, lambda p: p.__setitem__("cleared", rec))


def post_read(inp):
    if inp.get("agent_id") or inp.get("tool_name") not in (None, "Read"):
        return
    ti = inp.get("tool_input")
    if not isinstance(ti, dict):
        return
    fp = ti.get("file_path")
    # A cheap pre-filter before any git call, on every Read: only a path whose
    # own name is HANDOFF.md can adopt. A Read through a differently named
    # symlink to the manifest does not adopt - that fails safe (a header, not
    # the full manifest). The realpath comparison below is the identity test.
    if not isinstance(fp, str) or os.path.basename(fp) != MANIFEST_NAME:
        return
    if ti.get("offset") is not None or ti.get("limit") is not None:
        return
    sid = inp.get("session_id")
    if not isinstance(sid, str) or not sid:
        return
    R = _rehydrate()
    cwd = inp.get("cwd") or os.getcwd()
    target = os.path.realpath(fp if os.path.isabs(fp) else os.path.join(cwd, fp))
    # Whose manifest is this? A path inside the per-session store answers with
    # its own session directory (L.manifest_sid: realpath containment, the sid
    # is the first component, the relative path is exactly <sid>/HANDOFF.md).
    # Anything else is compared, as before, against the legacy repo manifest.
    store = L.manifest_sid(target)
    if store is not None:
        if store == L.safe_sid(sid):
            return          # its own store file: ours by path, nothing to record
        text = R.read_text(target)
        if text is None:
            return
    else:
        path, _top, text = R.read_manifest(cwd)
        if not path or target != os.path.realpath(path):
            return
    fm = R.front_matter(text)
    if fm.get("mode") != "handoff":
        return
    v = R.manifest_version(text, fm)
    if not v["owner"]:
        return                       # ownerless: already everyone's
    rec = {"owner": v["owner"], "sha": v["sha"], "at": time.time()}
    if store is not None:
        # The ADDRESS of the file read, kept apart from the pin that seals it.
        # A record with no `sid` (this arm, or one written before the store
        # existed) seals the legacy repo file and addresses no store directory.
        rec["sid"] = store
    L.update_state(sid, lambda st: st.__setitem__("manifest_adopted", rec))


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(inp, dict):
        return
    ev = inp.get("hook_event_name")
    if ev == "SessionEnd":
        session_end(inp)
    elif ev == "PostToolUse":
        try:
            read_list.mark_read(L, inp)
        except Exception:
            pass
        post_read(inp)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    print(json.dumps({}))
    sys.exit(0)
