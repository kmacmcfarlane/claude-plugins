#!/usr/bin/env python3
"""usage_report — read Claude Code transcripts and account for token spend.

Library plus a thin CLI skeleton (`scan`, `summary`). The full report tables
are deliberately not here yet; this file owns the parsing, the attribution and
the arithmetic, and the printing stays small until the report feature lands.

What it reads (nothing else, and never writes):

    <config>/projects/<slug>/<session-id>.jsonl                 main session
    <config>/projects/<slug>/<session-id>/subagents/agent-<id>.jsonl
    <config>/projects/<slug>/<session-id>/subagents/agent-<id>.meta.json

`<config>` is CLAUDE_CODE_CONFIG_DIR / CLAUDE_CONFIG_DIR, default ~/.claude;
`--projects-dir` overrides the projects root outright (used by the tests).

Constraints this file lives under:

- stdlib only; read-only; no network. Dollar figures are a *local list-price
  estimate* — Claude Code has not written costUSD since 1.0.9 — and on a
  subscription plan they are not what is billed.
- **Dedupe by (`message.id`, `requestId`) across every file read, keeping the
  line with the largest `output_tokens`.** One API response is streamed as
  several lines (`apiBlockIndex` 1,2,...); only the last carries the final
  `output_tokens`, so keeping the first undercounts output. A resumed or forked
  session copies earlier history into its new file with the same message.id
  and requestId, so a per-file dedupe counts that history twice. Ties keep the
  first line read. The key is built from what exists: a line with a message.id
  but no requestId is keyed (id, None) — it still dedupes its own streamed
  lines, and never matches a line that has a requestId; a line with no
  message.id has no identity and is counted as it stands.
- Attribution comes from the path plus the meta file: the directory gives the
  parent session, the filename gives the agentId, `meta.model` gives the
  *requested* tier (sonnet/opus/fable/inherit, or absent when inherited), and
  `message.model` on each assistant line gives the model actually served.
- Prices are data, not constants: scripts/prices.json, versioned, with a
  `retrieved` date. An unknown model warns once to stderr and falls back to a
  configurable default — it never raises.
- Opus-equivalent tokens: per token class, tokens * (price(model, class) /
  price(opus, class)), summed over classes. It answers "how many tokens of the
  same kind would have cost this much on Opus", which is the honest unit for
  judging routing when dollars are fiction.
- This is an offline analysis tool. It must never be wired into the statusline
  or a hook: it re-reads whole transcripts, and that path has its own gauge in
  plugins/context-guard/hooks/lib_context.py.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOKEN_CLASSES = ("input", "output", "cache_creation", "cache_read")
PRICE_CLASSES = ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read")
DEFAULT_PRICES = Path(__file__).resolve().parent / "prices.json"
DATE_SUFFIX_RE = re.compile(r"-\d{8}$")
NO_MODEL = "(no model)"
UNKNOWN_PREFIX = "unknown:"
SLUG_RE = re.compile(r"[^a-zA-Z0-9]")


# --------------------------------------------------------------------------
# paths and scope


def config_dir():
    """The Claude Code config directory (CLAUDE_CONFIG_DIR wins, else ~/.claude)."""
    for var in ("CLAUDE_CODE_CONFIG_DIR", "CLAUDE_CONFIG_DIR"):
        value = os.environ.get(var)
        if value:
            return Path(value).expanduser()
    return Path.home() / ".claude"


def projects_dir(override=None):
    if override:
        return Path(override).expanduser()
    return config_dir() / "projects"


def slug_for_path(path):
    """Claude Code's project-directory slug: every non-alphanumeric character to '-'."""
    return SLUG_RE.sub("-", str(Path(path).resolve()))


def resolve_scope(root, cwd=None, all_projects=False):
    """The project directories in scope.

    The slug for `cwd` wins outright when that directory exists. Only when it
    does not is an ancestor used: the longest existing slug that prefixes the
    cwd slug *at a path-component boundary*, so a worktree under a project
    resolves to that project while `/foo/barbaz` never matches `-foo-bar`.
    """
    root = Path(root)
    if not root.is_dir():
        return []
    dirs = sorted(p for p in root.iterdir() if p.is_dir())
    if all_projects:
        return dirs
    want = slug_for_path(cwd or Path.cwd())
    exact = [p for p in dirs if p.name == want]
    if exact:
        return exact
    prefixes = [p for p in dirs
                if want.startswith(p.name) and want[len(p.name):len(p.name) + 1] == "-"]
    if prefixes:
        return [max(prefixes, key=lambda p: len(p.name))]
    return []


def parse_since(value, now=None):
    """`7d` / `2026-09-01` / a full ISO timestamp -> an aware UTC datetime."""
    if value is None:
        return None
    text = str(value).strip()
    match = re.fullmatch(r"(\d+)\s*d", text, re.IGNORECASE)
    if match:
        base = now or datetime.now(timezone.utc)
        return base - timedelta(days=int(match.group(1)))
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("--since wants an ISO date/timestamp or Nd, got %r" % value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


# --------------------------------------------------------------------------
# prices


class PriceTable:
    """The versioned price table, with alias/date-suffix resolution."""

    def __init__(self, data, default_model=None, warn=None):
        self.data = data
        self.models = data.get("models", {})
        self.aliases = {k: v for k, v in (data.get("aliases") or {}).items() if v}
        self.base = data.get("normalization_base")
        self.default_model = default_model or data.get("default_model")
        self.version = data.get("version")
        self.retrieved = data.get("retrieved")
        self._warn = warn if warn is not None else _stderr_warn
        self._warned = set()
        self.unknown_models = []

    @classmethod
    def load(cls, path=None, default_model=None, warn=None):
        path = Path(path or DEFAULT_PRICES)
        with path.open(encoding="utf-8") as handle:
            return cls(json.load(handle), default_model=default_model, warn=warn)

    def canonical(self, model):
        """The price-table key for a model id, or None when it is unknown."""
        if not model:
            return None
        if model in self.models:
            return model
        if model in self.aliases:
            return self.aliases[model]
        stripped = DATE_SUFFIX_RE.sub("", model)
        if stripped in self.models:
            return stripped
        if stripped in self.aliases:
            return self.aliases[stripped]
        return None

    def prices_for(self, model):
        """(key, prices, known). Unknown models warn once and fall back.

        A line with no model at all (an API-error or synthetic assistant line
        that still carries a usage block) is an unknown model like any other:
        it warns under the NO_MODEL sentinel and is priced at the default,
        never silently folded into the default model's row.
        """
        key = self.canonical(model)
        if key:
            return key, self.models[key], True
        warn_key = model or NO_MODEL
        if warn_key not in self._warned:
            self._warned.add(warn_key)
            self.unknown_models.append(warn_key)
            self._warn("usage_report: unknown model %r; pricing it as %r"
                       % (warn_key, self.default_model))
        fallback = self.canonical(self.default_model)
        if fallback is None:
            return None, {c: 0.0 for c in PRICE_CLASSES}, False
        return fallback, self.models[fallback], False

    def weight(self, price_class, prices):
        """price(model, class) / price(opus, class) — the Opus-equivalent weight."""
        base = self.models.get(self.base) or {}
        divisor = base.get(price_class)
        if not divisor:
            return 0.0
        return float(prices.get(price_class, 0.0)) / float(divisor)

    def is_uncertain(self, key):
        return bool((self.models.get(key) or {}).get("uncertain"))


def _stderr_warn(message):
    print(message, file=sys.stderr)


# --------------------------------------------------------------------------
# records


class Record:
    """One deduped API response, with its tokens priced and normalised."""

    __slots__ = ("project", "session_id", "agent_id", "message_id", "request_id",
                 "dedupe_key", "model", "timestamp", "tokens", "cache_write_5m",
                 "cache_write_1h", "price_key", "model_known", "cost_usd",
                 "opus_equivalent_tokens")

    def __init__(self, project, session_id, agent_id, message_id, model,
                 timestamp, tokens, cache_write_5m, cache_write_1h,
                 request_id=None, dedupe_key=None):
        self.project = project
        self.session_id = session_id
        self.agent_id = agent_id
        self.message_id = message_id
        self.request_id = request_id
        self.dedupe_key = dedupe_key
        self.model = model
        self.timestamp = timestamp
        self.tokens = tokens
        self.cache_write_5m = cache_write_5m
        self.cache_write_1h = cache_write_1h
        self.price_key = None
        self.model_known = True
        self.cost_usd = 0.0
        self.opus_equivalent_tokens = 0.0

    @property
    def total_tokens(self):
        return sum(self.tokens.values())

    def price(self, table):
        """Fill in price_key, cost_usd and opus_equivalent_tokens."""
        key, prices, known = table.prices_for(self.model)
        self.price_key = key
        self.model_known = known
        priced = (("input", self.tokens["input"]),
                  ("output", self.tokens["output"]),
                  ("cache_read", self.tokens["cache_read"]),
                  ("cache_write_5m", self.cache_write_5m),
                  ("cache_write_1h", self.cache_write_1h))
        cost = 0.0
        equivalent = 0.0
        for price_class, count in priced:
            if not count:
                continue
            cost += count * float(prices.get(price_class, 0.0)) / 1_000_000.0
            equivalent += count * table.weight(price_class, prices)
        self.cost_usd = cost
        self.opus_equivalent_tokens = equivalent
        return self


def usage_tokens(usage):
    """Token counts by class, plus the 5m/1h cache-creation split."""
    tokens = {
        "input": int(usage.get("input_tokens") or 0),
        "output": int(usage.get("output_tokens") or 0),
        "cache_creation": int(usage.get("cache_creation_input_tokens") or 0),
        "cache_read": int(usage.get("cache_read_input_tokens") or 0),
    }
    split = usage.get("cache_creation") or {}
    write_5m = int(split.get("ephemeral_5m_input_tokens") or 0)
    write_1h = int(split.get("ephemeral_1h_input_tokens") or 0)
    if not (write_5m or write_1h):
        # No split recorded: price the whole creation figure at the 5m rate.
        write_5m = tokens["cache_creation"]
    elif write_5m + write_1h != tokens["cache_creation"]:
        # The split is authoritative when the two disagree.
        tokens["cache_creation"] = write_5m + write_1h
    return tokens, write_5m, write_1h


class FileScan:
    """The result of reading one transcript file."""

    def __init__(self, path, records, boundaries=0, duplicates=0,
                 skipped=0, malformed=0):
        self.path = Path(path)
        self.records = records
        self.boundaries = boundaries
        self.duplicates = duplicates
        self.skipped = skipped
        self.malformed = malformed


def dedupe_key(message, obj):
    """The identity of one API response: (message.id, requestId), or None.

    None means the line has no message.id and cannot be matched to any other
    line, so it is never deduped. A missing requestId keys as None rather than
    disabling the dedupe, because such a line still repeats its response once
    per streamed block.
    """
    message_id = message.get("id")
    if not message_id:
        return None
    return (message_id, obj.get("requestId") or None)


def _supersedes(record, held):
    """True when `record` should replace `held`: strictly more output tokens."""
    return record.tokens["output"] > held.tokens["output"]


def read_transcript(path, project=None, session_id=None, agent_id=None,
                    table=None, since=None):
    """Parse one JSONL transcript into deduped, priced records.

    Within this file, lines sharing a dedupe_key() collapse to the one with the
    largest output_tokens (the last streamed line carries the final count).
    Cross-file duplicates are removed afterwards by dedupe_scans(). `--since`
    is applied to the surviving line, after the dedupe. Lines without a usage
    block (user turns, tool results, the compact-summary injection) are
    skipped; `compact_boundary` system lines are counted, not summed — a
    boundary resets the context window, never the spend.
    """
    path = Path(path)
    candidates = []
    best = {}
    boundaries = duplicates = skipped = malformed = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                malformed += 1
                continue
            if not isinstance(obj, dict):
                malformed += 1
                continue
            if obj.get("subtype") == "compact_boundary":
                boundaries += 1
                continue
            message = obj.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            if not isinstance(usage, dict):
                skipped += 1
                continue
            key = dedupe_key(message, obj)
            tokens, write_5m, write_1h = usage_tokens(usage)
            record = Record(
                project=project if project is not None else path.parent.name,
                session_id=session_id or obj.get("sessionId"),
                agent_id=agent_id or obj.get("agentId"),
                message_id=message.get("id") or "%s#%d" % (path.name, number),
                model=message.get("model"),
                timestamp=parse_timestamp(obj.get("timestamp")),
                tokens=tokens,
                cache_write_5m=write_5m,
                cache_write_1h=write_1h,
                request_id=obj.get("requestId") or None,
                dedupe_key=key,
            )
            if key is not None and key in best:
                duplicates += 1
                slot = best[key]
                if _supersedes(record, candidates[slot]):
                    candidates[slot] = record
                continue
            if key is not None:
                best[key] = len(candidates)
            candidates.append(record)
    records = []
    for record in candidates:
        if since is not None and (record.timestamp is None or record.timestamp < since):
            skipped += 1
            continue
        if table is not None:
            record.price(table)
        records.append(record)
    return FileScan(path, records, boundaries, duplicates, skipped, malformed)


def dedupe_scans(scans):
    """Remove records duplicated across files, in place; return the count dropped.

    For each dedupe_key the record with the most output_tokens survives, in
    whichever file it was read from; on a tie the first one read (in `scans`
    order) survives. Each dropped record adds one to its own file's
    `duplicates`. Idempotent: a second pass over the same scans drops nothing.
    """
    winners = {}
    losers = []
    for scan in scans:
        for record in scan.records:
            key = record.dedupe_key
            if key is None:
                continue
            held = winners.get(key)
            if held is None:
                winners[key] = (scan, record)
            elif _supersedes(record, held[1]):
                losers.append(held)
                winners[key] = (scan, record)
            else:
                losers.append((scan, record))
    drop = {}
    for scan, record in losers:
        drop.setdefault(id(scan), (scan, set()))[1].add(id(record))
    for scan, ids in drop.values():
        scan.records = [r for r in scan.records if id(r) not in ids]
        scan.duplicates += len(ids)
    return len(losers)


def session_scans(sessions):
    """Every FileScan in `sessions`, in read order: each main file, then its dispatches."""
    scans = []
    for session in sessions:
        if session.main_scan is not None:
            scans.append(session.main_scan)
        scans.extend(d.scan for d in session.dispatches)
    return scans


# --------------------------------------------------------------------------
# sessions and dispatches


class Dispatch:
    """One sub-agent dispatch: its meta file, its transcript, its children."""

    def __init__(self, agent_id, meta, scan):
        self.agent_id = agent_id
        self.meta = meta or {}
        self.scan = scan
        self.children = []

    @property
    def records(self):
        return self.scan.records

    @property
    def agent_type(self):
        return self.meta.get("agentType")

    @property
    def description(self):
        return self.meta.get("description")

    @property
    def parent_agent_id(self):
        return self.meta.get("parentAgentId")

    @property
    def spawn_depth(self):
        try:
            return int(self.meta.get("spawnDepth") or 1)
        except (TypeError, ValueError):
            return 1

    @property
    def requested_tier(self):
        """The tier asked for, or None when the dispatch inherited it."""
        return self.meta.get("model")

    @property
    def tier_source(self):
        return "meta" if "model" in self.meta else "inherited"

    def models_used(self):
        return sorted({r.model for r in self.records if r.model})

    def own_and_descendants(self):
        out = [self]
        stack = list(self.children)
        seen = {self.agent_id}
        while stack:
            child = stack.pop()
            if child.agent_id in seen:
                continue
            seen.add(child.agent_id)
            out.append(child)
            stack.extend(child.children)
        return out


class Session:
    def __init__(self, project, session_id, main_scan, dispatches):
        self.project = project
        self.session_id = session_id
        self.main_scan = main_scan
        self.dispatches = dispatches

    @property
    def main_records(self):
        return self.main_scan.records if self.main_scan else []

    def all_records(self):
        out = list(self.main_records)
        for dispatch in self.dispatches:
            out.extend(dispatch.records)
        return out

    def top_level_dispatches(self):
        """Dispatches that nothing else in this session spawned."""
        known = {d.agent_id for d in self.dispatches}
        return [d for d in self.dispatches
                if d.parent_agent_id is None or d.parent_agent_id not in known]


def link_dispatches(dispatches):
    """Wire parentAgentId into a tree and return the roots (spawnDepth 1)."""
    by_id = {d.agent_id: d for d in dispatches}
    roots = []
    for dispatch in dispatches:
        parent = by_id.get(dispatch.parent_agent_id)
        if parent is not None and parent is not dispatch:
            parent.children.append(dispatch)
        else:
            roots.append(dispatch)
    # A cycle or a missing parent would strand a dispatch; anything not
    # reachable from a root is promoted to a root so nothing is lost.
    reachable = set()
    for root in roots:
        reachable.update(d.agent_id for d in root.own_and_descendants())
    for dispatch in dispatches:
        if dispatch.agent_id not in reachable:
            roots.append(dispatch)
            reachable.update(d.agent_id for d in dispatch.own_and_descendants())
    return roots


def read_session(session_jsonl, table=None, since=None, project=None):
    """One main transcript plus every sub-agent file beside it."""
    session_jsonl = Path(session_jsonl)
    session_id = session_jsonl.stem
    project = project if project is not None else session_jsonl.parent.name
    main = read_transcript(session_jsonl, project=project, session_id=session_id,
                           table=table, since=since)
    dispatches = []
    subagents = session_jsonl.with_suffix("") / "subagents"
    if subagents.is_dir():
        for agent_jsonl in sorted(subagents.glob("agent-*.jsonl")):
            agent_id = agent_jsonl.stem[len("agent-"):]
            meta_path = agent_jsonl.with_suffix(".meta.json")
            meta = {}
            if meta_path.is_file():
                try:
                    with meta_path.open(encoding="utf-8") as handle:
                        loaded = json.load(handle)
                    if isinstance(loaded, dict):
                        meta = loaded
                except ValueError:
                    meta = {}
            scan = read_transcript(agent_jsonl, project=project,
                                   session_id=session_id, agent_id=agent_id,
                                   table=table, since=since)
            dispatches.append(Dispatch(agent_id, meta, scan))
    link_dispatches(dispatches)
    session = Session(project, session_id, main, dispatches)
    dedupe_scans(session_scans([session]))
    return session


def read_project(project_dir, table=None, since=None):
    project_dir = Path(project_dir)
    sessions = []
    for session_jsonl in sorted(project_dir.glob("*.jsonl")):
        sessions.append(read_session(session_jsonl, table=table, since=since,
                                     project=project_dir.name))
    dedupe_scans(session_scans(sessions))
    return sessions


# --------------------------------------------------------------------------
# aggregation


def empty_totals():
    totals = {c: 0 for c in TOKEN_CLASSES}
    totals["total_tokens"] = 0
    totals["opus_equivalent_tokens"] = 0.0
    totals["cost_usd"] = 0.0
    totals["records"] = 0
    return totals


def add_records(totals, records):
    for record in records:
        for token_class in TOKEN_CLASSES:
            totals[token_class] += record.tokens[token_class]
        totals["total_tokens"] += record.total_tokens
        totals["opus_equivalent_tokens"] += record.opus_equivalent_tokens
        totals["cost_usd"] += record.cost_usd
        totals["records"] += 1
    return totals


def totals_for(records):
    return round_totals(add_records(empty_totals(), records))


def round_totals(totals):
    totals["opus_equivalent_tokens"] = round(totals["opus_equivalent_tokens"])
    totals["cost_usd"] = round(totals["cost_usd"], 6)
    return totals


def model_bucket(record):
    """The by-model key for a record.

    A guessed price never hides inside the row of the model it was guessed as:
    unknown ids (and lines with no model at all) get their own visible
    `unknown:` key.
    """
    if record.model_known and record.price_key:
        return record.price_key
    return UNKNOWN_PREFIX + (record.model or NO_MODEL)


def dispatch_row(dispatch, flat):
    """One dispatch row; when not flat, nested dispatches roll up into it."""
    members = [dispatch] if flat else dispatch.own_and_descendants()
    records = [r for member in members for r in member.records]
    models = sorted({m for member in members for m in member.models_used()})
    return {
        "agent_id": dispatch.agent_id,
        "agent_type": dispatch.agent_type,
        "description": dispatch.description,
        "session_id": dispatch.scan.records[0].session_id if dispatch.records else None,
        "parent_agent_id": dispatch.parent_agent_id,
        "spawn_depth": dispatch.spawn_depth,
        "requested_tier": dispatch.requested_tier,
        "tier_source": dispatch.tier_source,
        "models": models,
        "rolled_up_dispatches": len(members) - 1,
        "totals": totals_for(records),
    }


def summarize(sessions, table, flat=False, scope=None, since=None):
    """The whole report as plain data — the shape `summary --json` prints."""
    totals = empty_totals()
    by_model = {}
    by_tier = {}
    dispatch_rows = []
    session_rows = []
    boundaries = duplicates = 0

    for session in sessions:
        session_records = session.all_records()
        for record in session_records:
            key = model_bucket(record)
            add_records(by_model.setdefault(key, empty_totals()), [record])
        add_records(totals, session_records)
        boundaries += session.main_scan.boundaries if session.main_scan else 0
        duplicates += session.main_scan.duplicates if session.main_scan else 0
        for dispatch in session.dispatches:
            boundaries += dispatch.scan.boundaries
            duplicates += dispatch.scan.duplicates

        roots = session.dispatches if flat else session.top_level_dispatches()
        rows = [dispatch_row(d, flat) for d in roots]
        for row in rows:
            tier = row["requested_tier"] or "inherit"
            add_bucket = by_tier.setdefault(tier, empty_totals())
            for token_class in TOKEN_CLASSES:
                add_bucket[token_class] += row["totals"][token_class]
            add_bucket["total_tokens"] += row["totals"]["total_tokens"]
            add_bucket["opus_equivalent_tokens"] += row["totals"]["opus_equivalent_tokens"]
            add_bucket["cost_usd"] += row["totals"]["cost_usd"]
            add_bucket["records"] += row["totals"]["records"]
        dispatch_rows.extend(rows)

        session_rows.append({
            "project": session.project,
            "session_id": session.session_id,
            "dispatch_files": len(session.dispatches),
            "main": totals_for(session.main_records),
            "totals": totals_for(session_records),
        })

    warnings = []
    for model in table.unknown_models:
        warnings.append("unknown model %s priced as %s" % (model, table.default_model))
    if any(table.is_uncertain(k) for k in table.models):
        warnings.append("price table %s (retrieved %s) contains entries marked "
                        "uncertain; dollars are a list-price estimate, not a bill"
                        % (table.version, table.retrieved))

    return {
        "scope": scope or [],
        "since": since.isoformat() if since else None,
        "flat": bool(flat),
        "prices": {"version": table.version, "retrieved": table.retrieved,
                   "normalization_base": table.base,
                   "default_model": table.default_model},
        "totals": round_totals(totals),
        "by_model": {k: round_totals(v) for k, v in sorted(by_model.items())},
        "by_requested_tier": {k: round_totals(v) for k, v in sorted(by_tier.items())},
        "sessions": session_rows,
        "dispatches": dispatch_rows,
        "compact_boundaries": boundaries,
        "duplicate_lines_dropped": duplicates,
        "warnings": warnings,
    }


def collect(args, table):
    """Resolve scope, read every session in it, return (sessions, scope names)."""
    root = projects_dir(args.projects_dir)
    since = parse_since(args.since)
    scope = resolve_scope(root, all_projects=args.all)
    sessions = []
    for project_dir in scope:
        sessions.extend(read_project(project_dir, table=table, since=since))
    # A resumed or forked session can copy history across projects too.
    dedupe_scans(session_scans(sessions))
    return sessions, [p.name for p in scope], since


# --------------------------------------------------------------------------
# CLI


def cmd_scan(args, table):
    sessions, scope, since = collect(args, table)
    data = {
        "projects_dir": str(projects_dir(args.projects_dir)),
        "scope": scope,
        "since": since.isoformat() if since else None,
        "sessions": [{
            "project": s.project,
            "session_id": s.session_id,
            "main_records": len(s.main_records),
            "dispatch_files": len(s.dispatches),
            "duplicates_dropped": (s.main_scan.duplicates if s.main_scan else 0)
                                  + sum(d.scan.duplicates for d in s.dispatches),
            "compact_boundaries": (s.main_scan.boundaries if s.main_scan else 0)
                                  + sum(d.scan.boundaries for d in s.dispatches),
        } for s in sessions],
    }
    if args.json:
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if not scope:
        print("no project directory in scope under %s" % data["projects_dir"])
        return 0
    print("projects: %s" % ", ".join(scope))
    for row in data["sessions"]:
        print("  %s  records=%d dispatches=%d dupes=%d boundaries=%d"
              % (row["session_id"], row["main_records"], row["dispatch_files"],
                 row["duplicates_dropped"], row["compact_boundaries"]))
    print("%d session(s)" % len(data["sessions"]))
    return 0


def cmd_summary(args, table):
    sessions, scope, since = collect(args, table)
    data = summarize(sessions, table, flat=args.flat, scope=scope, since=since)
    if args.json:
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    totals = data["totals"]
    print("scope: %s" % (", ".join(scope) or "(none)"))
    print("sessions: %d   dispatches: %d   boundaries: %d"
          % (len(data["sessions"]), len(data["dispatches"]),
             data["compact_boundaries"]))
    print("tokens: " + "  ".join("%s=%d" % (c, totals[c]) for c in TOKEN_CLASSES))
    print("opus-equivalent tokens: %d" % totals["opus_equivalent_tokens"])
    print("list-price estimate: $%.2f (not a bill)" % totals["cost_usd"])
    for warning in data["warnings"]:
        print("warning: %s" % warning, file=sys.stderr)
    return 0


COMMON_DEFAULTS = {"projects_dir": None, "prices": None, "default_model": None,
                   "all": False, "since": None, "flat": False, "json": False}


def _common_parser():
    """The shared flags, accepted both before and after the subcommand.

    Defaults are suppressed so a flag given before the subcommand is not
    overwritten by the subparser's own default; main() fills the gaps.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--projects-dir", default=argparse.SUPPRESS,
                        help="projects root to read (default: "
                             "$CLAUDE_CONFIG_DIR/projects, else ~/.claude/projects)")
    common.add_argument("--prices", default=argparse.SUPPRESS,
                        help="path to the price table JSON")
    common.add_argument("--default-model", default=argparse.SUPPRESS,
                        help="model to price unknown model ids as")
    common.add_argument("--all", action="store_true", default=argparse.SUPPRESS,
                        help="every project directory (default: the one matching cwd)")
    common.add_argument("--since", metavar="WHEN", default=argparse.SUPPRESS,
                        help="only records at or after an ISO date/timestamp, or Nd")
    common.add_argument("--flat", action="store_true", default=argparse.SUPPRESS,
                        help="keep nested dispatches separate (default: roll them "
                             "up into the top-level dispatch)")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="emit JSON")
    return common


def build_parser():
    common = _common_parser()
    parser = argparse.ArgumentParser(
        prog="usage_report.py", parents=[common],
        description="Account for Claude Code token spend per session, model and "
                    "sub-agent dispatch, from the local transcripts only.",
        epilog="Dollar figures are a local list-price estimate from "
               "scripts/prices.json, not a bill.")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("scan", parents=[common],
                   help="list the transcripts in scope and what was read")
    sub.add_parser("summary", parents=[common],
                   help="totals by model, tier and dispatch")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    for name, default in COMMON_DEFAULTS.items():
        if not hasattr(args, name):
            setattr(args, name, default)
    if not args.command:
        parser.print_help()
        return 1
    try:
        table = PriceTable.load(args.prices, default_model=args.default_model)
    except (OSError, ValueError) as exc:
        print("usage_report: cannot read price table: %s" % exc, file=sys.stderr)
        return 3
    try:
        if args.command == "scan":
            return cmd_scan(args, table)
        return cmd_summary(args, table)
    except ValueError as exc:
        print("usage_report: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
