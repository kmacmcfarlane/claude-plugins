#!/usr/bin/env python3
"""item_spend — one work item's list-price spend, per phase, by agent id.

The cost-budget reader (plan series f65b, serials 00-06). It takes a work-item
file, joins every agent id on its `agent:` lines to the agents' local
transcripts, and sums list-price dollars per phase. Run it as
`usage_report.py item <item file>` (or `item_spend.py <item file>`); it reads,
never writes.

The rules, each from the series:

- **Ids.** Every agent id on any `agent:` line counts, whatever the line's
  shape: role first (`agent: reviewer <id> round 2`), id first
  (`agent: <id> (plan reviewer r2)`), no role (`agent: <id> round 5
  (resumed)`), or several ids on one line. An id is `a` + 16 hex, or a named
  agent's `a<words>-<16 hex>`. The role is read from the line's text (its first
  word when that is a role); a line with none takes an earlier line's role for
  the same id, else the agent meta's `description`, else `unknown`.
- **Segments.** Each id's transcript is split at its user-text turns (the
  brief, then each coordinator message). Every segment counts: an id with more
  segments than `agent:` lines is flagged `unrecorded` and its spend is still
  summed; one with fewer is flagged `lost`.
- **Nested agents** (an agent's own sub-agents, by `parentAgentId` in their
  meta, recursively) are segments of their own, placed by their own start
  times. They count as spend and are never review boundaries.
- **Phases split by time.** `budget: <UTC> <plan|build> $<total> — <source>`
  opens a phase at the first such line's time; a segment belongs to the phase
  whose first `budget:` time is the latest at or before the segment's start.
  The amount in force is the phase's last `budget:` line (a total, never a
  delta). A segment that starts before every `budget:` line is its own phase,
  `unbudgeted`, flagged, never dropped. With no timestamped `budget:` line (an
  old record) the phases are inferred as the evidence script did: with a
  planner and an implementer, segments before the first implementer segment
  are `plan` and the rest `build`; otherwise one phase, `plan` when a planner
  ran or the type is `spike`, else `build`. That is flagged too.
- **Records.** Deduped per API response by (`message.id`, `requestId`), the
  line with the most output tokens kept. Zero-token records (`<synthetic>`)
  are skipped. Claude models only: a record whose model has no `claude` in it
  is left out of the dollars and reported. A Claude model with tokens that the
  price table does not know makes its phase **unread** — it is never priced as
  another model.
- **Transcript cleanup.** An id with no transcript makes its phase unread,
  unless a `cost: <UTC> <phase> $<spent> of $<budget> …` line of that phase
  follows the id's last `agent:` line: then the phase reads as that phase's
  last `cost:` line's spent plus every segment that starts after that line's
  time (serial 03 § 2), flagged `lost transcript`.
- **Reviews.** A review round is a reviewer segment that follows producer work
  (an implementer or planner segment), or the first review; reviewer segments
  with no producer work between them are one round. The cumulative spend after
  each review is every segment of the phase that started at or before that
  review ended.
- **The week.** Dollars are shown with their share of the weekly window at
  this window's local rate: every Claude record under the projects root since
  the window opened (its `resets_at` less seven days), priced and deduped the
  same way, divided by the weekly `used_percentage`. The reading comes from
  `--week-used`/`--week-resets-at`, else the newest status-line sensor record
  (`<config>/statusline/sensor/*.json`, written by statusline-hub; soft — with
  none, dollars are shown alone). Below 10% used the rate is too coarse and is
  not read. `--per-percent` gives the rate outright. The rate is measured, not
  a constant: the series saw $21-22 per 1% in two windows on one machine.

Known limits: a coordinator message sent mid-round splits that round (an extra
segment; totals unaffected); the orchestrator's own turns and sessions an agent
starts itself are not seen.
"""
import glob
import json
import os
import re
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage_report as ur  # noqa: E402

ID_RE = re.compile(r"(?<![\w-])a(?:[a-z0-9]+(?:-[a-z0-9]+)*-)?[0-9a-f]{16}(?![\w-])")
AGENT_RE = re.compile(r"^\s*agent:\s*(.*)$")
BUDGET_RE = re.compile(r"^\s*budget:\s*(\S+)\s+(plan|build)\s+\$([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$")
COST_RE = re.compile(r"^\s*cost:\s*(\S+)\s+(plan|build)\s+"
                     r"(?:\$([0-9][0-9,]*(?:\.[0-9]+)?)\s+of\s+\$([0-9][0-9,]*(?:\.[0-9]+)?)|(unread))(.*)$")
RIDER_RE = re.compile(r"^\s*(budget|cost):")
TYPE_RE = re.compile(r"^type:\s*(.*)$", re.M)
# Substring -> role, first match wins (the evidence script's order).
ROLES = (("fable second opinion", "cross-check"), ("cross-check", "cross-check"),
         ("(fable)", "cross-check"), ("plan reviewer", "reviewer"),
         ("reviewer", "reviewer"), ("planner", "planner"),
         ("implementer", "implementer"), ("research-lane", "research"),
         ("research-verifier", "research"), ("render", "helper"),
         ("brief writer", "helper"), ("scribe", "helper"), ("scout", "helper"))
LEADING_ROLES = {"reviewer": "reviewer", "reviewer-light": "reviewer",
                 "planner": "planner", "planner-deep": "planner",
                 "implementer": "implementer", "implementer-critical": "implementer",
                 "implementer-deep": "implementer", "cross-checker": "cross-check",
                 "cross-checker-deep": "cross-check", "scout": "helper",
                 "scribe": "helper", "research-lane": "research",
                 "research-verifier": "research"}
PRODUCERS = ("implementer", "planner")
PHASES = ("plan", "build")
UNBUDGETED = "unbudgeted"
MIN_WEEK_PERCENT = 10
WEEK = timedelta(days=7)


def _money(text):
    return float(text.replace(",", ""))


def role_of(text):
    """The role a line's text names, or None."""
    words = text.strip().lower().split()
    if words and words[0] in LEADING_ROLES:
        return LEADING_ROLES[words[0]]
    lowered = text.lower()
    for needle, role in ROLES:
        if needle in lowered:
            return role
    return None


# --------------------------------------------------------------------------
# the item record


class ItemRecord:
    """The lines of one item file the reader uses, in file order."""

    def __init__(self, text, name=None):
        self.name = name
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        match = TYPE_RE.search(head)
        self.type = match.group(1).strip().strip('"') if match else ""
        self.agent_lines = []   # (line number, ids, role or None)
        self.budgets = []       # dict(line, at, phase, amount, source)
        self.costs = []         # dict(line, at, phase, spent or None, budget)
        self.ignored = []       # (line number, why)
        for number, line in enumerate(text.splitlines(), 1):
            agent = AGENT_RE.match(line)
            if agent:
                ids = ID_RE.findall(agent.group(1))
                if ids:
                    self.agent_lines.append((number, ids, role_of(agent.group(1))))
                continue
            budget = BUDGET_RE.match(line)
            if budget:
                at = ur.parse_timestamp(budget.group(1))
                if at is None:
                    self.ignored.append((number, "budget: line without a UTC time"))
                    continue
                self.budgets.append(dict(line=number, at=at, phase=budget.group(2),
                                         amount=_money(budget.group(3)),
                                         source=budget.group(4).strip(" —-")))
                continue
            cost = COST_RE.match(line)
            if cost:
                at = ur.parse_timestamp(cost.group(1))
                if at is None:
                    self.ignored.append((number, "cost: line without a UTC time"))
                    continue
                self.costs.append(dict(
                    line=number, at=at, phase=cost.group(2),
                    spent=None if cost.group(5) else _money(cost.group(3)),
                    budget=None if cost.group(5) else _money(cost.group(4))))
                continue
            rider = RIDER_RE.match(line)
            if rider:
                self.ignored.append((number, "%s: line not in the timestamped shape "
                                     "(%s: <UTC> <plan|build> ...)" % (rider.group(1),
                                                                       rider.group(1))))

    @classmethod
    def load(cls, path):
        path = Path(path)
        return cls(path.read_text(encoding="utf-8", errors="replace"), name=path.stem)

    def ids_in_order(self):
        """(order of first appearance, line count per id, role per id)."""
        order, count, role = [], {}, {}
        for _, ids, line_role in self.agent_lines:
            for aid in ids:
                if aid not in count:
                    order.append(aid)
                    count[aid] = 0
                    role[aid] = line_role
                elif line_role and not role[aid]:
                    role[aid] = line_role
                count[aid] += 1
        return order, count, role

    def lines_of(self, aid):
        return [n for n, ids, _ in self.agent_lines if aid in ids]

    def phase_at_line(self, number):
        """The phase of the last budget: line above `number`, or None."""
        phase = None
        for budget in self.budgets:
            if budget["line"] < number:
                phase = budget["phase"]
        return phase


# --------------------------------------------------------------------------
# transcripts


class TranscriptIndex:
    """Every sub-agent transcript under a projects root, with its meta."""

    def __init__(self, root):
        self.root = Path(root)
        self.files, self.meta, self.children = {}, {}, {}
        pattern = str(self.root / "*" / "*" / "subagents" / "agent-*.jsonl")
        for path in sorted(glob.glob(pattern)):
            aid = os.path.basename(path)[len("agent-"):-len(".jsonl")]
            self.files.setdefault(aid, Path(path))
            meta = {}
            try:
                with open(path[:-len(".jsonl")] + ".meta.json", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    meta = loaded
            except (OSError, ValueError):
                pass
            self.meta.setdefault(aid, meta)
        for aid, meta in self.meta.items():
            parent = meta.get("parentAgentId") or meta.get("parent_agent_id")
            if parent and parent != aid:
                self.children.setdefault(parent, []).append(aid)
        self._reads = {}

    def read(self, aid, table):
        """The AgentRead for an id, or None when it has no transcript."""
        if aid not in self._reads:
            path = self.files.get(aid)
            self._reads[aid] = read_agent(path, table) if path else None
        return self._reads[aid]

    def descendants(self, aid):
        out, seen, stack = [], {aid}, list(self.children.get(aid, []))
        while stack:
            child = stack.pop(0)
            if child in seen:
                continue
            seen.add(child)
            out.append(child)
            stack.extend(self.children.get(child, []))
        return out


class Segment:
    __slots__ = ("id", "role", "start", "end", "usd", "tokens", "models", "unknown",
                 "phase")

    def __init__(self, start):
        self.id = None
        self.role = None
        self.start = start
        self.end = start
        self.usd = 0.0
        self.tokens = 0
        self.models = {}
        self.unknown = {}
        self.phase = None


class AgentRead:
    def __init__(self, segments, non_claude, synthetic):
        self.segments = segments
        self.non_claude = non_claude
        self.synthetic = synthetic


def is_claude(model):
    return bool(model) and "claude" in model.lower()


def price_tokens(prices, tokens, write_5m, write_1h):
    return (tokens["input"] * prices["input"] + tokens["output"] * prices["output"]
            + write_5m * prices["cache_write_5m"] + write_1h * prices["cache_write_1h"]
            + tokens["cache_read"] * prices["cache_read"]) / 1_000_000.0


def _is_text_turn(obj):
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    return (isinstance(content, list) and bool(content) and isinstance(content[0], dict)
            and content[0].get("type") == "text")


def iter_records(path):
    """Stream one transcript: ('turn', timestamp) for each user-text turn and
    ('usage', timestamp, model, key, tokens, write_5m, write_1h) per usage line."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue
            kind = obj.get("type")
            if kind == "user":
                if _is_text_turn(obj):
                    yield ("turn", ur.parse_timestamp(obj.get("timestamp")))
                continue
            if kind != "assistant":
                continue
            message = obj.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            if not isinstance(usage, dict):
                continue
            tokens, write_5m, write_1h = ur.usage_tokens(usage)
            yield ("usage", ur.parse_timestamp(obj.get("timestamp")), message.get("model"),
                   ur.dedupe_key(message, obj), tokens, write_5m, write_1h)


def read_agent(path, table):
    """Split one agent transcript into priced segments."""
    bounds, kept, keyless = [], {}, []
    for event in iter_records(path):
        if event[0] == "turn":
            bounds.append(event[1])
            continue
        _, at, model, key, tokens, write_5m, write_1h = event
        record = (at, model, tokens, write_5m, write_1h)
        if key is None:
            keyless.append(record)
        elif key not in kept or tokens["output"] > kept[key][2]["output"]:
            kept[key] = record
    records = list(kept.values()) + keyless
    segments = [Segment(b) for b in bounds] or [Segment(None)]
    non_claude, synthetic = {}, 0
    for at, model, tokens, write_5m, write_1h in records:
        total = sum(tokens.values())
        if not total:
            synthetic += 1
            continue
        index = 0
        for j, bound in enumerate(bounds):
            if bound is not None and at is not None and at >= bound:
                index = j
        segment = segments[index]
        key = table.canonical(model)
        if key is None and not is_claude(model) and model not in (None, "<synthetic>"):
            non_claude[model] = non_claude.get(model, 0) + total
            continue
        if key is None:
            name = model or ur.NO_MODEL
            segment.unknown[name] = segment.unknown.get(name, 0) + total
        else:
            usd = price_tokens(table.models[key], tokens, write_5m, write_1h)
            segment.usd += usd
            segment.models[key] = segment.models.get(key, 0.0) + usd
        segment.tokens += total
        if at is not None and (segment.end is None or at > segment.end):
            segment.end = at
    if segments[0].start is None:
        stamps = [r[0] for r in records if r[0] is not None]
        segments[0].start = min(stamps) if stamps else None
        if segments[0].end is None:
            segments[0].end = segments[0].start
    return AgentRead(segments, non_claude, synthetic)


# --------------------------------------------------------------------------
# the reading


def _key(at):
    return (at is None, at)


def infer_phases(segments, item_type):
    has_plan = any(s.role == "planner" for s in segments)
    impl = [s.start for s in segments if s.role == "implementer" and s.start is not None]
    impl_start = min(impl) if impl else None
    for s in segments:
        if has_plan and impl_start is not None:
            s.phase = "plan" if (s.start is not None and s.start < impl_start) else "build"
        else:
            s.phase = "plan" if (has_plan or item_type == "spike") else "build"


def timed_phases(segments, budgets):
    starts = {}
    for budget in budgets:
        if budget["phase"] not in starts or budget["at"] < starts[budget["phase"]]:
            starts[budget["phase"]] = budget["at"]
    opened = sorted(starts.items(), key=lambda kv: kv[1])
    for s in segments:
        s.phase = UNBUDGETED
        for phase, at in opened:
            if s.start is not None and s.start >= at:
                s.phase = phase


def review_series(segments):
    """Cumulative spend after each review round, in time order."""
    reviews, fresh = [], True
    for s in segments:
        if s.role in PRODUCERS:
            fresh = True
        elif s.role == "reviewer":
            if fresh or not reviews:
                reviews.append([s.start, s.end])
                fresh = False
            elif s.end is not None and (reviews[-1][1] is None or s.end > reviews[-1][1]):
                reviews[-1][1] = s.end
    out = []
    for _, end in reviews:
        out.append(round(sum(y.usd for y in segments
                             if y.start is not None and end is not None and y.start <= end), 2))
    return out


def read_item(item, index, table):
    """The whole reading of one item as plain data (the `--json` shape)."""
    order, line_count, line_role = item.ids_in_order()
    flags = []
    segments, missing, non_claude, synthetic = [], [], {}, 0
    placed = set(order)
    for aid in order:
        role = line_role[aid] or role_of(index.meta.get(aid, {}).get("description") or "") \
            or "unknown"
        read = index.read(aid, table)
        if read is None:
            missing.append(aid)
            continue
        if len(read.segments) > line_count[aid]:
            flags.append(dict(flag="unrecorded", id=aid,
                              count=len(read.segments) - line_count[aid],
                              note="rounds with no agent: line of their own (counted)"))
        elif len(read.segments) < line_count[aid]:
            flags.append(dict(flag="lost", id=aid,
                              count=line_count[aid] - len(read.segments),
                              note="agent: lines with no transcript segment of their own"))
        members = [(aid, role, read)]
        for child in index.descendants(aid):
            if child in placed:
                continue
            placed.add(child)
            child_read = index.read(child, table)
            if child_read is not None:
                members.append((child, "nested", child_read))
        for member, member_role, member_read in members:
            for model, count in member_read.non_claude.items():
                non_claude[model] = non_claude.get(model, 0) + count
            synthetic += member_read.synthetic
            for segment in member_read.segments:
                segment.id, segment.role = member, member_role
                segments.append(segment)
    segments.sort(key=lambda s: _key(s.start))

    if item.budgets:
        timed_phases(segments, item.budgets)
        phase_source = "budget"
        if any(s.phase == UNBUDGETED and s.usd for s in segments):
            flags.append(dict(flag="unbudgeted",
                              note="segments that started before the first budget: line "
                                   "(counted in their own phase)"))
    else:
        infer_phases(segments, item.type)
        phase_source = "inferred"
        flags.append(dict(flag="phases inferred",
                          note="no timestamped budget: line; phases split at the first "
                               "implementer segment"))
    for number, why in item.ignored:
        flags.append(dict(flag="ignored line", line=number, note=why))
    if non_claude:
        flags.append(dict(flag="non-Claude", models=non_claude,
                          note="tokens left out of the dollars"))

    names = [p for p in (UNBUDGETED,) + PHASES if any(s.phase == p for s in segments)]
    for budget in item.budgets:
        if budget["phase"] not in names:
            names.append(budget["phase"])
    phases, raw = {}, {}
    for name in names:
        mine = [s for s in segments if s.phase == name]
        unknown = {}
        for s in mine:
            for model, count in s.unknown.items():
                unknown[model] = unknown.get(model, 0) + count
        models = {}
        for s in mine:
            for model, usd in s.models.items():
                models[model] = models.get(model, 0.0) + usd
        budgets = [b for b in item.budgets if b["phase"] == name]
        phase = dict(usd=round(sum(s.usd for s in mine), 2),
                     budget=budgets[-1]["amount"] if budgets else None,
                     budget_source=budgets[-1]["source"] if budgets else None,
                     opened=budgets[0]["at"].isoformat() if budgets else None,
                     segments=len(mine),
                     cumulative_after_review=review_series(mine),
                     models={k: round(v, 4) for k, v in sorted(models.items())},
                     reading="read", unread=[], lost_transcripts=[])
        if unknown:
            phase["reading"] = "unread"
            phase["unread"].append("unknown model with tokens: %s (never priced as "
                                   "another model)" % ", ".join(
                                       "%s %d" % kv for kv in sorted(unknown.items())))
        phases[name] = phase
        raw[name] = sum(s.usd for s in mine)

    # Lost transcripts: covered by a later cost: line of the same phase, or unread.
    for aid in missing:
        lines = item.lines_of(aid)
        phase_name = item.phase_at_line(lines[0]) if item.budgets else None
        costs = [c for c in item.costs if c["phase"] == phase_name]
        last = costs[-1] if costs else None
        if phase_name is None:
            phase_name = "build" if "build" in phases else (names[0] if names else "build")
        phase = phases.setdefault(phase_name, dict(
            usd=0.0, budget=None, budget_source=None, opened=None, segments=0,
            cumulative_after_review=[], models={}, reading="read", unread=[],
            lost_transcripts=[]))
        if last is not None and last["spent"] is not None and last["line"] > lines[-1]:
            phase["lost_transcripts"].append(aid)
            phase["covered_by_cost"] = dict(at=last["at"].isoformat(), spent=last["spent"])
        else:
            phase["reading"] = "unread"
            phase["unread"].append("no transcript for %s, and no cost: line of this phase "
                                   "after its agent: line" % aid)
    for name, phase in phases.items():
        cover = phase.get("covered_by_cost")
        if cover and phase["reading"] == "read":
            at = ur.parse_timestamp(cover["at"])
            after = sum(s.usd for s in segments
                        if s.phase == name and s.start is not None and s.start > at)
            raw[name] = cover["spent"] + after
            phase["usd"] = round(raw[name], 2)
            flags.append(dict(flag="lost transcript", ids=phase["lost_transcripts"],
                              phase=name, note="read through the cost: line at %s"
                              % cover["at"]))

    unread = any(p["reading"] == "unread" for p in phases.values())
    return dict(
        item=item.name, type=item.type or None,
        prices=dict(version=table.version, retrieved=table.retrieved),
        phase_source=phase_source,
        ids=len(order), ids_joined=len(order) - len(missing), missing=missing,
        reading="unread" if unread else "read",
        usd=None if unread else round(sum(raw.get(n, 0.0) for n in phases), 2),
        phases=phases, flags=flags, synthetic_skipped=synthetic,
        segments=[dict(id=s.id, role=s.role, phase=s.phase,
                       start=s.start.isoformat() if s.start else None,
                       usd=round(s.usd, 4)) for s in segments])


# --------------------------------------------------------------------------
# the week


def sensor_week(config):
    """(used %, resets_at datetime) from the newest status-line sensor record, or None."""
    best = None
    for path in glob.glob(str(Path(config) / "statusline" / "sensor" / "*.json")):
        try:
            with open(path, encoding="utf-8") as handle:
                record = json.load(handle)
            limits = record.get("rate_limits") or {}
            week = limits.get("seven_day") or {}
            used, resets = float(week["used_percentage"]), float(week["resets_at"])
            at = float(limits.get("at") or os.path.getmtime(path))
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            continue
        if best is None or at > best[0]:
            best = (at, used, resets)
    if best is None:
        return None
    return best[1], ur.datetime.fromtimestamp(best[2], ur.timezone.utc)


def week_spend(root, start, table):
    """Claude list-price spend of every record under `root` at or after `start`."""
    best = {}
    keyless = 0.0
    floor = start.timestamp()
    for path in glob.glob(str(Path(root) / "**" / "*.jsonl"), recursive=True):
        try:
            if os.path.getmtime(path) < floor:
                continue
        except OSError:
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if '"usage"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                message = obj.get("message") if isinstance(obj, dict) else None
                usage = message.get("usage") if isinstance(message, dict) else None
                if not isinstance(usage, dict):
                    continue
                at = ur.parse_timestamp(obj.get("timestamp"))
                if at is None or at < start:
                    continue
                key = table.canonical(message.get("model"))
                if key is None:
                    continue
                tokens, write_5m, write_1h = ur.usage_tokens(usage)
                usd = price_tokens(table.models[key], tokens, write_5m, write_1h)
                ident = ur.dedupe_key(message, obj)
                if ident is None:
                    keyless += usd
                elif ident not in best or tokens["output"] > best[ident][0]:
                    best[ident] = (tokens["output"], usd)
    return keyless + sum(v[1] for v in best.values())


def week_rate(args, table, root):
    """dict(per_percent, basis) or dict(per_percent=None, why)."""
    if args.per_percent:
        return dict(per_percent=float(args.per_percent), basis="given (--per-percent)")
    if args.no_week:
        return dict(per_percent=None, why="not asked (--no-week)")
    if args.week_used is not None and args.week_resets_at:
        used = float(args.week_used)
        resets = ur.parse_timestamp(args.week_resets_at)
        if resets is None:
            try:
                resets = ur.datetime.fromtimestamp(float(args.week_resets_at), ur.timezone.utc)
            except ValueError:
                return dict(per_percent=None, why="--week-resets-at not understood")
        source = "given"
    else:
        reading = sensor_week(ur.config_dir())
        if reading is None:
            return dict(per_percent=None, why="no weekly reading (no status-line sensor "
                                              "record; pass --week-used and --week-resets-at)")
        used, resets = reading
        source = "sensor record"
    if used < MIN_WEEK_PERCENT:
        return dict(per_percent=None, why="only %g%% of the week used; under %d%% the rate "
                                          "is too coarse to read" % (used, MIN_WEEK_PERCENT))
    start = resets - WEEK
    spend = week_spend(root, start, table)
    return dict(per_percent=spend / used, basis="local Claude spend $%.2f since %s over %g%% "
                                                "used (%s)" % (spend, start.isoformat(), used,
                                                               source))


# --------------------------------------------------------------------------
# CLI


def _share(usd, rate):
    if usd is None or not rate:
        return ""
    return " (≈%.2f%% of a week)" % (usd / rate)


def render(data, week):
    rate = week.get("per_percent")
    lines = ["item: %s (type %s)" % (data["item"], data["type"] or "none"),
             "prices: v%s, retrieved %s (list-price estimate, not a bill)"
             % (data["prices"]["version"], data["prices"]["retrieved"]),
             "ids: %d on agent: lines, %d with a transcript" % (data["ids"], data["ids_joined"])]
    for name, phase in data["phases"].items():
        if phase["reading"] == "unread":
            lines.append("%-10s unread — %s" % (name, "; ".join(phase["unread"])))
            continue
        budget = (" of $%.2f (%s)" % (phase["budget"], phase["budget_source"] or "budget:")
                  if phase["budget"] is not None else "")
        series = ", ".join("%.2f" % v for v in phase["cumulative_after_review"])
        lines.append("%-10s $%.2f%s%s; %d review(s)%s" % (
            name, phase["usd"], budget, _share(phase["usd"], rate),
            len(phase["cumulative_after_review"]),
            (", cumulative after each: " + series) if series else ""))
    if data["reading"] == "unread":
        lines.append("%-10s unread (a phase has no reading)" % "total")
    else:
        lines.append("%-10s $%.2f%s" % ("total", data["usd"], _share(data["usd"], rate)))
    if rate:
        lines.append("week: $%.2f per 1%% — %s" % (rate, week["basis"]))
    else:
        lines.append("week: no share shown — %s" % week["why"])
    for flag in data["flags"]:
        detail = flag.get("id") or ", ".join(flag.get("ids") or []) or ""
        if flag.get("count"):
            detail += " %d" % flag["count"]
        if flag.get("models"):
            detail += " " + ", ".join("%s %d tokens" % kv for kv in flag["models"].items())
        if flag.get("line"):
            detail += " line %d" % flag["line"]
        lines.append("flag: %s%s — %s" % (flag["flag"], (" " + detail.strip()) if detail.strip()
                                          else "", flag["note"]))
    return "\n".join(lines)


def add_arguments(parser):
    parser.add_argument("item_file", help="the work-item file whose agent: lines to read")
    parser.add_argument("--per-percent", type=float, default=None, metavar="DOLLARS",
                        help="list-price dollars per 1%% of the week (skips the measurement)")
    parser.add_argument("--week-used", type=float, default=None, metavar="PERCENT",
                        help="the weekly window's used_percentage")
    parser.add_argument("--week-resets-at", default=None, metavar="WHEN",
                        help="the weekly window's resets_at (ISO time or epoch seconds)")
    parser.add_argument("--no-week", action="store_true",
                        help="show dollars alone; do not measure the week's rate")


def run(args, table):
    path = Path(args.item_file)
    if not path.is_file():
        print("usage_report: no item file %s" % path, file=sys.stderr)
        return 1
    root = ur.projects_dir(getattr(args, "projects_dir", None))
    item = ItemRecord.load(path)
    data = read_item(item, TranscriptIndex(root), table)
    week = week_rate(args, table, root)
    data["week"] = week
    for name, phase in data["phases"].items():
        phase["share_of_week_percent"] = (round(phase["usd"] / week["per_percent"], 3)
                                          if week.get("per_percent") and
                                          phase["reading"] == "read" else None)
    data["share_of_week_percent"] = (round(data["usd"] / week["per_percent"], 3)
                                     if week.get("per_percent") and data["usd"] is not None
                                     else None)
    if getattr(args, "json", False):
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(render(data, week))
    return 0


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog="item_spend.py", description="One work item's list-price spend per phase, "
                                          "by the agent ids on its agent: lines.")
    add_arguments(parser)
    parser.add_argument("--projects-dir", default=None)
    parser.add_argument("--prices", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        table = ur.PriceTable.load(args.prices)
    except (OSError, ValueError) as exc:
        print("usage_report: cannot read price table: %s" % exc, file=sys.stderr)
        return 3
    return run(args, table)


if __name__ == "__main__":
    sys.exit(main())
