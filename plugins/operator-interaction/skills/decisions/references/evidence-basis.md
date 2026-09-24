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
occur"). When likelihood matters, say it in words on the option's impact line (*likely*,
*unlikely*), never as a number, and never folded into the basis word.
