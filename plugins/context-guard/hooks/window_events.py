#!/usr/bin/env python3
"""SessionStart + PostModelSwitch: bookkeeping for the window mirror.

SessionStart records `proc` in the session's state: where this Claude Code
process's part of the transcript starts (a byte offset), which process it is
(lib_context.proc_key(): pid and /proc start time) and when. The long-context
-credits latch lives in Claude Code's memory for the life of the process, so
only a credits API-error line at or after that offset proves it is set now:
  startup / resume / fork  offset = the transcript's size now (0 when new);
                           a resumed or forked transcript's older lines came
                           from another process.
  clear                    a new transcript in the SAME process: offset 0,
                           and the pid-keyed process record carries any latch
                           set before the /clear.
  compact                  same process, same transcript: `proc` is kept.

PostModelSwitch records `model_switch` = {to_model, at, size}: the transcript
gets its next model line only when the next request is built, so until then
the switch is the newer word on the model. A full `claude-...` id replaces the
transcript's model; an alias ("opus", "sonnet[1m]") leaves the derived window
unresolved until the model line lands. Only the model string is stored.

Never blocks, never raises: prints {} and exits 0.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L


def _size(path):
    try:
        return os.path.getsize(path) if path else 0
    except OSError:
        return 0


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(inp, dict):
        return
    sid = inp.get("session_id") or "unknown"
    ev = inp.get("hook_event_name")
    path = inp.get("transcript_path") or ""
    now = time.time()
    if ev == "SessionStart":
        source = inp.get("source") or "startup"
        if source == "compact":
            return
        rec = {"offset": 0 if source == "clear" else _size(path),
               "key": L.proc_key(), "at": now, "source": source}
        L.update_state(sid, lambda st: st.__setitem__("proc", rec))
    elif ev == "PostModelSwitch":
        to = inp.get("to_model")
        if not isinstance(to, str) or not to.strip():
            return
        rec = {"to_model": to.strip()[:200], "at": now, "size": _size(path)}
        L.update_state(sid, lambda st: st.__setitem__("model_switch", rec))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    print(json.dumps({}))
    sys.exit(0)
