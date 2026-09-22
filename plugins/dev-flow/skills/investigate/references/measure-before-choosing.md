# Measure before choosing

Loaded from `investigate` Step 9a, which is conditional: it runs when the plan will offer
genuinely-open alternatives. Step 9a names the rules; this file holds them in full.

**When the plan will offer genuinely-open alternatives, take the cheapest measurement that
discriminates between them — before you recommend one.** Skip with one line when there is only
one viable approach, or when nothing measurable separates the candidates.

Specs and vendor numbers rank options; a measurement on the real system *eliminates* them. The
difference matters most where the alternatives differ by an order of magnitude in cost, because
that is exactly where reasoning from datasheets quietly picks the expensive one.

- **Measure the worst thing you already own.** A floor established on hardware or a
  configuration that is indisputably inferior to every option on the table often settles the
  question outright — if the worst candidate already clears the requirement by a wide margin,
  the differences above it are unobservable and the cheap option wins on evidence.
- **Bound the blast radius.** Measure idle or spare capacity first. Loading a production path
  needs explicit consent, a hard time cap, and a health check straight after — say plainly what
  could break and what it cost last time.
- **Two instruments beat one.** A synthetic benchmark that agrees with the system's own
  telemetry converts a plausible diagnosis into a confirmed one.
- Record the command, the conditions and the number. It goes in the investigation as evidence,
  and it is the baseline `implement` re-runs to prove the change worked.

If the discriminating measurement cannot be taken, say which option the decision rests on and
mark it for `implement` to settle.
