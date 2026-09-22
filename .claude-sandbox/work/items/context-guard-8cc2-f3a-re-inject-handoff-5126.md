---
id: context-guard-8cc2-f3a-re-inject-handoff-5126
title: "context-guard 8cc2-F3a: re-inject HANDOFF.md in full only to its lineage (authorship check)"
type: feature
status: doing
priority: 1
deps:
  - context-guard-8cc2-f2-hard-advice-fits-t-1f9d
parent: context-guard-turn-gate-8cc2
owner: unknown@360f41058e92
claimed: 2026-09-22T15:13Z
created: 2026-09-21
updated: 2026-09-22
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port — design awaits the 02 serial (plan review round 2: pin lineage/adoption to the manifest version seen; Read adopts only mode: handoff manifests; header wording for non-lineage authors).

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

- 2026-09-22: answer 48 (a) — build from plan 00–03 as written. dispatch: implementer opus — hook code in context-guard (gate re-injection); fable signal (code that gates) → fable unavailable in this session, fallback opus, recorded
- impl r0 DONE_WITH_CONCERNS a69452d (opus): lib_context manifest_sha/owned_version/lineage_of/linked_lineage; new hooks/lineage.py (SessionEnd clear link pinning an owned version; PostToolUse Read adoption of mode: handoff); rehydrate injects in full only an owned version, else a foreign header; hooks.json; 38 tests (fail on main 12F/20E); checkpoint docs + README hooks sentence. Deviations: foreign header keeps dead-claim/unparseable/Next-withheld lines, drops mode_skill; author echoed only when a safe sid; fork lineage written once. OQ7 (teammate /clear) unverified. 47(c) makes the third-session guard + foreign header largely redundant; lineage link, Read adoption and version pin stay needed; F3b re-points paths. Fresh-process successor sees no mode_skill hint until it Reads the handoff.
- dispatch: reviewer opus — gates re-injection (fable signal; fable unavailable → opus, recorded)
- review r1 (opus) at a69452d: NEEDS_CHANGES. Seven Checks OK (context-guard 510); matchers verified against binary 2.1.278; probes: third-session overwrite, Read variants, stale links, garbage input all hold; cleared-record race safe (per-process key + update_state lock). Deviations judged sound.
  - [medium] handoff-format.md:17, checkpoint SKILL.md:119-133 — no stated source for the `session:` id, now the ownership key; a /clear successor copying the predecessor's id loses its own memory and hands its goal to a resumed predecessor. Pass: name $CLAUDE_CODE_SESSION_ID (never the replaced manifest's id); ideally the mark step verifies it.
  - [low] lineage.py:71-81 hash the Read's content, not the file now; [low] :65 basename before realpath (symlink target Read never adopts, fails safe); [low] handoff-format.md:145-149 foreign header carries check lines; [low] operator-playbook.md:112-113 unqualified "re-injected".
- dispatch: implementer opus — fix round 1 (resume, tier kept)
