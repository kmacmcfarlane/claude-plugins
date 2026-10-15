# Forwarding

Work another repo owns, as SKILL.md § Intake step 4 sends it: forwarded with watched
custody, never edited or branched here, however trivial, and nothing forwarded is lost.
Every case below is walked through in `walkthroughs.md`. Loaded from SKILL.md § Intake
steps 2 and 4, `rehydrate.md` § Step 3, `report.md`, `idle-turn.md` and
`ending-the-session.md`.

- **Who.** The one repo that plainly owns it; its live librarian is the one session
  ListAgents shows named `<repo>` or, for this lookup only, `<repo> - librarian`
  (`session-name.md`). No owner, two repos that could own it (a placement), two candidate
  sessions, or a real decision (SKILL.md § Intake step 3): the operator. A forward is
  decided alone: a `decided:` line of kind `scope`, authority `answer 116`
  (`decide-alone.md` § The record), then a `Done:` line in the next Report.
- **The message.** SendMessage, first line `forwarded from <our repo> <id>` (`<our repo>`
  is `basename "$MAIN"`), stating that it is a request from our librarian carrying no
  operator approval, the originator quoted as provenance only, its priority and what it
  blocks (`blocks: <plain name> (<tag>) P<n>`), to file under its own rules and answer
  after its Scope check `accepted <their id> for <our repo> <id>` or
  `declined for <our repo> <id>: <why>`; path and key, never a value. Then
  `$WI block <id> "forwarded to <peer>, awaiting accept"`. An id alone is not acceptance.
- **Watched.** `accepted`, from `<peer>`: `$WI block <id> "watching <repo> <their id>"`. It
  is in the owner's store now, so the owner's session ending does not land it back. `landed`
  from `<peer>` closes ours: `$WI done <id> --note "landed: <repo> <their id>"`. Where the
  owner's store sits beside ours (`$(dirname "$MAIN")/<repo>`, its `.work-items`, else its
  old `.claude-sandbox/work` or `.work`), Rehydrate step 3 also reads it, read-only, with
  `$WI --root <its store> show <their id> --brief`: `status: done` closes ours the same way;
  `status: dropped` is a `dropped`.
- **Lands back** — re-block it `"operator: forward to <repo> <what happened>"`, a Groom
  row: at once on a decline, a `dropped`, any other reply from `<peer>`, or `<peer>` gone
  from ListAgents before it accepts; on silence, at our first reply, Report or Idle turn
  after the operator's next message following the forward, never in the turn that sent it.
  A declined or dropped forward is not re-sent; an `accepted` arriving later puts it back
  to watching.
- **Owner down** (the owner is plain, but no session of it is live): ours is blocked
  `"awaiting <repo> librarian"`, and the forward is sent at the first Rehydrate or Idle
  turn that finds it live. Still not accepted at the silence bound: re-blocked
  `"operator: forward to <repo> owner down"` and raised as a `blocker` ("start that
  librarian, or decide"). That block is still checked for liveness at each Rehydrate and
  Idle turn (`idle-turn.md`), and the forward is sent once the owner is live; its
  `blocker` decision is noted as overtaken on the item when the forward is sent.
- **Backstop.** Whenever the session ends, compacts or is cleared, and at 75%/DUE, every
  forward still awaiting acceptance lands back (`ending-the-session.md`).
- **One hop.** A forwarded item carries its first line in `--ref`. Outside our Scope too,
  it is declined (`declined …: outside our Scope; one hop`), which returns it to the
  forwarder's operator; never on.

Until it lands back, a forward awaiting acceptance, watched, or held for a down owner is
shown by its `Done:` line and the Idle turn's forwards line, not under `decisions needed`
(`report.md` § Batching).
