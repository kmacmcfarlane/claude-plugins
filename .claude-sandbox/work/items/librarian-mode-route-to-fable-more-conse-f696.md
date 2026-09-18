---
id: librarian-mode-route-to-fable-more-conse-f696
title: "librarian-mode: route to fable more conservatively"
type: feature
status: doing
priority: 1
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T19:21Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer claude-sandbox librarian; claude-sandbox f3ab
---

Peer claude-sandbox librarian (its f3ab), relaying its operator, 2026-09-18: fable usage runs out fast; rule 3 sent a one-line CRLF fix to fable (then 429, done on opus). Narrow rule 3 (hard-to-reverse/harness, security, every fix round 2) so small or low-risk changes stay on opus. Settle together with the >2h fallback item. Lands after ed88.

## Handoff
- doing: in review/fix loop in worktree (see item body)
- next: review -> land
- blocked: —
- learned: —

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

## Librarian design (2026-09-18; operator delegated: "get as much as you can done yourself")
Bundle f696 + 7db3 + f518 in one worktree (all rewrite Route / § Rounds). Rule 3 narrowed:
- fable only for (a) hooks/code that gate or block edits, commits or tool calls, (b) security-relevant changes (credentials, permission allowlists, sandbox config, mounts/sockets/host access), (c) the operator names it — AND the change is non-trivial (more than a small, local edit: e.g. >~20 changed lines of executable logic, or more than one file). A one-line or mechanical fix in such code stays opus.
- the round signal: the last fix round before the cap (now fix round 3 under cap 4) goes to fable only when the previous review carried a critical or high finding; rounds fixing mediums/lows/wording stay at their tier.
- Fallback (7db3; decisions 28, 29): routed tier unavailable (429/usage) and reset >2h or unknown -> opus, recorded `dispatch: <role> opus — fable unavailable (resets in Xh|unknown); fallback`, named in verified:; reset <=2h -> ask the operator (wait vs opus). Reviewer floor stays opus. Where to learn the reset: the 429 text if it carries one; the status line rate_limits in the context-guard state record when present; else unknown.
- Cap (f518): 4 review rounds = first review + three fix rounds.
dispatch: implementer opus — doctrine (Route), >3 files

impl: DONE_WITH_CONCERNS ac8951f. Librarian accepts: (1) operator pin stays a floor that can reach fable regardless of size (rule 8 wins), and a pinned fable that is unavailable -> ask, never fall back; (2) dispatch line `(resets in <X>h)` / `(unknown)`; (3) reset source empty today -> filed context-guard follow-up; (4) threshold heuristic kept, reviewer may tighten.
dispatch: reviewer opus — rule 4

review round 1 (opus): NEEDS_CHANGES — medium 1 (">1 file" makes a one-line hook fix + its test non-trivial), 2 (<=2h/pinned ask bypasses decision N protocol; parallel 429s); lows 3 (SKILL rule 6 lacks pin exception), 4 (troubleshooting ignores pin), 5 (cites this repo's decision numbers in a shared skill), 6 (mid-run 429 leaves partial work in the worktree); nits 7, 8.
dispatch: implementer opus fix round 1 — resume

fix round 1 (opus): DONE 5a4aa76 (all 8; declined F2 optional SKILL.md clause — rule 6 names the ask, topic mix).
dispatch: reviewer opus review round 2 — resume
