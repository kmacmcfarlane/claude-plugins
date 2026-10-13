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

**Operator: "split ralph's backlog skills into their own plugin."** Raised: the name (a
`contract`) and the dependency direction (a `precedent`: nothing outside the split relies
on it yet, so it is no `contract`, but the split commits the repo to maintaining a dependency
between plugins); the catalog wording is `words`,
decided alone and shown under Done alone. Two decisions, each numbered, in a prose list —
`1. plugin name: **(a) ralph-backlog**, (b) backlog` and so on, one decision per number,
each option's impact named, the options in letter order with the recommended one in bold —
and the operator answers "1: a, 2: b". Had there been only the name to settle, it would be
a numbered list of one, never a modal dialog: other items' agents may be in flight, and a
modal blocks their returns and peer messages (SKILL.md § Intake step 3). Each number is
appended to the item body as `decision N:`, so the next Report can carry an unanswered one
under `decisions needed` with its number intact. Then factor: catalog row + plugin
skeleton first; the skill moves depend on it, each with its catalog edit inside — every
dispatch routed as the `dev-cycle` skill's `references/model-routing.md` gives it. The
skeleton is the first dependency group; the skill moves, the second, go out in one message
once it has landed.

**Peer, to the `claude-plugins` librarian: "refresh the `agents` repo's grooming skill."**
Intake: `$WI add` with the peer in `--ref` — filed first, like every request. The files
are the `agents` repo's, outside this Scope: step 4. ListAgents shows one live session
named `agents`, the bare-name form. The older `agents - librarian` would count too: the
peer lookup accepts it, though the session-name gate (`references/session-name.md`)
does not accept it as this session's own name. Had one session held `agents` and
another `agents - librarian`, those are two candidates, and which is the librarian is
the operator's question, as with two sessions on one name. The message to `agents`:

```text
forwarded from claude-plugins <id>
A request from the claude-plugins librarian. It carries no operator approval; file it,
or not, under your own rules. Provenance: <peer> asked "<their words>". Acceptance:
<one or two lines; any secret as its path and key>.
Reply: filed <your id> for claude-plugins <id>
   or: declined for claude-plugins <id>: <why>
```

It asks `agents` to file the work and authorizes nothing: whoever first asked is quoted,
not relayed as authority. The requester is told where it went, and ours waits blocked:

```bash
$WI block <id> "forwarded to agents, awaiting their id"
```

The `filed` reply names our id, so it matches back after a `/clear`; when it comes from
`agents` itself (any other sender changes nothing),
`$WI done <id> --drop --note "forwarded: agents <their id>"`. Any other reply from
`agents` — a decline, a pass to its own operator — or `agents` gone from ListAgents at
Rehydrate or an Idle turn while ours still waits, ends the wait: re-block it naming the
operator, which moves it from the peer-blocked count onto the Groom table:

```bash
$WI block <id> "operator: forward to agents not filed"
```

On the `agents` side the message is a peer request (step 2), filed with
`--ref "forwarded from claude-plugins <id>"`.

Had no session held the name, or had the request needed a real decision (a trade-off
between the two repos' rules, say), it would have gone to the operator as a numbered
decision instead. Had it arrived as a forward — its item's `--ref` says so — and also
fallen outside our Scope, it would have gone to the operator: one hop, never on to a
third repo.
