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

## Plan review round 1 — NEEDS_CHANGES (opus) on serial 04
Design sound, answer 47 read correctly, format compliant, every file:line citation checks out.
- [high] F3b-3's migration copy turns a SEALED foreign manifest into an unsealed own one: is_ours covers ownerless/pinned/adopted, all re-evaluated each SessionStart today; after the copy they never are. B adopts A's manifest, copies it, A rewrites with a CORRECTION → B reads its frozen copy forever (today it falls to the foreign header). And an operator's ownerless hand-written HANDOFF.md is copied by EVERY session, then re-dated FRESH and re-owned because the copy resets mtime inside STAMP_WINDOW_S. Pass: copy only when owner == sid; leave the other arms as a live re-sealed read.
- [high] the feature order leaves main with no rehydration for two merges: F3b-1 re-points resolve_manifest while the legacy arm is gated on F3b-3, so every existing (repo) manifest becomes unreachable; F3b-2 then stamps the store path while the skill still writes the repo path, so checkpoints break end to end. Pass: put the read-only legacy fallback in F3b-1 (copying stays in F3b-3).
- [medium] resolve steps 2/3 key on `owner` (frontmatter content) where they must key on the linked session id — manifest_path(pin.owner) can point at a third session's dir exactly during migration; manifest_adopted needs the store sid recorded from the path that was Read.
- [medium] adopt_fork_state is a fourth pin site, missing from the re-point table, and forces a call-order change in main (resolve_manifest must run after the link/adopt block) — F3b-1's fork acceptance cannot pass without it. mark_checkpoint.session_warnings also reads the repo file and would warn on every mark.
- [medium] the "F1 is disjoint" Confirmed Assumption is false: F1 touches checkpoint SKILL.md, the playbook, ending-the-session.md and README.md — F3b-4's own list.
- [medium] the cross-container workaround is asserted, not specified: wi handoff carries four fields and cannot hold Holds, In flight, Copy forward, Read in full or CORRECTION/REFUSED. Say which the handoff block must duplicate, or say the workaround is lossy.
- lows: contradictory fallback for an unusable top: (cwd toplevel vs "(head unverified)"); read_list's top mischaracterised; F3b-2's --path edits mark_checkpoint.main, which calls L.mark_checkpoint — either a separate entry point (keeps opus/opus) or the reviewer routes fable; the fable rule as phrased sets the reviewer, where the routing doc sets the implementer and rule 4 follows.
- reviewer answers the librarian's cross-container worry: NOT broken here — CLAUDE_CONFIG_DIR is unset, so the store is /home/rt/.claude/claude-kit/handoff/, the host-mounted dir every sandbox shares; a printed absolute path resolves in every sibling sandbox, and the librarian rehydrates from wi prime + git anyway. The break is a tree exporting its own config dir, another host, or a non-sandbox reader.
- reviewer on decision 65: the bystander loss is the strongest argument for (b) — after F3b a fresh session in a repo has no mechanism at all to learn a handoff is waiting, and the operator must paste a config-dir path they cannot guess. Also notes /home/rt/.claude/claude-kit/handoff/ already holds three flat <sid>.md files from an abandoned layout (no collision; say they are ignored).
- note: collapsing _claimable drops the "argv id ≠ env grants nothing" rule unless the store path is manifest_path(this_session(sid, environ)) — state it, or H1's closed finding reopens.
dispatch: planner opus — plan fix round 1 (resume); revision as serial 05 with Supersedes
