"""The window mirror: Claude Code's context-window selection, re-derived in a hook.

Hooks are never told the context window (200K or 1M), and the status line that
is told it is optional. This module mirrors the two functions Claude Code uses:

- lf(model, sdkBetas) - the MODEL window, the number the status line reports
  as context_window_size and `-p` reports as modelUsage.contextWindow;
- HE(model, autoCompactWindow) - the AUTO-COMPACT window, min(lf, configured),
  the point where Claude Code compacts on its own.

Both are pure functions of inputs a hook can read (the transcript's model
line, the environment, the settings files, the served-model-catalog cache),
except for a few it cannot (SDK betas, server client data, experiments,
gateway mode from credential slots, flag settings layers, the legacy global
config, the long-context-credits latch of a process the hook cannot
identify). Every result carries `resolved`: True only when every input the
rule depends on was observed. The gate may hard-block on a resolved window
and only warns on an unresolved one.

The governing rule: a false hard-block is never acceptable. Any input
Claude Code could take from a layer a hook cannot observe makes the result
UNRESOLVED. What the unobservable inputs can do, and why the rest resolve:
- a window can only be LOWERED by them (betas and 1M-native models aside,
  which are unresolved anyway): gateway mode (vae()), the served catalog,
  the latch, client data and experiments for the auto-compact window. A
  wrong-high window under-warns; it never blocks early. So a resolved 200K
  window (haiku-4-5 and the other non-beta 200K models, DISABLE_1M, a seen
  latch) is safe, and a resolved 1M window needs only the latch to be known
  absent for this process (lib_context._latch).
- an auto-compact window is the other direction - it lowers the gate - so it
  resolves only when every layer that could set or cancel it was read
  (autocompact()).

The account file in the home directory is never read: in RULES_CC_VERSION no
field of it feeds lf() (see the d63e plan, section 0), and it holds secrets.

Re-deriving the table from a new Claude Code binary
(~/.local/share/claude/versions/<v>, a Bun bundle readable with `grep -a`):
anchors `function lf(`, `function Jz(`, `function Hy(`, `function HE(`,
`Hand-maintained baked-in model catalog` (the per-model `context` blocks),
`longContext1mCreditsBlocked` (the credits latch and its 429 phrases), and
`CLAUDE_CODE_AUTO_COMPACT_WINDOW`. Bump RULES_CC_VERSION when done. A mismatch
with the status line (lib_context.cross_check) demotes the Claude Code version
it was seen on to warn-only until then.

Stdlib only. Nothing here prints or returns an environment value: env inputs
become booleans, small ints and a provider name.
"""
import glob, os, re, sys
from urllib.parse import urlsplit

RULES_CC_VERSION = "2.1.277"

W200K = 200_000
W1M = 1_000_000
ACW_MIN, ACW_MAX = 100_000, 1_000_000    # U2e, GZe: the auto-compact window's clamp

# The baked-in catalog's `context` blocks (2.1.277): canonical id ->
# (window, native_1m, supports_1m_beta, providers where 1M is native on 3P).
CATALOG = {
    "claude-3-5-haiku": (W200K, False, False, ()),
    "claude-3-5-sonnet": (W200K, False, False, ()),
    "claude-3-7-sonnet": (W200K, False, False, ()),
    "claude-haiku-4-5": (W200K, False, False, ()),
    "claude-sonnet-4-0": (W200K, False, True, ()),
    "claude-sonnet-4-5": (W200K, False, True, ()),
    "claude-sonnet-4-6": (W200K, False, True, ()),
    "claude-sonnet-5": (W1M, True, True, ("bedrock", "vertex", "foundry")),
    "claude-opus-4-0": (W200K, False, False, ()),
    "claude-opus-4-1": (W200K, False, False, ()),
    "claude-opus-4-5": (W200K, False, False, ()),
    "claude-opus-4-6": (W200K, False, True, ()),
    "claude-opus-4-7": (W1M, True, True, ()),
    "claude-opus-4-8": (W1M, True, True, ()),
    "claude-opus-5": (W1M, True, True, ()),
    "claude-fable-5": (W1M, True, True, ()),
    "claude-fable-5-1": (W1M, True, True, ()),
    "claude-mythos-5": (W1M, True, True, ()),
    "claude-mythos-5-1": (W1M, True, True, ()),
    # qz(): native 1M by name, outside the catalog rows.
    "claude-mythos-preview": (W1M, True, False, ()),
}
# First-party ids that differ from the canonical id (We()).
FIRST_PARTY = {
    "claude-3-5-haiku-20241022": "claude-3-5-haiku",
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet",
    "claude-3-7-sonnet-20250219": "claude-3-7-sonnet",
    "claude-haiku-4-5-20251001": "claude-haiku-4-5",
    "claude-sonnet-4-20250514": "claude-sonnet-4-0",
    "claude-sonnet-4-5-20250929": "claude-sonnet-4-5",
    "claude-opus-4-20250514": "claude-opus-4-0",
    "claude-opus-4-1-20250805": "claude-opus-4-1",
    "claude-opus-4-5-20251101": "claude-opus-4-5",
}
# Provider-selecting env vars (Me()). Gateway mode can also come from host
# credential slots no hook can see; that only ever narrows 1M (never widens a
# window), and any selected provider other than first party is unresolved.
PROVIDER_ENV = (("CLAUDE_CODE_USE_GATEWAY", "gateway"),
                ("CLAUDE_CODE_USE_BEDROCK", "bedrock"), ("CLAUDE_CODE_USE_VERTEX", "vertex"),
                ("CLAUDE_CODE_USE_FOUNDRY", "foundry"),
                ("CLAUDE_CODE_USE_ANTHROPIC_AWS", "anthropicAws"),
                ("CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD", "anthropicGoogleCloud"),
                ("CLAUDE_CODE_USE_MANTLE", "mantle"))
# nue(): the 429 message fragments that set the long-context-credits latch.
NUE_PHRASES = ("Extra usage is required for long context",
               "Usage credits are required for long context")
LATCH_API_ERROR = "long_context_credits_required"
# HE(): ZPr, the models whose sub-1M window keeps a 200K auto-compact default.
ACW_200K_MODELS = ("claude-sonnet-4-6", "claude-opus-4-6", "claude-opus-4-8", "claude-opus-5")
# HE() via JPr/e$t: claude-sonnet-5's auto-compact default on these entrypoints.
ACW_SURFACE_ENTRYPOINTS = ("remote_cowork", "local-agent")
ACW_SURFACES = {"claude-sonnet-5": 500_000}
# Managed (policy) settings: the files, and the drop-in dirs of *.json.
MANAGED_SETTINGS = ("/etc/claude-code/managed-settings.json",
                    "/Library/Application Support/ClaudeCode/managed-settings.json")
MANAGED_DROPINS = ("/etc/claude-code/managed-settings.d",
                   "/Library/Application Support/ClaudeCode/managed-settings.d")
# The cached remote (server-managed) policy settings, under the config dir.
REMOTE_SETTINGS = "remote-settings.json"
# Points Claude Code at another managed-settings directory.
MANAGED_PATH_ENV = "CLAUDE_CODE_MANAGED_SETTINGS_PATH"
# Remote (server-managed) policy can never be positively ruled out by a hook
# in 2.1.277: whether an account is eligible (f() in the remote-settings
# chunk) depends on the subscription type kept in the global config, which a
# hook never reads, and on gateway credential slots it cannot see; and when
# the tengu_hover_rest storage backend is on (F(): CLAUDE_CODE_HOVER_REST, or
# a server flag), the remote policy lives in that backend, not in
# remote-settings.json. So a settings-derived auto-compact window, and an
# autoCompactEnabled read from settings, are never resolved.
REMOTE_POLICY_RULED_OUT = False
_DEFAULT_PORT = {"http": 80, "https": 443, "ws": 80, "wss": 443, "ftp": 21}

_ONE_M = re.compile(r"\[1m\]", re.I)
# Yl()/N(): Claude Code's integer parse for env values.
_SCI = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)[eE][+-]?\d+")
_THOUSANDS = re.compile(r"[+-]?\d{1,3}([_,\u00A0\u202F ])\d{3}(?:\1\d{3})*")
_LEADING_INT = re.compile(r"[+-]?\d+")
_TRUE = ("1", "true", "yes", "on")


def truthy(v):
    """Claude Code's boolean env parse: 1/true/yes/on, trimmed, any case."""
    return isinstance(v, str) and v.strip().lower() in _TRUE


def js_int(v):
    """Claude Code's Yl(): trim; N() takes scientific notation that is an
    integer (5e5) and grouped digits (1,000,000 / 1_000_000); otherwise JS
    parseInt(s, 10) - the leading integer, so "900k" is 900. None for NaN
    (no leading digits, or a non-integer 1.5e0)."""
    if not isinstance(v, str):
        return None
    s = v.strip()
    if len(s) <= 32:
        if _SCI.fullmatch(s):
            try:
                f = float(s)
            except ValueError:
                return None
            return int(f) if f == f and f not in (float("inf"), float("-inf")) \
                and f == int(f) else None
        if _THOUSANDS.fullmatch(s):
            return int(re.sub(r"[_,\u00A0\u202F ]", "", s))
    m = _LEADING_INT.match(s)
    return int(m.group(0)) if m else None


def env_inputs(environ):
    """The env-derived inputs, as booleans, ints and a provider name only."""
    g = environ.get
    mct = js_int(g("CLAUDE_CODE_MAX_CONTEXT_TOKENS"))
    raw_acw = g("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    providers = [name for var, name in PROVIDER_ENV if truthy(g(var))]
    base = g("ANTHROPIC_BASE_URL") or ""
    direct_url = not base or url_host(base) == "api.anthropic.com" \
        or truthy(g("_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL"))
    provider = providers[0] if len(providers) == 1 else (
        "firstParty" if not providers else "ambiguous")
    return {
        "d1m": truthy(g("CLAUDE_CODE_DISABLE_1M_CONTEXT")),
        "mct": mct if mct and mct > 0 else None,
        "disable_compact": truthy(g("DISABLE_COMPACT")),
        "disable_auto_compact": truthy(g("DISABLE_AUTO_COMPACT")),
        "acw": js_int(raw_acw),
        "acw_set": bool(raw_acw),
        "provider": provider,
        "first_party_direct": provider == "firstParty" and direct_url,
        "surface_entrypoint": (g("CLAUDE_CODE_ENTRYPOINT") or "").strip()
        in ACW_SURFACE_ENTRYPOINTS,
        "sdk_entrypoint": (g("CLAUDE_CODE_ENTRYPOINT") or "").strip().lower().startswith("sdk"),
    }


def url_host(url):
    """WHATWG URL.host as Claude Code's Yw() compares it: the lowercased
    hostname plus ":port" unless the port is the scheme's default. None when
    the URL does not parse (Claude Code then treats it as not first party)."""
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
    """The catalog id for a model string ([1m] stripped, lowercased,
    first-party dated ids folded), or None when it is not a catalog model."""
    if not isinstance(model_id, str):
        return None
    m = _ONE_M.sub("", model_id).strip().lower()
    if m in CATALOG:
        return m
    if m in FIRST_PARTY:
        return FIRST_PARTY[m]
    return None


def served_declared(config_dir, canon, read_json):
    """A window the served-model-catalog cache declares for `canon`
    (runtime.max_input_tokens, else context_window), or None. Reads only
    <config>/cache/model-catalog/*.json and, of those, only each model row's
    id and window fields. File names (they carry account ids) are never
    returned. `read_json` is lib_context.read_json_file (regular files
    only, no hang on a FIFO). Never raises."""
    if not canon or not config_dir:
        return None
    try:
        paths = sorted(glob.glob(os.path.join(config_dir, "cache", "model-catalog", "*.json")))[:8]
        for p in paths:
            doc = read_json(p)
            models = (((doc or {}).get("catalog") or {}).get("config") or {}).get("models") \
                if isinstance(doc, dict) else None
            if not isinstance(models, list):
                continue
            for row in models:
                if not isinstance(row, dict) or canonical(row.get("id")) != canon:
                    continue
                rt = row.get("runtime") if isinstance(row.get("runtime"), dict) else {}
                for v in (rt.get("max_input_tokens"), row.get("context_window")):
                    if isinstance(v, int) and not isinstance(v, bool) and v > 0:
                        return max(8192, min(v, W1M))
    except Exception:
        return None
    return None


def _res(window, resolved, rule):
    return {"window": window, "resolved": bool(resolved), "rule": rule}


def derive(model_id, env, latch=False, latch_known=True, served=None):
    """lf(): the model window for `model_id` under `env` (env_inputs()).

    latch: a long-context-credits 429 was seen in this Claude Code process.
    latch_known: the process start is known, so `latch` is trustworthy.
    served: the served catalog's declared window for this model, if any.
    Returns {"window", "resolved", "rule"}; window is None only for no model.
    """
    mct = env.get("mct")
    # 1. Xz(): DISABLE_COMPACT + MAX_CONTEXT_TOKENS overrides everything.
    if env.get("disable_compact") and mct:
        return _res(mct, True, "max_context_tokens")
    # 2. No model line yet.
    if not isinstance(model_id, str) or not model_id.strip():
        return _res(None, False, "no_model")
    base = _derive_base(model_id, env, served)
    # 10. Xsr(): the credits latch caps any window above 200K. When this
    #     process's latch cannot be known, a window above 200K may already be
    #     200K in Claude Code: unresolved.
    if base["window"] and base["window"] > W200K:
        if latch:
            return _res(W200K, base["resolved"] and latch_known, "credits_latch")
        if not latch_known:
            return _res(base["window"], False, "latch_unknown")
    return base


def _derive_base(model_id, env, served):
    """Jz(): steps 3-9 of the plan's algorithm."""
    if not isinstance(model_id, str) or not model_id.strip():
        return _res(None, False, "no_model")
    d1m = env.get("d1m")
    canon = canonical(model_id)
    row = CATALOG.get(canon)
    # 3. au(): a [1m] suffix is 1M - no model-support check, as in lf().
    if _ONE_M.search(model_id) and not d1m:
        return _res(W1M, True, "suffix_1m")
    # 4. SDK betas (context-1m) lift beta-capable 200K models on any
    #    provider (xU() has no provider check for them); unobservable.
    if row and not d1m and row[2] and row[0] < W1M:
        return _res(W200K, False, "beta_unobservable")
    # 5. Served catalog: a declared window wins over the baked table.
    if served:
        native = bool(row and row[1]) and not d1m
        win = served if (served <= W200K or native) else W200K
        return _res(win, False, "served_catalog")
    # 6. Hy(): natively 1M.
    if row and row[1] and not d1m:
        if env.get("first_party_direct"):
            return _res(W1M, True, "native_1m")
        return _res(W1M, False, "native_1m_3p")
    # 7. c6t(): an experiment can set claude-sonnet-4-6's window.
    if canon == "claude-sonnet-4-6" and not d1m:
        return _res(W200K, False, "experiment")
    # 8. A custom or unknown model: MAX_CONTEXT_TOKENS applies, else 200K.
    if not row:
        if env.get("mct"):
            return _res(env["mct"], False, "max_context_tokens_custom")
        return _res(W200K, False, "unknown_model")
    # 9. A known catalog model at its catalog window (DISABLE_1M caps at 200K).
    if d1m and row[0] > W200K:
        return _res(W200K, True, "disable_1m")
    return _res(row[0], True, "catalog_200k")


def autocompact(model_id, model_window, env, settings, observable=False, latch=False,
                served=None):
    """HE(): the auto-compact window, where Claude Code compacts on its own.

    `settings` is settings_autocompact()'s result; `observable` is True only
    when the running Claude Code process's command line was read and carries
    no flag that adds or narrows a settings layer (lib_context.proc_info).
    Returns {"window", "resolved", "source"}: `window` is set only when it is
    below model_window. RESOLVED needs every input Claude Code could use to be
    seen, because a wrong lower window would HARD-block early:
      - the value comes from CLAUDE_CODE_AUTO_COMPACT_WINDOW or from a valid
        autoCompactWindow setting (an int in [100000, 1000000], Claude Code's
        schema; anything else is skipped, as Claude Code skips it);
      - auto-compact is known ON: an observable settings layer sets
        autoCompactEnabled: true (without one, Claude Code falls back to the
        legacy global config, which a hook never reads);
      - no unobservable layer can override: `observable`, no SDK entrypoint
        (flag settings arrive at runtime), no unreadable policy file.
    Otherwise a lower window is UNRESOLVED: named in advisories, never a hard
    stop. Not observable at all (source "auto", nothing lowered): server
    client data and the claude-opus-4-8 experiment.
    """
    if not model_window:
        return {"window": None, "resolved": False, "source": "no_window"}
    # Wf(): these env vars turn auto-compact off outright.
    if env.get("disable_compact") or env.get("disable_auto_compact"):
        return {"window": None, "resolved": True, "source": "disabled"}
    if settings.get("enabled") is False:
        # Off in the highest observable layer. A hidden layer could only turn
        # it back on, which lowers the window: an under-warning, never a block.
        return {"window": None, "resolved": False, "source": "disabled_setting"}
    # Resolved only if no layer the hook cannot read can set or cancel it: a
    # policy tier present (any: Claude Code's managedSourcesBehavior picks
    # among them), remote policy not ruled out, a flag layer possible, or the
    # Claude Code process unverified all leave it unresolved.
    certain = bool(observable and settings.get("enabled") is True
                   and not settings.get("unsure") and not settings.get("policy", True)
                   and settings.get("remote_ruled_out") and not env.get("sdk_entrypoint"))

    def lowered(w, resolved, source):
        w = int(w)
        return {"window": w if w < model_window else None,
                "resolved": bool(resolved), "source": source}

    if env.get("acw_set"):
        v = env.get("acw")
        if v and v > 0:   # NaN or <= 0 is "invalid": Claude Code falls through
            return lowered(min(model_window, max(ACW_MIN, min(v, ACW_MAX))), certain, "env")
    s = settings.get("window")
    if s:
        return lowered(min(model_window, s), certain, "settings")
    canon = canonical(model_id) if isinstance(model_id, str) else None
    # Past this point client data and experiments (unreadable) come first.
    if model_window < W1M and (canon in ACW_200K_MODELS or latch
                               or (env.get("d1m") and served and served > W200K)):
        if model_window > W200K:
            return lowered(W200K, False, "model_default")
    if canon in ACW_SURFACES and env.get("surface_entrypoint"):
        return lowered(min(model_window, ACW_SURFACES[canon]), False, "model_default_surface")
    return {"window": None, "resolved": False, "source": "auto"}


def _valid_acw(v):
    """Claude Code's schema for autoCompactWindow: int().min(1e5).max(1e6)
    .catch(undefined) - anything else is as if the key were absent."""
    return isinstance(v, int) and not isinstance(v, bool) and ACW_MIN <= v <= ACW_MAX


def settings_autocompact(config_dir, project_dir, read_json, managed_paths=None,
                         dropin_dirs=None, environ=None):
    """The autoCompactWindow and autoCompactEnabled settings, merged by
    Claude Code's precedence: policy (the managed-settings files and
    drop-ins, the cached remote policy) > local > project > user. The flag
    layers (--settings, --managed-settings, SDK apply_flag_settings) are not
    files; lib_context.proc_info reports whether they can be in play. Reads
    only these two keys, from <config>/settings.json,
    <project>/.claude/settings.json, <project>/.claude/settings.local.json,
    the managed files and drop-ins, and <config>/remote-settings.json.
    Returns {"window": int|None, "enabled": bool|None, "unsure": bool,
    "policy": bool, "remote_ruled_out": bool}: `unsure` when a policy file
    exists but cannot be read, or a layer holds an autoCompactEnabled that
    is not a boolean; `policy` when ANY policy tier may be present - a
    managed-settings file or drop-in, remote-settings.json,
    CLAUDE_CODE_MANAGED_SETTINGS_PATH set, or an OS with an MDM tier (macOS,
    Windows) - since Claude Code then chooses among tiers by rules a hook
    does not model; `remote_ruled_out` is REMOTE_POLICY_RULED_OUT. Never
    raises."""
    if managed_paths is None:
        managed_paths = MANAGED_SETTINGS
    if dropin_dirs is None:
        dropin_dirs = MANAGED_DROPINS
    environ = os.environ if environ is None else environ
    out = {"window": None, "enabled": None, "unsure": False,
           "policy": bool(environ.get(MANAGED_PATH_ENV))
           or sys.platform in ("darwin", "win32"),
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
