"""Shared context-depth accounting for claude-kit hooks.

Reads the session transcript and reports how full the context window is, using
the exact token counts Claude Code records in each assistant message's `usage`
block. That beats byte-size estimation: it is the same number the API charged.
"""
import json, os

DEFAULTS = (200_000, 1_000_000)


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
    """Return (current_tokens, peak_tokens). Zero when unknown."""
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
    """Context window size. Explicit override wins; otherwise infer from peak.

    Inference is deliberately crude but safe: it can only ever *raise* the
    denominator, so a wrong guess under-reports pressure rather than crying
    wolf every turn.
    """
    env = os.environ.get("CLAUDE_KIT_CONTEXT_WINDOW")
    if env and env.isdigit():
        return int(env)
    small, large = DEFAULTS
    return large if peak > small * 0.95 else small


def depth(transcript_path):
    """Return (tokens, window, pct_full)."""
    cur, peak = read_usage(transcript_path)
    w = window(peak)
    return cur, w, (100.0 * cur / w if w else 0.0)
