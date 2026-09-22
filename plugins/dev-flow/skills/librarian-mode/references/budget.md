# Budget: the quota sense and the librarian store

Every librarian on one subscription spends from the same five-hour and weekly windows.
`scripts/quota_budget.py` measures them and prints the inputs a budgeted idle turn needs.
It decides nothing. It prints the numbers (used, velocity, allowed rate and reserve per
window, the binding window, the fresh-claim count) and `next_check`, and nothing else. The
mode and the concurrency cap N are chosen in F2's idle turn from those numbers, and that
integration has not landed yet. The reason is the librarian's decision on R1, recorded on
work item 9882: F2 owns the mode table and the N formula, and the agents policy is about to
change the librarian count that formula divides by. Computing N here would bake in a
formula that is about to change.

**Who owns what.** This file owns the mechanics: where the store lives, its schema, and how
the numbers are computed. The **values** belong to the `agents` repo's
`librarian-budget-policy` series (its item 8ad9): the reserve table, the claim TTLs and the
absent-signal pool. They are defaults until the operator ratifies them. A value changes
there first and is then copied into the constants at the top of the script, never the other
way round.

## Running it

```bash
python3 scripts/quota_budget.py            # from the skill dir; one JSON object on stdout
```

| Flag | Effect |
|---|---|
| `--session ID` | the session whose sensor record is read (default `$CLAUDE_CODE_SESSION_ID`, which Claude Code exports to its Bash tool) |
| `--repo NAME` | the claim's repo (default: basename of the main checkout, from `git rev-parse --git-common-dir`, so a worktree resolves to its repo) |
| `--read-only` | write nothing: no sample appended, no claim written |
| `--takeover` | overwrite a fresh claim held by another session (see § Claims) |
| `--stale-after S` | a reading older than S seconds counts as no signal (default 1800) |
| `--sink-dir DIR` | the claude-analytics samples dir (default: discovered, § Sources) |

Exit 0 with the result. Exit 1 when a store write failed: the result is still printed,
with an `errors` list, and a message goes to stderr. Exit 1 also on an internal error: a
minimal `{"v": 1, "signal": "none", "reason": "internal error", "next_check": 900}` is
printed, and the exception goes to stderr. Exit 2 on a bad argument. It never raises. A
poisoned input never reaches an error, though: an unreadable, oversized or deeply nested
JSON file reads as absent, and a bad line in a `.jsonl` file is skipped.

## The store

`CFG` is `${CLAUDE_CONFIG_DIR:-~/.claude}` (an empty value counts as unset). The store is
**per subscription**: the config dir is what one subscription's sandboxes share.

```
CFG/claude-kit/librarian/          0700
  samples.jsonl                    0600  fallback history, appended one line per call
  samples.lock                     0600  flock held across each append and prune
  intent.json                      0600  operator intent (written by the intent feature; read here)
  claims/<repo>.json               0600  one claim per repo; each librarian writes only its own
  claims/stale/                          tombstones (not read by the count)
```

Every JSON file is written to a unique temp file in the same directory and then
`os.replace`d, so a reader never sees a torn file. `samples.jsonl` takes one small
`O_APPEND` write per line. Once it passes 1 MiB it is rewritten, the same temp-and-rename
way, keeping 8 days and dropping any line that does not parse. Append and prune both hold
an exclusive `flock` on `samples.lock`, so a prune never loses a concurrent append.
`samples.jsonl` and `samples.lock` are opened without following a symlink: one planted at
either name fails the append as a store write error, and nothing outside the store is
created or written. Every store, lock, claim and sink data file is opened non-blocking and
used only if it is a regular file: a FIFO or other non-regular file never blocks the call,
fails a write as a store write error, and reads as absent. The script creates each directory it is missing with mode 0700, from
`claude-kit/` down. It also sets the directory it writes into to 0700 on every write
(`librarian/` and `claims/`), even when that directory already existed. Directories above
those, including an existing `claude-kit/`, keep their modes. The store holds percentages,
session ids and intent, never a settings value. The script never reads a settings file or
Claude Code's user-level state file.

### `samples.jsonl`

One line per call, on the fallback path only (§ Sources):

```json
{"v": 1, "at": 1789760000.0, "session": "<session id>",
 "five_hour": {"used_percentage": 23.5, "resets_at": 1789763600.0},
 "seven_day": {"used_percentage": 41.0, "resets_at": 1790019200.0}}
```

`at` is the sensor record's `rate_limits.at`, the moment the payload was read, not the
moment of the call. Lines from every librarian mix in one file. That is correct: the
windows are account-wide.

### `intent.json`

```json
{"mode": "away", "until": 1789790000.0, "set_by": "<session name>", "at": 1789760000.0}
```

`mode` is `present`, `away`, `done-for-the-day` or `vacation`. Spaces or underscores for
the hyphens are accepted, and so is any letter case. `until` is epoch seconds or ISO 8601.
An absent file, an unknown mode or a past `until` all read as `present`, the most
protective five-hour reserve. Only a librarian that heard the operator's own words writes
this file (the policy's first-hand rule). This script only reads it.

### `claims/<repo>.json`

```json
{"v": 1, "repo": "claude-plugins", "session_id": "<id>", "session_name": "<name>",
 "pid": 268, "pidDomain": "<domain>", "procStart": "<start>", "at": 1789760000.0,
 "in_flight": []}
```

`<repo>` passes through the sensor contract's safe-name rule; any other name becomes
`repo-<sha256 prefix>`. `session_name`, `pid`, `pidDomain` and `procStart` come from this
session's own registry file, `CFG/sessions/$CLAUDE_PID.json`, and only when that file's
`sessionId` is this session's. Otherwise they are `null`. The script writes `at` as the
heartbeat, and `in_flight` as a list of `{item, tier, since}`. It keeps any other field in
a claim of its own session, such as `demand`, `mode` or `hold_two_writers`, which the
idle-turn integration writes.

## Sources

- **The reading** is this session's sensor record, `CFG/statusline/sensor/<sid>.json`,
  whose `v: 1` shape the `statusline-hub` plugin writes (the sensor contract). Only
  `rate_limits.five_hour` and `seven_day` are read (`used_percentage`, `resets_at`), along
  with `rate_limits.at`.
- **The history** comes from the claude-analytics sampler's sink when it is live. That is
  a `samples/` directory under `CFG/plugins/data/claude-analytics-*/` (or `--sink-dir`)
  holding a line dated within `--stale-after`. The reader follows the sampler's *designed*
  schema, one line per render in `samples/YYYY-MM-DD.jsonl` carrying `ts` (epoch seconds
  or ISO 8601), `session_id` and the payload's `rate_limits`. The sampler is not built yet,
  so this path is tested only against synthetic lines. Only `YYYY-MM-DD.jsonl` files are
  read (never, say, `usage-cache-*.jsonl`). A line stamped more than 5 min in the future is
  dropped before anything else, so a skewed clock can neither keep the sink live nor win
  the reading. A live sink also supplies the
  reading when the session's own record is missing or stale, and then no sample is
  appended (the design's rule against sampling twice). With no live sink, the history is
  `samples.jsonl`, and this call's reading is appended to it.

## The numbers

- **Window identity.** Samples belong to one window when their `resets_at` values lie
  within 60 s of each other. A rate is never taken across a reset boundary.
- **Velocity** (percentage points per hour, per window). Within the current window the
  points are made monotone with a running maximum. A cumulative percentage cannot fall
  inside a window, so a lower reading is a stale payload. The rate runs to the newest
  point from the newest point that is at least the lookback old (2 h for the five-hour
  window, 6 h for the weekly), or from the window's oldest point when none is that old. It
  is `null` with fewer than two points or a span under 10 min.
- **Allowed rate** per window: `max(0, 100 − used − reserve) ÷ hours to reset`. The window
  with the smaller one is `binding`, and its rate is the top-level `allowed`. `headroom` is
  `100 − used − reserve` before the clamp. When it is ≤ 0 the window is spent down to its
  reserve.
- **Reserves** (percentage points, five-hour / weekly), from the intent:

  | Intent | 5h | Weekly |
  |---|---|---|
  | `present` | 25 | 15 |
  | `away` | 10 | 15 |
  | `done-for-the-day` | 0 | 15 |
  | `vacation` | 5 | 10 |

  away's five-hour reserve is 10, not the 5 that 1222's 00 gave in its F1 section: the
  agents policy resolved that series' F1/F5 disagreement that way.
- **No signal.** The result is `signal: "none"` with a `reason` when there is no session
  id or sensor record, the record's `v` is not 1, it has no rate limits (an API-key
  session, or no render yet), it lacks either window, it is older than `--stale-after`, it
  is stamped more than 5 min in the future, or a window has reset since it was read. The
  idle turn maps no signal to the policy's absent-signal pool (`N_total = 2`, estate-wide).
- **`next_check`** (seconds): with a signal, the soonest `resets_at` + 60 s, clamped to
  60–3600. With no signal, 900.

## Claims

The script writes or refreshes this repo's claim on every call (unless `--read-only`),
then counts fresh claims.

| Claim on disk | Action | `in_flight` |
|---|---|---|
| none | `created`, by an exclusive create | `[]` |
| a regular file of at most 1 MiB that does not parse as a JSON object | `replaced-unreadable` | `[]` |
| anything else it cannot read as a claim: not a regular file (a directory, a symlink it cannot read as a claim), over 1 MiB, or unreadable | `conflict` with `unusable: true`: not written, `--takeover` or no | — |
| this session's | `refreshed`, other fields kept (an identity field this call cannot read keeps its stored value) | kept |
| another session's, expired | `replaced-expired` | `[]` |
| another session's, fresh, same process (`pid`, `pidDomain`, `procStart` all equal and present: a `/clear`) | `takeover-same-process` | `[]` |
| another session's, fresh, with `--takeover` | `takeover` | `[]` |
| another session's, fresh, otherwise | `conflict`: not written | — |

A symlink at the claim path that reads as a claim is judged by its content like any other
claim; a write then replaces the link itself with a regular file and leaves its target
alone.

A takeover resets `in_flight`, per the policy's takeover rule: a new session's agents are
the only ones it can vouch for. A `conflict` is for the idle turn to judge: a restart it
may take over, or two live writers. It uses ListAgents to tell them apart, which a script
cannot call.

**Races.** A new claim is written in full to a temp file and then hard-linked into place.
`link` fails on an existing name, so when several sessions start at once exactly one
creates the claim. The others re-read it and report `conflict`. Every replace (refresh,
expiry, takeover) re-reads the file afterwards. If another session's claim is there, the
report is `conflict` with `lost_race: true` and `written: false`.

One window remains. A refresh reads its own claim and then replaces it. If a takeover lands
between that read and that replace, the refresh overwrites it. Its re-read then sees its own
claim, and the taker's post-replace re-read may already have passed. The taker's next call
sees a fresh foreign claim and reports `conflict`, so the clash surfaces within one call.
It is not prevented: closing the window needs a lock that every writer holds across its
read and its replace, and F2's two-writer hold is where that judgement lives.

**Freshness.** A claim is fresh while its `at` is within 2 h, or within 4 h when
`in_flight` is a non-empty list, because the librarian gets no turn while a long agent
runs. An unreadable `at` is never fresh. The count reads `claims/*.json` only, never
`claims/stale/`.

## The result

```json
{"v": 1, "now": 1789760000.0, "session": "<id>", "signal": "ok", "reason": null,
 "reading_at": 1789759990.0,
 "source": {"reading": "sensor", "history": "samples", "sink_dirs": []},
 "intent": {"mode": "present", "source": "default", "stored": null, "until": null,
            "set_by": null, "at": null, "expired": false},
 "reserves": {"five_hour": 25.0, "seven_day": 15.0},
 "windows": {"five_hour": {"used": 23.5, "resets_at": 1789763600.0, "hours_to_reset": 1.0,
                           "reserve": 25.0, "headroom": 51.5, "velocity": 6.2,
                           "velocity_points": 9, "velocity_span_s": 7210.0, "allowed": 51.5},
             "seven_day": {"...": "the same keys"}},
 "binding": "seven_day", "allowed": 0.41,
 "claims": {"repo": "claude-plugins", "path": "...", "written": true, "action": "refreshed",
            "previous": null, "fresh": 2, "fresh_in_flight": 1},
 "next_check": 3600}
```

With no signal, `windows`, `binding` and `allowed` are `null`. `intent`, `reserves` and
`claims` are still filled in. Readers ignore keys they do not know. A change of meaning to
an existing key bumps `v`.

## Not here yet

These are the policy's asks for later features, not built here: the mode table and the
pool arithmetic, the claim-flip detector and the two-writer hold, tombstoning,
`escalations/` markers, `claims.log.jsonl`, and the decaying weekly reserve.
