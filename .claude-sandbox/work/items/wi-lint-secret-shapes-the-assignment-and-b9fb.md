---
id: wi-lint-secret-shapes-the-assignment-and-b9fb
title: "wi lint: secret shapes the assignment and key/value rules still miss"
short_display_name: lint misses other secret shapes
type: bug
status: done
priority: 3
created: 2026-10-08
updated: 2026-10-09
closed: 2026-10-09
refs:
  - wi-lint-catch-key-value-secrets-after-a-d8a5 review 1
---

From the d8a5 review 1 notes, 2026-10-08: lowercase or mixed-case keys (db_pass=...), spaces around = (KEY = value), KEY: value, JSON "KEY":"value", and --flag=value pass both rules unless the key holds a key/value-rule word. Acceptance: decide per shape with real-store before/after; tests pin each.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
dispatch: implementer opus medium — build, worktree (bug)
- 2026-10-09 claimed by Kyle-McFarlane@2d49f8460283
agent: implementer a7035ad4054cec38e
return: DONE worktree-agent-a7035ad4054cec38e f526872 (third rule SECRET_SHAPE_RE for five looser shapes, value gated: 12+ chars, letter and digit, not hex, not date-led, not short-segment id/path; placeholders ignored; 13 caught, 25 clean, 4 refused tests; store scan 0 hits over 461 files after two false positives fixed; reported 10 Checks)
dispatch: reviewer opus high — review round 1 of f526872
agent: reviewer ae593bcd6eb1d1d1a
verdict: review round 1 NEEDS_CHANGES (high 1: quoted values missed in every new shape but JSON; medium 2: short-segment exemption misses ~17% of 22-char url-safe tokens and flags long path segments; medium 3: hex/letters/UUID exemptions ignore the key — a 40-hex value under a secret-word key passes; lows: symbol passwords, a dot before the key, => and := forms, test gaps; low 6 (camelCase, Bearer) for a follow-up)
dispatch: implementer opus medium — fix round 1 (resume a7035ad4054cec38e)
return: DONE fd24d2d (quoted values; reworked segment rule; key-aware gate, 8+ non-space under a secret-word key; dotted keys, => and :=; tests incl. base64, JWT-like, quoted, long paths; store 0 hits over 462 files; plugins/ code hits 633, mostly key=func() and fixtures, outside lint's reach; miss rate under secret keys 0%, plain-key 16-byte url-safe 3.4-4.0%)
dispatch: reviewer opus high — review round 2 (resume ae593bcd6eb1d1d1a)
note: a background commit security review flagged a secret-detection-bypass in wi.py (no detail given); passed to review round 2 as a lead
verdict: review round 2 NEEDS_CHANGES (high 1: regression — a secret after an earlier pair on the same line is never checked (compact JSON, joined pairs), likely the flagged bypass; medium 2: notes quoting code or token counts refused — secret word matched as a substring, no exemption for calls, attribute access, numbers, paths; medium 3: Markdown emphasis or code spans around keys and values defeat all rules (pre-existing); low 4: zero-width and fullwidth characters defeat all rules); round-1 findings fixed; 12 Checks pass
dispatch: implementer opus medium — fix round 2 (resume a7035ad4054cec38e)
return: DONE 764863a (search resumes at each value, cap 256; secret word as a whole key segment, plurals excluded, webhook added; calls/subscripts/attributes/numbers/paths skipped only with harmless segments; Markdown stripped; NFKC and Cf dropped; 12/12 Checks; store 0 hits; misses under secret-word keys 0 of 10,000)
dispatch: reviewer opus high — review round 3 (resume ae593bcd6eb1d1d1a)
note: the background commit security review flagged two security-control-regression issues in wi.py on 764863a (no detail); passed to review round 3 with a main-vs-branch differential to run
verdict: review round 3 NEEDS_CHANGES (high 1: the Markdown/Unicode cleanup makes the old rules miss 4,103 of 36,000 generated lines main catches — run rules on raw OR cleaned; medium 2: a secret shaped as a quoted string, a call or subscript wrapping it, a number or a digit path is skipped; medium-low 3: compound lowercase keys (dbpassword, apitoken) lost the secret-word check; low 4: <…> placeholder looser than documented; low 5: judgement calls); round-2 findings fixed
dispatch: implementer opus medium — fix round 3 (resume a7035ad4054cec38e); review 4 next, the convergence stop applies from it
return: DONE 727fe26 (rules on raw OR cleaned: main-only misses 0 of 36,000; skips narrowed (quoted none, call/subscript only when the inside wouldn't flag, numbers only with a count word or separators, paths 2+ harmless segments); compound keys by suffix; strict <…> placeholder; known strictness and gaps in format.md; 12/12 Checks; store 0, main-only 0)
dispatch: reviewer opus high — review round 4 (resume ae593bcd6eb1d1d1a); from here the convergence stop applies
verdict: review round 4 NEEDS_CHANGES (must-fix 1, down from 2: an unbounded slice per pair makes lint quadratic on very long lines (19s at 2M chars); lows: '+' counted harmless in path segments; follow-ups: tighter $/{} placeholders, a pass suffix with a deny-list, a spaced second call argument); main-only misses 0 of 36,000 confirmed; the three documented gaps judged acceptable
decided: 2026-10-09T12:34Z cap — must-fix fell 2 → 1, so the cycle continues; a finish round of the exact one-line fix and low 2 (authority answer 145)
dispatch: implementer opus medium — finish round (resume a7035ad4054cec38e)
return: DONE 1eaac17 (300-char bound per pair; cleaned pass only when the line changed; harmless segments letters and digits only; 2M chars 1.72s (was 19s); main-only 0 of 36,000; 313 tests)
review: self
verdict: finish round CLEAR — diff read: the bounded slice, the equivalent single pass when nothing was cleaned, the stricter segment rule
landed: 5c66a65 (merge of f526872..1eaac17); Checks 12/12 OK; wi lint over the real store: no secret findings
- 2026-10-09 done
