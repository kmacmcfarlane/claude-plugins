# Session name gate

Peers find a repo's librarian by its session name — in ListAgents and `/peers` — and
see only the registry's `name`: an AI-generated title never appears, and an unnamed
session shows a derived name such as `agents-61` that nobody can find. So `start` gets
the name right before the librarian takes requests. Pointed at from SKILL.md § Usage.

## The canonical form

`<repo> - librarian`, where `<repo>` is `basename "$MAIN"` (Rehydrate step 1) — for
example `claude-plugins - librarian`. One form, every repo: the repo name first so a
peer list sorts by repo, ` - librarian` spelled exactly so a peer can match it. Older
forms (`claude-kit librarian`, `mcfacehead-plugins librarian`) do not match.

`/rename` is a built-in Claude Code slash command: the skill cannot run it, only tell the
operator to type it.

## Reading this session's name

The session registry holds one file per running session,
`${CLAUDE_CONFIG_DIR:-~/.claude}/sessions/<pid>.json`, keyed by the pid of this session's
`claude` process (`CLAUDE_PID`); its `sessionId` names the session, `name` the name peers
see and `nameSource` where it came from (`user` after a `/rename`, `derived` otherwise).
Read only this session's file, and only when its `sessionId` equals
`CLAUDE_CODE_SESSION_ID`; never list the directory or print another session's data.

```bash
WANT="$(basename "$MAIN") - librarian"
python3 - "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/sessions/${CLAUDE_PID:-none}.json" "$WANT" <<'PY'
import json, os, sys
try: d = json.load(open(sys.argv[1]))
except (OSError, ValueError): d = {}
sid = os.environ.get('CLAUDE_CODE_SESSION_ID')
if not sid or not isinstance(d, dict) or d.get('sessionId') != sid: print('unobservable')
elif d.get('name') == sys.argv[2]: print('match')
else: print(f"mismatch: {d.get('name') or '(none)'} ({d.get('nameSource') or '?'})")
PY
```

## The gate (`start` only)

After Rehydrate, before the Idle turn:

- **`match`** — no gate; say nothing more than the name in the Rehydrate paragraph.
- **`mismatch`** — first look for a recorded decline (§ Keeping the name); one for this
  exact name lifts the gate: note "name kept by the operator" in the Rehydrate paragraph
  and continue. Otherwise a hard gate. End the turn with the current name and this line,
  exact text, on its own so it copies cleanly:

  ```
  /rename claude-plugins - librarian
  ```

  (with this repo's name), then "and tell me when done". Until then, start no new
  idle-turn dispatch; cycles already in flight — reviews, fix rounds, lands — continue,
  and a request that arrives meanwhile is still filed first (Critical), then waits. Each
  operator message re-runs the read; still a mismatch → show the line again, on every
  message, until it matches or the operator declines. A decline ("keep the name") is
  recorded (§ Keeping the name) and lifts the gate; never ask again for that name. This
  is the one `start` that ends its turn before the Idle turn — a wait on the operator,
  not an idle turn.
- **`unobservable`** — no registry, no pid, or a file that is not this session: a soft
  gate. Show the same line once, say the name cannot be checked, and continue into the
  Idle turn in the same turn; never ask again this session.

`intake` never gates: a request already in hand is filed first (Critical). After a
`/clear` the gate runs only on the next `start`.

## Keeping the name

A decline must outlive `/clear` and compaction, so it lives in the store, the way a
hold does (`idle-turn.md` § An operator hold): an item holding the operator's words and
one body line the gate can grep. It is closed at once — it holds nothing, so it never
enters the queue or the `hold:` line.

```bash
$WI add "keep session name: <current name>" -t chore -p 4 \
    --desc "Operator <date>, verbatim: '<their words>'." --ref "operator <date>"
printf 'name kept: %s\n' "<current name>" >> "$WI_ROOT/items/<id>.md"
$WI done <id> --note "operator kept the session name"
```

The gate's lookup, on a `mismatch` only, with the name the read printed:

```bash
grep -rqxF "name kept: <current name>" "$WI_ROOT" && echo kept   # kept → no gate
```

A decline covers the name it was given for: after a later `/rename` to anything but the
canonical form, the gate asks again.

## `status`

Read-only: run the read above and put the result in the expected-output paragraph —
"session name: `<name>` (canonical)", "session name: `<name>`; canonical is
`<repo> - librarian`" (plus "kept by the operator" when § Keeping the name records it),
or "session name: not observable". Never prints the `/rename`
line as a demand, never asks.
