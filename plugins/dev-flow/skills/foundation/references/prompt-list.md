# Prompt list

Loaded from `foundation` in phase 1 (the quality-scenario round) and at gate G2 (the
pre-mortem). These prompts always run, whatever the operator has already said: they are
where requirements go missing, and a requirement that arrives late costs review rounds
instead of a line.

## Quality-scenario round

Ask each, in the operator's terms. An answer that names a quality becomes a quality
scenario (quality, stimulus, response, measure); an answer of "not a concern" becomes a
non-goal when it could reasonably have been a goal; a "don't know" is held, with what needs
it.

| Quality | The prompt |
|---|---|
| Modifiability | What else might this need to run on or work with later: another vendor, harness, platform, machine or data source? What must not need a migration when that happens? |
| Privacy | What is never collected, stored or sent? Whose data passes through, and what of it may leave this process? |
| Durability | What cannot be rebuilt if it is lost? Does any data need to start accruing now because it cannot be recreated later? |
| Identity | What distinguishes one user, account, tenant or machine from another, in every store that keeps one? |
| Interoperability | Who reads our outputs, at which paths or interfaces, and which side defines each? |
| Operability | How does it fail, who notices, and how fast must they? |
| Cost | What may it spend (money, quota, compute, the operator's time), and what happens at the limit? |

An identity or interoperability answer usually also adds a glossary row (what "account"
means, across which stores) and a neighbours-table row.

## Questions inside a phase

At most five questions a round, ranked by impact × uncertainty, each carrying a hold
option. Before a question is asked it is triaged as the `investigate` skill's
`references/open-question-sweep.md` triages: verify what can be verified, ask only
decisions, record what is external as an Open Question.

## Pre-mortem

At gate G2, before the review: "It is a year on and this failed. Why?" Write each answer as
a risk (`K<n>`) with likelihood and impact, and give every H risk a mitigation or a spike.
An answer that is really a missing requirement is a raise, and may reopen requirements
(`references/moves.md`).
