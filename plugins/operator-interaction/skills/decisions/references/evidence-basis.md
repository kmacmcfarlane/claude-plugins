# Evidence basis

What a decision's claims rest on, shown as **one word and a reason** at a glance, with the
tags behind it on drill-down. It replaces a confidence number: an LLM's self-reported
confidence runs high whether or not it is right, and a percentage looks precise without being
so. Examples are **illustrative**.

## At a glance

```
basis **strong | partial | thin | none** — *one-clause reason*
```

- *basis **strong** — ran the full test suite; all 212 pass*
- *basis **partial** — the load test covered 2 of the 5 worker types*
- *basis **thin** — recalled from general practice, not checked here*
- *basis **none** — no evidence yet; see (c) investigate first*

The reason is part of the indicator, not decoration: a word alone gets read loosely, and the
reason anchors it to something the operator can check.

## The tags (drill-down)

Shown in a block, or when the operator asks to `expand` a card. Per load-bearing claim:

| Tag | Values | Meaning |
|---|---|---|
| Provenance | **observed** / **reported** / **inferred** / **recalled** | observed — you ran or read it yourself, this session, and can point at the tool result; reported — read in a summary, a log, another agent's words; inferred — reasoned from other evidence; recalled — general knowledge, nothing checked here |
| Completeness | complete / partial / none | how much of what the claim covers the evidence covers |
| Source | what was consulted: a test run, the primary document, a summary, an assumption | kept apart from provenance: a well-read weak source is still a weak source |
| Agreement | independent checks agree / conflict / single source | agreement between copies of the same model is not independent |

Write each claim with its link or pointer: *observed — this week's access log shows 2
partners calling the endpoint (link)*.

**Observed means a tool result.** Tag a claim observed only when it points at something you
ran or read this session. Agents' citations often look grounded — real links, relevant pages —
while the claim attributed to them is wrong; the pointer is what lets the operator spot-check
it.

## The rule

Derive the word; never pick it freely.

1. Start from the provenance of the weakest **load-bearing** claim — the one the
   recommendation depends on:

   | Provenance | Word |
   |---|---|
   | observed | strong |
   | reported, inferred | partial |
   | recalled | thin |
   | no evidence | none |

2. Name the deciding tag in the reason: *partial — the load test covered 2 of 5 worker types*.
   When completeness, the source or a conflict is what weakens the claim, the reason says so;
   the word does not step down by arithmetic (why: `references/rationale.md` § Evidence basis
   over confidence).

**A decision with no recommendation** — a preference, or a call outside your authority — has a
different load-bearing claim: *no fact settles it* (or *it is not mine to make*). Checked —
you looked for what depends on the choice and found nothing — is **strong**; assumed is
**thin**. So a trivial, warm, two-way preference you checked can stay a list line, and the
same preference three renders apart gets the same word.

## Keep it apart from likelihood

How well founded a claim is and how likely an outcome is are different questions. A
well-observed claim can still describe an uncertain outcome ("the race condition may still
occur"). Never fold likelihood into the basis word.

On a **risk decision**, one whose options trade against a failure that may or may not happen,
the card's **Likelihood:** line (`references/rendering.md` § Card) names the event it counts,
in plain words, then gives the strongest concrete fact available (answer 267 (a), widened), in
this order:

- an observed count with its window and source (*two outages in twelve months, the provider's
  status page*): kind *observed*;
- else another concrete fact, kind *observed*: when it last happened; an observed share with
  its source; whether the failing path is reachable, and from where (*any signed-in user can
  reach it*); a reproduction; whether a guard already exists;
- else, kind *evidence*, a description of the evidence there is and what would settle it (*no
  incident log covers this service; the code path is reachable from public uploads; a week of
  request logs would show it*).

An observed count is a fact, not a confidence. A bare *no data* is never the line; an
estimated probability never appears, and a percentage only as an observed share with its
source and window. Under it, **Best response?:** says whether acting here is the most
important response to that failure, and if not, what is.
