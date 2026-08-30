# Design rationale — context guardrails

Why the gate, the checkpoint skill, and the playbook look the way they do. Written 2026-08-30
from a forensic pass over one real session plus a review of how others handle the same
problem. Numbers are from that session; the shape generalises.

## 1. What actually filled a 1M window, twice

Transcript: 7,187 records, 18.7MB, two compaction boundaries, 267 user turns.

| Segment | user turns | assistant msgs | assistant output generated | tool results | compacted at → kept |
| --- | --- | --- | --- | --- | --- |
| 0 | 133 | 588 | 1,348K tok | ~105K tok | 974,753 → 13,709 |
| 1 | 120 | 1,066 | 1,198K tok | ~120K tok | 1,001,840 → 18,027 |

**Finding 1 — tool output was not the main consumer.** Tool results were ~11% of each fill.
Within a tool loop, the previous assistant output (text *and* thinking) accrues into context
at a measured ratio of 1.03. The five visible categories — assistant text (~74K), tool-call inputs (~84K), tool
results (~105K), user-turn text (~80K), harness attachments (~105K) — sum to ~449K of a
971K peak. **The remaining ~54% can only be retained thinking** (plus system prompt and tool
definitions, ~25K).

**Finding 2 — hidden reasoning is retained live and persisted nowhere.** 559 thinking blocks
on disk, 1.8K characters of content between them — effectively none — and a 428-char
signature each. It is simultaneously the largest
consumer of the window and the only thing that is a *total* loss at compaction. Nothing that
reads files after the fact — a subagent, a hook, `--resume` — can see it. Only the live
session can write it down, and only before compaction.

**Finding 3 — harness overhead is invisible and large.** 965 `attachment` records that never
appear in the terminal: a SessionStart hook injecting 53–60KB on every start/resume/compact
(context-mode; ~15K tokens), a `PreToolUse` hook on every `Agent` call adding 21–29K tokens per
fill (context-mode again), file-change diffs re-injected in full (142KB over 18), skill
listings (20KB × 6), queued-command echoes (69KB). Attachments totalled ~105–111K tokens per fill — as much as all tool output. Post-compaction
base was 75–107K tokens, of which the summary itself was only 14–18K.

**Finding 4 — a compaction keeps ~1.5%.** `postTokens/preTokens` = 1.4% and 1.8%. It took
141 s and 153 s. The things that survived were the things already on disk: investigation
serials, INDEX files, commits. The near-loss was *routing* knowledge — which repo each finding
belonged to — because that is intent, not content, and no summarizer can reconstruct intent.

**Finding 5 — avoidable single costs.** `TODO.md` at 49KB read whole (~12K tokens) by the
investigate skill on every run; a context-mode batch returning 44KB in one call (the
context-saving tool, asked for too much at once); a Fable→Opus switch mid-session costing a
full cache rebuild and +65K counted tokens. A separate +176K step with no content behind it
was a full re-serialisation from a 26K prefix; cause not determinable from the transcript.

**Finding 6 — subagents were the cheapest tool by an order of magnitude.** 24 `Agent` calls
returned 26KB total (2.7% of tool bytes) for work that would have been hundreds of KB inline.

## 2. What the literature converged on

Anthropic's own guidance names three levers — compaction, structured note-taking, and
sub-agent architectures — and frames the whole discipline as *"the smallest, most relevant set
of tokens that maximizes the probability of success."* Claude Code's docs add the operator
side: the context window is *the* resource; `/clear` between tasks; write a spec then start a
fresh session; delegate research to subagents; `/compact <instructions>`; `/rewind` →
summarize part of the conversation; `/btw` for side questions; a status line to track usage
continuously; CLAUDE.md instructions can steer what compaction preserves.

Cognition's follow-up to *Don't Build Multi-Agents* is the best statement of the write-side
constraint: multi-agent setups work when **writes stay single-threaded and the extra agents
contribute intelligence, not actions**. Read-only subagents "mostly resemble tool calls". That
is exactly the cheap pattern in Finding 6, and it is why the checkpoint skill delegates
*reading and drafting* to a fork but keeps the write decisions in one place.

The *Context Window Lifecycle* paper (Semenov & Dorofeev, 2026) is the sharpest theory of what
to keep. It types trajectory into **exploratory** episodes (what was learned; keep the
description) and **action** episodes (edits whose effects are *already persisted in the
environment*; evict first), links actions to the exploration they depended on, protects user
turns and anything the agent is actively reasoning over, and evicts oldest-and-most-recoverable
rather than oldest-in-time. Its stated failure modes of summarisation — *unpredictable
lossiness, destruction of causal structure, blocking cost, compression-induced hallucination* —
are the four things observed here. The design lesson: **a checkpoint's job is to convert
exploratory context (reasoning) into persisted effects (files), so that all of it becomes
safely evictable.** Compaction is then lossless in the only sense that matters.

The community "handoff" pattern (a `HANDOFF.md` distinct from `CLAUDE.md`: *standing context*
vs *one piece of work in flight, dead once it lands*) is the same idea at session granularity.
Point the next session at the file by path; never paste the summary.

## 3. The protocol

Three layers, escalating; the first two are hooks, the third is a skill.

1. **Sensor + gauge** — the status line receives `context_window.used_percentage` and
   `context_window_size` (the only place Claude Code exposes exact depth) and writes them to
   `~/.claude/claude-kit/context-gate/<session>.json`. Hooks read that; they do not get the
   fields themselves. Falls back to transcript `usage` inference.
2. **Bands** (`UserPromptSubmit`, 60/75/88%, once each, latching) — to the operator via
   `systemMessage`, to the model via `additionalContext`. Only one can act; only the other can
   decide.
3. **Gate** (`PreCompact`, matcher `auto`) — blocks the *first* auto-compact only. Per the hooks
   reference, blocking a proactive compaction is free; blocking one that fired to recover from a
   context-limit error already returned makes the in-flight request fail, and the hook cannot
   tell the two apart. One decision point, no wedged session. Manual `/compact` is never
   touched.
4. **Checkpoint skill** — Step 0 asks the operator the goal (*land / continue / handoff*)
   because that is the one input nobody else holds and it changes everything downstream:
   *land* means compaction is the wrong tool; *continue* means residue then `/compact` with
   drafted guidance; *handoff* means a brief in the owning repo. Step 2 writes reasoning residue
   from the live session (Finding 2). Step 3 routes twice — task knowledge to its owning repo,
   harness friction to the plugin repo — because a session has two outputs, and the second is
   the one that improves the next session. Step 4 delegates the mechanical flush to a **fork**
   (inherits history + cache; a fresh subagent starts empty and is the wrong primitive here).

## 4. Context injection beyond CLAUDE.md

The operator's model — a repo directory as the logical entrypoint that pulls in context, other
repos holding the skills the harness injects — maps onto Claude Code's layers by *scope*:

| Scope | Mechanism | Loaded when |
| --- | --- | --- |
| repo | `CLAUDE.md` (+ `~/.claude/CLAUDE.md`) | every session, in full — keep it to facts you would otherwise re-explain |
| subtree | nested `CLAUDE.md` | when a file in that subdirectory is read |
| file pattern | `.claude/rules/*.md` with `paths:` frontmatter | when a matching file is read (not on create) |
| procedure | skill (`description` always; body on invoke); path-scoped skills | on invocation / when work touches the path |
| worker | subagent definition; `skills:` preload; own auto-memory | when delegated |
| operator | auto-memory (`MEMORY.md` index ≤200 lines/25KB; topic files on demand) | index at start, detail on demand |
| event | hooks emitting `additionalContext` (`SessionStart`, `UserPromptSubmit`, `PostToolUse`) | on the event, conditionally |
| **state** | *missing in most setups* | — |

The missing layer is **state**: *what is in flight in this repo right now*. It is exactly what
compaction loses and what a `HANDOFF`/`INDEX.md` holds. The cheap implementation is a
`SessionStart` hook that injects a bounded (~2KB) digest for the cwd — the newest investigation
`INDEX.md` head, the top of `TODO.md`, the last commit — so every session, resumed or fresh,
starts knowing where the work stands without reading 49KB to find out. That is a candidate
for `claude-kit`; it is not built yet.

Two disciplines make every layer cheaper: **progressive disclosure** (a pointer in the
always-loaded layer, the body one read away) and **indexes over bodies** (`MEMORY.md`, series
`INDEX.md`, a `TODO.md` with a summary block at the top). Both are already this framework's
convention; the forensics say to apply them to `TODO.md` and to the SessionStart hook output.

## 5. Open questions

1. Does the compaction summarizer see prior thinking blocks? Undetermined. Design assumes not;
   Finding 2 makes the assumption safe.
2. Statusline sensor + hooks are unit-tested; the gate has not yet fired against a real
   auto-compact. First real trigger is the test.
3. The +176K re-serialisation step (Finding 5) is unexplained. Re-run `context_forensics.py`
   on the next long session and see whether it recurs and what precedes it.
4. `.claude-sandbox/investigations/` is gitignored in this repo, which is why this rationale
   lives under `references/` — the owner should decide whether that ignore is intended.

## Sources

- Anthropic, *Effective context engineering for AI agents* (2025-09)
- Claude Code docs: best practices; hooks reference; context window; sub-agents; status line;
  memory; interactive mode
- Cognition, *Don't Build Multi-Agents* and *Multi-Agents: What's Actually Working*
- Semenov & Dorofeev, *Beyond Compaction: Structured Context Eviction for Long-Horizon Agents*,
  arXiv:2606.11213 (2026)
- Manus, *Context Engineering for AI Agents: Lessons from Building Manus*
- thepushkarp/handoff; anthropics/claude-code issues #42817, #38483, #16299
