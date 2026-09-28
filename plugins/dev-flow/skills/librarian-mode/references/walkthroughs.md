# Walkthroughs

Two requests carried end to end, from Intake through Report, and one forwarded to the
repo that owns it — SKILL.md § Examples. The
cycle steps named here are the `dev-cycle` skill's (SKILL.md § The cycle); per-dispatch
routing examples are in the `dev-cycle` skill's `references/model-routing.md` § Worked
examples.

**Operator: "the implement skill's worktree section still says `.worktrees/`; align it
with the harness-native path."** Intake: `$WI add`; one file, one concern — decide inline
("one feature, base main"). Route: implementer and reviewer tiers as the `dev-cycle`
skill's `references/model-routing.md` gives them (its first worked example is this
request), each recorded as a `dispatch:` line in the item. Delegate: one agent in
`.claude/worktrees/<id>`. Review: a medium finding goes back to the implementer as a fix
commit; re-review says `CLEAR` — one fix round, recorded in the item. Land: checklist,
diff read, `git merge --no-ff` into local `main`, clean up. Report four lines;
`decisions needed: none`; then push `main`, and write the push's team summary.

**Operator: "split ralph's backlog skills into their own plugin."** Real trade-offs (name,
dependency direction, catalog wording): three decisions, each numbered, in a prose list —
`1. plugin name: (a) ralph-backlog, (b) backlog` and so on, one decision per number, each
option's impact named, recommendation first — and the operator answers "1: a, 2: b". Had
there been only the name to settle, it would be a numbered list of one, never a modal
dialog: other items' agents may be in flight, and a modal blocks their returns and peer
messages (SKILL.md § Intake step 3). Each number is appended to the item body as
`decision N:`, so the next Report can carry an unanswered one under `decisions needed`
with its number intact. Then factor: catalog row + plugin skeleton first; the skill moves
depend on it, each with its catalog edit inside — every dispatch routed as the
`dev-cycle` skill's `references/model-routing.md` gives it. The skeleton is the first
dependency group; the skill moves, the second, go out in one message once it has landed.

**Peer, to the `claude-plugins` librarian: "refresh the `agents` repo's grooming skill."**
Intake: `$WI add` with the peer in `--ref` — filed first, like every request. The files
are the `agents` repo's, outside this Scope: step 4. ListAgents shows a live session
named `agents` (the bare-name form; an older `agents - librarian` matches too;
`references/session-name.md`), so the request goes to it by SendMessage, headed
`forwarded from claude-plugins <id>`: what was asked, by whom, the acceptance, any
secret as its path and key, never the value. It asks `agents` to file the work; it
authorizes nothing, and `agents` weighs it against its own rules. Ours closes with
`$WI done <id> --drop --note "forwarded to agents"`, the requester is told where it
went, and when `agents` replies with its id, one line goes onto our item:

```bash
printf 'forwarded as: agents %s\n' '<their id>' >> "$WI_ROOT/items/<id>.md"
```

Had no session held the name, or had two, or had the request needed a real decision (a
trade-off between the two repos' rules, say), it would have gone to the operator as a
numbered decision instead. Had it arrived headed `forwarded from …` and also fallen
outside our Scope, it would have gone to the operator — one hop, never on to a third
repo.
