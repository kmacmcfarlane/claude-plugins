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
drift, dirty count — and labels it FRESH / AGED / STALE / LANDED.

Tiers by source:
  compact          full manifest + the ledger tail (reasoning survives)
  resume           full only if the manifest changed or the repo moved since
                   the last injection (state manifest.sha); else header
  startup / clear  header only (~120 tokens), labelled if stale
No manifest and nothing to say -> {} (silent).

Budget: total additionalContext <= 9,000 chars, under the harness's single
10,000-char cap (overflow would be replaced by a file stub, silently dropping
the mandatory tiers). Trim order: Scrolls, then Aware-of, never Doing/Goal/
Read-in-full.
"""
import glob, hashlib, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L
import ledger

CAP = 9000
LEDGER_BUDGET = 2500


def git(cwd, *args):
    try:
        r = subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
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


def front_matter(text):
    """Flat `key: value` pairs; a key with an empty value followed by `- x`
    lines (the `items:` list) collects them as a list."""
    fm, key = {}, None
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            s = ln.strip()
            if s.startswith("- ") and key and isinstance(fm.get(key), list):
                fm[key].append(s[2:].strip())
            elif ":" in ln:
                k, v = ln.split(":", 1)
                key, v = k.strip(), v.strip()
                fm[key] = [] if v == "" else v
    return {k: ("" if v == [] else v) for k, v in fm.items()}


def claimed_items(fm):
    """`items:` as a block list, `[a, b]`, or `a, b` -> list of ids."""
    v = fm.get("items")
    if isinstance(v, str):
        v = [x for x in v.strip("[]").split(",")]
    return [x.strip().strip("'\"") for x in (v or []) if x.strip().strip("'\"")]


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


def item_status(root, ref):
    """Status of work item `ref` (full id or unique prefix), live or archived;
    'missing' when no file matches."""
    paths = sorted(glob.glob(os.path.join(root, "items", "*.md"))) + \
        sorted(glob.glob(os.path.join(root, "archive", "*", "*.md")))
    exact = [p for p in paths if os.path.basename(p)[:-3] == ref]
    hits = exact or [p for p in paths if os.path.basename(p).startswith(ref)]
    if len(hits) != 1:
        return "missing" if not hits else "ambiguous"
    try:
        st = front_matter(open(hits[0], errors="replace").read()).get("status")
        return st if isinstance(st, str) and st else "unknown"
    except Exception:
        return "missing"


def dead_claims(fm, top):
    """`DEAD CLAIM <id> (<status>)` for every id the manifest expected open that
    the store now has done, dropped or missing. [] when no store (silent)."""
    ids = claimed_items(fm)
    root = store_root(top) if ids else None
    if not root:
        return []
    out = []
    for i in ids:
        st = item_status(root, i)
        if st in ("done", "dropped", "missing"):
            out.append(f"DEAD CLAIM {i} ({st})")
    return out


def head_moved(fm, top):
    """None when the recorded head still describes the repo; else the one line
    that replaces the `## Next` body. Store-only commits (librarian chores under
    .claude-sandbox/work) do not count as movement."""
    rec = fm.get("head")
    if not isinstance(rec, str) or not rec:
        return None
    cur = git(top, "rev-parse", "--short", "HEAD")
    if not cur:
        return None
    known = git(top, "rev-parse", "--verify", "-q", rec + "^{commit}") is not None
    ancestor = known and subprocess.run(
        ("git", "-C", top, "merge-base", "--is-ancestor", rec, "HEAD"),
        capture_output=True, timeout=5).returncode == 0
    n = git(top, "rev-list", "--count", f"{rec}..HEAD", "--", ".",
            ":!.claude-sandbox/work") if known else None
    n = int(n) if n and n.isdigit() else None
    if ancestor and not n:
        return None
    return (f"Next withheld: head moved {n if n is not None else '?'} commits since "
            f"this manifest ({rec}..{cur}"
            + ("" if ancestor else ", recorded head is not an ancestor")
            + "); run wi prime and git log.")


def withhold_next(body, line):
    i = body.find("\n## Next")
    if i < 0:
        return body
    j = body.find("\n## ", i + 1)
    return body[:i] + f"\n## Next\n{line}\n" + (body[j:] if j >= 0 else "")


def liveness(fm, top):
    if (fm.get("mode") or "").startswith("land"):
        return "LANDED"
    age_h = None
    try:
        t = time.strptime(fm.get("written", "")[:19], "%Y-%m-%dT%H:%M:%S")
        age_h = (time.time() - time.mktime(t)) / 3600
    except Exception:
        pass
    drift = None
    if fm.get("head"):
        d = git(top, "rev-list", "--count", f"{fm['head']}..HEAD")
        drift = int(d) if d and d.isdigit() else None
    if (age_h is not None and age_h > 7 * 24) or (drift is not None and drift > 30):
        return "STALE"
    if (age_h is not None and age_h > 24) or drift:
        return "AGED"
    return "FRESH"


def trim(body, budget):
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
        live = liveness(fm, top)
        dirty = git(top, "status", "--porcelain") or ""
        header = (f"[context-guard rehydration] {live} manifest {path} "
                  f"(written {fm.get('written', '?')}, head {fm.get('head', '?')}, "
                  f"now {len(dirty.splitlines())} dirty file(s)).")
        moved = head_moved(fm, top) if live != "LANDED" else None
        dead = dead_claims(fm, top) if live != "LANDED" else []
        if len(dead) > 20:
            dead = dead[:20] + [f"(+{len(dead) - 20} more)"]
        checks = ("Claims this manifest makes that the work-item store now "
                  "contradicts (the store wins):\n" + "\n".join(dead)) if dead else ""
        if moved:
            text = withhold_next(text, moved)

        seen = st.get("manifest") or {}
        full = source == "compact" or (
            source in ("resume", "fork") and (seen.get("sha") != sha or seen.get("top") != top))
        if full:
            preamble = ("Precedence: current repo state (git log, the work-item "
                        "store) beats this manifest; this manifest and the ledger beat "
                        "any machine summary of the old conversation; CORRECTION/"
                        "REFUSED/DEFERRED lines beat your own recollection."
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


main()
