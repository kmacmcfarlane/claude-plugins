#!/usr/bin/env python3
"""SessionStart: inject the rehydration manifest — "you forgot everything, but
this is what you were working on, and these are the scrolls we saved."

Current repo state outranks the manifest: when the manifest lists `items:`,
each id the work-item store now has done, dropped or missing is named as a
DEAD CLAIM; when HEAD has moved past the recorded `head` (store-only commits
excluded) or diverged from it, the `## Next` body is withheld, not warned.

The manifest (HANDOFF.md, spec: skills/checkpoint/references/handoff-format.md)
is AUTHORED by the checkpoint skill, never synthesized here: intent is a
snapshot only its author can write. This hook adds the live part — age, commit
drift, dirty count — and labels it FRESH / AGED / STALE / LANDED. The label
and the Next withhold read the same ancestry check (head_state), so a manifest
whose Next is withheld is never labelled FRESH.

Tiers by source:
  compact          full manifest + the ledger tail (reasoning survives)
  resume           full only if the manifest changed or the repo moved since
                   the last injection (state manifest.sha); else header
  startup / clear  header only (~120 tokens), labelled if stale
No manifest and nothing to say -> {} (silent).

Budget: total additionalContext <= 9,000 chars, under the harness's single
10,000-char cap (overflow would be replaced by a file stub, silently dropping
the mandatory tiers). Trim order: the frontmatter `items:` list, Scrolls, then
Aware-of, never Doing/Goal/Read-in-full.

Never exits non-zero: the staleness checks degrade to the plain manifest on
any internal error, and anything else degrades to {}.
"""
import glob, hashlib, json, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import ledger

CAP = 9000
LEDGER_BUDGET = 2500
MAX_ITEMS = 50
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*")
STORE_EXCLUDE = ("--", ".", ":!.claude-sandbox/work")
_FM_CLOSE = re.compile(r"^[ \t]*---[ \t]*$", re.M)
_ITEMS_RE = re.compile(r"^items:[^\n]*\n(?:[ \t]*-[^\n]*\n)*", re.M)
_git_hung = []


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
    {rec, cur, known, ancestor, n} (n = code commits rec..HEAD, store-only
    commits excluded; None when unknown), or None when there is no recorded
    head, git fails, or git hung. Never raises."""
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
        n = git(top, "rev-list", "--count", f"{rec}..HEAD", *STORE_EXCLUDE) if known else None
        if _git_hung:
            return None
        n = int(n) if n and n.isdigit() else None
        return {"rec": rec, "cur": cur, "known": known, "ancestor": ancestor, "n": n}
    except Exception:
        return None


def divergence(hs):
    """Why the recorded head no longer describes HEAD by ancestry, or None."""
    if not hs:
        return None
    if not hs["known"]:
        return "recorded head not found locally"
    if not hs["ancestor"]:
        return "recorded head is not an ancestor"
    return None


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


def liveness(fm, hs):
    """(label, reason or None). Reads the same head_state as the Next withhold:
    a recorded head missing locally or not an ancestor of HEAD (rewound,
    diverged) is AGED with that reason, never FRESH."""
    if is_landed(fm):
        return "LANDED", None
    age_h = None
    try:
        t = time.strptime(fm.get("written", "")[:19], "%Y-%m-%dT%H:%M:%S")
        age_h = (time.time() - time.mktime(t)) / 3600
    except Exception:
        pass
    drift = hs["n"] if hs else None
    why = divergence(hs)
    if (age_h is not None and age_h > 7 * 24) or (drift is not None and drift > 30):
        return "STALE", why
    if (age_h is not None and age_h > 24) or drift or why:
        return "AGED", why
    return "FRESH", None


def _trim_items(body):
    """Collapse the frontmatter `items:` list to one line (dead claims have
    already been computed from it). Only the frontmatter is searched: an
    `items:` line in the body is prose and stays."""
    open_ = re.match(r"[ \t]*---[ \t]*\n", body)
    if not open_:
        return body
    close = _FM_CLOSE.search(body, open_.end())
    end = close.start() if close else len(body)
    m = _ITEMS_RE.search(body, open_.end(), end)
    if not m:
        return body
    return body[:m.start()] + "items: (trimmed — read the manifest file)\n" + body[m.end():]



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


def _scan_data_dir(base, prefix):
    names = sorted(os.listdir(base)) if os.path.isdir(base) else []
    return next((os.path.join(base, n) for n in names
                 if n.startswith(prefix)), None)


def _restore_statusline(marker):
    """The self-heal proper: marked settings file lost its statusLine -> put it
    back, read-modify-write."""
    m = json.load(open(marker))
    sp, cmd = m.get("settings"), m.get("command")
    if not sp or not cmd or not os.path.exists(sp):
        return None
    d = json.load(open(sp))
    if "statusLine" in d:
        return None
    d["statusLine"] = {"type": "command", "command": cmd}
    json.dump(d, open(sp, "w"), indent=2, ensure_ascii=False)
    return (f"context-guard: restored statusLine in {sp} — a settings write "
            "from a stale session had dropped it.")


def _migrate_legacy_statusline(legacy_marker, data):
    """The context system used to ship inside the claude-kit plugin, so an
    installed statusLine points at .../plugins/data/claude-kit-<mkt>/
    current-hooks/statusline.py — a path nothing maintains any more. Repoint it
    at this plugin's data dir, move the marker over, drop the legacy one."""
    m = json.load(open(legacy_marker))
    sp = m.get("settings")
    if not sp or not m.get("command") or not os.path.exists(sp):
        return None
    script = os.path.join(data, "current-hooks", "statusline.py")
    cmd = f"python3 {json.dumps(script)}"
    d = json.load(open(sp))
    cur = d.get("statusLine")
    stale = not isinstance(cur, dict) or \
        "/plugins/data/claude-kit-" in (cur.get("command") or "")
    if stale:
        d["statusLine"] = {"type": "command", "command": cmd}
        json.dump(d, open(sp, "w"), indent=2, ensure_ascii=False)
    json.dump({"settings": os.path.abspath(sp), "command": cmd},
              open(os.path.join(data, "statusline-installed.json"), "w"), indent=2)
    try:
        os.remove(legacy_marker)
    except OSError:
        pass
    if stale:
        return (f"context-guard: migrated statusLine in {sp} to the context-guard "
                "plugin data path (the context system moved out of claude-kit).")
    return ("context-guard: adopted the legacy claude-kit statusline marker; "
            "your custom statusLine entry was left alone.")


def heal_statusline():
    """A settings write from a session launched before the statusline install
    serializes that session's stale in-memory snapshot and drops the entry
    (live-fired 2026-08-31: a /plugin toggle in a day-old session clobbered
    it, and the gate silently fell back to inference). The installer leaves a
    marker in plugin data; when the marked settings file has lost statusLine,
    restore it read-modify-write. With no marker of our own, fall back to the
    legacy claude-kit marker and migrate it. Returns a systemMessage, or None.

    The SessionStart symlink command is registered before this hook, so
    current-hooks normally resolves in the new data dir already; if the two
    ever ran concurrently and this lost the race, the next session start
    completes the marker move (write order makes the migration resumable)."""
    try:
        cfg = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
        base = os.path.join(cfg, "plugins", "data")
        data = os.environ.get("CLAUDE_PLUGIN_DATA") or \
            _scan_data_dir(base, "context-guard-")
        if data and os.path.exists(os.path.join(data, "statusline-installed.json")):
            return _restore_statusline(os.path.join(data, "statusline-installed.json"))
        legacy = _scan_data_dir(base, "claude-kit-")
        if not data or not legacy:
            return None
        legacy_marker = os.path.join(legacy, "statusline-installed.json")
        if not os.path.exists(legacy_marker):
            return None
        return _migrate_legacy_statusline(legacy_marker, data)
    except Exception:
        return None


def adopt_fork_state(sid, transcript_path):
    """A fork/branch gets a new session id, orphaning the parent's ledger and
    staged /compact guidance (Bug B, live-fired 2026-08-31 via /branch). Two
    recovery strategies: copied parent records that still carry the parent
    sessionId (/branch), else matching a copied record uuid against sibling
    transcripts (--fork-session, which rewrites sessionIds)."""
    if os.path.exists(L.ledger_path(sid)) or not transcript_path \
            or not os.path.exists(transcript_path):
        return
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
        return
    if not parent:
        return
    try:
        pl = L.ledger_path(parent)
        if os.path.exists(pl):
            with open(L.ledger_path(sid), "w") as out:
                out.write(f"# ledger {sid} (adopted from parent {parent})\n")
                out.write(open(pl, errors="replace").read())
        pst = L.load_state(parent)
        if pst.get("custom_instructions"):
            st = L.load_state(sid)
            st.setdefault("custom_instructions", pst["custom_instructions"])
            L.save_state(sid, st)
    except Exception:
        pass


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    source = inp.get("source", "startup")
    if source == "fork":
        adopt_fork_state(sid, inp.get("transcript_path"))
    cwd = inp.get("cwd") or os.getcwd()
    path, top = manifest_path(cwd)

    parts, sysmsg = [], None
    st = L.load_state(sid)

    if path:
        text = open(path, errors="replace").read()
        fm = front_matter(text)
        sha = hashlib.sha1(text.encode()).hexdigest()[:12]
        hs = None if is_landed(fm) else head_state(fm, top)
        live, why = liveness(fm, hs)
        dirty = git(top, "status", "--porcelain") or ""
        header = (f"[context-guard rehydration] {live}{f' ({why})' if why else ''} "
                  f"manifest {path} "
                  f"(written {fm.get('written', '?')}, head {fm.get('head', '?')}, "
                  f"now {len(dirty.splitlines())} dirty file(s)).")
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
        full = source == "compact" or (
            source in ("resume", "fork") and (seen.get("sha") != sha or seen.get("top") != top))
        if full:
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
            sysmsg = f"Rehydrated from {live} manifest ({fm.get('written', '?')})."
        else:
            parts.append(header + " Read it before resuming its thread."
                         + "".join("\n" + c for c in (checks, moved) if c))
        st["manifest"] = {"sha": sha, "top": top}

    if source == "compact":
        lt = ledger.tail(sid, max_chars=LEDGER_BUDGET)
        if lt:
            parts.append("[context-guard ledger — this session's reasoning trail, "
                         "newest last]\n" + lt)
        ci = st.pop("custom_instructions", None)
        if ci:
            parts.append(f"The operator's own /compact guidance was: {ci}")

    L.save_state(sid, st)
    healed = heal_statusline()
    if healed:
        sysmsg = f"{sysmsg} {healed}" if sysmsg else healed
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
