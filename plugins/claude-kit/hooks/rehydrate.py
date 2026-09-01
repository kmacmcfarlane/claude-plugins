#!/usr/bin/env python3
"""SessionStart: inject the rehydration manifest — "you forgot everything, but
this is what you were working on, and these are the scrolls we saved."

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
    fm = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


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


def heal_statusline():
    """A settings write from a session launched before the statusline install
    serializes that session's stale in-memory snapshot and drops the entry
    (live-fired 2026-08-31: a /plugin toggle in a day-old session clobbered
    it, and the gate silently fell back to inference). The installer leaves a
    marker in plugin data; when the marked settings file has lost statusLine,
    restore it read-modify-write. Returns a message for systemMessage, or None."""
    try:
        data = os.environ.get("CLAUDE_PLUGIN_DATA")
        if not data:
            cfg = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
            base = os.path.join(cfg, "plugins", "data")
            names = sorted(os.listdir(base)) if os.path.isdir(base) else []
            data = next((os.path.join(base, n) for n in names
                         if n.startswith("claude-kit-")), None)
        if not data:
            return None
        marker = os.path.join(data, "statusline-installed.json")
        if not os.path.exists(marker):
            return None
        m = json.load(open(marker))
        sp, cmd = m.get("settings"), m.get("command")
        if not sp or not cmd or not os.path.exists(sp):
            return None
        d = json.load(open(sp))
        if "statusLine" in d:
            return None
        d["statusLine"] = {"type": "command", "command": cmd}
        json.dump(d, open(sp, "w"), indent=2, ensure_ascii=False)
        return (f"claude-kit: restored statusLine in {sp} — a settings write "
                "from a stale session had dropped it.")
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
        header = (f"[claude-kit rehydration] {live} manifest {path} "
                  f"(written {fm.get('written', '?')}, head {fm.get('head', '?')}, "
                  f"now {len(dirty.splitlines())} dirty file(s)).")

        seen = st.get("manifest") or {}
        full = source == "compact" or (
            source in ("resume", "fork") and (seen.get("sha") != sha or seen.get("top") != top))
        if full:
            preamble = ("Precedence: this manifest and the ledger beat any machine "
                        "summary of the old conversation; CORRECTION/REFUSED/DEFERRED "
                        "lines beat everything including your own recollection."
                        + (" A goal line in a STALE manifest must be re-confirmed "
                           "with the operator before acting on it." if live == "STALE" else "")
                        + (" A machine compaction summary also exists for this "
                           "session; where they disagree, the manifest wins."
                           if st.get("compact_summary") else ""))
            parts += [header, preamble, trim(text, CAP - len(header) - len(preamble) - LEDGER_BUDGET - 400)]
            sysmsg = f"Rehydrated from {live} manifest ({fm.get('written', '?')})."
        else:
            parts.append(header + " Read it before resuming its thread.")
        st["manifest"] = {"sha": sha, "top": top}

    if source == "compact":
        lt = ledger.tail(sid, max_chars=LEDGER_BUDGET)
        if lt:
            parts.append("[claude-kit ledger — this session's reasoning trail, "
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
