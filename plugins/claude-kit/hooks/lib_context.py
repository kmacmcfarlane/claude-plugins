"""Shared context-depth accounting for claude-kit hooks.

Two sources, in order of preference:

1. EXACT - written by hooks/statusline.py, which receives
   `context_window.used_percentage` and `context_window_size` from Claude Code
   on every render. Hooks do not get those fields in their own input, so the
   status line doubles as the sensor and the hooks read its state file.
2. INFERRED - from the transcript's per-message `usage` blocks (the same
   numbers the API charged), with the window size guessed from the session's
   peak. Inference can only *raise* the denominator, so a wrong guess
   under-reports pressure rather than crying wolf every turn.
"""
import json, os, time

DEFAULTS = (200_000, 1_000_000)
EXACT_MAX_AGE_S = 600


def _state_dir():
    d = os.path.join(os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")),
                     "claude-kit", "context-gate")
    os.makedirs(d, exist_ok=True)
    return d


def state_path(session_id):
    return os.path.join(_state_dir(), (session_id or "unknown") + ".json")


def load_state(session_id):
    try:
        return json.load(open(state_path(session_id)))
    except Exception:
        return {}


def save_state(session_id, data):
    try:
        json.dump(data, open(state_path(session_id), "w"), indent=1)
    except Exception:
        pass


def read_usage(transcript_path):
    """Return (current_tokens, peak_tokens) from the transcript. Zero when unknown."""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0, 0
    cur = peak = 0
    try:
        with open(transcript_path, errors="replace") as fh:
            for line in fh:
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
