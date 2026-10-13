"""The window rules: which context window a Claude Code session gets, worked
out in a hook from documented and observed rules.

Hooks are never told the context window (200K or 1M), and the status line
that is told it is optional. This module derives two numbers:

- the MODEL window (derive()), the number the status line reports as
  context_window_size and `-p` reports as modelUsage.contextWindow;
- the AUTO-COMPACT window (autocompact()), the point where Claude Code
  compacts on its own, capped at the model window.

Every rule here is cited, in a comment beside it, to a page of the Claude
Code docs (doc: <URL>) or to an observation (observed: <method>, Claude Code
<version>). Nothing else counts as a source. RULES_CC_VERSION is the Claude
Code version the cited rules were last checked against; bump it when they
are re-checked. A mismatch with the status line (lib_context.cross_check)
demotes the Claude Code version it was seen on to warn-only.

Which context window a session gets, beyond the cited rules here, can be
derived from Claude Code's internals; it is not recorded here.

The inputs are what a hook can read (the transcript's model line, the
environment, the settings files) and some it cannot: betas requested with
ANTHROPIC_BETAS or --betas, settings passed with --settings, server-managed
settings, and the credits error of a process the hook cannot identify. Every
result carries `resolved`: True only when every input the rule depends on
was observed and the rule itself is cited. The gate may hard-block on a
resolved window and only warns on an unresolved one.

The governing rule: a false hard-block is never acceptable. Any input
Claude Code could take from a layer a hook cannot observe, any value
spelled in a way the docs do not describe, and any model no cited rule
covers make the result UNRESOLVED. A wrong-high window under-warns; it never
blocks early. So a resolved 200K window (a cited 200K model,
CLAUDE_CODE_DISABLE_1M_CONTEXT) is safe, and a resolved 1M window also needs
the credits error to be known absent for this process (lib_context._latch).
An auto-compact window is the other direction - it lowers the gate - so it
resolves only when every layer that could set or cancel it was read
(autocompact()).

The account file in the home directory is never read: it holds secrets.

Stdlib only. Nothing here prints or returns an environment value: env inputs
become booleans, small ints and a provider name.
"""
import glob, os, re, sys
from urllib.parse import urlsplit

RULES_CC_VERSION = "2.1.292"

DOC_MODEL_CONFIG = "https://code.claude.com/docs/en/model-config"
DOC_ENV_VARS = "https://code.claude.com/docs/en/env-vars"
DOC_ERRORS = "https://code.claude.com/docs/en/errors"

W200K = 200_000
W1M = 1_000_000
# doc: env-vars, CLAUDE_CODE_AUTO_COMPACT_WINDOW ("from 100000 to 1000000"),
# and settings-reference, autoCompactWindow (the same range).
ACW_MIN, ACW_MAX = 100_000, 1_000_000

# doc: model-config § Extended context - on the Anthropic API, Fable 5.1,
# Fable 5, Sonnet 5 and later, Haiku 5.5, and Opus 4.7 and later run with the
# 1M window on every plan (Haiku 5.5's ID, claude-haiku-5-5: model-config §
# Haiku 5.5 context window and pricing). Sonnet 5.5 and Opus 5.5 were also
# observed at 1M:
# `claude -p --model <id> --output-format json`, modelUsage.contextWindow,
# Claude Code 2.1.292.
NATIVE_1M = ("claude-fable-5", "claude-fable-5-1", "claude-sonnet-5", "claude-sonnet-5-5",
             "claude-haiku-5-5", "claude-opus-4-7", "claude-opus-4-8", "claude-opus-5", "claude-opus-5-5")
# doc: model-config § Extended context - Opus 4.6 and Sonnet 4.6 reach 1M only
# through their [1m] variant; without it they run at 200K. A beta requested
# through ANTHROPIC_BETAS or --betas (env-vars, cli-reference) is not
# observable, so their 200K never resolves.
SUFFIX_ONLY_1M = ("claude-opus-4-6", "claude-sonnet-4-6")
# observed: `claude -p --model <id> --output-format json` reports
# modelUsage.contextWindow 200000, Claude Code 2.1.292.
OBSERVED_200K = ("claude-haiku-4-5", "claude-opus-4-5")
# Every model a cited rule covers. Any other model is unresolved.
KNOWN = NATIVE_1M + SUFFIX_ONLY_1M + OBSERVED_200K
# doc: platform.claude.com/docs/en/about-claude/model-deprecations - the
# dated first-party ids of the cited models above.
FIRST_PARTY = {
    "claude-haiku-4-5-20251001": "claude-haiku-4-5",
    "claude-opus-4-5-20251101": "claude-opus-4-5",
}
# doc: env-vars - the provider-selecting variables, and
# CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST, set by a host platform that manages
# provider routing. An empty value counts as unset for provider selection
# (env-vars).
PROVIDER_ENV = (("CLAUDE_CODE_USE_BEDROCK", "bedrock"), ("CLAUDE_CODE_USE_VERTEX", "vertex"),
                ("CLAUDE_CODE_USE_FOUNDRY", "foundry"),
                ("CLAUDE_CODE_USE_ANTHROPIC_AWS", "anthropic-aws"),
                ("CLAUDE_CODE_USE_MANTLE", "mantle"),
                ("CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST", "host-managed"))
# The usage-credits error for 1M context, matched by its documented title.
# doc: errors § Usage credits required for 1M context
# (https://code.claude.com/docs/en/errors#usage-credits-required-for-1m-context):
# the error's index entry is this title, and its full text, as the docs show
# it on the CLI, opens "API Error: " followed by it and a hint after " · ".
# The hint differs in the Desktop app and before v2.1.268 (same section), so
# only the title is matched. The docs also say that, past 200K, Claude Code
# "compacts the conversation back under the standard context limit and keeps
# the session at that limit afterward". Not yet seen in a transcript on this
# machine: a miss leaves the window too high, which under-warns and never
# blocks.
CREDITS_MESSAGE = "Usage credits required for 1M context"
# Which errors make Claude Code hold a session at a 200K window can be
# derived from Claude Code's internals; it is not recorded here.
# doc: managed-settings - the managed-settings files and drop-in dirs of *.json.
MANAGED_SETTINGS = ("/etc/claude-code/managed-settings.json",
                    "/Library/Application Support/ClaudeCode/managed-settings.json")
MANAGED_DROPINS = ("/etc/claude-code/managed-settings.d",
                   "/Library/Application Support/ClaudeCode/managed-settings.d")
# doc: server-managed-settings - the cached server-managed settings, under the
# config dir.
REMOTE_SETTINGS = "remote-settings.json"
# Server-managed settings can never be ruled out by a hook. doc:
# server-managed-settings - Claude Code fetches them from Anthropic's servers
# at startup and polls hourly, and they sit in the highest (managed) tier
# (settings § precedence). A hook cannot know what the server will deliver.
# So a settings-derived auto-compact window, and an autoCompactEnabled read
# from settings, are never resolved.
REMOTE_POLICY_RULED_OUT = False
_DEFAULT_PORT = {"http": 80, "https": 443, "ws": 80, "wss": 443, "ftp": 21}

_ONE_M = re.compile(r"\[1m\]", re.I)
# doc: env-vars § Variables - booleans: 1/true/yes/on turn a behaviour on and
# 0/false/no/off turn it off, in any casing.
_ON = ("1", "true", "yes", "on")
_OFF = ("0", "false", "no", "off")
# doc: env-vars § Variables - numbers accept scientific notation and digit
# separators (`2e3`, `64_000`) as well as plain digits.
_PLAIN = re.compile(r"\d+")
_UNDERSCORE = re.compile(r"\d{1,3}(?:_\d{3})+")
_SCI = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)[eE]\+?\d+")
_LEADING_INT = re.compile(r"[+-]?\d+")


def flag(v):
    """A documented boolean variable: True (on), False (off, empty or unset),
    or None when the value is spelled in a way the docs do not describe."""
    if v is None:
        return False
    if not isinstance(v, str):
        return None
    s = v.strip().lower()
    if not s or s in _OFF:
        return False
    if s in _ON:
        return True
    return None


def doc_int(v):
    """A positive integer written in a documented numeric form (plain digits,
    `_` digit separators, or scientific notation with an integer value),
    else None. Surrounding text, other separators and suffixes are not
    documented forms and give None."""
    if not isinstance(v, str) or len(v) > 32:
        return None
    if _PLAIN.fullmatch(v) or _UNDERSCORE.fullmatch(v):
        n = int(v.replace("_", ""))
        return n if n > 0 else None
    if _SCI.fullmatch(v):
        try:
            f = float(v)
        except ValueError:
            return None
        if f != f or f in (float("inf"), float("-inf")) or f != int(f) or f <= 0:
            return None
        return int(f)
    return None


def acw_int(v):
    """CLAUDE_CODE_AUTO_COMPACT_WINDOW's reading. doc: env-vars - it accepts
    a plain integer only, and "a value like `500k` reads as `500`": the
    leading integer. Returns (value or None, documented): `documented` is
    False for a spelling the docs give no reading for (scientific notation,
    digit separators, no leading digits)."""
    if not isinstance(v, str):
        return None, False
    s = v.strip()
    m = _LEADING_INT.match(s)
    if not m:
        return None, False
    rest = s[m.end():]
    documented = not rest or rest[0].isalpha() and not _SCI.fullmatch(s)
    return int(m.group(0)), documented


def env_inputs(environ):
    """The env-derived inputs, as booleans, ints and a provider name only.
    A boolean is True, False, or None for an undocumented spelling."""
    g = environ.get
    raw_mct = g("CLAUDE_CODE_MAX_CONTEXT_TOKENS")
    mct = doc_int(raw_mct)
    raw_acw = g("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    acw, acw_doc = acw_int(raw_acw) if raw_acw else (None, True)
    states = [(name, flag(g(var))) for var, name in PROVIDER_ENV]
    providers = [name for name, on in states if on]
    base = g("ANTHROPIC_BASE_URL") or ""
    direct_url = not base or url_host(base) == "api.anthropic.com"
    if any(on is None for _, on in states):
        provider = "unknown"
    elif not providers:
        provider = "first-party"
    else:
        provider = providers[0] if len(providers) == 1 else "ambiguous"
    return {
        "d1m": flag(g("CLAUDE_CODE_DISABLE_1M_CONTEXT")),
        "mct": mct,
        "mct_bad": bool(raw_mct) and mct is None,
        "disable_compact": flag(g("DISABLE_COMPACT")),
        "disable_auto_compact": flag(g("DISABLE_AUTO_COMPACT")),
        "acw": acw,
        "acw_set": bool(raw_acw),
        "acw_doc": acw_doc,
        "provider": provider,
        "first_party_direct": provider == "first-party" and direct_url,
    }


def url_host(url):
    """ANTHROPIC_BASE_URL's host (doc: env-vars), lowercased, plus ":port"
    unless the port is the scheme's default. None when the URL does not
    parse; the session is then not treated as first party."""
    try:
        u = urlsplit(url.strip())
        if not u.scheme or not u.hostname:
            return None
        port = u.port
        scheme = u.scheme.lower()
        if port is None or port == _DEFAULT_PORT.get(scheme):
            return u.hostname.lower()
        return f"{u.hostname.lower()}:{port}"
    except Exception:
        return None


def canonical(model_id):
    """The cited id for a model string ([1m] stripped, lowercased, dated
    first-party ids folded), or None when no cited rule covers it."""
    if not isinstance(model_id, str):
        return None
    m = _ONE_M.sub("", model_id).strip().lower()
    if m in KNOWN:
        return m
    if m in FIRST_PARTY:
        return FIRST_PARTY[m]
    return None


def _res(window, resolved, rule):
    return {"window": window, "resolved": bool(resolved), "rule": rule}


def derive(model_id, env, latch=False, latch_known=True):
    """The model window for `model_id` under `env` (env_inputs()).

    latch: the documented credits error (CREDITS_MESSAGE) was seen in this
      Claude Code process.
    latch_known: the process start is known, so `latch` is trustworthy.
    Returns {"window", "resolved", "rule"}; window is None only for no model.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        return _res(None, False, "no_model")
    mct, dc = env.get("mct"), env.get("disable_compact")
    suffix = bool(_ONE_M.search(model_id))
    canon = canonical(model_id)
    # 1. doc: model-config § Correct the window for a gateway or custom
    #    model ID - for a recognized ID, CLAUDE_CODE_MAX_CONTEXT_TOKENS takes
    #    effect only with DISABLE_COMPACT; for an unrecognized ID without
    #    [1m] it applies directly; an unrecognized ID with [1m] is assumed
    #    1M and the variable "doesn't apply on its own" unless
    #    CLAUDE_CODE_DISABLE_1M_CONTEXT is also set.
    if (mct or env.get("mct_bad")) and dc is not False:
        if dc is None or env.get("mct_bad"):
            return _res(mct or _derive_base(model_id, env)["window"], False,
                        "max_context_tokens_unparsed")
        if canon or not suffix or env.get("d1m") is True:
            return _res(mct, True, "max_context_tokens")
        # Claude Code may or may not recognize this spelling: 1M or the value.
        return _res(W1M, False, "suffix_1m_unrecognized")
    base = _derive_base(model_id, env)
    # 2. doc: errors § Usage credits required for 1M context - after the
    #    error Claude Code keeps the session at the standard limit. Under
    #    answer 167 (a) that 200K window only warns. When this process's
    #    error state cannot be known, a window above 200K may already be
    #    200K in Claude Code: unresolved.
    if base["window"] and base["window"] > W200K:
        if latch:
            return _res(W200K, False, "credits_message")
        if not latch_known:
            return _res(base["window"], False, "latch_unknown")
    return base


def _derive_base(model_id, env):
    """The model window before the credits error is applied."""
    d1m = env.get("d1m")
    canon = canonical(model_id)
    # doc: model-config § Extended context - a [1m] suffix selects the 1M
    # window on a model documented as 1M-capable. With
    # CLAUDE_CODE_DISABLE_1M_CONTEXT set the suffix is sized like the same
    # spelling without it (model-config § Correct the window ...).
    if _ONE_M.search(model_id) and d1m is not True:
        if d1m is None:
            return _res(W1M, False, "flag_unparsed")
        if canon in NATIVE_1M or canon in SUFFIX_ONLY_1M:
            return _res(W1M, True, "suffix_1m")
        if canon:
            return _res(W1M, False, "suffix_1m_unsupported")
        # doc: model-config - an unrecognized ID with [1m] is assumed 1M;
        # whether Claude Code recognizes this spelling is not observable.
        return _res(W1M, False, "suffix_1m_unrecognized")
    if canon in SUFFIX_ONLY_1M:
        if d1m is True:
            return _res(W200K, True, "cited_200k")
        return _res(W200K, False, "beta_unobservable")
    if canon in NATIVE_1M:
        # doc: env-vars, model-config § Extended context -
        # CLAUDE_CODE_DISABLE_1M_CONTEXT holds a native 1M model at 200K.
        if d1m is True:
            return _res(W200K, True, "disable_1m")
        if d1m is None:
            return _res(W1M, False, "flag_unparsed")
        if env.get("first_party_direct"):
            return _res(W1M, True, "native_1m")
        return _res(W1M, False, "native_1m_3p")
    if canon in OBSERVED_200K:
        return _res(W200K, True, "cited_200k")
    # A custom or unknown model: CLAUDE_CODE_MAX_CONTEXT_TOKENS applies
    # (doc: model-config), else Claude Code's assumed window.
    if env.get("mct"):
        return _res(env["mct"], False, "max_context_tokens_custom")
    return _res(W200K, False, "unknown_model")


def autocompact(model_id, model_window, env, settings, observable=False):
    """The auto-compact window, where Claude Code compacts on its own.

    `settings` is settings_autocompact()'s result; `observable` is True only
    when the running Claude Code process's command line was read and carries
    no flag that adds or narrows a settings layer (lib_context.proc_info).
    Returns {"window", "resolved", "source"}: `window` is set only when it is
    below model_window. RESOLVED needs every input Claude Code could use to be
    seen, because a wrong lower window would HARD-block early:
      - the value comes from CLAUDE_CODE_AUTO_COMPACT_WINDOW (documented
        spelling) or from a valid autoCompactWindow setting (doc:
        settings-reference, an int from 100000 to 1000000);
      - auto-compact is known ON: a settings layer the hook reads sets
        autoCompactEnabled: true. Its documented default is true
        (settings-reference), but a managed layer may set it, so an
        explicit true is required, as caution;
      - no layer the hook cannot read can override: `observable`, no
        unreadable policy file, no policy tier, and server-managed settings
        ruled out (never, REMOTE_POLICY_RULED_OUT).
    Otherwise a lower window is UNRESOLVED: named in advisories, never a hard
    stop. With nothing configured the source is "auto": Claude Code then
    compacts at a window tuned for the model (settings-reference,
    autoCompactWindow), which is not modelled here.
    When auto-compaction starts on a session whose window was set below 1M
    can be derived from Claude Code's internals; it is not recorded here.
    """
    if not model_window:
        return {"window": None, "resolved": False, "source": "no_window"}
    dc, dac = env.get("disable_compact"), env.get("disable_auto_compact")
    # doc: env-vars - DISABLE_COMPACT and DISABLE_AUTO_COMPACT turn
    # auto-compaction off.
    if dc is True or dac is True:
        return {"window": None, "resolved": True, "source": "disabled"}
    if settings.get("enabled") is False:
        # Off in the highest observable layer. A hidden layer could only turn
        # it back on, which lowers the window: an under-warning, never a block.
        return {"window": None, "resolved": False, "source": "disabled_setting"}
    # Resolved only if no layer the hook cannot read can set or cancel it: a
    # policy tier present (any: managedSourcesBehavior, doc: managed-settings,
    # picks among them), server-managed settings not ruled out, a flag layer
    # possible, an undocumented spelling, or the Claude Code process
    # unverified all leave it unresolved.
    certain = bool(observable and settings.get("enabled") is True
                   and not settings.get("unsure") and not settings.get("policy", True)
                   and settings.get("remote_ruled_out")
                   and dc is False and dac is False)

    def lowered(w, resolved, source):
        w = int(w)
        return {"window": w if w < model_window else None,
                "resolved": bool(resolved), "source": source}

    if env.get("acw_set"):
        v = env.get("acw")
        if v and v > 0:
            # doc: env-vars - clamped to [100000, 1000000] and capped at the
            # model's context window.
            return lowered(min(model_window, max(ACW_MIN, min(v, ACW_MAX))),
                           certain and env.get("acw_doc"), "env")
        # No positive leading integer: the docs give no reading. The next
        # layer is used here, and nothing below can resolve.
        certain = False
    s = settings.get("window")
    if s:
        return lowered(min(model_window, s), certain, "settings")
    return {"window": None, "resolved": False, "source": "auto"}


def _valid_acw(v):
    """A valid autoCompactWindow value. doc: settings-reference
    (https://code.claude.com/docs/en/settings-reference#autocompactwindow):
    a number of tokens from 100000 to 1000000. Anything else is treated
    here as if the key were absent in that layer."""
    return isinstance(v, int) and not isinstance(v, bool) and ACW_MIN <= v <= ACW_MAX


def settings_autocompact(config_dir, project_dir, read_json, managed_paths=None,
                         dropin_dirs=None):
    """The autoCompactWindow and autoCompactEnabled settings, merged by
    the documented precedence (doc: settings § precedence): managed (the
    managed-settings files and drop-ins, the cached server-managed
    settings) > local > project > user. The flag layers (--settings, doc:
    cli-reference; an Agent SDK host's apply_flag_settings request, doc:
    hooks and agent-sdk/typescript) are not files; lib_context.proc_info
    reports whether they can be in play. Reads only these two keys, from
    <config>/settings.json, <project>/.claude/settings.json,
    <project>/.claude/settings.local.json, the managed files and drop-ins,
    and <config>/remote-settings.json.
    Returns {"window": int|None, "enabled": bool|None, "unsure": bool,
    "policy": bool, "remote_ruled_out": bool}: `unsure` when a policy file
    exists but cannot be read, or a layer holds an autoCompactEnabled that
    is not a boolean; `policy` when ANY policy tier may be present - a
    managed-settings file or drop-in, remote-settings.json, or an OS with an
    MDM tier (macOS, Windows; doc: managed-settings) - since Claude Code then
    chooses among tiers by rules a hook does not model; `remote_ruled_out`
    is REMOTE_POLICY_RULED_OUT. Never raises."""
    if managed_paths is None:
        managed_paths = MANAGED_SETTINGS
    if dropin_dirs is None:
        dropin_dirs = MANAGED_DROPINS
    out = {"window": None, "enabled": None, "unsure": False,
           "policy": sys.platform in ("darwin", "win32"),
           "remote_ruled_out": REMOTE_POLICY_RULED_OUT}
    try:
        user = [os.path.join(config_dir, "settings.json")] if config_dir else []
        proj = [os.path.join(project_dir, ".claude", "settings.json"),
                os.path.join(project_dir, ".claude", "settings.local.json")] \
            if project_dir else []
        policy = list(managed_paths)
        for d in dropin_dirs:
            policy += sorted(glob.glob(os.path.join(glob.escape(d), "*.json")))
        if config_dir:
            policy.append(os.path.join(config_dir, REMOTE_SETTINGS))
        win_set = en_set = False
        for p in reversed(user + proj + policy):     # highest precedence first
            exists = os.path.lexists(p)
            if exists and p in policy:
                out["policy"] = True
            d = read_json(p) if exists else None
            if not isinstance(d, dict):
                if exists and p in policy:
                    out["unsure"] = True
                continue
            if not win_set and _valid_acw(d.get("autoCompactWindow")):
                win_set = True
                out["window"] = d["autoCompactWindow"]
            if not en_set and d.get("autoCompactEnabled") is not None:
                en_set = True
                if isinstance(d["autoCompactEnabled"], bool):
                    out["enabled"] = d["autoCompactEnabled"]
                else:
                    out["unsure"] = True
    except Exception:
        out["unsure"] = out["policy"] = True
    return out
