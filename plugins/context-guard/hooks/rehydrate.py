#!/usr/bin/env python3
"""SessionStart: inject the rehydration manifest — "you forgot everything, but
this is what you were working on, and these are the scrolls we saved."

Current repo state outranks the manifest: when the manifest lists `items:`,
each id the work-item store now has done, dropped or missing is named as a
DEAD CLAIM; when HEAD has moved past the recorded `head` (store-only commits
excluded) or diverged from it, the `## Next` body is withheld, not warned. A
rewind or divergence whose skipped commits are all store-only is no code drift:
the manifest still describes the code, so it reads FRESH with Next shown.

The manifest (HANDOFF.md, spec: skills/checkpoint/references/handoff-format.md)
is AUTHORED by the checkpoint skill, never synthesized here: intent is a
snapshot only its author can write. This hook adds the live part — age, commit
drift, dirty count — and labels it FRESH / AGED / STALE / LANDED. Age is the
`written:` stamp read as UTC (mark_checkpoint.py stamps it); a missing, garbled
or future one ages by the file's mtime and says why, and a future stamp is
never FRESH (manifest_age). The label
and the Next withhold read the same ancestry check (head_state), so a manifest
whose Next is withheld is never labelled FRESH.

Tiers by source:
  compact          full manifest + the ledger digest (reasoning lines of
                   every epoch ahead of commit pointers; ledger.digest)
  resume           full only if the manifest changed or the repo moved since
                   the last injection (state manifest.sha); else header
  clear, linked    full manifest + the PREDECESSOR's ledger digest, when
                   link_clear linked this session to a predecessor that
                   pinned the version on disk now (linked_clear_pred): the
                   /clear of a handoff is a continuation of the same work
                   (not for a LANDED manifest: that /clear is a fresh start)
  startup / clear  header only (one line, ~100-150 tokens with a
                   mode_skill, plus the Holds lines), labelled if stale: an
                   unlinked /clear, a pin of None, or a version rewritten
                   since the pin
Every tier's header names the manifest's `mode_skill:` (the standing mode to
re-enter first), unless the manifest is LANDED; a STALE manifest's mode is
named for confirmation, not as an order. Only a strict slash-command shape is
shown (MODE_SKILL_RE): the header speaks in the hook's voice, and the manifest
is repo-committed text.
No manifest and nothing to say -> {} (silent).

WHICH manifest is this session's memory is resolve_manifest's question, and
the answer is one file per session, at
${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<safe_sid>/HANDOFF.md
(L.manifest_path). First hit wins: own (that path exists - ours by the path,
no comparison), inherited (the newest lineage entry whose pin still seals its
session's store manifest), adopted (the same for manifest_adopted), legacy
(the repo file of the old layout, read LIVE and READ-ONLY - nothing here ever
writes, rewrites or deletes it), else none. A pin is a seal, not an address:
the linked session id says which file to read, the pin says whether it is
still the version promised, and a pin that no longer seals is skipped. Every
derived check (head, dead claims, dirty count, Read-in-full paths) runs against
the repo the manifest records in `top:`, else the cwd's toplevel (resolve_top).

Those tiers apply only to a manifest that is OURS. own, inherited and adopted
are ours by construction; the legacy repo file, which every session in the repo
can see, is still decided by is_ours on the bytes read this SessionStart, so an
unmigrated repo behaves exactly as it did before the store existed (plus one
legacy_notice line, once per session). Ownership names a manifest VERSION,
{owner: its `session:`, sha: L.manifest_sha(raw text)}:
  - no `session:` (hand-written): everyone's, as before this rule;
  - `session:` is this session: every version;
  - the exact version a lineage link pinned: the /clear predecessor
    (link_clear, from the `cleared` record lineage.py writes at
    SessionEnd(clear)) or the fork parent (adopt_fork_state), and their own
    lineage in turn - a link pins a version only if it was the linking
    session's own (L.owned_version), else nothing;
  - the exact `mode: handoff` version this session read in full
    (lineage.py, PostToolUse Read: state `manifest_adopted`).
Anything else - another session's manifest, or a later rewrite of a linked or
adopted one - gets one foreign header line on every source (foreign_header):
no body, no precedence preamble, no standing mode. The ledger digest and the
/compact guidance still inject on compact: they are this session's own.

Holds (`## Holds`, one line per hold with its end condition) ride on every
tier of a manifest that is ours: the full tiers inject the section untrimmed,
and the header-only tiers append its lines in compact form (holds_block,
bounded, plain text). A hold whose end condition names a time already past is
marked `expired? confirm`, never dropped. The foreign header carries none:
another session's holds are not this session's.

Budget: total additionalContext <= 9,000 chars, under the harness's single
10,000-char cap (overflow would be replaced by a file stub, silently dropping
the mandatory tiers). Trim order (trim): the frontmatter `items:` list,
Scrolls, Next, the Aware-of lines other than CORRECTION/REFUSED, then any
other unprotected section; never Doing, Goal, Holds, In flight, Read in full
or Copy forward.

A full injection of our own manifest also records its Read-in-full paths
(read_list.py): a whole-file Read marks each one, and the next prompt names
the unread ones once (context_warn.py).

SessionStart is also where the gauge policy is published, first thing
(L.publish_gauge: gauge.json, the threshold anchors and labels for the
statusline plugin; rewritten only when missing or different), and where
orphaned state-dir dotfiles are swept (L.sweep_stale: stale temp files, dead
sessions' lock files; once a day).

It never writes settings.json. The statusLine entry belongs to the statusline
plugin; this hook only reads it, to show a "moved to the statusline plugin"
notice at most once a week while an entry still runs context-guard's (or
claude-kit's) deprecated copy and that plugin is not installed
(statusline_notice).

Never exits non-zero: the staleness checks degrade to the plain manifest on
any internal error, and anything else degrades to {}.
"""
import glob, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import ledger
import read_list as RL

CAP = 9000
LEDGER_BUDGET = 2500
MAX_ITEMS = 50
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*")
STORE_EXCLUDE = ("--", ".", ":!.claude-sandbox/work")
_FM_OPEN = re.compile(r"[ \t]*---[ \t]*(\r?\n)")
_FM_CLOSE = re.compile(r"^[ \t]*---[ \t]*\r?$", re.M)
_ITEMS_RE = re.compile(r"^items:[^\n]*\n(?:[ \t]*-[^\n]*\n)*", re.M)
_git_hung = []
# `/name` or `/plugin:name`, then at most four short plain arguments; nothing
# else (no backticks, quotes, prose punctuation or control characters) passes.
MODE_SKILL_RE = re.compile(
    r"/[A-Za-z0-9][\w.-]*(?::[\w.-]+)?(?: [\w.:=/-]+){0,4}", re.ASCII)


def git(cwd, *args, ok=False):
    """stdout (or, with ok=True, whether it exited 0); None on any failure.
    After one timeout every later call returns None at once, so a hanging git
    costs one 5s wait, not one per call."""
    if _git_hung:
        return None
    try:
        r = subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                           text=True, timeout=5)
        if ok:
            return r.returncode == 0
        return r.stdout.strip() if r.returncode == 0 else None
    except subprocess.TimeoutExpired:
        _git_hung.append(True)
        return None
    except Exception:
        return None


_top_cache = {}


def git_top(cwd):
    """The cwd's git toplevel, else the cwd. Cached for this process (one
    SessionStart), because the legacy arm and resolve_top would otherwise pay
    for the same `rev-parse --show-toplevel` twice."""
    if cwd not in _top_cache:
        _top_cache[cwd] = git(cwd, "rev-parse", "--show-toplevel") or cwd
    return _top_cache[cwd]


def legacy_manifest_path(cwd):
    """The repo manifest of the OLD layout: <top>/.claude-sandbox/HANDOFF.md,
    else <top>/HANDOFF.md, plus the git toplevel. Read live and read-only:
    nothing here ever writes, rewrites or deletes it (8cc2-F3b). Named
    `legacy_` so no caller confuses it with L.manifest_path(sid), the store
    path of a session's own manifest."""
    top = git_top(cwd)
    for base in (os.path.join(top, ".claude-sandbox"), top):
        if base.endswith(".claude-sandbox") and not os.path.isdir(base):
            continue
        p = os.path.join(base, L.MANIFEST_NAME)
        if os.path.exists(p):
            return p, top
    return None, top


def _uncomment(s):
    """Drop a YAML end-of-line comment (`#` at the start or after whitespace)."""
    return re.sub(r"(^|\s)#.*$", "", s).strip()


def front_matter(text):
    """Flat `key: value` pairs; a key with an empty value followed by `- x`
    lines (the `items:` list) collects them as a list. `# comments` dropped."""
    fm, key = {}, None
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            s = ln.strip()
            if s.startswith("- ") and key and isinstance(fm.get(key), list):
                fm[key].append(_uncomment(s[2:]))
            elif ":" in ln:
                k, v = ln.split(":", 1)
                key, v = k.strip(), _uncomment(v)
                fm[key] = [] if v == "" else v
    return {k: ("" if v == [] else v) for k, v in fm.items()}


def claimed_items(fm):
    """`items:` as a block list, `[a, b]`, or `a, b` -> (ids, n_unparseable).
    Only id-shaped tokens count; the first MAX_ITEMS are read."""
    v = fm.get("items")
    if isinstance(v, str):
        v = v.strip().strip("[]").split(",")
    ids, bad = [], 0
    for x in v or []:
        x = x.strip().strip("'\"").strip()
        if not x:
            continue
        if ID_RE.fullmatch(x):
            ids.append(x)
        else:
            bad += 1
    return ids[:MAX_ITEMS], bad


def store_root(top):
    """The work-item store: WI_ROOT, else the repo's .claude-sandbox/work, else
    .work (wi's own fallback). None when no items/ dir exists."""
    env = os.environ.get("WI_ROOT")
    cands = [os.path.join(top, env) if env else None,
             os.path.join(top, ".claude-sandbox", "work"), os.path.join(top, ".work")]
    for c in ([cands[0]] if env else cands[1:]):
        if c and os.path.isdir(os.path.join(c, "items")):
            return c
    return None


def store_index(root):
    """[(id, alias, status)] for every live and archived item — wi's own
    resolution: exact id or alias first, then unique id prefix."""
    idx = []
    for p in sorted(glob.glob(os.path.join(root, "items", "*.md"))) + \
            sorted(glob.glob(os.path.join(root, "archive", "*", "*.md"))):
        try:
            with open(p, errors="replace") as fh:
                fm = front_matter(fh.read())
        except Exception:
            continue
        iid = fm.get("id") if isinstance(fm.get("id"), str) and fm.get("id") \
            else os.path.basename(p)[:-3]
        st = fm.get("status")
        idx.append((iid, fm.get("alias") or None,
                    st if isinstance(st, str) and st else "unknown"))
    return idx


def item_status(idx, ref):
    """Status of work item `ref` (id, alias or unique id prefix); 'missing'
    when nothing matches, 'ambiguous' when a prefix matches several."""
    hits = [e for e in idx if ref in (e[0], e[1])] or \
        [e for e in idx if e[0].startswith(ref)]
    if len(hits) != 1:
        return "missing" if not hits else "ambiguous"
    return hits[0][2]


def dead_claims(fm, top):
    """(dead, notes): `DEAD CLAIM <id> (<status>)` for every id the manifest
    expected open that the store now has done, dropped or missing, and a note
    line when entries were unparseable. ([], []) when no store (silent)."""
    ids, bad = claimed_items(fm)
    root = store_root(top) if ids or bad else None
    if not root:
        return [], []
    idx = store_index(root)
    out = []
    for i in ids:
        st = item_status(idx, i)
        if st in ("done", "dropped", "missing"):
            out.append(f"DEAD CLAIM {i} ({st})")
    notes = [f"items: {bad} unparseable entr{'y' if bad == 1 else 'ies'} skipped"] \
        if bad else []
    return out, notes


def head_state(fm, top):
    """The one ancestry check both the label and the Next withhold read:
    {rec, cur, known, ancestor, n, behind} (n = code commits on HEAD's side of
    rec...HEAD, behind = code commits on the recorded head's side, store-only
    commits excluded from both; None when unknown), or None when there is no
    recorded head, git fails, or git hung. Never raises."""
    try:
        rec = fm.get("head")
        if not isinstance(rec, str) or not rec:
            return None
        cur = git(top, "rev-parse", "--short", "HEAD")
        if not cur:
            return None
        known = git(top, "rev-parse", "--verify", "-q", rec + "^{commit}") is not None
        if _git_hung:
            return None
        ancestor = bool(known and git(top, "merge-base", "--is-ancestor", rec, "HEAD",
                                      ok=True))
        lr = git(top, "rev-list", "--left-right", "--count", f"{rec}...HEAD",
                 *STORE_EXCLUDE) if known else None
        if _git_hung:
            return None
        lr = (lr or "").split()
        behind, n = (int(lr[0]), int(lr[1])) \
            if len(lr) == 2 and all(x.isdigit() for x in lr) else (None, None)
        return {"rec": rec, "cur": cur, "known": known, "ancestor": ancestor,
                "n": n, "behind": behind}
    except Exception:
        return None


def divergence(hs):
    """Why the recorded head no longer describes HEAD by ancestry, or None.
    Not an ancestor, but with no code commits on the recorded side (the
    commits HEAD lacks are all store-only): the recorded code is still under
    HEAD, so None - zero code commits ahead too is no drift at all (FRESH),
    and N ahead reads as plain forward movement ("N commits since")."""
    if not hs:
        return None
    if not hs["known"]:
        return "recorded head not found locally"
    if not hs["ancestor"] and hs.get("behind") != 0:
        return "recorded head is not an ancestor"
    return None


def code_drift(hs):
    """Code commits on both sides of rec...HEAD (ahead + behind), or None."""
    if not hs or hs["n"] is None:
        return None
    return hs["n"] + (hs.get("behind") or 0)


def unverified_reason(top):
    """Why a recorded head could not be checked: `git unavailable` when git
    itself does not run (missing, failing, hung), else `head unverified` (git
    works but there is no HEAD to check against: not a repo, or no commits)."""
    if _git_hung or git(top, "--version") is None:
        return "git unavailable"
    return "head unverified"


def head_moved(hs):
    """None when the recorded head still describes the repo; else the one line
    that replaces the `## Next` body. Store-only commits (librarian chores under
    .claude-sandbox/work) do not count as movement."""
    if not hs:
        return None
    why, n = divergence(hs), hs["n"]
    if not why and not n:
        return None
    moved = "? commits" if n is None else f"{n} commit{'' if n == 1 else 's'}"
    if why and hs["known"] and n is not None and hs.get("behind") is not None:
        moved += f" ahead, {hs['behind']} behind"   # rewound or diverged
    return (f"Next withheld: head moved {moved} since this manifest ({hs['rec']}.."
            f"{hs['cur']}{', ' + why if why else ''}); run wi prime and git log.")


_UNSET = object()


def stale_checks(fm, top, live, hs=_UNSET):
    """(moved line or None, dead-claim lines, note lines). Any internal error
    degrades to (None, [], []): the plain manifest, as before these checks."""
    if live == "LANDED":
        return None, [], []
    try:
        if hs is _UNSET:
            hs = head_state(fm, top)
        return (head_moved(hs),) + dead_claims(fm, top)
    except Exception:
        return None, [], []


def withhold_next(body, line):
    i = body.find("\n## Next")
    if i < 0:
        return body
    j = body.find("\n## ", i + 1)
    return body[:i] + f"\n## Next\n{line}\n" + (body[j:] if j >= 0 else "")


def is_landed(fm):
    return (fm.get("mode") or "").startswith("land")


def mode_skill(fm):
    """The optional `mode_skill:` key: the slash command that re-enters the
    standing mode the session was running, or "" when absent, landed, or not
    exactly MODE_SKILL_RE (dropped silently: it rides on every tier's header)."""
    v = fm.get("mode_skill")
    if is_landed(fm) or not isinstance(v, str):
        return ""
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
    return v if len(v) <= 200 and MODE_SKILL_RE.fullmatch(v) else ""


STAMP_SKEW_S = 600
_STAMP_RE = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?"
    r"[ \t]*(Z|[+-]\d{2}:?\d{2})?", re.ASCII | re.I)


def stamp_epoch(value):
    """A `written:` stamp as epoch seconds, or None when absent or garbled.
    UTC: `Z`, an explicit offset, or no zone at all (the format's stamps are
    UTC; the mark step writes `%Y-%m-%dT%H:%M:%SZ`). A named zone (`CDT`) or
    any other text is garbled."""
    import calendar, datetime
    if not isinstance(value, str):
        return None
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].strip()
    m = _STAMP_RE.fullmatch(v)
    if not m:
        return None
    try:
        y, mo, d, h, mi = (int(x) for x in m.groups()[:5])
        t = calendar.timegm(datetime.datetime(y, mo, d, h, mi,
                                              int(m.group(6) or 0)).timetuple())
    except (ValueError, OverflowError):
        return None
    z = (m.group(7) or "Z").upper()
    if z != "Z":
        hh, mm = int(z[1:3]), int(z[-2:])
        if hh > 14 or mm > 59:
            return None
        t -= (1 if z[0] == "+" else -1) * (hh * 3600 + mm * 60)
    return t


def manifest_age(fm, mtime=None, now=None):
    """(age in hours or None, reason or None). The `written:` stamp when it is
    readable and not ahead of now by more than STAMP_SKEW_S; else the file's
    mtime, with the reason the stamp was not trusted: `no stamp`, `stamp
    unreadable`, `stamp in the future`. An mtime also ahead of now by more
    than STAMP_SKEW_S gives no age, and `, file time in the future` is added
    (liveness then reads it AGED: nothing trustworthy dates the file)."""
    now = time.time() if now is None else now
    raw = fm.get("written")
    t = stamp_epoch(raw)
    if t is not None and t - now <= STAMP_SKEW_S:
        return max(now - t, 0) / 3600, None
    why = ("stamp in the future" if t is not None
           else "stamp unreadable" if isinstance(raw, str) and raw.strip()
           else "no stamp")
    if not isinstance(mtime, (int, float)):
        return None, why
    if mtime - now > STAMP_SKEW_S:
        return None, why + ", file time in the future"
    return max(now - mtime, 0) / 3600, why


def liveness(fm, hs, unverified_why="git unavailable", mtime=None, now=None):
    """(label, reason or None). Reads the same head_state as the Next withhold:
    a recorded head missing locally or not an ancestor of HEAD (rewound,
    diverged) is AGED with that reason, never FRESH. A recorded head that could
    not be checked carries `unverified_why` (main passes unverified_reason():
    `git unavailable` or `head unverified`), so an unverified manifest never
    reads as plain FRESH. Drift counts code commits on both sides (ahead +
    behind): a HEAD 50 commits behind is as STALE as one 50 ahead.
    Age is manifest_age: a missing, garbled or future `written:` is aged by
    the file's `mtime` instead and names why in the reason, and a future
    stamp is never FRESH (a hand-typed stamp hours ahead once read FRESH)."""
    if is_landed(fm):
        return "LANDED", None
    age_h, stamp_why = manifest_age(fm, mtime, now)
    drift = code_drift(hs)
    why = divergence(hs)
    rec = fm.get("head")
    unverified = unverified_why if hs is None and isinstance(rec, str) and rec \
        else None
    reason = "; ".join(r for r in (why or unverified, stamp_why) if r) or None
    if (age_h is not None and age_h > 7 * 24) or (drift is not None and drift > 30):
        return "STALE", reason
    if (age_h is not None and age_h > 24) or drift or why \
            or (stamp_why and "in the future" in stamp_why):
        return "AGED", reason
    return "FRESH", reason


def _trim_items(body):
    """Collapse the frontmatter `items:` list to one line (dead claims have
    already been computed from it). Only the frontmatter is searched: an
    `items:` line in the body is prose and stays."""
    open_ = _FM_OPEN.match(body)
    if not open_:
        return body
    close = _FM_CLOSE.search(body, open_.end())
    end = close.start() if close else len(body)
    m = _ITEMS_RE.search(body, open_.end(), end)
    if not m:
        return body
    return body[:m.start()] + "items: (trimmed — read the manifest file)" + \
        open_.group(1) + body[m.end():]


TRIMMED = "(trimmed — read the manifest file)"
# Sections the trim never touches: what the successor must know or do first.
PROTECTED = ("doing", "goal", "holds", "in flight", "read in full", "copy forward")
# Lines a collapsed section keeps: the Aware-of tags that outrank everything
# else, and the hook's own Next-withheld line.
_KEEP_AWARE = re.compile(r"[ \t]*(?:[-*][ \t]*)?(?:CORRECTION|REFUSED)\b")
_KEEP_NEXT = re.compile(r"Next withheld:")


# `## Holds:` and `## Holds (2)` name the section `holds`; applied to the
# stripped heading (a CRLF manifest's headings end in `\r`).
_HEAD_TAIL = re.compile(r"\s*(?:\(.*)?[\s:]*$")


def _sections(body):
    """[[name, text]]: the text before the first `## ` line (name None: the
    frontmatter and any preamble), then one entry per `## ` section, its
    lower-cased name and its text heading included. Joined, the texts are the
    body again."""
    out = []
    for chunk in re.split(r"(?m)^(?=## )", body):
        if not chunk:
            continue
        name = _HEAD_TAIL.sub("", chunk.split("\n", 1)[0][3:].strip()).strip().lower() \
            if chunk.startswith("## ") else None
        out.append([name, chunk])
    return out


def _collapse(sec, keep=None):
    """Replace a section's body with the trimmed marker, keeping the lines
    `keep` matches; unchanged when that would not make it shorter."""
    head, _, rest = sec[1].partition("\n")
    kept = "".join(ln + "\n" for ln in rest.split("\n") if keep and keep.match(ln))
    new = f"{head}\n{kept}{TRIMMED}\n" + ("\n" if sec[1].endswith("\n\n") else "")
    if len(new) < len(sec[1]):
        sec[1] = new


def trim(body, budget):
    """Fit the body into `budget` chars. Order: the frontmatter `items:` list,
    Scrolls, Next (its withheld line kept), the Aware-of lines other than
    CORRECTION/REFUSED, then every other section not in PROTECTED and not
    one of those steps, last first (a stepped section keeps what its step
    kept). Doing, Goal, Holds, In flight, Read in full and Copy forward are
    never trimmed: only a body whose protected part alone exceeds the budget
    is cut at the end."""
    if len(body) <= budget:
        return body
    body = _trim_items(body)
    secs = _sections(body)

    def over():
        return sum(len(t) for _, t in secs) > budget

    steps = [("scrolls", None), ("next", _KEEP_NEXT), ("aware of", _KEEP_AWARE)]
    stepped = {name for name, _ in steps}
    for name, keep in steps:
        for sec in secs:
            if not over():
                break
            if sec[0] == name:
                _collapse(sec, keep)
    for sec in reversed(secs):
        if not over():
            break
        if sec[0] is not None and sec[0] not in PROTECTED \
                and sec[0] not in stepped:
            _collapse(sec)
    return "".join(t for _, t in secs)[:budget]


# ── Holds: what the successor must not do, and until when ──────────────────
HOLDS_MAX = 8            # lines the header tiers carry
HOLD_LINE_MAX = 240      # chars per line
HOLDS_BUDGET = 800       # chars for the whole header block
EXPIRED = "expired? confirm"
_CTRL = re.compile(r"[\x00-\x1f\x7f-\x9f\u061c\u2028\u2029\u200b-\u200f"
                   r"\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]")
_WHEN_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}(?::\d{2})?))?(?:[ \t]*(Z|[+-]\d{2}:?\d{2})\b)?",
    re.ASCII | re.I)
_HOLD_RE = re.compile(r"(?:\*\*)?HOLD\b", re.I)
_BULLET = re.compile(r"^[ \t]*[-*][ \t]+")


def _hold(ln):
    """A Holds-section line's entry when it is a hold (`HOLD …`, any case,
    bold allowed, bullet optional), else None: prose such as the spec's template sentence is not
    a hold."""
    s = _BULLET.sub("", ln).strip()
    return s if _HOLD_RE.match(s) else None


def hold_lines(text):
    """The `## Holds` section's entries, raw: each line that starts with
    `HOLD` (a leading `- ` or `* ` dropped); [] when the section is absent,
    `None`, or holds only prose."""
    for name, chunk in _sections(text or ""):
        if name == "holds":
            return [h for h in map(_hold, chunk.split("\n")[1:]) if h]
    return []


_UNTIL_RE = re.compile(r"(?<![^\W_])until(?::\s*|\s+)", re.I)


def hold_end(line):
    """A hold's end-condition clause: the text after its last `until` (then
    a space or `:`), else after its last ` — ` separator, else the whole
    line."""
    m = None
    for m in _UNTIL_RE.finditer(line):
        pass
    if m:
        return line[m.end():]
    j = line.rfind(" — ")
    return line[j + 3:] if j >= 0 else line


def hold_expired(line, now=None):
    """True when the hold's end condition is a time already past: the end
    clause LEADS with a UTC stamp (`2026-09-22T18:00Z`, an explicit offset,
    or no zone) or a bare date, which ends with that UTC day. A decision
    number or an event is no time, even one that mentions a date later in
    the clause: it never reads expired and stays in force until confirmed."""
    now = time.time() if now is None else now
    m = _WHEN_RE.match(hold_end(line).strip())
    if not m:
        return False
    date, clock, zone = m.groups()
    t = stamp_epoch(f"{date}T{clock or '23:59:59'}{zone or 'Z'}")
    return t is not None and t < now


def _mark(line, now):
    return f"{line} [{EXPIRED}: its end time has passed]" \
        if hold_expired(line, now) else line


def annotate_holds(text, now=None):
    """The manifest text with every expired hold in `## Holds` marked
    `[expired? confirm: …]` in place (the full tiers inject it this way)."""
    secs = _sections(text or "")
    for sec in secs:
        if sec[0] != "holds":
            continue
        lines = sec[1].split("\n")
        for k in range(1, len(lines)):
            s = _hold(lines[k])
            if s and hold_expired(s, now):
                cr = "\r" if lines[k].endswith("\r") else ""
                lines[k] = lines[k].rstrip() + f" [{EXPIRED}: its end time has passed]" + cr
        sec[1] = "\n".join(lines)
        return "".join(t for _, t in secs)
    return text


def holds_block(text, now=None):
    """The compact Holds block the header tiers append, or "" when the
    manifest records none. Plain text in the hook's voice: control and
    bidi characters stripped, each line bounded, at most HOLDS_MAX lines and
    HOLDS_BUDGET chars, the rest counted."""
    lines = [_CTRL.sub(" ", ln)[:HOLD_LINE_MAX] for ln in hold_lines(text)]
    if not lines:
        return ""
    out = ["Holds this manifest records (each stands until its end condition is "
           f"met; one marked `{EXPIRED}` names a time already past: ask the "
           "operator before acting against it or lifting it):"]
    used = len(out[0])
    for k, ln in enumerate(lines):
        row = "- " + _mark(ln, now)
        rest = len(lines) - k
        if k >= HOLDS_MAX or used + len(row) + 1 > HOLDS_BUDGET - 60:
            out.append(f"(+{rest} more hold{'' if rest == 1 else 's'} — read the "
                       f"manifest file)")
            break
        out.append(row)
        used += len(row) + 1
    return "\n".join(out)


def _parent_by_record_uuid(sid, transcript_path):
    """--fork-session rewrites every copied record's sessionId to the child
    (live-fired 2026-09-01: zero parent references survive), but the record
    uuids are copied verbatim — so the parent is the sibling transcript that
    contains this transcript's first conversation-record uuid."""
    first_uuid = None
    with open(transcript_path, errors="replace") as fh:
        for i, line in enumerate(fh):
            if i > 50:
                break
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") in ("user", "assistant") and d.get("uuid"):
                first_uuid = d["uuid"]
                break
    if not first_uuid:
        return None
    proj = os.path.dirname(transcript_path)
    sib = [p for p in glob.glob(os.path.join(proj, "*.jsonl"))
           if os.path.basename(p) != os.path.basename(transcript_path)]
    for p in sorted(sib, key=os.path.getmtime, reverse=True)[:40]:
        try:
            with open(p, errors="replace") as fh:
                for line in fh:
                    if first_uuid not in line:
                        continue
                    # substring alone is not identity: a transcript that merely
                    # QUOTED the uuid (tool output, pasted logs) matches too —
                    # live-fired 2026-09-01, adopting the wrong parent. Only a
                    # record whose own uuid field is this uuid is the parent copy.
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("uuid") != first_uuid:
                        continue
                    ps = d.get("sessionId")
                    if ps and ps != sid:
                        return ps
        except Exception:
            continue
    return None


# The status line moved to the statusline plugin, whose footer draws through
# the statusline-hub plugin. context-guard keeps its deprecated copy
# (hooks/statusline.py) for one release and never writes settings.json: it
# only notices, read-only, when a settings entry still runs a predecessor
# copy and the statusline plugin is not there - once it is, it registers the
# footer with the hub, and the hub's SessionStart takes the entry over.
NOTICE_EVERY_S = 7 * 24 * 3600
NOTICE_STAMP = ".statusline-moved-notice"
# The predecessor fingerprint: a command running
# <cfg>/plugins/data/{claude-kit,context-guard}-<mkt>/current-hooks/statusline.py
# (the older copies statusline-hub's classify() counts as the footer's own).
PREDECESSOR_RE = re.compile(
    r'\s*python3\s+"?[^"]*/plugins/data/(?:claude-kit|context-guard)-[^/"]+'
    r'/current-hooks/statusline\.py"?\s*')
NOTICE = ("context-guard: the status line moved to the `statusline` plugin: "
          "/plugin install statusline@kmacmcfarlane. This copy is removed in a "
          "later update.")


def _data_dirs(cfg, prefix):
    base = os.path.join(cfg, "plugins", "data")
    try:
        return [os.path.join(base, n) for n in sorted(os.listdir(base))
                if n.startswith(prefix) and os.path.isdir(os.path.join(base, n))]
    except OSError:
        return []


def _runs_predecessor(settings_path):
    d = L.read_json_file(settings_path)
    cur = d.get("statusLine") if isinstance(d, dict) else None
    cmd = cur.get("command") if isinstance(cur, dict) else None
    return isinstance(cmd, str) and bool(PREDECESSOR_RE.fullmatch(cmd))


def statusline_notice(now=None):
    """The one-line "moved" notice, or None. Read-only on settings: it fires
    when a settings file (user settings, or one a predecessor install marker
    names) still runs context-guard's or claude-kit's copy of the status line
    AND the statusline plugin is absent - any plugins/data/statusline-<mkt>
    dir means it is installed, and with it statusline-hub, whose SessionStart
    takes the entry over once the footer registers as its display hook, so
    context-guard stays silent. A statusline-hub-<mkt> dir alone does not
    count: the hub takes a predecessor entry over only once the statusline
    footer has registered. At most once per
    NOTICE_EVERY_S across all sessions (a stamp in the state dir); when the
    stamp cannot be written the notice is withheld, so it can never repeat
    every session. Never raises."""
    try:
        now = time.time() if now is None else now
        cfg = L._base_dir()
        if any(not os.path.basename(d).startswith("statusline-hub-")
               for d in _data_dirs(cfg, "statusline-")):
            return None
        stamp = os.path.join(L._state_dir(), NOTICE_STAMP)
        try:
            age = now - os.lstat(stamp).st_mtime
            if 0 <= age < NOTICE_EVERY_S:
                return None
        except OSError:
            pass
        cands = [os.path.join(cfg, "settings.json")]
        for d in _data_dirs(cfg, "context-guard-") + _data_dirs(cfg, "claude-kit-"):
            m = L.read_json_file(os.path.join(d, "statusline-installed.json"))
            sp = m.get("settings") if isinstance(m, dict) else None
            if isinstance(sp, str) and sp and sp not in cands:
                cands.append(sp)
        if not any(_runs_predecessor(sp) for sp in cands):
            return None
        return NOTICE if L._touch_stamp(stamp, now) else None
    except Exception:
        return None


def fork_parent(sid, transcript_path):
    """The session this fork/branch was copied from, or None. Two recovery
    strategies: copied parent records that still carry the parent sessionId
    (/branch), else matching a copied record uuid against sibling transcripts
    (--fork-session, which rewrites sessionIds)."""
    parent = None
    try:
        with open(transcript_path, errors="replace") as fh:
            for i, line in enumerate(fh):
                if i > 300:
                    break
                try:
                    ps = json.loads(line).get("sessionId")
                except Exception:
                    continue
                if ps and ps != sid:
                    parent = ps
                    break
        if not parent:
            parent = _parent_by_record_uuid(sid, transcript_path)
    except Exception:
        return None
    return parent if isinstance(parent, str) and parent else None


def adopt_fork_state(sid, transcript_path, cwd=None):
    """A fork/branch gets a new session id, orphaning the parent's ledger and
    staged /compact guidance (Bug B, live-fired 2026-08-31 via /branch): copy
    them over unless this session already has its own ledger. Also link the
    child to its parent (state `lineage`), once, even when the ledger exists:
    the parent first, pinning the version on disk now of the PARENT'S OWN
    manifest (own_manifest: its store file, else the legacy repo file) only if
    it was the parent's own (L.owned_version, with the parent's state), then
    the parent's lineage. Returns the parent, or None."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None
    has_ledger = os.path.exists(L.ledger_path(sid))
    has_lineage = "lineage" in L.load_state(sid)
    if has_ledger and has_lineage:
        return None
    parent = fork_parent(sid, transcript_path)
    if not parent:
        return None
    try:
        pst = L.load_state(parent)
        if not has_ledger:
            pl = L.ledger_path(parent)
            if os.path.exists(pl):
                with open(L.ledger_path(sid), "w") as out:
                    out.write(f"# ledger {sid} (adopted from parent {parent})\n")
                    out.write(open(pl, errors="replace").read())
            if pst.get("custom_instructions"):
                L.update_state(sid, lambda st: st.setdefault(
                    "custom_instructions", pst["custom_instructions"]))
        if not has_lineage:
            p, t = own_manifest(parent, cwd or os.getcwd())
            version = manifest_version(t) if p else None
            pin = version if L.owned_version(pst, parent, version) else None
            lin = L.linked_lineage(parent, pin, pst.get("lineage"))
            L.update_state(sid, lambda st: st.setdefault("lineage", lin))
    except Exception:
        pass
    return parent


def link_clear(sid, now=None):
    """SessionStart(clear): /clear ran SessionEnd(clear) for the old session
    in this same process (lineage.py wrote `cleared` on the process record),
    then regenerated the session id. Pop that record and, when it is recent
    (CLEAR_LINK_MAX_AGE_S) and names another session, set this session's
    lineage: the predecessor with the version it pinned, then its lineage.
    No verified process (proc_key None): no link. Returns the predecessor's
    session id when it linked, else None."""
    key = L.proc_key()
    if not key:
        return None
    rec_sid = L.PROC_PREFIX + key
    if not isinstance(L.load_state(rec_sid).get("cleared"), dict):
        return None
    box = []
    L.update_state(rec_sid, lambda p: box.append(p.pop("cleared", None)))
    c = box[0] if box else None
    if not isinstance(c, dict):
        return None
    old, at = c.get("sid"), L._finite(c.get("at"))
    now = time.time() if now is None else now
    if not isinstance(old, str) or not old or old == sid or at is None \
            or L._future_skewed(at) or now - at > L.CLEAR_LINK_MAX_AGE_S:
        return None
    lin = L.linked_lineage(old, c.get("manifest"), c.get("lineage"))
    L.update_state(sid, lambda st: st.__setitem__("lineage", lin))
    return old


def linked_clear_pred(st, pred, v):
    """The predecessor whose ledger a /clear successor inherits, or None: the
    session link_clear just linked (`pred`), when it is the head of this
    session's lineage and pinned exactly version `v` - the manifest on disk
    now, with an owner (a link never pins an ownerless one). A pin of None (a
    third session overwrote the manifest before the /clear) or a version
    rewritten since the pin gives None, and so the header. Only a safe
    session-id token is returned: it is echoed in the injected label."""
    lin = L.lineage_of(st)
    if not pred or not lin or lin[0]["sid"] != pred \
            or not L._SAFE_SID.fullmatch(pred):
        return None
    want = L._version(v)
    return pred if want is not None and lin[0]["manifest"] == want else None


def manifest_version(text, fm=None):
    """{owner, sha}: the manifest's `session:` (None when absent or not a
    plain string) and L.manifest_sha of the raw text."""
    fm = front_matter(text) if fm is None else fm
    owner = fm.get("session")
    return {"owner": owner if isinstance(owner, str) and owner else None,
            "sha": L.manifest_sha(text)}


def is_ours(st, sid, v):
    """The injection rule: an ownerless (hand-written) manifest is everyone's;
    otherwise only a version this session owns (L.owned_version)."""
    return not v["owner"] or L.owned_version(st, sid, v)


def read_text(path):
    """A file's raw text, read with errors="replace" - what manifest_sha
    hashes - or None when it cannot be read."""
    try:
        with open(path, errors="replace") as fh:
            return fh.read()
    except Exception:
        return None


def read_manifest(cwd):
    """(path, top, raw text or None) for the LEGACY repo manifest. The raw
    text, read with errors="replace", is what manifest_sha hashes."""
    path, top = legacy_manifest_path(cwd)
    if not path:
        return None, top, None
    text = read_text(path)
    return (path, top, text) if text is not None else (None, top, None)


def read_store_manifest(sid):
    """(path, raw text) of `sid`'s own per-session manifest, or (None, None).

    The file must exist AND really be `sid`'s (L.own_store_manifest, the test
    the mark step applies before it writes): the store directory is shared by
    every session reading this config dir, and this reader is the one gate
    between it and a session's memory - every caller (own_manifest's pin
    sites, resolve_manifest's own arm, _sealed) takes the file it returns on
    the path alone, with no owner comparison. A symlink planted at
    <sid>/HANDOFF.md, or at the <sid>/ directory above it, resolves out of
    that session's slot and is (None, None): no store manifest, so the caller
    falls through to its next arm exactly as it does for a missing file."""
    p = L.manifest_path(sid)
    if not os.path.exists(p) or not L.own_store_manifest(p, sid):
        return None, None
    text = read_text(p)
    return (p, text) if text is not None else (None, None)


def own_manifest(sid, cwd):
    """The manifest a PIN SITE reads for session `sid`: its own store file when
    it exists, else the legacy repo manifest. (path, text) or (None, None).

    All four pin sites resolve this way - SessionEnd(clear) (lineage.py), fork
    (adopt_fork_state), Read adoption (lineage.py) and the successor's
    inheritance (resolve_manifest). A site that resolved differently from the
    site that will read its pin would be a silent break."""
    p, t = read_store_manifest(sid)
    if p:
        return p, t
    path, _top, text = read_manifest(cwd)
    return (path, text) if path else (None, None)


def _sealed(author, pin):
    """(path, text) of `author`'s store manifest when its version on disk NOW
    is exactly the pin {owner, sha}; None otherwise. A pin is a seal, not an
    address: the linked session id says which file to read, and the pin only
    says whether it is still the version that was promised."""
    want = L._version(pin)
    if want is None or not isinstance(author, str) or not author:
        return None
    p, t = read_store_manifest(author)
    if not p or manifest_version(t) != want:
        return None
    return p, t


def resolve_manifest(st, sid, cwd):
    """Which manifest is this session's memory: (path, text, kind, author),
    first hit wins, else (None, None, None, None).

      own        L.manifest_path(sid) exists and is really that path (not a
                 planted link: read_store_manifest). Ours by the PATH - no sha
                 and no owner comparison; this is the common case.
      inherited  the newest lineage entry whose pinned {owner, sha} still is
                 the version of that ENTRY'S SESSION's store manifest. The
                 lookup is e["sid"], the session the link names, never the
                 pin's `owner` (frontmatter content, which during migration
                 can name a session that never wrote a store manifest).
      adopted    the same, for manifest_adopted["sid"] - the store manifest
                 this session read in full.
      legacy     the repo file of the old layout, read live and read-only.
                 Its tier is decided by today's is_ours on the bytes read this
                 SessionStart, so an unmigrated repo behaves as it always did.
      none       no manifest.

    A pin that no longer seals (a rewrite since the link, or an author with no
    store file) is SKIPPED and the search falls through - the fail-safe
    direction: a header or nothing, never another session's memory."""
    p, t = read_store_manifest(sid)
    if p:
        return p, t, "own", sid
    for e in L.lineage_of(st):
        got = _sealed(e["sid"], e.get("manifest"))
        if got:
            return got[0], got[1], "inherited", e["sid"]
    ad = (st or {}).get("manifest_adopted")
    if isinstance(ad, dict):
        got = _sealed(ad.get("sid"), ad)
        if got:
            return got[0], got[1], "adopted", ad["sid"]
    path, _top, text = read_manifest(cwd)
    if path:
        return path, text, "legacy", None
    return None, None, None, None


def resolve_top(fm, cwd):
    """The repo every derived check runs against (head_state, dead_claims,
    store_root, the dirty count, read_list.paths_from_manifest): the manifest's
    `top:` when it is a string naming an existing directory, resolved with
    realpath; else the cwd's git toplevel; else the cwd. `(head unverified)` is
    not an alternative to that fallback - it is the existing liveness reason
    for a resolved directory that is not a repo.

    `top:` is repo text, used verbatim: no `~` expansion and no shell, so a
    `top:` of `~` names nothing and falls back rather than pointing every
    derived check at the reader's home. The mark step writes an absolute
    path."""
    v = fm.get("top") if isinstance(fm, dict) else None
    if isinstance(v, str) and v.strip():
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1].strip()
        try:
            if v and os.path.isabs(v) and os.path.isdir(v):
                return os.path.realpath(v)
        except Exception:
            pass
    return git_top(cwd)


def legacy_notice(sid, path):
    """The one line that tells an operator the layout moved, appended once per
    session to whatever tier the legacy arm produced. A session that resolved a
    store manifest is never told about a repo file that is not its memory."""
    return (f"[context-guard rehydration] {path} is a repo manifest of the old "
            f"layout: read here, never written. The manifest becomes one file "
            f"per session - this session's own is {L.manifest_path(sid)} - once "
            f"a later update points the checkpoint skill's Step 4b there; until "
            f"then Step 4b still writes the repo file. Nothing rewrites or "
            f"deletes it: remove it when you choose.")


def foreign_header(label, path, owner):
    """The one line a session gets for a manifest that is not its own. The
    author id comes from repo text, so only a safe session-id token is
    echoed."""
    who = f"session {owner}" if isinstance(owner, str) \
        and L._SAFE_SID.fullmatch(owner) else "another session"
    return (f"[context-guard rehydration] {label} manifest {path}, written by "
            f"{who} (not this session). If the operator's opener names this "
            f"manifest, read it in full; otherwise it is another session's and "
            f"not your memory.")


def main():
    # First: the gauge policy does not depend on the input, and nothing below
    # may keep the statusline plugin from getting it. Never raises.
    L.publish_gauge()
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    source = inp.get("source", "startup")
    cwd = inp.get("cwd") or os.getcwd()
    pred = None
    # The link/adopt block runs FIRST: steps 2 and 3 of resolve_manifest read
    # `lineage` and `manifest_adopted`, so a fork child or a /clear successor
    # must be linked before its manifest is resolved.
    if source == "fork":
        adopt_fork_state(sid, inp.get("transcript_path"), cwd)
    elif source == "clear":
        try:
            pred = link_clear(sid)
        except Exception:
            pred = None
        if pred and L._SAFE_SID.fullmatch(pred):
            # The new ledger names where it came from (ledger continuity).
            ledger.successor_title(sid, pred)

    parts, sysmsg = [], None
    # Read-only snapshot: the git and store checks below are slow, so the
    # write-back at the end is a locked update of only the keys this hook owns.
    st = L.load_state(sid)
    path, text, kind, _author = resolve_manifest(st, sid, cwd)
    fm = front_matter(text) if path else {}
    version = manifest_version(text, fm) if path else None
    top = resolve_top(fm, cwd) if path else cwd
    seen_new = None
    notice = None
    # A LANDED manifest says the thread is done: its /clear is the fresh start
    # the land path asks for, so it keeps the header.
    clear_pred = linked_clear_pred(st, pred, version) \
        if source == "clear" and path and not is_landed(fm) else None
    # Its reasoning trail, read up front so the systemMessage names it only
    # when there is one to inject.
    clear_digest = ledger.digest(clear_pred, budget=LEDGER_BUDGET) \
        if clear_pred else ""
    summary_used = False
    reads_new = None     # this injection's Read-in-full list (read_list.py)

    if path:
        sha = version["sha"]
        # own/inherited/adopted were decided by resolve_manifest - by the path,
        # or by a pin that still seals the file. Only the legacy repo file,
        # which every session in the repo can see, still asks the F3a question.
        ours = True if kind != "legacy" else is_ours(st, sid, version)
        hs = None if is_landed(fm) else head_state(fm, top)
        rec = fm.get("head")
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        live, why = liveness(fm, hs, unverified_reason(top) if hs is None
                             and not is_landed(fm) and isinstance(rec, str) and rec
                             else "git unavailable", mtime)
        dirty = git(top, "status", "--porcelain") or ""
        label = f"{live}{f' ({why})' if why else ''}"
        header = (f"[context-guard rehydration] {label} "
                  f"manifest {path} "
                  f"(written {fm.get('written', '?')}, head {fm.get('head', '?')}, "
                  f"now {len(dirty.splitlines())} dirty file(s)).")
        ms = mode_skill(fm)
        if ms and live == "STALE":
            header += (f" The manifest names a standing mode, `{ms}`; it is STALE, "
                       f"so confirm with the operator before re-entering it.")
        elif ms:
            header += (f" The session was in a standing mode: re-enter it first "
                       f"with `{ms}`.")
        moved, dead, notes = stale_checks(fm, top, live, hs)
        if len(dead) > 20:
            dead = dead[:20] + [f"(+{len(dead) - 20} more)"]
        checks = "\n\n".join(b for b in (
            ("Claims this manifest makes that the work-item store now "
             "contradicts (the store wins):\n" + "\n".join(dead)) if dead else "",
            ("Manifest `items:` entries not checked against the store:\n"
             + "\n".join(notes)) if notes else "") if b)
        if moved:
            text = withhold_next(text, moved)
        holds = holds_block(text) if ours else ""

        if kind == "legacy" and not st.get("legacy_notice"):
            # Computed before the tiers so the trim pays for it: the budget
            # below is the whole injection's, and the notice is part of it.
            notice = legacy_notice(sid, path)
        seen = st.get("manifest") or {}
        full = ours and (source == "compact" or bool(clear_pred) or (
            source in ("resume", "fork") and (seen.get("sha") != sha or seen.get("top") != top)))
        if not ours:
            # Another session's manifest (or a version of it this session
            # never linked or adopted): never its memory. No body, no
            # precedence preamble, no standing mode; nothing that invites an
            # unrelated session to read, and so adopt, it.
            parts.append(foreign_header(label, path, version["owner"])
                         + "".join("\n" + c for c in (checks, moved) if c))
        elif full:
            preamble = ("Precedence: current repo state (git log, the work-item "
                        "store) beats this manifest; this manifest and the ledger beat "
                        "any machine summary of the old conversation; CORRECTION/"
                        "REFUSED/DEFERRED lines beat everything else, including your "
                        "own recollection."
                        + (" A goal line in a STALE manifest must be re-confirmed "
                           "with the operator before acting on it." if live == "STALE" else "")
                        + (" A machine compaction summary also exists for this "
                           "session; where they disagree, the manifest wins."
                           if st.get("compact_summary") else ""))
            # That sentence is for the injection right after the compaction
            # that wrote the summary: write_back pops it, so a later resume
            # or /clear-continued injection does not repeat it.
            summary_used = bool(st.get("compact_summary"))
            parts += [header, preamble] + ([checks] if checks else []) + \
                [trim(annotate_holds(text), CAP - len(header) - len(preamble) - len(checks)
                      - len(notice or "") - LEDGER_BUDGET - 400)]
            reads_new = RL.paths_from_manifest(text, top, cwd)
            sysmsg = (f"Rehydrated from {live}{f' ({why})' if why else ''} manifest "
                      f"({fm.get('written', '?')})"
                      + (f" and the ledger digest of predecessor {clear_pred}"
                         if clear_digest else "") + ".")
        else:
            parts.append(header + " Read it before resuming its thread."
                         + "".join("\n" + c for c in (holds, checks, moved) if c))
        if notice:
            parts.append(notice)
        if ours:
            # `manifest` = the version last shown to this session as its own.
            seen_new = {"sha": sha, "top": top}

    if source == "compact":
        # Digest by kind, not a raw tail: commit pointers once crowded the
        # reasoning out (13 of 17 injected lines), so R/C/D/X/U/Q from every
        # epoch come first and the P pointers fill what is left.
        lt = ledger.digest(sid, budget=LEDGER_BUDGET)
        if lt:
            parts.append("[context-guard ledger — this session's reasoning trail, "
                         "reasoning kept ahead of commit pointers, file order, "
                         "newest last]\n" + lt)
        ci = st.get("custom_instructions")
        if ci:
            parts.append(f"The operator's own /compact guidance was: {ci}")
    elif clear_digest and parts:
        # A linked /clear continues the predecessor's work: its reasoning
        # trail comes along (this session's own ledger is new and empty). The
        # full tier above reserved LEDGER_BUDGET + 400 for this block.
        parts.append(f"[context-guard ledger — predecessor {clear_pred}, by "
                     f"/clear: its reasoning trail, reasoning kept ahead of "
                     f"commit pointers, file order, newest last]\n" + clear_digest)

    def write_back(cur):
        if seen_new is not None:
            cur["manifest"] = seen_new
        if notice is not None:
            cur["legacy_notice"] = True
        if reads_new is not None:
            try:
                RL.record(cur, reads_new)
            except Exception:
                pass
        if source == "compact" and "custom_instructions" in st \
                and cur.get("custom_instructions") == st.get("custom_instructions"):
            # Consumed once; a newer /compact guidance written meanwhile stays.
            cur.pop("custom_instructions", None)
        if summary_used and cur.get("compact_summary") == st.get("compact_summary"):
            # Used once, by the full injection above; a newer summary stays.
            cur.pop("compact_summary", None)

    L.update_state(sid, write_back)
    L.sweep_stale(keep=sid)
    moved_note = statusline_notice()
    if moved_note:
        sysmsg = f"{sysmsg} {moved_note}" if sysmsg else moved_note
    if not parts and not sysmsg:
        print(json.dumps({})); return
    out = {}
    if parts:
        out["hookSpecificOutput"] = {"hookEventName": "SessionStart",
                                     "additionalContext": "\n\n".join(parts)[:CAP + 900]}
    if sysmsg:
        out["systemMessage"] = sysmsg
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({}))
    sys.exit(0)
