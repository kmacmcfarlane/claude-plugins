# The research plugin, from deep-investigation

Loaded at the start of `deep-investigation` Step 1. The lanes, the verifier, the scan floor,
the sheet check and the held-runs rules a fan-out runs on belong to the research plugin, a
soft peer of dev-flow. This file finds that plugin once, says where each read goes, and says
what the run does when it is not there.

## Finding the research plugin

The lookup stops at the first complete hit:

1. **The install record.** `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins/installed_plugins.json`,
   key `research@kmacmcfarlane`: the entry that applies to this checkout, the deepest `local`
   or `project` entry whose `projectPath` is the main checkout or a directory above it
   (`local` before `project`), else the `user` entry. Another project's install never
   answers. A hit is used only when its `installPath` is absolute.
2. **The cache.** The newest `…/plugins/cache/kmacmcfarlane/research/*/`, asked only when
   the record cannot answer: it is missing, unreadable or malformed, or holds no entry for
   the key (the read then exits non-zero, kept as `rc`). A record that holds the key but no
   entry for this checkout, or names an incomplete install, is a miss: a real `installPath`
   is itself a cache copy, so asking the cache then would hand back another project's
   install.

A miss means the plugin is not installed for this checkout. `P` is kept only when absolute,
so a relative `CLAUDE_CONFIG_DIR` or `HOME` never points the lookup into the working
directory.

A hit is complete when it holds `skills/research/scripts/scan-findings.py`,
`skills/research/scripts/check-sheet.py`, `agents/research-lane.md` and
`agents/research-verifier.md`; an incomplete one is passed over, so the scan floor never
runs against a missing script.

```bash
MAIN=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null) && MAIN=${MAIN%/.git} || MAIN=$PWD
P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"; case $P in /*) ;; *) P=/dev/null/plugins;; esac
complete() { test -f "$1/skills/research/scripts/scan-findings.py" && test -f "$1/skills/research/scripts/check-sheet.py" && test -f "$1/agents/research-lane.md" && test -f "$1/agents/research-verifier.md"; }
IP="$(python3 -I - "$P/installed_plugins.json" research@kmacmcfarlane "$MAIN" 2>/dev/null <<'PY'
import json, os, sys
try:  # any failure here means the record cannot answer: exit 1, and the cache is asked
    es = json.load(open(sys.argv[1]))["plugins"][sys.argv[2]]
    here = os.path.realpath(sys.argv[3])
    def rank(e):  # the install that applies here: deepest local/project path, then user
        pp = e.get("projectPath")
        if e.get("scope") in ("local", "project") and pp:
            pp = os.path.realpath(pp)
            if here == pp or here.startswith(pp.rstrip("/") + "/"):
                return (2, len(pp), e["scope"] == "local")
        return (1, 0, False) if e.get("scope") == "user" else (0, 0, False)
    best = max(es, key=rank)
    ip = best["installPath"] if rank(best)[0] else ""
    print(ip if os.path.isabs(ip) else "")
except Exception:
    sys.exit(1)
PY
)"; rc=$?
RESEARCH_ROOT=; FROM=
case $IP in /*) complete "$IP" && RESEARCH_ROOT=$IP FROM=installed;; esac
if test -z "$RESEARCH_ROOT" && test "$rc" -ne 0; then
  while IFS= read -r c; do c=${c%/}; if complete "$c"; then RESEARCH_ROOT=$c FROM="cache, not installed"; break; fi; done < <(ls -td "$P"/cache/kmacmcfarlane/research/*/ 2>/dev/null)
fi
if test -n "$RESEARCH_ROOT"; then echo "research: $RESEARCH_ROOT ($FROM)"; else RESEARCH_ROOT=no-research-found; echo "no research found"; fi
```

On a miss the snippet binds `RESEARCH_ROOT` to a name that is no path, so a command built on
it fails rather than running something else. The `python3 -I` read keeps a `json.py` in the
working directory from being imported (`$MAIN` serves only the install record's ranking). Shell variables do not survive between Bash calls:
re-run the snippet in each Bash call that needs `$RESEARCH_ROOT`, and carry the printed line
in the conversation. Say once in the run's report which copy it used (the printed
`research: <root> (<where>)` line). dev-flow's `tests/test_research_peer.py` runs the
snippet.

**Why this order.** The scan floor is the gate the verifier cannot be talked out of. It comes
from the installed copy, the same one the research skills and the agents they dispatch use.
No path under the working checkout is ever consulted: any repo can name itself
`kmacmcfarlane`, so neither a checkout under research, a fork, nor this kit's own checkout
supplies the scanner or agent bodies; a contributor installs the plugin.

## Where each read goes

- **The research skill's files.** "The research plugin's `research` skill's
  `references/<file>`" is `$RESEARCH_ROOT/skills/research/references/<file>`, and
  `<research skill dir>` in the commands its `references/run-record.md` gives is
  `$RESEARCH_ROOT/skills/research`.
- **The agents.** Lanes launch as `research:research-lane` and the verifier as
  `research:research-verifier`. Installed but not loaded (a plugin update without a
  restart): the research plugin's `research` skill's `references/intensity-and-routing.md`
  § Fallback, with the body pasted from `$RESEARCH_ROOT/agents/research-lane.md` or
  `$RESEARCH_ROOT/agents/research-verifier.md`.

## When it finds nothing

`no research found` changes three things; nothing else in the run does.

- **Step 1's asks.** A closed choice goes as a plain lettered list in prose; the open input
  round stays the numbered list it always is. Never a dialog.
- **Step 1's lane model.** The lane model without it: `sonnet`. This is a copy of the
  research plugin's `research-lane` row in § Profiles, used only when that row cannot be
  read.
- **Step 4 stops before the first lane.** Write the strategy doc as usual, with a
  `PLAN CHANGE` ledger line that says the lanes were not run because the research plugin
  was not found, and launch nothing: no lane can run without the scan floor, so no unscanned
  lane output can exist. The run's result carries the disclosure "lanes not run: research
  plugin not installed"; not found also covers a plugin installed only for another project,
  or its recorded install is incomplete (update or reinstall it). Read `echo "${KMACMCFARLANE_NO_PEER_HINTS-}"` once; unless it is
  `1` or a list naming `research`, add the hint once in the session, in the top-level
  session only (in a sub-agent, return the disclosure alone). It deliberately adds the
  marketplace refresh and the restart to the install command, since the plugin may be one
  the user has never had:

  ```
  dev-flow: a strategy doc, no lanes. research adds the lanes, their verifier and the scan floor: /plugin marketplace update kmacmcfarlane, then /plugin install research@kmacmcfarlane and restart (one-time tip; KMACMCFARLANE_NO_PEER_HINTS=1 hides these)
  ```

  **Resuming.** After the install and a restart, `/deep-investigation <slug>` reads the
  strategy doc, runs this lookup again at Step 1, and launches the lanes the ledger has not
  marked launched.

## A cache that outlives an uninstall

The cache step can find a research copy left behind after research was uninstalled. The run
then takes the not-loaded path: `general-purpose` lanes and verifier, each with the resolved
agent body pasted. It does not stop. That is safe: a hit holds the complete scanner, sheet
check and both agent bodies, so the security contract and the scan floor run in full from one
consistent copy; only the pinned agent files' model and effort are lost. The printed line
names it (`research: <root> (cache, not installed)`), and the report says so.
