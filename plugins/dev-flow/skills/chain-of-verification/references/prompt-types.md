# Prompt Type Adaptations

The CoVe pipeline adapts its verification strategy based on the type of prompt. The core 4-step structure stays the same — what changes is how you generate and focus verification questions.

## List-based questions

Questions that expect a list of entities (e.g., "Name all countries in South America", "What are the SOLID principles?").

**Verification mode:** General knowledge (or Codebase if listing code entities)

**Verification focus:**
- Verify each list item exists and belongs to the category
- Check for false inclusions (hallucinated entities that don't exist or don't belong)
- Check for missing items (important members of the category omitted)
- Verify any attributes attached to list items (dates, descriptions, relationships)

**Example verification questions:**
- "Is [entity] a real [category member]?"
- "Does [entity] actually have [claimed attribute]?"
- "Are there major [category members] missing from this list?"

## Short-answer / factoid questions

Questions with a specific, concise answer (e.g., "When was the Treaty of Versailles signed?", "What's the time complexity of quicksort?").

**Verification mode:** General knowledge

**Verification focus:**
- Verify the core factual claim directly
- Check for common confusions (similar entities, dates, or values often mixed up)
- Verify supporting context if provided

**Example verification questions:**
- "Is [claimed answer] correct, or is it being confused with [similar entity]?"
- "What is the commonly cited [metric/date/value] for [subject]?"

## Long-form / explanatory prompts

Questions requiring multi-paragraph responses with reasoning, narrative, or analysis (e.g., "Explain how mRNA vaccines work", "What caused the 2008 financial crisis?").

**Verification mode:** General knowledge

**Verification focus:**
- Break the narrative into discrete factual claims (one per verification question)
- Pay special attention to causal chains — verify each link independently
- Verify that the logical flow is accurate (A causes B causes C — not just that A and C are true)
- Check that technical terms are used correctly
- Verify that claimed relationships between concepts are accurate

**Example verification questions:**
- "Does [mechanism A] actually lead to [outcome B]?"
- "Is [technical term] being used correctly in this context?"
- "Did [event A] actually precede and contribute to [event B]?"

## Code-related prompts

Questions about programming, APIs, or technical systems where codebase verification is possible.

**Verification mode:** Codebase

**Verification focus:**
- Use `Grep` and `Read` to verify claims against actual source code
- Check that function signatures, return types, and behavior match claims
- Verify API endpoints, configuration options, and command flags exist
- Check version-specific claims against actual dependency files

**Verification tools:**
- `Grep` for symbol existence and usage patterns
- `Read` for implementation details
- `Glob` for file existence claims

## Research and knowledge questions

Questions about history, science, current events, people, geography, or any domain where the answer exists in external sources rather than local files.

**Verification mode:** General knowledge

**Verification focus:**
- Use `WebSearch` to find authoritative sources for each claim
- Prefer primary sources: official government data, peer-reviewed papers, organizational websites, standards bodies
- Avoid relying on forums, social media, or AI-generated content as verification sources
- Cross-reference across multiple sources when claims are contentious

**Example verification questions:**
- "According to [authoritative source], is [claimed statistic] accurate?"
- "Do primary sources confirm [claimed historical event] happened in [claimed year]?"
- "Does [organization's] official documentation describe [claimed feature/policy]?"

**Source quality hierarchy:**
1. Official documentation, government data, peer-reviewed papers
2. Reputable news outlets, established encyclopedias
3. Industry blogs, technical documentation
4. Forums, social media (use only to corroborate, never as sole source)

## Planning and strategy prompts

Questions about best practices, architectural decisions, process recommendations, or "how should I..." questions that blend factual claims with opinion.

**Verification mode:** General knowledge (for factual claims embedded in recommendations)

**Verification focus:**
- Separate factual claims from opinions/recommendations
- Only verify the factual underpinnings, not the subjective advice
- Check that cited frameworks, methodologies, or standards actually exist and are described correctly
- Verify that claimed trade-offs are accurate

**Example verification questions:**
- "Does [framework/methodology] actually recommend [claimed practice]?"
- "Is [claimed trade-off] between [X] and [Y] accurate?"
- "Does [standard/RFC/spec] actually specify [claimed requirement]?"

## Mixed-domain prompts

Questions that span local code AND external knowledge (e.g., "Does our implementation follow OWASP guidelines?", "How does our API compare to the Stripe API?").

**Verification mode:** Mixed

**Verification focus:**
- Split verification questions into codebase vs. general-knowledge buckets
- Codebase questions verify what the code actually does
- General-knowledge questions verify what the external standard/comparison actually says
- The final revision synthesizes both sets of verified facts

## Comparative / superlative claims

Prompts involving "the first", "the largest", "better than", "the only", etc.

**Verification mode:** General knowledge (or Mixed if comparing against local implementation)

**Verification focus:**
- Verify the superlative is accurate (is it really the first/largest/only?)
- Check for common misconceptions around priority disputes
- Verify the comparison criteria are applied consistently

**Example verification questions:**
- "Is [X] actually the first [category], or are there earlier examples?"
- "Is [X] larger than [Y] by [claimed metric]?"
- "Are there other [things] that also satisfy [claimed unique property]?"
