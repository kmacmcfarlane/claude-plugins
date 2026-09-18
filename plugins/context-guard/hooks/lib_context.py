"""Shared state and depth accounting for the context-guard context-gate hooks.

Depth sources, in order of preference:
1. EXACT - written by statusline.py, which receives context_window.used_percentage
   and context_window_size from Claude Code on every render. Hooks never get
   those fields in their own input, so the status line doubles as the sensor.
2. INFERRED - from the transcript's per-message `usage` blocks (the numbers the
   API charged), window guessed from the session's peak. A guess can be wrong
   in either direction (live-fired 2026-09-16: a 1M session with a stale exact
   record was scored against 200K and HARD-blocked), so an inferred depth may
   warn but never block; context_warn.py requires source "exact" to exit 2.
   An exact record that has gone stale (older than EXACT_MAX_AGE_S) still
   pins the window - a session's window never shrinks with time - and its
   token count is a floor for the re-derived one. A new epoch (reset_epoch)
   demotes the record to window-only: a fresh record written seconds before
   a compaction or /clear describes the OLD fill and must not gate the new
   epoch, and the status line may not have re-rendered yet.

State is per session under $CLAUDE_CONFIG_DIR/claude-kit/context-gate/, and is
EPOCH-aware: a compaction (PostCompact) or /clear starts a new epoch, resetting
advisories, DUE/HARD accounting and the deferred-compaction flag. The v1 hooks
latched once per session, which is why a session's second fill got no warning.

Writers never load-modify-save the file bare: update_state(sid, fn) runs the
read-modify-write under a per-session advisory lock (fcntl.flock, bounded by
LOCK_TIMEOUT_S; on timeout, error, or a platform without fcntl it proceeds
unlocked - today's behaviour - rather than block a session). save_state writes
a unique temp file in the same dir (created O_EXCL, as tempfile.mkstemp does,
without the ~5 ms tempfile import on every status-line render) and
os.replace()s it, so a racing writer can never install a torn file. A session id becomes a file name only
when it is a safe token; anything else is hashed, so no id escapes the dir.
"""
import json, os, re, time
try:
    import fcntl
except ImportError:  # not POSIX: no lock, unique temp names still hold
    fcntl = None

DEFAULTS = (200_000, 1_000_000)
EXACT_MAX_AGE_S = 600


def _base_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))


def _state_dir():
    d = os.path.join(_base_dir(), "claude-kit", "context-gate")
    os.makedirs(d, exist_ok=True)
    return d


LOCK_TIMEOUT_S = 0.2
_SAFE_SID = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]{0,127}")


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


def state_path(session_id):
    return os.path.join(_state_dir(), safe_sid(session_id) + ".json")


def ledger_path(session_id):
    d = os.path.join(_base_dir(), "claude-kit", "ledger")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, safe_sid(session_id) + ".md")


def load_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            st = json.load(f)
        return st if isinstance(st, dict) else {}
    except Exception:
        return {}


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


def save_state(session_id, data):
    """Atomic write: a unique temp file in the same dir, then os.replace.
    Callers that modify existing state go through update_state instead."""
    tmp = None
    try:
        path = state_path(session_id)
        fd, tmp = _mkstemp(os.path.dirname(path), "." + safe_sid(session_id) + ".")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, path)
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _acquire(session_id):
    """Take the session's advisory lock, waiting at most LOCK_TIMEOUT_S.
    Returns the locked fd, or None (no fcntl, timeout, any error): the caller
    then proceeds unlocked. Never raises."""
    if fcntl is None:
        return None
    fd = None
    try:
        fd = os.open(os.path.join(_state_dir(), "." + safe_sid(session_id) + ".lock"),
                     os.O_RDWR | os.O_CREAT, 0o600)
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except (BlockingIOError, InterruptedError):
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.002)
    except Exception:
        pass
    if fd is not None:
        try:
            os.close(fd)
        except Exception:
            pass
    return None


def _release(fd):
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    except Exception:
        pass
    try:
        os.close(fd)
    except Exception:
        pass


def update_state(session_id, fn):
    """Read-modify-write the session's state under its lock: load, fn(state)
    mutates it in place, save. Returns the saved state. Every writer uses this
    so a concurrent writer's keys are never overwritten with a stale copy.
    The lock wait is bounded; on timeout the update runs unlocked."""
    fd = _acquire(session_id)
    try:
        st = load_state(session_id)
        fn(st)
        save_state(session_id, st)
        return st
    finally:
        _release(fd)


def epoch(state):
    return int(state.get("epoch", 0))


def reset_epoch(session_id, compact_summary=None):
    """New epoch: advisories and DUE/HARD accounting start over; the deferred
    flag clears; the checkpoint requirement re-arms. The ledger survives."""
    return update_state(session_id, lambda st: _reset(st, compact_summary))


def _reset(st, compact_summary):
    st["epoch"] = epoch(st) + 1
    st.pop("compact_deferred", None)
    st.pop("due", None)
    st["prompt_n"] = 0
    ex = st.get("exact") or {}
    if ex.get("window"):
        # Demote, don't stamp: the record's tokens/pct describe the epoch that
        # just ended, so a still-fresh one would HARD-block a 3% session until
        # the status line re-renders. With `at` zeroed and the tokens dropped,
        # depth() takes its existing stale path - the window survives as the
        # floor (a compaction never shrinks the model's window) and the count
        # comes from the post-boundary transcript alone, boundary line or not
        # (/clear starts a transcript with no compact_boundary). The next
        # status-line render overwrites the block with a fresh exact record.
        st["exact"] = {"window": int(ex["window"]), "at": 0}
    if compact_summary is not None:
        st["compact_summary"] = compact_summary[:20000]


def mark_checkpoint(session_id):
    def mark(st):
        st["checkpoint_epoch"] = epoch(st)
        st["checkpoint_at"] = time.strftime("%F %T")
    return update_state(session_id, mark)


def checkpointed_this_epoch(state):
    return state.get("checkpoint_epoch") == epoch(state)


def thresholds(window):
    """Action thresholds in REMAINING tokens, per threads/A-checkpoint-timing.md.

    Anchored at (200K -> due 70K, hard 40K) and (1M -> due 150K, hard 60K);
    linear between, clamped outside. A full checkpoint costs ~16-60K in the
    live window and one operator exchange is p90 ~20K, so `hard` is the floor
    below which only /checkpoint itself is affordable.
    """
    w = max(int(window or 0), 1)
    lo_w, hi_w = 200_000, 1_000_000
    if w <= lo_w:
        return {"due": 70_000, "hard": 40_000}
    if w >= hi_w:
        return {"due": 150_000, "hard": 60_000}
    f = (w - lo_w) / (hi_w - lo_w)
    return {"due": int(70_000 + f * 80_000), "hard": int(40_000 + f * 20_000)}


def read_usage(transcript_path):
    """Return (current_tokens, peak_tokens) from the transcript. Zero when unknown."""
    cur, peak, _ = scan_usage(transcript_path)
    return cur, peak


def scan_usage(transcript_path):
    """Return (current_tokens, peak_tokens, saw_boundary). `saw_boundary` is
    True when a compact_boundary was read: the current count then describes a
    new window and older state (a stale exact record) must not floor it."""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0, 0, False
    cur = peak = 0
    boundary = False
    try:
        with open(transcript_path, errors="replace") as fh:
            for line in fh:
                if '"compact_boundary"' in line:
                    # Bug A (live-fired 2026-08-31): pre-boundary usage records
                    # described the OLD window; reading them after a compaction
                    # reported 62% used on a ~2% session. Keep peak (the model
                    # window did not change); reset current.
                    cur = 0
                    boundary = True
                    continue
                if '"usage"' not in line:
                    continue
                try:
                    u = (json.loads(line).get("message") or {}).get("usage")
                except Exception:
                    continue
                if not u:
                    continue
                t = sum(u.get(k) or 0 for k in
                        ("input_tokens", "cache_read_input_tokens",
                         "cache_creation_input_tokens"))
                if t:
                    cur = t
                    peak = max(peak, t)
    except Exception:
        return 0, 0, False
    return cur, peak, boundary


def window(peak, floor=0):
    """Guess the window from the session's peak usage. `floor` is a window that
    was once reported exactly (by the status line): the guess never returns
    less than it. CLAUDE_KIT_CONTEXT_WINDOW pins the window outright."""
    env = os.environ.get("CLAUDE_KIT_CONTEXT_WINDOW")
    if env and env.isdigit():
        return int(env)
    small, large = DEFAULTS
    guess = large if peak > small * 0.95 else small
    return max(guess, int(floor or 0))


def depth(transcript_path, session_id=None):
    """Return (tokens, window, pct_full, source).

    source is "exact" when the status line's record is fresh; otherwise it
    starts with "inferred" - the tokens are a guess and must not hard-block.
    A stale exact record still contributes its window (as the floor of the
    guess) and its tokens (as the floor of the transcript-derived count).
    """
    ex = {}
    if session_id:
        ex = load_state(session_id).get("exact") or {}
        if ex.get("window") and time.time() - ex.get("at", 0) < EXACT_MAX_AGE_S:
            return ex["tokens"], ex["window"], ex["pct"], "exact"
    cur, peak, boundary = scan_usage(transcript_path)
    known = int(ex.get("window") or 0)
    w = window(peak, floor=known)
    src = "inferred"
    if known:
        if not boundary:
            # After a compaction the stale record describes the OLD epoch's
            # fill; only its window still holds.
            cur = max(cur, int(ex.get("tokens") or 0))
        src = "inferred, window from status line"
    return cur, w, (100.0 * cur / w if w else 0.0), src
