#!/usr/bin/env python3
"""statusline-hub tee: status-line stdin JSON -> the sensor record. Prints nothing.

Claude Code hands the status-line command a JSON payload on every render, and
that payload is the only live source of the exact context depth
(`context_window`) and the plan usage windows (`rate_limits`). Whoever renders
the status line must write them down for tools that never see the payload -
the sensor record, ${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<sid>.json
(v1; the contract is the statusline plugin's references/sensor-contract.md).
This command does only that, so a status line drawn by something else - a
ccstatusline Custom Command widget, a Starship `custom` module, a shell wrapper
around any other renderer - still feeds those readers:

    python3 /path/to/statusline-hub/hooks/tee.py < payload.json

It reads stdin once (at most READ_MAX characters; a longer payload is not
one Claude Code sends, and writes nothing), writes the record, prints nothing
and exits 0 - whatever the input, it never raises. Arguments are ignored
(F1 has no output modes).

VENDORED CONTRACT. Everything between the two VENDORED markers is a verbatim
copy of the statusline plugin's writer - hooks/sensor.py (the path, safe_sid,
the atomic merge-write) and hooks/statusline.py (num, obj, limits_record) -
because a plugin may not import another plugin's code. sensor_blocks() below
the copy restates, line for line, how statusline.py's main() builds the two
blocks. tests/test_parity.py fails when a copied definition drifts from its
source and runs statusline's record cases against both writers, whenever the
two plugins sit side by side in the source repo.

No pruning here: records are pruned from SessionStart - this plugin's
(housekeeping.py) and the statusline plugin's, whichever runs first that day.
In owner mode hub.py calls tee() on every render, before any hook runs.
"""
import json, math, os, re, sys, time

# -- VENDORED from statusline hooks/sensor.py and hooks/statusline.py (verbatim) --

SENSOR_V = 1
READ_MAX = 1 << 20
FUTURE_SLACK_S = 60
_SAFE_SID = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]{0,127}")


def base_dir():
    """${CLAUDE_CONFIG_DIR:-~/.claude}: an empty value counts as unset."""
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude")


def safe_sid(session_id):
    """The file-name form of a session id. A safe token (the UUIDs Claude Code
    issues) passes unchanged; anything else - a path separator, a leading dot,
    '..', over 128 chars, a non-string - becomes 'sid-<sha256 prefix>', so a
    hostile or garbled id can never name a path outside the state dir."""
    if not session_id:
        return "unknown"
    if isinstance(session_id, str) and _SAFE_SID.fullmatch(session_id):
        return session_id
    import hashlib  # lazily: only a malformed id pays for it
    raw = session_id if isinstance(session_id, str) else repr(session_id)
    return "sid-" + hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:32]


def sensor_dir():
    return os.path.join(base_dir(), "statusline", "sensor")


def sensor_path(session_id):
    return os.path.join(sensor_dir(), safe_sid(session_id) + ".json")


def _load(path):
    """The JSON object at path, or None (missing, unreadable, oversized, not
    an object)."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read(READ_MAX + 1)
        if len(raw) > READ_MAX:
            return None
        d = json.loads(raw)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _is_v(d, v):
    return isinstance(d, dict) and type(d.get("v")) is int and d["v"] == v


def _at(block):
    """A block's finite `at`, else 0.0."""
    if not isinstance(block, dict):
        return 0.0
    x = block.get("at")
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        return 0.0
    return float(x)


def read_sensor(session_id):
    """This session's sensor record (v1 dict), or {} when absent or not v1."""
    d = _load(sensor_path(session_id))
    return d if _is_v(d, SENSOR_V) else {}


def _mkstemp(d, prefix):
    """tempfile.mkstemp's contract (a new file no other writer can share,
    mode 0600) at os-module cost."""
    for _ in range(100):
        name = os.path.join(d, f"{prefix}{os.getpid()}.{os.urandom(6).hex()}.tmp")
        try:
            return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), name
        except FileExistsError:
            continue
    raise FileExistsError("no unique temp name")


def _mkdir_private(d):
    for p in (os.path.dirname(d), d):
        try:
            os.mkdir(p, 0o700)
        except FileExistsError:
            pass


def write_sensor(session_id, exact=None, rate_limits=None, now=None):
    """Merge `exact` / `rate_limits` into this session's record and replace it
    atomically. `now` is when the payload was read. Returns True when written;
    False when there was nothing to write, a newer render's record is already
    on disk, or anything failed. Never raises."""
    if not session_id or not (exact or rate_limits):
        return False
    tmp = None
    try:
        now = time.time() if now is None else now
        path = sensor_path(session_id)
        d = os.path.dirname(path)
        _mkdir_private(d)
        old = read_sensor(session_id)
        newest = max(_at(old.get("exact")), _at(old.get("rate_limits")))
        if now < newest <= now + FUTURE_SLACK_S:
            return False
        rec = {"v": SENSOR_V}
        ex = exact or old.get("exact")
        rl = rate_limits or old.get("rate_limits")
        if isinstance(ex, dict):
            rec["exact"] = ex
        if isinstance(rl, dict):
            rec["rate_limits"] = rl
        fd, tmp = _mkstemp(d, "." + safe_sid(session_id) + ".")
        with os.fdopen(fd, "w") as f:
            json.dump(rec, f, separators=(",", ":"))
        os.replace(tmp, path)
        tmp = None
        return True
    except Exception:
        return False
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


MAX_AHEAD = 366 * 86400


def num(v):
    """`v` as a finite float, or None: a missing, bool, text, NaN or infinite
    field is not a number the gauge or the sensor record can use."""
    if isinstance(v, bool):
        return None
    try:
        v = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return v if math.isfinite(v) else None


_WINDOW_KEY = re.compile(r"[a-z0-9_]{1,40}")
LIMIT_FIELDS = ("used_percentage", "resets_at")
WINDOWS_MAX = 16


def limits_record(rate_limits, now=None):
    """The sensor-record form of `rate_limits`, or None when there is nothing to record.

    `{<window>: {"used_percentage": float, "resets_at": float}, ..., "at": now}`
    with every window the payload carries -- five_hour, seven_day, spend_limit,
    and any other (a per-model window such as seven_day_opus lands under its own
    name) -- as long as its name is a short lowercase identifier. At most
    WINDOWS_MAX windows are kept: the first ones, in payload order (JSON object
    order, which json.load preserves), that pass the checks below, so the same
    payload always yields the same set. Only the two
    numeric fields are kept, each only when it is a finite number, and a
    resets_at more than MAX_AHEAD out (a milliseconds mix-up) is dropped; a
    window left with neither field is skipped. A past resets_at is kept: the
    reader compares it with the clock. Never raises.
    """
    try:
        if not isinstance(rate_limits, dict):
            return None
        now = time.time() if now is None else now
        rec = {}
        for key, w in rate_limits.items():
            if len(rec) >= WINDOWS_MAX:
                break
            if key == "at" or not isinstance(key, str) or not _WINDOW_KEY.fullmatch(key):
                continue
            if not isinstance(w, dict):
                continue
            fields = {f: num(w.get(f)) for f in LIMIT_FIELDS}
            if fields["resets_at"] is not None and fields["resets_at"] - now > MAX_AHEAD:
                fields["resets_at"] = None
            fields = {f: v for f, v in fields.items() if v is not None}
            if fields:
                rec[key] = fields
        if not rec:
            return None
        rec["at"] = now
        return rec
    except Exception:
        return None


def obj(v):
    """`v` when it is a JSON object, else {}: any payload block may be missing,
    null, or the wrong type."""
    return v if isinstance(v, dict) else {}

# -- end VENDORED --


def sensor_blocks(d, now):
    """(session id, exact block, rate_limits block) from one payload, built as
    statusline.py's main() builds them: `exact` only for a window size of at
    least 1 and a finite used percentage (clamped to 0-100), `rate_limits` by
    limits_record(); each None when there is nothing to record, and the id
    None when it is not a string. Never raises."""
    try:
        d = obj(d)
        cw = obj(d.get("context_window"))
        pct = num(cw.get("used_percentage"))
        size = num(cw.get("context_window_size") or 0)
        tok = num(cw.get("total_input_tokens") or 0)
        if size is None or tok is None or size < 1:
            pct = None
        else:
            size, tok = int(size), max(int(tok), 0)
        if pct is not None:
            pct = min(max(pct, 0.0), 100.0)
        sid = d.get("session_id")
        if not isinstance(sid, str):
            sid = None
        exact = ({"pct": pct, "tokens": tok, "window": size, "at": now}
                 if pct is not None and size else None)
        return sid, exact, limits_record(d.get("rate_limits"), now)
    except Exception:
        return None, None, None


def tee(text, now=None):
    """Write the sensor record for one payload given as JSON text. Returns
    True when a record was written (see write_sensor). Never raises."""
    try:
        if not isinstance(text, str) or len(text) > READ_MAX:
            return False
        now = time.time() if now is None else now
        sid, exact, rl = sensor_blocks(json.loads(text), now)
        return bool(sid) and write_sensor(sid, exact, rl, now)
    except Exception:
        return False


def main():
    try:
        text = sys.stdin.read(READ_MAX + 1)
    except Exception:
        return
    # `at` is when the payload was read, as in statusline.py.
    tee(text, time.time())


if __name__ == "__main__":
    try:
        main()
    except BaseException:  # a tee never raises and never prints
        pass
    sys.exit(0)
