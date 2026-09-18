"""The status line's sensor record and gauge policy. Stdlib only; never raises.

VENDORED CONTRACT, see skills/install-statusline/references/sensor-contract.md;
tests/test_contract.py enforces parity with the gauge publisher's own copy when
both plugins sit side by side in the source repo.

The sensor record: ${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<sid>.json
(v1: `exact`, `rate_limits`), written by statusline.py only. One writer, so no
lock: a render writes a unique temp file in the same dir (O_EXCL, 0600) and
os.replace()s it, so a reader never sees a torn file. Overlapping renders of
one session are last-writer-wins; each merges from what it read (a render
without `exact` keeps the stored one, likewise `rate_limits`), and a render
that finds a newer record on disk skips its write, so an older payload never
regresses a newer one.

The gauge policy: remaining-token thresholds, interpolated over (window, due,
hard) anchors - linear between anchors, clamped outside. DEFAULT_ANCHORS apply
unless a gauge publisher is active for this session (publisher()): then its
published anchors, labels and epoch are used instead.
"""
import json, math, os, re, time

SENSOR_V = 1
GAUGE_V = 1
# (window, due, hard) in REMAINING tokens, sorted by window.
DEFAULT_ANCHORS = ((200_000, 70_000, 40_000), (1_000_000, 150_000, 60_000))
# Where the optional gauge publisher keeps gauge.json and its per-session state
# (read-only here; never written). The soft dependency, in one place.
CG_DIR = ("claude-kit", "context-gate")
READ_MAX = 1 << 20          # bytes read from any file this module parses
LABEL_MAX = 40              # columns of a published label shown at most
ANCHORS_MAX = 16
FUTURE_SLACK_S = 60         # an on-disk `at` this far ahead of ours is a newer render
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


def publisher_dir():
    return os.path.join(base_dir(), *CG_DIR)


def gauge_path():
    return os.path.join(publisher_dir(), "gauge.json")


def publisher_state_path(session_id):
    return os.path.join(publisher_dir(), safe_sid(session_id) + ".json")


def thresholds(window, anchors=DEFAULT_ANCHORS):
    """{"due", "hard"} in remaining tokens for a window: linear between the
    anchors, clamped outside, each value truncated to an int."""
    w = max(int(window or 0), 1)
    lo_w, lo_d, lo_h = anchors[0]
    if w <= lo_w:
        return {"due": lo_d, "hard": lo_h}
    for hi_w, hi_d, hi_h in anchors[1:]:
        if w < hi_w:
            f = (w - lo_w) / (hi_w - lo_w)
            return {"due": int(lo_d + f * (hi_d - lo_d)),
                    "hard": int(lo_h + f * (hi_h - lo_h))}
        lo_w, lo_d, lo_h = hi_w, hi_d, hi_h
    return {"due": lo_d, "hard": lo_h}


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


def _int(x):
    return x if type(x) is int else None


def parse_anchors(thr):
    """The anchors of a v1 `thresholds` block as a sorted tuple of (window,
    due, hard) ints, or None when anything is off: a unit or interpolation
    other than v1's, no anchors, too many, a non-integer or negative field, a
    window below 1, or two anchors on one window."""
    if not isinstance(thr, dict):
        return None
    if thr.get("unit", "tokens_remaining") != "tokens_remaining" or \
            thr.get("interp", "linear_clamped") != "linear_clamped":
        return None
    raw = thr.get("anchors")
    if not isinstance(raw, list) or not 1 <= len(raw) <= ANCHORS_MAX:
        return None
    out = []
    for a in raw:
        if not isinstance(a, dict):
            return None
        w, du, h = _int(a.get("window")), _int(a.get("due")), _int(a.get("hard"))
        if w is None or du is None or h is None or w < 1 or du < 0 or h < 0:
            return None
        out.append((w, du, h))
    out.sort()
    if any(out[i][0] == out[i + 1][0] for i in range(len(out) - 1)):
        return None
    return tuple(out)


def _label(x):
    """A published label as one printable line of at most LABEL_MAX chars."""
    if not isinstance(x, str):
        return ""
    s = "".join(ch if ch.isprintable() else " " for ch in x[:4 * LABEL_MAX])
    return " ".join(s.split())[:LABEL_MAX].strip()


def publisher(session_id):
    """The gauge publisher's policy for this session, or None (standalone).

    Active only when gauge.json is v1 with valid anchors AND the publisher's
    own state file for THIS session exists - proof its hooks ran here, so a
    gauge.json left behind by an uninstalled publisher never switches it on.
    Returns {"anchors": tuple, "labels": {"due": str, "hard": str},
    "epoch": int or None}. Never raises."""
    try:
        if not session_id:
            return None
        state = publisher_state_path(session_id)
        if not os.path.isfile(state):
            return None
        g = _load(gauge_path())
        if not _is_v(g, GAUGE_V):
            return None
        anchors = parse_anchors(g.get("thresholds"))
        if not anchors:
            return None
        lab = g.get("labels") if isinstance(g.get("labels"), dict) else {}
        st = _load(state)
        ep = None
        if st is not None:
            ep = st.get("epoch", 0)
            ep = ep if type(ep) is int and ep >= 0 else None
        return {"anchors": anchors,
                "labels": {"due": _label(lab.get("due")), "hard": _label(lab.get("hard"))},
                "epoch": ep}
    except Exception:
        return None
