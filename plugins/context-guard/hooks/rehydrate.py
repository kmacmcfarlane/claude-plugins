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
  compact          full manifest + the ledger tail (reasoning survives)
  resume           full only if the manifest changed or the repo moved since
                   the last injection (state manifest.sha); else header
  startup / clear  header only (one line, ~100-150 tokens with a
                   mode_skill), labelled if stale
Every tier's header names the manifest's `mode_skill:` (the standing mode to
re-enter first), unless the manifest is LANDED; a STALE manifest's mode is
named for confirmation, not as an order. Only a strict slash-command shape is
shown (MODE_SKILL_RE): the header speaks in the hook's voice, and the manifest
is repo-committed text.
No manifest and nothing to say -> {} (silent).

Those tiers apply only to a manifest that is OURS (is_ours). Ownership names a
manifest VERSION, {owner: its `session:`, sha: L.manifest_sha(raw text)}:
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
no body, no precedence preamble, no standing mode. The ledger tail and the
/compact guidance still inject on compact: they are this session's own.

Budget: total additionalContext <= 9,000 chars, under the harness's single
10,000-char cap (overflow would be replaced by a file stub, silently dropping
the mandatory tiers). Trim order: the frontmatter `items:` list, Scrolls, then
Aware-of, never Doing/Goal/Read-in-full.

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


def manifest_path(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel") or cwd
    for base in (os.path.join(top, ".claude-sandbox"), top):
        if base.endswith(".claude-sandbox") and not os.path.isdir(base):
            continue
        p = os.path.join(base, "HANDOFF.md")
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
        t -= (1 if z[0] == "+" else -1) * (hh * 3600 + mm * 60)
    return t


def manifest_age(fm, mtime=None, now=None):
    """(age in hours or None, reason or None). The `written:` stamp when it is
    readable and not ahead of now by more than STAMP_SKEW_S; else the file's
    mtime, with the reason the stamp was not trusted: `no stamp`, `stamp
    unreadable`, `stamp in the future`."""
    now = time.time() if now is None else now
    raw = fm.get("written")
    t = stamp_epoch(raw)
    if t is not None and t - now <= STAMP_SKEW_S:
        return max(now - t, 0) / 3600, None
    why = ("stamp in the future" if t is not None
           else "stamp unreadable" if isinstance(raw, str) and raw.strip()
           else "no stamp")
    age = (max(now - mtime, 0) / 3600) if isinstance(mtime, (int, float)) else None
    return age, why


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
            or stamp_why == "stamp in the future":
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


def trim(body, budget):
    if len(body) > budget:
        body = _trim_items(body)
    for sec in ("## Scrolls", "## Aware of"):
        if len(body) <= budget:
            break
        i = body.find(sec)
        if i >= 0:
            j = body.find("\n## ", i + 1)
            body = body[:i] + f"{sec}\n(trimmed — read the manifest file)\n" + \
                (body[j:] if j >= 0 else "")
    return body[:budget]


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


def adopt_fork_state(sid, transcript_path, version=None):
    """A fork/branch gets a new session id, orphaning the parent's ledger and
    staged /compact guidance (Bug B, live-fired 2026-08-31 via /branch): copy
    them over unless this session already has its own ledger. Also link the
    child to its parent (state `lineage`), once, even when the ledger exists:
    the parent first, pinning the manifest `version` on disk now only if it
    was the parent's own (L.owned_version, with the parent's state), then the
    parent's lineage. Returns the parent, or None."""
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
    No verified process (proc_key None): no link."""
    key = L.proc_key()
    if not key:
        return
    rec_sid = L.PROC_PREFIX + key
    if not isinstance(L.load_state(rec_sid).get("cleared"), dict):
        return
    box = []
    L.update_state(rec_sid, lambda p: box.append(p.pop("cleared", None)))
    c = box[0] if box else None
    if not isinstance(c, dict):
        return
    old, at = c.get("sid"), L._finite(c.get("at"))
    now = time.time() if now is None else now
    if not isinstance(old, str) or not old or old == sid or at is None \
            or L._future_skewed(at) or now - at > L.CLEAR_LINK_MAX_AGE_S:
        return
    lin = L.linked_lineage(old, c.get("manifest"), c.get("lineage"))
    L.update_state(sid, lambda st: st.__setitem__("lineage", lin))


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


def read_manifest(cwd):
    """(path, top, raw text or None). The raw text, read with
    errors="replace", is what manifest_sha hashes."""
    path, top = manifest_path(cwd)
    if not path:
        return None, top, None
    try:
        with open(path, errors="replace") as fh:
            return path, top, fh.read()
    except Exception:
        return None, top, None


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
    path, top, text = read_manifest(cwd)
    fm = front_matter(text) if path else {}
    version = manifest_version(text, fm) if path else None
    if source == "fork":
        adopt_fork_state(sid, inp.get("transcript_path"), version)
    elif source == "clear":
        try:
            link_clear(sid)
        except Exception:
            pass

    parts, sysmsg = [], None
    # Read-only snapshot: the git and store checks below are slow, so the
    # write-back at the end is a locked update of only the keys this hook owns.
    st = L.load_state(sid)
    seen_new = None

    if path:
        sha = version["sha"]
        ours = is_ours(st, sid, version)
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

        seen = st.get("manifest") or {}
        full = ours and (source == "compact" or (
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
            parts += [header, preamble] + ([checks] if checks else []) + \
                [trim(text, CAP - len(header) - len(preamble) - len(checks)
                      - LEDGER_BUDGET - 400)]
            sysmsg = (f"Rehydrated from {live}{f' ({why})' if why else ''} manifest "
                      f"({fm.get('written', '?')}).")
        else:
            parts.append(header + " Read it before resuming its thread."
                         + "".join("\n" + c for c in (checks, moved) if c))
        if ours:
            # `manifest` = the version last shown to this session as its own.
            seen_new = {"sha": sha, "top": top}

    if source == "compact":
        lt = ledger.tail(sid, max_chars=LEDGER_BUDGET)
        if lt:
            parts.append("[context-guard ledger — this session's reasoning trail, "
                         "newest last]\n" + lt)
        ci = st.get("custom_instructions")
        if ci:
            parts.append(f"The operator's own /compact guidance was: {ci}")

    def write_back(cur):
        if seen_new is not None:
            cur["manifest"] = seen_new
        if source == "compact" and "custom_instructions" in st \
                and cur.get("custom_instructions") == st.get("custom_instructions"):
            # Consumed once; a newer /compact guidance written meanwhile stays.
            cur.pop("custom_instructions", None)

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
