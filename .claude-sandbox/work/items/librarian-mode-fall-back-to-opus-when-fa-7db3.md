---
id: librarian-mode-fall-back-to-opus-when-fa-7db3
title: "librarian-mode: fall back to opus when fable is out for more than 2h"
type: feature
status: todo
priority: 1
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer claude-sandbox librarian; claude-sandbox d5ac
---

Peer claude-sandbox librarian (its d5ac), relaying its operator, 2026-09-18. A fix-round-2 fable implementer hit HTTP 429 'out of usage credits'; rule 6 (a tier never falls) left only asking. Rule: routed special tier unavailable and resets in >2h -> dispatch opus by default, record 'dispatch: <role> opus — fable unavailable (resets in Xh); fallback', note it in verified:; resets within 2h -> ask the operator (wait vs opus); reviewer floor stays opus. Open detail: how the librarian learns the reset time (the 429 text had none) — candidates: status line rate_limits in the context-guard state record, or unknown = >2h. Settle together with the conservative-fable item. Lands after ed88 (librarian-mode moves to dev-flow).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

decision 28 answered (operator 2026-09-18): run fable-routed items on opus while fable is out, recorded as fallbacks, until 7db3/f696 land.
decision 29 answered: unknown reset time = treat as >2h -> opus.
