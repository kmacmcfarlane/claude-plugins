---
name: chain-of-verification
description: Run Chain-of-Verification (CoVe) on a prompt to reduce hallucinations. Generates a baseline response, plans verification questions, answers them independently via subagent, then revises. Use when user says "cove", "chain of verification", "verify this", "fact-check this response", "reduce hallucinations", or wants a high-accuracy factual answer.
disable-model-invocation: false
allowed-tools: Agent, WebSearch, WebFetch, Read, Glob, Grep
argument-hint: [question or prompt to verify]
---

# Chain-of-Verification (CoVe)

A 4-step pipeline that forces self-verification to dramatically reduce hallucinations. Based on Dhuliawala et al. (2023) — "Chain-of-Verification Reduces Hallucination in Large Language Models" (arXiv:2309.11495).

The user's prompt: $ARGUMENTS

## Why this works

LLMs are poor at generating long, perfectly factual narratives in one shot. But they are highly accurate at answering short, targeted verification questions. CoVe exploits this asymmetry.

Classic Chain-of-Thought (CoT) prompting does NOT help here and sometimes hurts — "thinking step by step" is not the same as checking facts. CoT addresses reasoning errors; CoVe addresses hallucinated facts. They solve different failure modes.

Empirical results from the paper (Dhuliawala et al., 2023):
- **List tasks (Wikidata):** Precision more than doubles (0.17 → 0.36), hallucinated entities drop from 2.95 to 0.68
- **MultiSpanQA (closed book):** F1 improves 0.39 → 0.48
- **Biography generation:** FACTSCORE improves 55.9 → 71.4 (Factor+Revise variant)

This skill implements the **Factor+Revise** variant — the strongest in the paper — which adds an explicit cross-check step between verification and final revision (~8 FACTSCORE points over plain Factored).

## When NOT to use CoVe

CoVe costs 3-4x the tokens of a direct response and adds 30-60 seconds of latency (multiple LLM calls + tool use). Do NOT use it when:

- **The prompt has no falsifiable factual content** — opinion questions, creative writing, brainstorming, code generation from spec. CoVe adds cost with no accuracy benefit.
- **Latency matters** — customer-facing chatbots, real-time interactions. CoVe is designed for background jobs, research, reports, and situations where accuracy outweighs speed.
- **The answer is trivially verifiable** — "What's 2+2?" doesn't need a verification pipeline.
- **The user just wants a rough draft** — if they'll fact-check themselves, skip CoVe and save tokens.

## Critical

- **Step 3 MUST be independent.** Verification runs in a subagent with NO access to the baseline draft. This prevents the model from repeating its own biased reasoning.
- **Grounded observation, not inference.** Never verify by reasoning from memory. Actually read the file, run the search, fetch the page. If you can't reach the system needed to check, say so explicitly.
- **Never skip steps.** Even if the baseline looks correct, run the full pipeline.
- **Be ruthless in Step 4.** If a verification answer contradicts the baseline, the baseline is wrong. Remove or correct the claim — do not hedge with "some sources say."

## Pipeline

### Step 1: Generate Baseline Response

Respond to the user's prompt naturally and completely. This is a rough draft — prioritize coverage over caution. Include specific claims, names, dates, numbers, and details. The more concrete the baseline, the more verification questions it generates.

Output format:
```
## Baseline Draft

[Full response to the user's prompt]
```

### Step 2: Plan Verification Questions

Scan the baseline draft and identify every factual claim that could be wrong. For each claim, write a short, targeted verification question **paired with a concrete method for checking it**. Focus on:

- Named entities (people, places, organizations)
- Dates, numbers, statistics
- Causal claims ("X caused Y")
- Comparative claims ("X is the largest/first/only")
- Technical specifications or definitions
- Relationships between entities ("X founded Y", "X is part of Y")

Each question MUST be:
- **Specific** — answerable by reading a file, running a command, searching the web, or checking docs
- **Independent** — stands alone, not depending on answers to other questions
- **Falsifiable** — a wrong answer would actually change the conclusion. Don't generate trivial questions that couldn't plausibly be wrong.

Aim for 5-15 questions depending on response complexity.

Output format:
```
## Verification Questions

1. [Question] → [How to check: file to read, command to run, search to perform, doc to consult]
2. [Question] → [How to check]
...
```

### Step 3: Classify Verification Mode

Before executing verifications, classify the prompt to determine the right subagent configuration:

- **Codebase mode** — the prompt asks about code, APIs, configs, or architecture in the current project. Verification uses `Read`, `Glob`, `Grep` against local files.
- **General knowledge mode** — the prompt asks about history, science, people, events, technical concepts, or anything not grounded in local files. Verification uses `WebSearch` and `WebFetch` to cross-reference claims against external sources.
- **Mixed mode** — the prompt spans both (e.g., "How does our auth implementation compare to OWASP recommendations?"). Spawn both subagent types and merge results.

### Step 4: Execute Verifications Independently (via Subagent)

**Two non-negotiable rules:**

1. **Isolation** — verification questions MUST be answered in a separate context (subagent) to prevent attention bias from the baseline draft. The subagent has NO access to the baseline. This is the key architectural insight from the paper.
2. **Grounded observation** — never answer verification questions by reasoning from memory alone. Actually do the check: read the file, run the search, fetch the page. Verification is grounded in observation, not inference. If a check requires a system you can't reach, say so explicitly rather than guessing.

Pass both the questions AND their how-to-check methods (from Step 2) to the subagent.

#### Codebase mode

Spawn an `Agent` subagent with `subagent_type: "general-purpose"`:

```
You are a fact-checker verifying claims about a codebase. For each question below,
actually perform the check described — read the file, grep for the symbol, check
the config. Do NOT answer from memory. Do NOT assume any prior context.

IMPORTANT: If a check method says "read file X", actually read it. If it says
"grep for Y", actually grep. Grounded observation only.

Questions:
1. [question] → [how to check]
2. [question] → [how to check]
...

For each question, respond with:
- **Q:** [the question]
- **Evidence:** [what you actually observed — file contents, grep output, etc.]
- **A:** [your answer based on the evidence]
- **Status:** Confirmed | Corrected | Uncertain
```

#### General knowledge mode

Spawn an `Agent` subagent with `subagent_type: "general-purpose"`:

```
You are a fact-checker. For each question below, actually perform the check
described — search the web, fetch the page, find the primary source.
Do NOT answer from memory alone. Do NOT assume any prior context.

Use WebSearch to find authoritative sources. Prefer primary sources (official docs,
peer-reviewed papers, government data) over secondary ones. When you find a relevant
source, use WebFetch to read it and extract the specific fact.

If no reliable source can be found after searching, mark as Uncertain — do NOT guess.

Questions:
1. [question] → [how to check]
2. [question] → [how to check]
...

For each question, respond with:
- **Q:** [the question]
- **Evidence:** [what you actually found — page content, search results, etc.]
- **A:** [your answer based on the evidence]
- **Source:** [URL or "unable to verify"]
- **Status:** Confirmed | Corrected | Uncertain
```

#### Mixed mode

Spawn two subagents in parallel — one for codebase questions, one for general knowledge questions. Split the verification questions by type before dispatching.

#### Batching

If there are more than 8 verification questions, split into batches of 5-8 per subagent call. Run batches in parallel where possible.

Output format (merged from subagent results):
```
## Verification Answers

1. **Q:** [question]
   **Evidence:** [what was observed]
   **A:** [answer based on evidence]
   **Source:** [file path, URL, or "unable to verify"]
   **Status:** Confirmed | Corrected | Uncertain

2. ...
```

### Step 5: Cross-Check (the "Revise" in Factor+Revise)

This is the step that separates Factor+Revise from plain Factored (~8 FACTSCORE points improvement). Before writing the final response, explicitly compare each baseline claim against its verification result in a structured table. This gives the revision step something concrete to operate on.

Output format — use a structured table, NOT prose:
```
## Cross-Check

| # | Baseline Claim | Verification Finding | Status |
|---|---------------|---------------------|--------|
| 1 | [claim from baseline] | [what verification found] | Consistent / Contradicted / Unverified |
| 2 | [claim from baseline] | [what verification found] | Consistent / Contradicted / Unverified |
...

Consistent: N | Contradicted: N | Unverified: N
```

### Step 6: Final Verified Response

Using the cross-check table (NOT the baseline), choose the appropriate response strategy:

- **ALL CONSISTENT** → State confidence in the baseline. Briefly note what was checked. No rewrite needed — present the baseline as verified.
- **ANY CONTRADICTED** → Rewrite the response from scratch. Use consistent claims as-is, replace contradicted claims with verified facts, drop unverified claims. Do NOT hedge with "some sources say" — if the verification found the answer, use it.
- **MOSTLY UNVERIFIED** → State what couldn't be verified and what additional information or sources are needed. Recommend the user cross-reference with authoritative sources.

Output format:
```
## Verification Summary
- Checked: N claims
- Consistent: X | Contradicted: Y | Unverified: Z
- Result: VERIFIED | CORRECTED | PARTIAL

## Verified Response

[If VERIFIED: the baseline response, confirmed]
[If CORRECTED: full rewrite with corrections incorporated naturally]
[If PARTIAL: best-effort response with unverified claims explicitly qualified, plus a list of what needs external verification]
```

## Adapting to prompt type

Consult `references/prompt-types.md` for guidance on how to adapt the verification strategy for different types of prompts (list-based, short-answer, long-form).

## Examples

**Example 1: Factual question**
User says: `/chain-of-verification Who were the first 5 presidents of the United States and what are they known for?`
Pipeline produces: baseline with 5 presidents and claims about each, verification questions targeting each biographical claim, independent answers, then a corrected final list.

**Example 2: Technical claim**
User says: `/chain-of-verification How does Rust's borrow checker prevent data races?`
Pipeline produces: baseline explanation, verification questions about specific mechanisms described, independent answers checking each technical claim, then a corrected explanation.

## Troubleshooting

**"Yes-Man" loop (confirmation bias)**
The verification subagent answers questions in a way that supports the original draft rather than checking independently. Symptoms: ALL CONFIRMED on a response you'd expect to have errors, or verification answers that parrot phrasing from the baseline.
Cause: The subagent prompt leaked baseline context, or the questions were leading rather than neutral.
Solution: Ensure subagent prompt contains ONLY the verification questions and how-to-check methods — never the baseline text. Rewrite leading questions (bad: "Confirm that X is true" → good: "What is X?"). If the problem persists, consider using `model: haiku` for the verification subagent to get a different "opinion."

**Verifier fallibility / false assurance**
ALL CONFIRMED doesn't mean the response is correct — it means the verifier couldn't find errors. The verifier can fail if: (1) the model is uniformly ignorant on the topic (garbage in, garbage out), (2) the verification questions don't target the actual weak points, or (3) web sources themselves are wrong.
Solution: Treat VERIFIED as "passed available checks," not "proven correct." For high-stakes content, note in the summary that verification is bounded by the model's and tools' capabilities. If a topic is obscure enough that no web sources exist, say so.

**No verifiable factual claims in the prompt**
The prompt is purely opinion-based, creative, or procedural (e.g., "Write me a poem", "How should I structure my project?"). CoVe adds no value here.
Solution: Tell the user CoVe is designed for factual accuracy. Offer to answer the prompt directly without the pipeline.

**All or most verifications come back Uncertain**
The questions are outside the model's reliable knowledge, or the topic is too niche.
Solution: In Step 6, explicitly qualify every uncertain claim. Add a note to the Verification Summary recommending the user cross-reference with authoritative sources. List which specific claims could not be verified.

**Subagent fails or times out in Step 4**
The verification subagent may fail if there are too many questions or if codebase searches are expensive.
Solution: Split into batches of 5-8 questions per subagent call. Retry failed batches once.

**Baseline is empty or trivially short**
The model doesn't have enough knowledge to draft a meaningful baseline (e.g., extremely obscure topic).
Solution: Tell the user the topic may be outside the model's training data. Suggest they provide reference material or context to ground the response.
