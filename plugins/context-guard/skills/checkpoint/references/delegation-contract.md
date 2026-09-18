# Delegation contract — launching subagents and joining their results

What worked, measured: subagent results were 2.7% of one session's tool bytes for work that
would have been hundreds of KB inline, and reads delegated to clean contexts came back as
conclusions instead of file dumps. What made it work was the contract, not the delegation.
Skills reference this file instead of restating it.

## The launch contract

1. **Self-contained brief.** The subagent sees none of your conversation. Give it the facts it
   needs restated (numbers, paths, SHAs, prior findings *as content, not references*), then
   the question. If the brief needs your full context, use a **fork** — it inherits the
   conversation and the prompt cache; a fresh subagent starts empty.
2. **Deliverable to a file, findings in the reply.** The full work product goes to a named
   path (scratchpad for session-scoped, the owning repo for durable). The reply is bounded —
   **≤400 words** — and carries conclusions with the numbers that support them.
3. **Side-effect boundary, stated.** Read-only unless the brief says otherwise; name the
   directories it may write; "no git commands" when the parent owns staging. Writes stay
   single-threaded: one writer per path, and the parent reviews every diff.
4. **Honesty markers required.** "Could not determine" beats a guess; **unverified/secondhand
   claims flagged inline**; confounds stated. A subagent's confident wrong answer costs more
   than its silence.
5. **Right-size the worker.** Read-heavy locate → `Explore`. Read-and-reason →
   `general-purpose`. Needs this session's knowledge → fork. Never spawn what a single grep
   answers.

## The join contract (the parent's half)

1. **Thread results as they land.** Relay what matters to the operator per arrival — updating
   a running synthesis — rather than buffering everything for one dump.
2. **Route immediately.** Each finding goes to its owning repo's record (investigation
   threads, decisions, ledger) *on arrival*, not at session end; a result that only ever
   lived in the conversation dies at compaction.
3. **Corrections propagate.** When a subagent's finding overturns something already written,
   the supersession is recorded where the original claim lives — not just noted in chat.
4. **Never predict a pending result.** Until the notification arrives you know nothing; say
   "still running", never a forecast.
5. **Conflicting results are a finding.** Two agents disagreeing (e.g. docs-derived vs
   code-derived) is signal — surface the disagreement and which source wins and why; the code
   wins over a SKILL body, primary sources win over summaries.

## Anti-patterns, observed

- Briefs that say "see the plan" — the subagent cannot.
- Unbounded replies that refill the window the delegation was meant to protect.
- Parallel writers on one file, or a subagent committing what the parent hasn't reviewed.
- Re-running a delegated search yourself while it is still out.
- Treating a subagent's summary of a document as the document (mark it secondhand).
