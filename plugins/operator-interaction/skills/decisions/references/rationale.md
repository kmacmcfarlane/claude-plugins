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
  (en.wikipedia.org/wiki/Completed_staff_work; *secondhand*, a reference page). The doctrine
  states no exceptions.
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

## Everything to act on, on the card

The operator's asks, on two cards they could not act on from where they were shown: "A
decision should have all the MUST-HAVE inputs the decider needs to make the decision"
(2026-10-06), on a card that asked them to run a check without saying where its files were
or what to paste; and "Before this decision was shown, it should have included …"
(2026-10-07), on a card whose options were named by labels from a plan they had not read —
what those labels stood for. The floor was written for understanding and answering a
decision, not for carrying out an option the operator performs; its gloss rule covered ids
and names, not terms or a source document's labels.

- **Completed staff work, its second half.** The decider approves or disapproves from the
  document alone, "with no further work" (§ The floor; *secondhand*, a reference page). The
  floor had made a rule of the first half only. What it takes to act is the second, and the
  cold read is the acceptance test the research behind this skill proposed for every card:
  could a decider with no prior context approve or disapprove from this alone? It is
  extended here from approving to carrying out.
- **The decision memo encloses what is signed.** A U.S. Army decision memorandum states its
  recommendation as the thing the principal signs, and tabs that item first among its
  enclosures (AR 25-50, *Preparing and Managing Correspondence*, para 4-4,
  https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN42124-AR_25-50-007-WEB-13.pdf;
  *secondhand*, via an earlier research pass). The **To act on** part is its analogue: what
  the operator acts on is on the card, not to be fetched. By analogy only: no source found
  covers a decision whose option the decider performs, with paths, commands and text to
  paste.
- **Observed in practice.** Cards and the one-line digests of open decisions leaned on
  labels a cold reader could not resolve: a plan's step and tier names, short ids, rules
  named by a section number. One card promised its steps for a later turn, and its command
  held a fill-in placeholder.
- **Why inputs get a part and terms do not.** Inputs are long, structured and checkable
  (steps, commands, text to paste): a part of their own keeps them out of the option line,
  gives a store one line to keep them on, and gives an answer page one field to check. A
  term is best said in its place, in the words it stands for; a glossary part would be one
  more thing to store and render, and a pointer to the source is not a definition. These are
  the reasons behind the two rulings (`references/rulings.md`, **Inputs to act** and
  **Terms defined where shown**).
- **Why a cold read and not a scanner.** Whether a reader knows a term is not decidable by a
  program, and a card composed in chat would have to be written out to be scanned on every
  raise. The decidable parts — a fill-in placeholder, an `act` field's shape on the page, the
  worked examples staying free of both failures — are checked by the page and the tests; the
  rest is the cold read.

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
detail and the slower the answer. The two are judged by you, and shown to the operator as
the Undo and Reach facets (§ Impact in every view), in words that say how and who rather
than a stakes label.

## Impact in every view

The operator's ask (2026-10-06): "I want to ALWAYS see some form of impact that a decision
has, even in the one-line version. The impact of the decision is critical for me, and it's
not currently visible in a way I can understand it at all times." Then, on a first proposal
that changed the list line only: "I want it to be in the other sizes of outputs too … Consider
how to structure the impact as you get more space to work with." The ruling
took five facets in one vocabulary, shown more fully as space grows.

- **Why these five.** Effect and Wait are the two sides a decider weighs at a glance: what
  happens on yes, what happens on waiting — the decision aids' "outcome of each option,
  doing nothing included" (§ The floor). Reach and Undo are the stakes dimensions
  (§ Stakes), told as who and how instead of as a label: *reversible, narrow* named a tier
  without saying what reversing takes. Cost is what a round ask already had to justify
  (§ Asks for another round), for every option.
- **One order at every size.** The facets are learned once and read the same way in a
  table row and a block, so a larger view adds to the smaller one and never re-sorts it.
- **Stored at raise.** The tightest views (a caller's table row, a report's line of numbers)
  have no room to open the options, and deriving the impact there from option text each
  time reads less clearly; written once with the card, it is read the same way everywhere,
  as the context cue is (§ Who is reading).

## Who is reading: events, not the clock

- Clinical handover (I-PASS; PMC7382547, citing the NEJM 2014 multicentre study,
  *secondhand* for the outcome figures) and air-traffic position relief (*secondhand*) trigger
  re-grounding on an **event** — a handover — not on elapsed time.
- Supervisory control of many autonomous agents (Crandall & Goodrich 2003, primary) separates
  how long a task may be neglected before it degrades from how long it takes the supervisor to
  deal with it. Bounded deferral (Horvitz; *secondhand*) holds a notification back for a bounded
  time, never resolves it.

Hence two clocks: events since the operator last touched it (depth), and time until something
breaks (urgency). Age is shown and breaks ties; no rule batches by it. The event that matters
most in a long session happens to the operator, not the agent: a card printed while they were
away was rendered, not seen, so "no operator turn since it was shown" counts as an event.

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
  skill adds is where the harm is: the read-back before a one-way option acts. Clark and I-PASS
  support a read-back before an irreversible *action*; a reversible choice on a ⚠ decision
  costs a revert if misread, so it is echoed, not read back.
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
- The basis word keeps only the start and the named reason. A step-down arithmetic — one level
  per partial completeness, weak source or conflict, never above the start — was specified in
  v1 and no render ever applied it past the first step; the reason clause carries those
  weaknesses in words the operator can check instead.
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
wake — a deferral never woken is a default by omission. The default wake is a natural break in
the agent's own work (the next time it finishes something and reports) rather than a count of
turns or hours: interruption research favours breakpoints (McFarlane 2002; bounded deferral,
Horvitz, *secondhand*), and it is one rule every caller can explain.

## Order

Popular "decision fatigue" did not replicate (a 23-lab registered replication found no effect;
the parole-judges study has a scheduling confound; *secondhand*). The reason to put the most
pressing decisions first is different: if the operator stops partway, the answers that matter
most are already in. Grouping related decisions spares the re-grounding cost of each context
switch — the operator's own reason for grouping.

The deadline rule is asymmetric on purpose: listing a deadline decision first when the
operator was back in time costs nothing, while listing it low can lose the lease. So with the
return unknown every stated deadline goes first, with no hour threshold to tune.

**Where it sits.** The operator reads in a terminal, where the end of the message is what is on
screen when the agent stops. So the decisions come last, after any report or summary, and the
compact list with the hint is the very last thing — the operator's own ask (2026-09-24): "the
compact, one-line decision list below the cards/blocks so you can answer some/all of them
without scrolling up".

## Options and recommendations, as the operator reads them

The operator's rulings (2026-09-29), each from reading decisions shown the other way:

- **Letter order, the recommendation in bold.** "These options should be in abc...z order,
  if you have a recommendation, let's bold it." Putting the recommended option first is a
  modal dialog's convention, where the first choice is the default. In a card the operator
  reads the options as a list and answers by letter, so the letters run in order and the
  recommendation is marked where it stands.
- **Every decision's own recommendation.** Four related decisions shown as one grouped
  entry drew: "you haven't provided any recommendations?" A group spares context switches
  (§ Order) only while each decision in it can still be answered from where it is shown; the
  folded entry kept the topic and lost the answer — the failure § The floor observed in
  checkpoint digests.

## Asks for another round

A review-cap waiver asked with its fixed options and little else drew: "each ask for another
turn needs to justify why it's worth the cost of an operator decision along with the ask. If
the impact is high, it's justified. I have no insight into the impact, so I can't make a
decision." A template spares the operator reading the options again, not the weighing.
What the leftover findings would break and what the round costs are the two sides of that
weighing, and both change every time. Completed staff work (§ The floor) asks the same: the
decider can approve or disapprove from what is shown alone.

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
