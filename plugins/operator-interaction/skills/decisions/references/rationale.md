# Rationale

Why each rule exists, with its sources. *Secondhand* marks a source read through a summary or
restatement rather than its primary text; the rule still stands on the convergence of the
sources beside it.

## The goal: understood where it is shown

The operator's framing: the goal is not to get the decision, it is for the operator to
understand it — its context and impact — where it is shown; a decision shown without enough
context to see what is being decided and what it costs cannot be answered at all.

## The floor

Five traditions outside software converge on a minimum every decision carries, at any length:

- **Completed staff work** (military staff doctrine): the decider must be able to approve or
  disapprove from the document alone, with no further work
  (en.wikipedia.org/wiki/Completed_staff_work). The doctrine states no exceptions.
- **Informed-consent materiality** (*Canterbury v. Spence*, D.C. Cir. 1972, primary case
  text): a fact must be disclosed when a reasonable person in the decider's position would
  weigh it. Brevity does not excuse dropping it.
- **Situation awareness** (Endsley 1995; *secondhand*): perception, comprehension and
  projection must all be present to act — what is, what it means, what each option leads to.
- **Patient decision aids** (IPDAS; Cochrane review of decision aids, Stacey et al. 2024,
  primary): options including doing nothing, the outcome of each, their likelihood, and what
  matters to the decider.
- **Briefing formats** (BLUF, policy decision memos, decision papers): every one keeps the ask
  and "why it matters now" at any length.

Observed in practice: in one estate's history of agent-raised decisions, whether options and a
recommendation were present predicted a one-letter answer; line length did not. Decisions
raised as bare topics all needed a paragraph from the operator to reconstruct the options.
The one-line digests of open decisions at a context checkpoint dropped the options, the
recommendation, the impacts, and glossed no ids — and were the decisions the operator could
not answer.

More detail is **not** shown to help in itself: the Cochrane review excluded the detailed-vs-
simple comparisons for lack of a usual-care control, and no single decision-aid attribute
reliably predicts effectiveness. Content completeness is the variable, not length.

## Exceptions

Assembled from adjacent practice, since the strictest source allows none: preference
elicitation (no fact to recommend from), authority (a call outside the agent's standing),
time-critical alerts (the cost of forming options exceeds the alert's value), and framing
questions (the decision is not defined yet). Each must be labelled, or it reads as the bare
topic the floor exists to prevent.

## Stakes: reversibility and blast radius together

- Amazon's 2015 shareholder letter (SEC EDGAR, exhibit 99.1 to the 8-K filed 2016-04-05,
  primary): Type 1 decisions are "consequential and irreversible or nearly irreversible —
  one-way doors" and "must be made methodically, carefully, slowly"; most decisions are
  two-way doors. One compound criterion, not two summed scores.
- Gutfraind, *PeerJ Computer Science* 2024 (primary): reversibility is one of nineteen
  properties that each independently reduce a decision problem's difficulty — important, and
  not the only driver.
- ITIL change management (*secondhand*): pre-approved "standard changes" are narrow and
  reversible; risk tiering follows blast radius.

Hence ⚠ = one-way *and* high impact, answered on its own, and the higher the stakes, the more
detail and the slower the answer.

## Who is reading: events, not the clock

- Clinical handover (I-PASS; PMC7382547, citing the NEJM 2014 multicentre study,
  *secondhand* for the outcome figures) and air-traffic position relief (*secondhand*) trigger
  re-grounding on an **event** — a handover — not on elapsed time.
- Supervisory control of many autonomous agents (Crandall & Goodrich 2003, primary) separates
  how long a task may be neglected before it degrades from how long it takes the supervisor to
  deal with it. Bounded deferral (Horvitz; *secondhand*) holds a notification back for a bounded
  time, never resolves it.

Hence three clocks: events since the operator last touched it (depth), time since raised
(batching), time until something breaks (urgency).

## Presentation that can mislead

- A better verification interface made people **more confident when wrong** (Hedges' g 0.85)
  with no gain in accuracy (Grunde-McLaughlin et al., "Overseeing Agents Without Constant
  Oversight", arXiv 2602.16844, primary). Detail is not the lever.
- Explanations did not reliably improve human–AI team accuracy and sometimes raised acceptance
  of wrong answers (Bansal et al., CHI 2021); overreliance tracks the **cost of verifying** the
  AI's output (Vasconcelos et al., CSCW 2023, 5 studies, N=731, primary abstract). Hence
  checkable evidence and links over prose rationale.
- Forcing the human to commit before seeing the AI's answer reduces overreliance but costs
  speed and satisfaction (Buçinca et al. 2021, N=199; *secondhand*). The only friction this
  skill adds is where the harm is: the ⚠ read-back.
- A one-keystroke answer is weak evidence of understanding: in the grounding literature an
  acknowledgement sits near the bottom of the evidence of understanding, below demonstration
  (Clark & Schaefer 1989, Clark & Brennan 1991; *secondhand*). Handover protocols require a
  read-back for the same reason. Hence the read-back before a one-way action, and the burden
  on what is shown before the keystroke.

## Evidence basis over confidence

- LLM verbalized confidence is overconfident (Xiong et al., ICLR 2024; the abstract confirms
  overconfidence; the strength of the clustering is *secondhand*). P(True) and sampling
  methods discriminate better but need re-running the model (Kadavath et al. 2022, primary
  abstract).
- Deep-research agents' citations: 94%+ valid links, 80%+ topically relevant, 39–77% factually
  accurate, degrading with more tool calls ("Cited but Not Verified", arXiv 2605.06635,
  primary). Hence provenance from tool results, not self-report.
- Intelligence analysis keeps confidence in the evidence separate from the likelihood of the
  claim (US ICD 203; *secondhand*, via a restatement); the NATO Admiralty code rates source
  reliability and information credibility separately and never merges them (*secondhand*);
  GRADE starts from study design and downgrades by named domains (CDC ACIP GRADE handbook,
  primary). Readers misread verbal probability terms, and pairing a word with an anchor helps
  (Budescu et al.; *secondhand*). Evidentiality — observed, inferred, reported, assumed — is
  marked grammatically in about a quarter of the world's languages (Aikhenvald; *secondhand*).
- A confidence number used to **order** decisions answers the wrong question (how likely a
  claim is right, not when the operator should look) and invites inflation, the same failure
  as self-declared urgency.

## Silence and defaults

- Apache lazy consensus (community.apache.org, primary): silence counts as consent after about
  72 hours, for matters the proposer is confident the community would accept.
- IETF Last Call is not "silence = approval": a chair judges rough consensus and objections
  must be addressed (RFC 2418, primary).
- Warnock's dilemma (*secondhand*): silence cannot tell agreement from not having seen, not
  having understood, or not caring.
- No practice surveyed lets silence decide a matter that is hard to undo or that others build
  on; the harm in every failure case came from someone relying on the outcome before review.

Hence no timed defaults on actions, status-quo defaults allowed, and every deferral with a
wake — a deferral never woken is a default by omission.

## Order

Popular "decision fatigue" did not replicate (a 23-lab registered replication found no effect;
the parole-judges study has a scheduling confound; *secondhand*). The reason to put the most
pressing decisions first is different: if the operator stops partway, the answers that matter
most are already in. Grouping related decisions spares the re-grounding cost of each context
switch — the operator's own reason for grouping.

## Replies

Deciders answer with more than choices: a request for information tied to a decision point
(military RFI practice, *secondhand*), more tests or watchful waiting (medicine), approve /
request changes / comment (code review, GitHub docs, primary). In one estate's history about
a quarter of answers were not choices: "you decide", reframes, requests for more, and decisions
overtaken by events. Asking an agent to clarify only when the answer would change the response
is learnable (CIGAsk, arXiv 2609.24290, primary). Hence the reply types, the echo, and keeping
the decision's number stable across rounds.

## Timing of interruptions

Immediate interruption is the most disruptive of the coordination methods (McFarlane 2002,
primary); whether now is a good moment for the operator has no observable signal in a text
session today, so this skill leaves it alone.
