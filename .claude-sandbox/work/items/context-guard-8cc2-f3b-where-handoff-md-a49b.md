---
id: context-guard-8cc2-f3b-where-handoff-md-a49b
title: "context-guard 8cc2-F3b: where HANDOFF.md lives (per-session memory + repo handoff file)"
type: feature
status: doing
priority: 2
deps:
  - context-guard-8cc2-f3a-re-inject-handoff-5126
parent: context-guard-turn-gate-8cc2
owner: unknown@360f41058e92
claimed: 2026-09-22T17:54Z
created: 2026-09-21
updated: 2026-09-22
---

Port plan .claude-sandbox/investigations/8cc2-turn-gate-port OQ1 — blocked on operator decision 47.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

answer 47 (operator 2026-09-22) — see 8cc2: per-session manifests only (C); checkpoint goals continue|handoff (land dropped); handoff manifest not under .claude-sandbox; final turn always prints the full HANDOFF.md path; handoff prints location + example continuation commands (`/compact ...`, and a `then <next-skill>` one when args name it). This changes the F3b design and the checkpoint skill: planner writes serial 04 of 8cc2-turn-gate-port folding it in after F3a lands.
- from H1 (9852) fix r1, 2026-09-22 — F3b input: lineage entries need a link timestamp so the mark step can tell a fork child's own rewrite from a still-running fork parent's rewrite after the fork.
- (from H1 r2) the same gap applies to adoption: a still-running handoff author's rewrite after the adopter's Read; record a link/adoption time.
dispatch: planner opus — serial 04 of 8cc2-turn-gate-port (plan mode, no worktree): fold answer 47(c) + the H1/H5/lineage-timestamp inputs

## Notes
- 2026-09-22 claimed by unknown@360f41058e92

## Plan result (opus, 2026-09-22) — serial 04_per-session-manifest.md in .claude-sandbox/investigations/8cc2-turn-gate-port/ (INDEX regenerated)
One manifest per session at ${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<safe_sid>/HANDOFF.md — a directory per session so the basename stays HANDOFF.md (keeps lineage's pre-filter and the operator's "full HANDOFF.md path" literal). A successor reaches it by the /clear link (H5, by lineage id), by a whole-file Read of the printed absolute path, or through wi handoff / the series for anything repo-durable; nothing is written into a repo. rehydrate gains resolve_manifest: own → inherited (newest lineage pin whose {owner, sha} still matches) → adopted → legacy → none. A new `top:` field records the manifest's repo. Re-pointed: rehydrate manifest_path/read_manifest, lineage's pin and Read-identity test, mark_checkpoint.stamp_manifest, read_list's top, H5's linked_clear_pred, the docs. Input (i): the lineage timestamp is no longer needed — per-session paths close H1's fork-parent/handoff-author residual by construction, and handoff-format's F3b caveat is deleted. Input (ii): owner == sid is subsumed by the path; the ownerless clause survives only on the legacy path. Also lands next_skill:, the one-line opener naming the Read tool, the always-printed absolute path with continuation commands, and goal options continue|handoff. Migration: a legacy repo manifest that is ours is copied into the store once, byte-identical; a foreign one gives one notice; nothing ever rewrites or deletes a repo HANDOFF.md. Features F3b-1 store+resolve (opus), F3b-2 mark on the own path (opus), F3b-3 migration (opus), F3b-4 checkpoint contract incl. two plugins (opus), F3b-5 the repo-visible channel (blocked on the decision below). Any build touching L.mark_checkpoint, context_warn.decide or hard_applies sends its reviewer to fable.
librarian decisions on the planner's questions: OQ2 (a) — the hook keeps reading `mode: land*`, the skill stops writing it. OQ3 (a) — no pruning of the manifest store for now; filed with the ledger as a follow-up. OQ4 (a) — keep the lineage `at` field (one optional value, useful for the migration window and diagnosis).
Concerns recorded: a handoff between two trees with DIFFERENT CLAUDE_CONFIG_DIRs now shares no file — the printed absolute path may not resolve in the reader's container (only the stub option would fix it; the work item is the workaround). A bystander session now sees nothing on SessionStart instead of a foreign header, which was also how an operator noticed a manifest existed (playbook line in F3b-4). 0509's stage-boundary handoff and librarian-mode's trackInHost manifest commit both change: the manifest leaves git.
decision 65: your answer 47 said a handoff manifest "should not go in .claude-sandbox, because not all consumers use claude-sandbox". The plan reads that as the per-session config-dir store, with nothing in the repo. Which did you mean? — (a) nothing in the repo; the manifest lives in the config dir and its absolute path is printed [recommended by the planner and the librarian]; (b) also drop a repo-root pointer stub — absolute path, author, timestamp, opener line, no body, so it can never be injected as memory; it gives a git-visible trace and something a non-Claude-Code consumer can find; (c) the whole manifest at <repo>/HANDOFF.md in handoff mode, which brings back the overwriting between sessions that 47 removed.
dispatch: plan reviewer opus — dev-cycle plan-review variant on serial 04
