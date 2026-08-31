---
name: product-research
description: Structured, goal-driven product research that runs requirements gathering, broad web search, candidate analysis, and a comparison writeup with prices, vendor links, and pros/cons. Use this whenever the user is trying to decide what to buy, asks for recommendations, wants options compared, or says things like "what's the best X", "help me pick a Y", "I need something that does Z" — even if they don't use the word "research". Also use it when the user invokes it by name with a goal statement as the argument.
---

# Product Research

Turn a one-line goal into a defensible purchase recommendation. The value of this skill
is discipline: requirements before searching, breadth before depth, and verified
availability before anything is recommended.

## Input

The user supplies a **goal statement** as the argument — what they're trying to buy and
why. For example: "a mechanical keyboard for long coding sessions in a shared office."

**If no goal is provided, or the goal is too vague to derive requirements from, stop and
ask for one before doing anything else.** Do not guess and do not start searching. A
vague goal produces a research plan that quietly optimizes for the wrong thing, and the
user won't notice until the results are already wrong. Ask a single direct question, e.g.
"What are you looking to buy, and what's the job it needs to do?"

A goal is workable when you can name the product category and at least one constraint or
success condition. "Something for my desk" is not workable. "A monitor arm for a 34-inch
ultrawide on a thin desk" is.

## Phase 1 — Requirements and research methodology

Do this before any search.

1. **State your assumptions explicitly.** List what you're inferring that the user didn't
   say — budget band, region/currency, new vs. used, skill level, existing gear it has to
   work with, timeline. Surfacing these lets the user correct you cheaply now instead of
   expensively later.
2. **Ask the follow-up questions you actually need.** Batch them into one message rather
   than drip-feeding. Ask only what would change the shortlist — if the answer wouldn't
   move a candidate on or off the list, don't ask it. Then wait for answers.
3. **Derive research criteria** from the goal plus the answers. Separate them into:
   - **Hard constraints** — disqualifying. Budget ceiling, physical fit, compatibility,
     must-have features, regional availability.
   - **Weighted preferences** — how you'll rank the survivors, roughly ordered by how
     much the user seems to care.
4. **Plan the searches, then run them in parallel.** Issue multiple distinct queries in a
   single turn rather than one at a time. Cover several angles so you're not trapped in
   one publication's worldview:
   - category overviews and "best of" roundups (recent — check dates)
   - specific candidate model names as they surface
   - enthusiast/community discussion for failure modes reviewers miss
   - retailer and manufacturer pages for current price and stock

Show the criteria to the user before or alongside the search. It is the contract the
results will be judged against.

## Phase 2 — Analysis

1. **Score candidates against the criteria.** Drop anything that fails a hard constraint
   and say why it was dropped — a visible reject list is evidence the search was broad.
2. **Fill gaps with targeted follow-up searches.** If a candidate's spec, price, or
   reliability record is unclear, look it up specifically rather than hedging in the
   writeup.
3. **Verify current availability.** This is non-negotiable. Product research goes stale
   fast: models get discontinued, replaced by a successor, or stay listed at inflated
   prices long after they stopped making sense. For every finalist, confirm it is
   currently sold and note if a newer revision exists. Flag anything discontinued,
   perpetually out of stock, or superseded.
4. **Raise new questions if the evidence demands it.** If the research surfaces a
   trade-off the user hasn't weighed in on — a big price cliff, a durability concern, a
   category that fits the goal better than the one they named — say so now. This is
   optional; use it when the finding would genuinely change the decision, not as a
   reflex.

## Phase 3 — Present results

Present 3–5 candidates unless the user asked for a different number. Use this structure:

```markdown
## Criteria recap
[Hard constraints and weighted preferences, one line each]

## Candidates

### [Product name]
**Price:** [estimate, with currency] · **Where:** [vendor link]
[Two or three sentences on what it is and who it fits]

**Pros**
- [specific and tied to the criteria]

**Cons**
- [real trade-offs, not filler]

## Also considered / ruled out
[Name + one-line reason each]

## Recommendation
[Your pick and why, plus the runner-up and when it would win instead]
```

Rules for the writeup:

- **Price** — give a figure or a range, and say what it's based on (list price, current
  street price, typical sale price). If prices vary by vendor, note the spread.
- **Links** — link the manufacturer page or a major retailer when you have a real URL
  from search results. Never invent a URL. If you don't have one, say where to look
  instead.
- **Cons** — every candidate has them. A candidate with no cons listed means the research
  wasn't deep enough, not that the product is perfect.
- **Recommendation** — commit to a pick. Hedging across five options is a non-answer.
  Name the condition under which the runner-up would beat it, so the user can check that
  condition against their own situation.

Close by offering to go deeper on any candidate, or to re-run the shortlist against
revised criteria. Discussion is the point — the first shortlist is a starting position,
not a verdict.

## Notes on judgment

- Prefer recent sources. In fast-moving categories a two-year-old roundup is actively
  misleading.
- Be skeptical of heavily SEO'd "best of" content and affiliate-driven listicles. Weight
  hands-on reviews, teardown/measurement sites, and community consensus higher.
- Where sources disagree, say so rather than silently picking one.
- If the honest answer is "the thing you already have is fine" or "this category won't
  solve your problem," say that. A recommendation the user shouldn't act on is worse than
  no recommendation.
