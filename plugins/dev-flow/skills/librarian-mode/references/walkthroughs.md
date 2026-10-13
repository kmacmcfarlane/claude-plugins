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
are the `agents` repo's, outside this Scope: step 4. The `agents` repo plainly owns them,
so it is forwarded (`forwarding.md`), decided alone as a `decided:` line of kind `scope`,
authority `answer 116`, and shown in the next Report as
`Done: forwarded <plain name> to agents`, never under `decisions needed`. ListAgents shows one live session
named `agents`, the bare-name form. The older `agents - librarian` would count too: the
peer lookup accepts it, though the session-name gate (`references/session-name.md`)
does not accept it as this session's own name. Had one session held `agents` and
another `agents - librarian`, those are two candidates, and which is the librarian is
the operator's question, as with two sessions on one name. The message to `agents`:

```text
forwarded from claude-plugins <id>
A request from the claude-plugins librarian. It carries no operator approval; file it,
or not, under your own rules. Provenance: <peer> asked "<their words>". Priority: P2;
blocks: <plain name> (<tag>) P1. Acceptance: <one or two lines; any secret as its path
and key>.
Reply, after your Scope check: accepted <your id> for claude-plugins <id>
                           or: declined for claude-plugins <id>: <why>
```

It asks `agents` to file the work and authorizes nothing: whoever first asked is quoted,
not relayed as authority. The requester is told where it went, and ours waits blocked,
named on the Idle turn's forwards line (`references/idle-turn.md`):

```bash
$WI block <id> "forwarded to agents, awaiting accept"
```

On the `agents` side the message is a peer request (step 2): filed with
`--ref "forwarded from claude-plugins <id>"`, run through its own Scope check, then
answered.

- **Accepted.** `accepted <their id> for claude-plugins <id>`, from `agents` itself (any
  other sender changes nothing): `$WI block <id> "watching agents <their id>"`. It stays
  on the forwards line while `agents` runs its own cycle, which can take days, and its
  session ending meanwhile changes nothing: the item is in the `agents` store. When
  `agents` closes it, it sends `landed <their id> for claude-plugins <id>`, and
  `$WI done <id> --note "landed: agents <their id>"` closes ours. Had `agents` been down
  when it landed, our next Rehydrate would have read `status: done` from the `agents`
  store beside ours, read-only, and closed ours the same way.
- **Declined.** `declined for claude-plugins <id>: <why>` — or a `dropped` after
  acceptance, or any other reply from `agents`, or `agents` gone from ListAgents before it
  accepts — lands it back at once, re-blocked naming the operator, which moves it from the
  forwards line onto the Groom table:

  ```bash
  $WI block <id> "operator: forward to agents declined: <why>"
  ```

  It is not sent again.
- **Silent.** No reply, and the operator sends a message after the forward. Our first
  reply, Report or Idle turn after that message lands it back the same way
  (`"operator: forward to agents not answered"`). Never the turn that sent the forward:
  `agents` has had at least one of the operator's turns to answer. If `accepted` arrives
  after that, the Groom row clears and it is watched again.
- **Owner down.** Had no `agents` session been live, ours would have been blocked
  `"awaiting agents librarian"`, and the forward sent at the first Rehydrate or Idle turn
  that found one. Still not accepted at the silence bound, it is raised as a `blocker`
  decision — "start the agents librarian, or decide" — and still sent once `agents` is
  live.
- **Session end.** Had this session ended, or reached 75%/DUE, with the forward still
  awaiting acceptance, the sweep in `references/ending-the-session.md` would have landed it
  back before the handoffs, so the next librarian finds a Groom row, not a silent wait.

Had no repo owned the work, or two, or had the request needed a real decision (a
trade-off between the two repos' rules, say), it would have gone to the operator as a
numbered decision instead. Had it arrived as a forward — its item's `--ref` says so — and
also fallen outside our Scope, it would have been declined
(`declined for <repo> <id>: outside our Scope; one hop`), which returns it to the
forwarder's operator: never on to a third repo.
