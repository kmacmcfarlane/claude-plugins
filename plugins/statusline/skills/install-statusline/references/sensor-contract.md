# Sensor and gauge contract (v1)

The canonical statement of the two files the status line shares with other tools. Both
directions are **soft**: each side works without the other. This file is the reference for
anyone reading the sensor record or publishing a gauge policy; the status line's own copy of
the shared pieces is `hooks/sensor.py`, and `hooks/tests/test_contract.py` checks it against
the publisher's copy whenever both plugins sit side by side in the source repo.

`CFG` below is `${CLAUDE_CONFIG_DIR:-~/.claude}`: the environment variable when it is set
**and non-empty**, else `~/.claude`, with `~` expanded.

## 1. Session id to file name (`safe_sid`)

Both sides name per-session files the same way:

- an empty or missing id becomes `unknown`;
- a string matching `[A-Za-z0-9_-][A-Za-z0-9._-]{0,127}` (whole string; the UUIDs Claude
  Code issues) is used unchanged;
- anything else (a path separator, a leading dot, `..`, over 128 characters, a non-string)
  becomes `sid-` plus the first 32 hex digits of the SHA-256 of its UTF-8 bytes (errors
  replaced; a non-string is hashed via its `repr`).

No id can name a path outside its directory.

## 2. The sensor record (status line → any reader)

- Path: `CFG/statusline/sensor/<safe_sid>.json`. The status line is its **only writer**. The
  directory is created 0700 and files are 0600.
- Write: a unique temp file in the same directory (`.<safe_sid>.<pid>.<hex>.tmp`, created
  exclusively), then `os.replace`. A reader never sees a torn file. There is no lock: with one
  writer none is needed. Each render merges from the record it read (a render without an
  `exact` block keeps the stored one; likewise `rate_limits`), and skips its write when the
  record on disk carries an `at` newer than its own (up to 60 s ahead), so an older render
  never regresses a newer one.
- Shape:

  ```json
  {"v": 1,
   "exact": {"pct": 42.0, "tokens": 420000, "window": 1000000, "at": 1789760000.0},
   "rate_limits": {"five_hour": {"used_percentage": 23.5, "resets_at": 1789763600.0},
                   "seven_day": {"used_percentage": 91.0, "resets_at": 1790019200.0},
                   "at": 1789760000.0}}
  ```

- `exact`: written only when the payload has a context window size of at least 1 and a
  finite used percentage, which is clamped to 0–100. `tokens` is the payload's
  `total_input_tokens` (an int ≥ 0), `window` its `context_window_size` (an int). `at` is the
  epoch time at which the payload was **read**, stamped before the write.
- `rate_limits`: every window in the payload whose name matches `[a-z0-9_]{1,40}` (at most
  16, in payload order), each with only `used_percentage` and `resets_at`, each only when it
  is a finite number; a `resets_at` more than 366 days out is dropped; a window left with
  neither field is skipped. A past `resets_at` is kept (the reader compares it with the
  clock). `at` as above.
- A record, or block, may be absent: a session that has not rendered yet has no file, and a
  render with neither block writes nothing.

## 3. The gauge policy (optional publisher → status line)

A context-window plugin may publish the thresholds it acts on, so the gauge colours by the
same policy. Today the publisher is the `context-guard` plugin of this marketplace, which is
why its directory name appears here; the status line never writes there.

- Path: `CFG/claude-kit/context-gate/gauge.json`. Shape:

  ```json
  {"v": 1, "writer": "context-guard",
   "thresholds": {"unit": "tokens_remaining", "interp": "linear_clamped",
                  "anchors": [{"window": 200000, "due": 70000, "hard": 40000},
                              {"window": 1000000, "due": 150000, "hard": 60000}]},
   "labels": {"due": "checkpoint DUE", "hard": "HARD gate"}}
  ```

- Per-session state, read-only here: `CFG/claude-kit/context-gate/<safe_sid>.json`. The status
  line reads only its `epoch` (an int ≥ 0; a missing key is 0). `checkpoint_epoch` is reserved
  and not rendered in v1. The publisher keeps these key names while `gauge.json` says v1.

**Publisher mode** holds for a render only when **both**: `gauge.json` parses with `v` an
integer equal to 1 and valid anchors, **and** this session's per-session state file exists.
The second condition proves the publisher's hooks ran in this session, so a `gauge.json`
left behind after an uninstall never switches the mode on. Otherwise the render is
**standalone**.

Reading is defensive; any of these makes the gauge standalone, never an error: a missing,
unreadable, oversized (over 1 MiB) or non-object file; `v` absent, not an integer, or not 1;
a `unit` other than `tokens_remaining` or an `interp` other than `linear_clamped` when
present; anchors that are not a list of 1–16 objects with integer `window` ≥ 1 and integer
`due`, `hard` ≥ 0, or that repeat a window. Labels are optional: a missing or non-string label
shows no word; a label is reduced to one printable line of at most 40 characters. An
unreadable state file, or a non-integer or negative `epoch`, keeps publisher mode but shows no
epoch.

### 3.1 The comparison rule

With `size` the payload's context window size and `tokens` its total input tokens:

```
left = max(size - tokens, 0)
colour = green   if left > due
         yellow  if left > hard      (and not green)
         red     otherwise
```

Both comparisons are strict: `left == due` is yellow, `left == hard` is red. In publisher mode
the word after the gauge follows the same bands: none when green, `labels.due` when yellow,
`labels.hard` when red, shown as `  ·  <label>`; the epoch appears as `  e<epoch>` right after
`left`. Standalone, there is no word and no epoch.

### 3.2 The interpolation, exactly

`due` and `hard` for a window come from anchors `(window, due, hard)` sorted by window:
the publisher's in publisher mode, else the defaults `(200000, 70000, 40000)` and
`(1000000, 150000, 60000)` (equal to the publisher's today, so the colours do not jump).

```
w = max(int(size or 0), 1)
if w <= a[0].window:            return a[0].due, a[0].hard
for each consecutive pair (lo, hi):
    if w < hi.window:
        f = (w - lo.window) / (hi.window - lo.window)        # float division
        return int(lo.due  + f * (hi.due  - lo.due)),         # int() truncates toward 0
               int(lo.hard + f * (hi.hard - lo.hard))
return a[-1].due, a[-1].hard     # at or beyond the last anchor
```

Linear between anchors, clamped outside. An anchor's own window returns that anchor's values
exactly.

## 4. Versioning

- Every record carries an integer `v`. Adding a field does not bump it: readers ignore
  unknown keys. Changing the meaning, unit or name of an existing field bumps it.
- A reader that sees a `v` it does not know treats the record as **absent**: the status line
  goes standalone; a sensor reader falls back to whatever it does without the sensor. It never
  misreads.
- A writer that bumps `v` writes both versions for one release when a reader that gates on it
  depends on the record.
