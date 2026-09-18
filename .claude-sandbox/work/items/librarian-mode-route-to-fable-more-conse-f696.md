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
- doing: —
- next: —
- blocked: —
- learned: —

decision 28 answered (operator 2026-09-18): run fable-routed items on opus while fable is out, recorded as fallbacks, until 7db3/f696 land.
decision 29 answered: unknown reset time = treat as >2h -> opus.

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
