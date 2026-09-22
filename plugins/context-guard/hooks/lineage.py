#!/usr/bin/env python3
"""SessionEnd(clear) + PostToolUse(Read): the links that make a rehydration
manifest (HANDOFF.md) a session's own memory when another session wrote it.
rehydrate.py applies the rule (is_ours); this hook records two of its inputs.

SessionEnd, reason "clear": /clear ends the old session under its own id,
then regenerates the id and runs SessionStart(clear) in the SAME Claude Code
process. So the ending session leaves `cleared` = {sid, lineage, manifest,
at} on the process record _proc-<key> (lib_context.proc_key; no verified
process, no record, no link), and rehydrate.link_clear pops it. `manifest`
pins the version on disk now only when it was the ending session's own
(lib_context.owned_version with that session's state), else None: a manifest
a third session overwrote is never handed to the successor.

PostToolUse, tool Read: a whole-file Read (no offset, no limit) of this
repo's manifest whose frontmatter says `mode: handoff` records
`manifest_adopted` = {owner, sha, at} - that version, and only that one, is
then this session's. A `continue` or `landed` manifest is never adopted; a
partial Read, `cat` or `grep` looks without adopting. Skipped inside a
subagent (`agent_id` present), whose Read is not the main session's.

The version is lib_context.manifest_sha of the raw text, the same function
rehydrate.py uses. Never blocks, never raises: prints {} and exits 0.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

MANIFEST_NAME = "HANDOFF.md"


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
    path, _top, text = R.read_manifest(inp.get("cwd") or os.getcwd())
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
    if not isinstance(fp, str) or os.path.basename(fp) != MANIFEST_NAME:
        return
    if ti.get("offset") is not None or ti.get("limit") is not None:
        return
    sid = inp.get("session_id")
    if not isinstance(sid, str) or not sid:
        return
    R = _rehydrate()
    cwd = inp.get("cwd") or os.getcwd()
    path, _top, text = R.read_manifest(cwd)
    if not path:
        return
    target = fp if os.path.isabs(fp) else os.path.join(cwd, fp)
    if os.path.realpath(target) != os.path.realpath(path):
        return
    fm = R.front_matter(text)
    if fm.get("mode") != "handoff":
        return
    v = R.manifest_version(text, fm)
    if not v["owner"]:
        return                       # ownerless: already everyone's
    rec = {"owner": v["owner"], "sha": v["sha"], "at": time.time()}
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
        post_read(inp)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    print(json.dumps({}))
    sys.exit(0)
