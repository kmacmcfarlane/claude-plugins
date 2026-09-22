---
id: context-guard-f3b-4-the-checkpoint-contr-0426
title: "context-guard F3b-4: the checkpoint contract (continue|handoff, printed path, commands, opener, next_skill)"
type: feature
status: done
priority: 1
parent: context-guard-8cc2-f3b-where-handoff-md-a49b
created: 2026-09-22
updated: 2026-09-22
closed: 2026-09-22
refs:
  - a49b
---

Plan of record .claude-sandbox/investigations/8cc2-turn-gate-port (04 § Features/Files row F3b-4, as amended by 05-08). Filed as a child by the librarian 2026-09-22 so it runs its own cycle. Acceptance per 04: every checkpoint's final message prints the absolute manifest path; a handoff also prints the commands; the three places listing the modes agree; next_skill: rides on every owned header. Brief also carries the lows listed in a49b: SKILL.md:213 four machine fields vs handoff-format's five; operator-playbook 'run from the repo'; handoff_path.py argv contract. Route opus/opus.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

## Notes
- 2026-09-22 claimed by unknown@bf9f9839222c

target: full context-guard-f3b-4-the-checkpoint-contr-0426 /home/rt/work/src/github.com/kmacmcfarlane/claude-plugins/.claude/worktrees/context-guard-f3b-4-the-checkpoint-contr-0426
dispatch: implementer opus — executable logic (rehydrate.py, stop_relay.py) + 8 files across two plugins; plan routes opus
agent: implementer aa20b5c90a21fc74c round 1
return: implementer DONE_WITH_CONCERNS 5c1f57a
changed: checkpoint SKILL.md, references/{handoff-format,operator-playbook,design-rationale}.md, hooks/rehydrate.py, hooks/stop_relay.py, hooks/tests/test_rehydrate.py, librarian-mode/references/ending-the-session.md, README.md
librarian on OQs: trim-budget low stays with F3b-3 (c3e1 carries it); size and the config-dir Write-permission question go to the reviewer.
dispatch: reviewer opus — rule 4, implementer tier
agent: reviewer a965bfca3fa096feb round 1
verdict: NEEDS_CHANGES round 1 at 5c1f57a
findings:
- [medium] checkpoint SKILL.md:198-216 + :53-95 — Step 4b Writes the manifest to ~/.claude/claude-kit/handoff/<sid>/HANDOFF.md, outside cwd and inside a protected .claude dir: prompts in default and acceptEdits, denied in dontAsk, classifier in auto; no allow rule or allowed-tools changes it. An unattended mid-turn checkpoint stalls at 4b outside bypass mode. Pass: route the store write through an allowlistable plugin Bash command, or at minimum document it.
- [low] SKILL.md ~5.9K tokens vs ~5000 bar (main already 5.2K) — move the argv contract and Step 7 example to references/.
- [low] SKILL.md:309 /compact guidance from Step 0 q3, which the unattended path skips.
- [low] SKILL.md:277-279 unlinked /clear "gets nothing" — except an old-layout repo file.
- [nit] rehydrate.py:1131-1132 comment "the land path".
notes: dropping land is operator answer 47 (04:14-15, 05:344); legacy-arm strip still has teeth; carried lows closed.
librarian decision on the medium (the obvious best way, within F3b-4's aim): the Write tool never targets the store. Step 4b drafts the manifest in the session scratchpad (no prompt); the mark step — already a plugin Bash command the checkpoint runs — gains an install option that copies the draft into L.manifest_path(sid) atomically (same own_store_manifest guard, 0700 dirs, temp+os.replace) and then stamps it. handoff_path.py stays write-free (05's property kept). Files in scope widened: hooks/mark_checkpoint.py and its tests. Playbook names the Bash command operators allowlist for unattended use.
dispatch: implementer opus — fix round 1 (resume)
return: implementer DONE_WITH_CONCERNS 7851aba
changed: + hooks/mark_checkpoint.py (--from install), hooks/tests/test_lineage.py
dispatch: reviewer opus — review r2 (resume)
verdict: NEEDS_CHANGES round 2 at 7851aba
findings:
- [medium] mark_checkpoint.py:220-278 install_draft — the installed file's mtime is always now, so the 30-min STAMP_WINDOW guard never fires on --from: a 3h-old draft (e.g. a draft Write refused after compaction) is sealed and printed as this checkpoint's manifest. Pass: judge age by the draft (refuse/warn not stamped when the draft is older than STAMP_WINDOW_S, or os.utime the installed file to the draft's mtime); test with an old draft.
- [low] :432-434 lone --from reads as sid "--from" — usage error like handoff_path.py.
- [low] ledger_pointer no longer records "P wrote HANDOFF.md" — install appends ledger.append(sid, "P", "installed HANDOFF.md", ref=target).
- [low] operator-playbook.md:150-163 — allow rules are literal prefix matches; add "run the command exactly as printed".
notes: round-1 medium closed end to end; install safety verified by hand; successor Read prompt acceptable (interactive).
dispatch: implementer opus — fix round 2 (resume)
return: implementer DONE eb400fa
dispatch: reviewer opus — review r3 (resume); last round before the cap
verdict: CLEAR round 3 at eb400fa
nits declined by the librarian: future-dated draft mtime (the Write tool always sets now); written: records install time (immaterial to tiers)
landed: 48a4bae
- 2026-09-22 done: 48a4bae
