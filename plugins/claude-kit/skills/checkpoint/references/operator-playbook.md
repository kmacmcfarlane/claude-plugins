# Operator playbook — staying in the context power band

Measured from a real 1M-token session that filled its window twice (`design-rationale.md`
has the full numbers). The short version: **the window was not filled by tool output. It was
filled by the assistant's own output, most of it hidden reasoning, plus harness overhead the
operator never sees.** Fixing that is mostly about session *shape*, not about reading fewer files.

## The numbers that matter

| Fact | Value | Consequence |
| --- | --- | --- |
| Cost of a turn, averaged | ~7K tokens | 1M ≈ 130 turns; 200K ≈ 25 turns |
| What a compaction keeps | 14–18K of ~1M (1.4–1.8%) | everything not on disk is gone |
| Compaction wall time | 140–150 s | plus a full prompt-cache rebuild after |
| Base cost after compaction | 75–107K | summary + CLAUDE.md + hooks + tool/skill listings |
| One SessionStart hook (context-mode) | ~15K tokens per start/resume/compact | 7.5% of a 200K window before you type |
| Subagent results, 24 calls | 2.7% of tool bytes | cheapest way to read a lot |
| A model switch mid-session | full cache rebuild, ±65K counted | avoid mid-thread |
| Hidden thinking persisted to disk | 1.8K chars of 559 blocks (≈0) | only the live session can write it down |
| Harness attachments per fill (hooks, diffs, listings) | ~105K tokens | as much as all tool output; audit with `context_forensics.py` |

**The gate thinks in remaining tokens, not percent.** Advisories at 60/75% used; **DUE** when
~150K tokens remain (1M window; 70K on 200K) — finish things, run `/checkpoint`; **HARD** at
60K/40K left — the gate blocks every prompt except `/checkpoint`, `/compact`, `/clear` until a
checkpoint records. All of it resets per epoch (each compaction or `/clear`).

## Tools, and when

| Tool | Use it when | What it costs / keeps |
| --- | --- | --- |
| `/clear` | the task is done and its state is on disk | everything; cheapest reset there is |
| `/rename <name>` | at the start of any thread you may resume | nothing; makes `--resume` findable |
| `/compact <guidance>` | the thread is open-ended and must continue *here* | keeps ~2%; guidance is a documented input, use it |
| `/rewind` → *Summarize up to here* | old turns are noise, recent ones are load-bearing | condenses only the old part; recent turns verbatim |
| `/btw <question>` | a side question that needn't enter history | answers from context; never stored |
| `/subtask` (fork) | a side task that needs everything this session knows | inherits history + cache; tool calls stay out |
| `/fork` | a competing plan from this exact point | whole session copied to a background session |
| "use a subagent to …" | read-heavy research, log digging, doc reading | returns 1–2K tokens; the reads never enter your window |
| `Explore` / `Plan` agents | codebase survey before implementation | skip CLAUDE.md, cheap, read-only |
| `/context` | any time you want the truth | free |
| status line | always | shows `used_percentage`; also feeds the gate hooks |

Environment & knobs: `/autocompact 900k` lowers the auto-compact trigger so the gate's deferral
is provably safe (`CLAUDE_CODE_AUTO_COMPACT_WINDOW=900000` per project — plain integer, `900k`
reads as 900); `CLAUDE_KIT_LEDGER_EVERY` tunes the ledger nudge (default 60000);
`CLAUDE_CODE_TASK_LIST_ID=<name>` shares a task list across sessions.

## Session shapes that stay in the band

1. **One workstream per session.** Investigate in one session, write the plan to disk,
   implement in a fresh one. The docs say the same: *write a spec, then start a fresh session
   to execute it.* A session that spans two repos will accumulate two repos' worth of context.
2. **Rename at the start, clear at the end.** Named sessions are branches; `--resume` is
   checkout.
3. **Delegate reads, keep writes.** Anything that would return more than a screen goes to a
   subagent; the main session stays single-threaded on writes (this is also what the
   multi-agent literature converged on).
4. **Write as you go.** Investigation serials, `INDEX.md`, commit messages with the reasoning.
   The compaction survivors in the measured session were exactly the things already on disk.
5. **Don't switch models mid-thread.** Do it at a boundary.
6. **Trim fixed overhead.** Every start pays for CLAUDE.md, rules, skill descriptions, MCP tool
   lists, and SessionStart hook output. Look at `/context` once and cut what you don't read.
7. **Large files: index, don't read.** A 49KB `TODO.md` costs ~12K tokens per read; a skill
   that reads it every time pays that on every invocation. Keep an index at the top and grep
   the rest.

## The three questions at the gate

When the depth warning fires, answer these before touching anything:

1. **What is the goal from here** — land one thing, continue, or hand off? Only you know.
2. **What did we decide, reject, or correct that isn't written down yet?** That is the only
   content that cannot be recovered later.
3. **Which repo owns each of those?** Working in one repo on another repo's problem is fine;
   leaving the knowledge there is not.

Then `/checkpoint <mode>`. The ledger (`~/.claude/claude-kit/ledger/<session>.md`) has been
collecting decisions as you worked — the checkpoint is a delta, and after compaction the
manifest + ledger are re-injected and outrank the machine summary.
