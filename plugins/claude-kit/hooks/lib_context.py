"""Shared state and depth accounting for the claude-kit context-gate hooks.

Depth sources, in order of preference:
1. EXACT - written by statusline.py, which receives context_window.used_percentage
   and context_window_size from Claude Code on every render. Hooks never get
   those fields in their own input, so the status line doubles as the sensor.
2. INFERRED - from the transcript's per-message `usage` blocks (the numbers the
   API charged), window guessed from the session's peak. Inference can only
   raise the denominator, so a wrong guess under-reports pressure.

State is per session under $CLAUDE_CONFIG_DIR/claude-kit/context-gate/, and is
EPOCH-aware: a compaction (PostCompact) or /clear starts a new epoch, resetting
advisories, DUE/HARD accounting and the deferred-compaction flag. The v1 hooks
latched once per session, which is why a session's second fill got no warning.
"""
import json, os, time

DEFAULTS = (200_000, 1_000_000)
EXACT_MAX_AGE_S = 600


def _base_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))


def _state_dir():
    d = os.path.join(_base_dir(), "claude-kit", "context-gate")
    os.makedirs(d, exist_ok=True)
    return d


def state_path(session_id):
    return os.path.join(_state_dir(), (session_id or "unknown") + ".json")


def ledger_path(session_id):
    d = os.path.join(_base_dir(), "claude-kit", "ledger")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, (session_id or "unknown") + ".md")


def load_state(session_id):
    try:
        return json.load(open(state_path(session_id)))
    except Exception:
        return {}


def save_state(session_id, data):
    try:
        tmp = state_path(session_id) + ".tmp"
        json.dump(data, open(tmp, "w"), indent=1)
        os.replace(tmp, state_path(session_id))
    except Exception:
        pass


def epoch(state):
    return int(state.get("epoch", 0))


def reset_epoch(session_id, compact_summary=None):
    """New epoch: advisories and DUE/HARD accounting start over; the deferred
    flag clears; the checkpoint requirement re-arms. The ledger survives."""
    st = load_state(session_id)
    st["epoch"] = epoch(st) + 1
    st.pop("compact_deferred", None)
    st.pop("due", None)
    st["prompt_n"] = 0
    if compact_summary is not None:
        st["compact_summary"] = compact_summary[:20000]
    save_state(session_id, st)
    return st


def mark_checkpoint(session_id):
    st = load_state(session_id)
    st["checkpoint_epoch"] = epoch(st)
    st["checkpoint_at"] = time.strftime("%F %T")
    save_state(session_id, st)
    return st


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
    if not transcript_path or not os.path.exists(transcript_path):
        return 0, 0
    cur = peak = 0
    try:
        with open(transcript_path, errors="replace") as fh:
            for line in fh:
                if '"compact_boundary"' in line:
                    # Bug A (live-fired 2026-08-31): pre-boundary usage records
                    # described the OLD window; reading them after a compaction
                    # reported 62% used on a ~2% session. Keep peak (the model
                    # window did not change); reset current.
                    cur = 0
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
        return 0, 0
    return cur, peak


def window(peak):
    env = os.environ.get("CLAUDE_KIT_CONTEXT_WINDOW")
    if env and env.isdigit():
        return int(env)
    small, large = DEFAULTS
    return large if peak > small * 0.95 else small


def depth(transcript_path, session_id=None):
    """Return (tokens, window, pct_full, source) where source is 'exact' or 'inferred'."""
    if session_id:
        ex = load_state(session_id).get("exact") or {}
        if ex and time.time() - ex.get("at", 0) < EXACT_MAX_AGE_S and ex.get("window"):
            return ex["tokens"], ex["window"], ex["pct"], "exact"
    cur, peak = read_usage(transcript_path)
    w = window(peak)
    return cur, w, (100.0 * cur / w if w else 0.0), "inferred"
