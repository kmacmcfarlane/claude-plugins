---
id: spike-shape-skill-a-shaping-session-vali-d985
title: "spike: shape skill — a shaping session (validate, gather, offer shapes, commit items, launch)"
type: spike
status: todo
priority: 2
created: 2026-09-24
updated: 2026-09-24
refs:
  - operator 2026-09-24 via agents librarian
---

Filed directly in this store by the agents librarian at the operator's request (2026-09-24): "Send a detailed message to the agent around the shape skill idea, perhaps it's most efficient for you to just create the detailed work item with our rich context from here in that repo and notify that agent you added the item and to read the work-item description." The operator decides; this is a request.

## What the operator wants
A skill that repeats a kind of turn the operator ran with the agents librarian on 2026-09-24. They asked what to call it. The agents librarian proposed "shaping session", after Shape Up's *shaping*: turning rough ideas into bounded options with a stated appetite before anyone commits. The operator liked the summary. Working name: `shape`.

## The workflow, as the operator laid it out (their goals for that turn, verbatim)
- "get a validation of the shape and connections between components we are building as they relate to the other in-flight repos as I'm describing"
- "gather more requirements from me and other information you have access to on-disk or through web search to get ready to make your plan"
- "create a plan to author these critical research spikes. Offer me different shapes and scopes so I can decide what will work best"
- "iterate with me as I review the plan"
- "execute the plan by creating rich work-items that encapsalate the background of what we are building and how these partially disjoint parts fit together"
- "launch some or all of the research tonight"
- plus: "Do some quick research directly in the chat to inform your response".

OMIT landing decisions. The operator was answering open decisions in the same turn, but excluded that from the skill: "I don't think that landing decisions should be a part of it, that was just what was going on when I thought to do this activity, so omit it."

## Steps as the librarian ran them (the worked example)
1. **Take in the initiatives**, in the operator's words, and keep their words verbatim for the items.
2. **Quick in-chat research.** A handful of web searches plus on-disk reads (e.g. the live quota from the status-line sensor, the relevant skills and repos). Mark results as reported/unverified, with links.
3. **Validate the shape.** Draw the components as layers or planes (front end / control plane / work / knowledge / telemetry / compute). Map each in-flight repo onto them, name what is missing and which pieces share a problem, and say where the operator's struggle comes from.
4. **Gather requirements.** A few numbered questions (Q1..Qn), each with a recommendation, so a reply can be "Q1 rec".
5. **Offer plan shapes with cost.** 2-3 shapes (e.g. separate runs vs one fan-out vs a staged hybrid). State cost against the live quota. Raise the choice as one decision per the operator-interaction decisions skill.
6. **Iterate** until the operator says go. Record every answer with an echo.
7. **Commit.** Create rich work items: a parent carrying the shared background (the map, principles, operator pain), one item per spike carrying its own requirements verbatim, sequencing, and consumers.
8. **Launch** the top-priority research, within the quota.
9. **Document the validated shape** durably, so future agents are oriented (the operator asked for this too).

## Operator addendum (2026-09-24, verbatim)
"the spike that claude-plugins does should include doing research on the shaping practice/workflow from high-quality sources on the web". So this spike starts with research, e.g. via the dev-flow research skill:
- Shape Up (Basecamp / Ryan Singer: shaping, appetite, breadboarding, fat-marker sketches, the betting table, rabbit holes, no-gos)
- dual-track agile / continuous discovery (Teresa Torres)
- design-sprint framing
- "discovery" and "inception" practices
- how those map onto an agent-plus-operator turn
Primary and authoritative sources, per the operator's quality bar.

## Evidence (read-only, in the agents repo)
- agents work items from that turn (each carries the shared map): estate-architecture-constitution-md-docu-5297, research-r1-self-hosted-work-system-for-18fb, research-r4-control-plane-factoring-back-254d, research-r2-route-a-free-task-class-to-l-60ec, research-r3-agent-wiki-vs-alternatives-i-857b. Store: /home/rt/work/src/github.com/kmacmcfarlane/agents/.work/items/
- The agents librarian session transcript is ba4716eb (2026-09-24 turns).

## Acceptance (suggested)
A research-backed design for a `shape` skill, including:
- its steps
- its relationship to investigate, research, deep-investigation, dev-cycle and operator-interaction:decisions
- where the plugin lives
- what it writes: items, a map doc
The operator reviews it before anything is built.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
