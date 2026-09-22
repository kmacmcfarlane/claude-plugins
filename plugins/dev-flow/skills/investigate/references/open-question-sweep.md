# Open-question sweep

Loaded from `investigate` Step 11, after the plan is drafted and before anything is written
to disk. Step 11 carries the summary; this file is the full procedure.

## 1. Sweep your own draft

Look for hedged language ("likely", "presumably", "should be", "may need"), any claim with no
`file:line` or command behind it, a choice left implicit, a section written thinly because
you did not know, and anything already sitting in Open Questions. Each is a candidate.

One candidate is standing, not draft-dependent: ownership and contract facts about
neighbouring components recorded in an earlier round of this same investigation. Ownership can
move while the investigation runs; re-check any such fact against current HEAD and the README
catalog before the review gate, even if the draft states it with confidence.

## 2. Classify every candidate

| Class | Test | Handling |
|---|---|---|
| **Agent-verifiable** | The answer exists somewhere reachable — code, `git`, a config, a running system, docs | Batch into one background agent (§ 3) |
| **User decision** | An opinion, a scope call, a preference. "Should we also…", "is X in scope", "which behaviour" | Ask the user (§ 4) |
| **External / blocked** | Depends on someone else's decision, or a system you cannot reach | Straight to Open Questions, with owner and blocks-or-not |

A question that is both — verifiable in principle, but only matters given a decision — goes to
the user first. Do not verify a branch that may be discarded.

## 3. Launch ONE background agent for the verifiable batch — first

Launch it first, so it works while the user reads. One agent for the whole batch, not one per
question; the point is to keep high-volume tool output out of your context and return only
findings. Use a fresh `general-purpose` agent with a self-contained brief: the questions, the
repo paths and their SHAs, and what counts as verified (a command's output, a `file:line`, a
doc quote). Require it to report **answer / evidence / confidence** per question, and to say
"could not determine" rather than guess. Tell it to flag any *new* uncertainty it finds.

## 4. Meanwhile, ask the user the decision-class questions

Ask per the SKILL.md's **Asking at a gate**. Every one carries a defer option, offered as a
dialog option or, in a list, as a closing line: any item may be answered "leave open". Its
wording:

> **Leave open and record in the investigation** — defer this; it will be listed under Open
> Questions with its owner and whether it blocks implementation.

Deferring is one click or one word, never a negotiation. Some questions genuinely need data
nobody has yet, and forcing an answer produces a worse record than an honest Open Question.

## 5. Fold in and loop

Verified facts become findings **with their evidence**; decisions become **Confirmed
Assumptions**; deferred and external items become **Open Questions** with owner and
blocks-or-not. If either source produced a *new* question, run another round — verification
frequently reveals a second-order question. **Stop** when a round yields nothing new, or when
everything remaining is deferred or external.
