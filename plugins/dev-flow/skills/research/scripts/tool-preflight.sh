#!/bin/sh
# Research tool preflight. POSIX sh. Read-only: it checks and never installs.
# Prints one TOOLS line; inside claude-sandbox one CHILD line (which child
# Dockerfile, if any, built this session's image, and how sure it is); then one
# MISSING line per absent package and one FIX line. Always exits 0. The output
# is data: tool names, package names and local paths, never fetched text.
# It never tells a session to create a project-level .claude-sandbox/Dockerfile:
# the nearest one wins, so a new project file would drop a parent one's tools.
# Limit: paths are word-split, so a search chain containing whitespace prints
# "CHILD unknown (path contains whitespace)" instead of a verdict. mountinfo
# escapes a space in a mount point as \040, which is not decoded here; such a
# mount point never matches, and the whitespace check reports those paths first.
# An unreadable mountinfo counts every level as visible.
# Test hooks (defaults in brackets): RESEARCH_PREFLIGHT_MOUNTINFO [/proc/self/mountinfo],
# RESEARCH_PREFLIGHT_OS_RELEASE [/etc/os-release],
# RESEARCH_PREFLIGHT_SANDBOX_MARKER [/opt/claude-sandbox/bin/entrypoint.sh].
# RESEARCH_PREFLIGHT_EXTRA adds tool names to check (for example sqlite3).
# Ported from agent-research's research-tooling series (02 § The script), with
# its round-3 review lows fixed: the matched Dockerfile is checked to still exist,
# nearer= needs a nearer chain position, and the $PWD fallback is physical.

WANT="pdftotext pdfinfo pdftoppm ${RESEARCH_PREFLIGHT_EXTRA:-}"
MOUNTINFO=${RESEARCH_PREFLIGHT_MOUNTINFO:-/proc/self/mountinfo}
OS_RELEASE=${RESEARCH_PREFLIGHT_OS_RELEASE:-/etc/os-release}
MARKER=${RESEARCH_PREFLIGHT_SANDBOX_MARKER:-/opt/claude-sandbox/bin/entrypoint.sh}

pkg() { # <tool> <manager> -> package name
  case "$1" in
    pdftotext|pdfinfo|pdftoppm) case "$2" in brew|pacman) echo poppler ;; *) echo poppler-utils ;; esac ;;
    sqlite3) case "$2" in apt) echo sqlite3 ;; *) echo sqlite ;; esac ;;
    *) echo "$1" ;;
  esac
}

host_kind() {
  [ "$(uname -s)" = Darwin ] && { echo brew; return; }
  id=; like=
  if [ -r "$OS_RELEASE" ]; then
    id=$(. "$OS_RELEASE"; echo "${ID:-}"); like=$(. "$OS_RELEASE"; echo "${ID_LIKE:-}")
  fi
  case " $id $like " in
    *" fedora "*|*" rhel "*|*" centos "*) echo dnf ;;
    *" debian "*|*" ubuntu "*) echo apt ;;
    *" arch "*) echo pacman ;;
    *) echo unknown ;;
  esac
}

# A level is visible when a mount point other than / equals it or contains it.
# The project is always mounted at its host path (claude-sandbox CS-LNCH-007),
# so the project level is always visible. Limit: an extra mount of a different
# host path onto this path also reads as visible.
visible() {
  [ -r "$MOUNTINFO" ] || return 0
  while read -r _a _b _c _d mp _rest; do
    [ "$mp" = / ] && continue
    case "$1/" in "$mp"/*) return 0 ;; esac
  done < "$MOUNTINFO"
  return 1
}

walk() { d=$1; while [ "$d" != / ] && [ "$d" != . ]; do echo "$d"; d=$(dirname "$d"); done; }

# The launcher's search chain: the project's parents, or, for a linked git
# worktree, its own levels then its main checkout's (claude-sandbox paths.Chain).
chain() {
  gd=$(git -C "$1" rev-parse --path-format=absolute --git-dir 2>/dev/null) || gd=
  cd_=$(git -C "$1" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || cd_=
  if [ -n "$gd" ] && [ "$gd" != "$cd_" ] && [ "$(basename "$cd_")" = .git ]; then
    up=$(walk "$(dirname "$cd_")")
    walk "$1" | while read -r d; do printf '%s\n' "$up" | grep -qxF "$d" || echo "$d"; done
    printf '%s\n' "$up"
  else
    walk "$1"
  fi
}

# claude-sandbox names a child image claude-sandbox-df-<slug(context)>-<h6>,
# h6 = sha256(dockerfile NUL context)[:6] (imagebuild.ImageSlug). For a
# <level>/.claude-sandbox/Dockerfile found by the default rule, context = <level>.
slug() { basename "$1" | tr 'A-Z' 'a-z' | sed 's/[^a-z0-9._-]/-/g'; }
h6() { printf '%s\000%s' "$1/.claude-sandbox/Dockerfile" "$1" | sha256sum | cut -c1-6; }

# Most-local visible setting of a top-level config key (the cascade merges
# scalars most-local-wins): prints "<value> <file>" or nothing.
cfg_key() { # <key> <levels...>
  k=$1; shift
  for l in "$@"; do
    c="$l/.claude-sandbox/config.yaml"
    [ -f "$c" ] || continue
    v=$(sed -n "s/^$k:[[:space:]]*\"\{0,1\}\([^\"#[:space:]]*\).*/\1/p" "$c" | head -1)
    grep -q "^$k:" "$c" && { echo "${v:-<empty>} $c"; return; }
  done
}

sandbox_child() { # prints: <verdict> <detail...>
  # The launcher passes the physical project path; match it when the variable is unset.
  p=${CLAUDE_SANDBOX_PROJECT_DIR:-$(pwd -P)}
  levels=$(chain "$p")
  ws=$(printf ' \t')
  case "$p$levels" in *["$ws"]*) echo "unknown (path contains whitespace)"; return ;; esac
  seen=; near=; near_i=; unseen=; i=0
  for lvl in $levels; do
    i=$((i + 1))
    if ! visible "$lvl"; then unseen=$lvl; break; fi
    seen="$seen $lvl"
    if [ -z "$near" ] && [ -f "$lvl/.claude-sandbox/Dockerfile" ]; then
      near="$lvl/.claude-sandbox/Dockerfile"; near_i=$i
    fi
  done
  img=
  if command -v docker >/dev/null 2>&1; then
    self=$(cat /etc/hostname 2>/dev/null)   # the container ID, unless --hostname was set
    img=$(timeout 5 docker inspect -f '{{.Config.Image}}' "$self" 2>/dev/null) || img=
  fi
  parent=${img%:run}
  if [ "$parent" = claude-sandbox ]; then echo "base-image -"; return; fi
  case "$parent" in
    claude-sandbox-df-?*-??????)
      want_slug=${parent#claude-sandbox-df-}; want_slug=${want_slug%-??????}; want_h=${parent##*-}
      i=0
      for lvl in $levels; do   # every chain level, mounted or not: the tag depends only on paths
        i=$((i + 1))
        [ "$(slug "$lvl")" = "$want_slug" ] && [ "$(h6 "$lvl")" = "$want_h" ] || continue
        f="$lvl/.claude-sandbox/Dockerfile"
        # Only a mounted level can show the file is gone; an unmounted one is taken as present.
        if visible "$lvl" && [ ! -f "$f" ]; then
          # The next launch resolves anew: by the default rule, from the nearest visible file.
          if [ -n "$near" ]; then echo "confirmed $f removed next=$near"; else echo "confirmed $f removed"; fi
        elif [ -n "$near" ] && [ "$near_i" -lt "$i" ]; then
          echo "confirmed $f nearer=$near"
        else
          echo "confirmed $f"
        fi
        return
      done
      echo "built-from-unseen $parent"; return ;;
  esac
  set -- $(cfg_key baseOnly $seen)
  case "${1:-}" in true|True|TRUE) echo "override baseOnly $2"; return ;; esac
  for k in dockerfileDir dockerfile; do
    set -- $(cfg_key $k $seen)
    [ -n "${1:-}" ] && [ "$1" != '<empty>' ] && { echo "override $k $2"; return; }
  done
  if [ -n "$near" ]; then echo "nearest-visible $near"; return; fi
  echo "unseen ${unseen:-/}"
}

ok=; missing=; pkgs=
if [ -n "${CLAUDE_SANDBOX_VERSION:-}" ] || [ -x "$MARKER" ]; then
  env=sandbox; mgr=apt
else
  mgr=$(host_kind); env=host-$mgr
fi
for t in $WANT; do
  if command -v "$t" >/dev/null 2>&1; then ok="$ok,$t"; else
    missing="$missing,$t"; pk=$(pkg "$t" "$(echo "$mgr" | sed 's/^unknown$/apt/')")
    case " $pkgs " in *" $pk "*) ;; *) pkgs="$pkgs $pk" ;; esac
  fi
done
echo "TOOLS env=$env ok=${ok#,} missing=${missing#,}" | sed 's/=$/=none/; s/ok= /ok=none /'
if [ "$env" = sandbox ]; then
  set -- $(sandbox_child); verdict=$1; shift; detail="$*"
  echo "CHILD $verdict $detail"
fi
[ -z "$pkgs" ] && exit 0
for pk in $pkgs; do echo "MISSING $pk"; done
list=$(echo $pkgs)
LAUNCH="The launch output names the file: the last level marked 'Dockerfile (nearest wins)' under 'Sandbox config cascade', plus 'Found Dockerfile in ...' when it is above the project or 'WARNING: No child Dockerfile found' when there is none"
UNSEEN="host env CLAUDE_SANDBOX_BASE_ONLY/CLAUDE_SANDBOX_DOCKERFILE(_DIR) and config.yaml files outside the mounts are not visible here"
DONT="Do not create a project-level .claude-sandbox/Dockerfile to fix this: the nearest one wins, so it would drop every tool a parent-level one installs"
case "$env:${verdict:-}" in
  sandbox:confirmed)
    set -- $detail
    file=$1; shift
    removed=; other=
    for a in "$@"; do
      case "$a" in removed) removed=1 ;; nearer=*|next=*) other=${a#*=} ;; esac
    done
    if [ -n "$removed" ]; then
      msg="FIX this session's image was built from $file, which no longer exists, so the next launch resolves the child Dockerfile anew"
      if [ -n "$other" ]; then
        msg="$msg: by the launcher's default rule it builds from $other; add '$list' to an apt-get install line there, then relaunch, or ask the operator. Not confirmed: $UNSEEN. $LAUNCH"
      else
        msg="$msg and finds none on the levels this container mounts. $LAUNCH. Ask the operator to add '$list' to that file, or to take the upstream base change. $DONT"
      fi
    else
      msg="FIX add '$list' to an apt-get install line in $file (this session's image was built from it), then relaunch; the child image rebuilds on its own"
      if [ -n "$other" ]; then
        msg="$msg. Note: $other is nearer and now exists; unless a config override points at $file, the next launch builds from $other, so add it there, or ask the operator"
      fi
    fi
    echo "$msg" ;;
  sandbox:nearest-visible)
    echo "FIX by the launcher's default rule the child Dockerfile is $detail: add '$list' to an apt-get install line there, then relaunch. Not confirmed: $UNSEEN. $LAUNCH" ;;
  sandbox:base-image)
    echo "FIX this session runs the plain claude-sandbox base image (no child Dockerfile, or baseOnly set). Ask the operator: the upstream base change, or a child Dockerfile that starts 'FROM claude-sandbox' at a level they choose (baseOnly skips any child)" ;;
  sandbox:unknown)
    echo "FIX this session's project path contains whitespace, which this preflight cannot resolve. $LAUNCH. Ask the operator to add '$list' to that file, or to take the upstream base change. $DONT" ;;
  sandbox:built-from-unseen)
    echo "FIX this session's child image $detail was built from a Dockerfile no level of the search chain accounts for (usually a dockerfile/dockerfileDir override). $LAUNCH, and 'Building ... child image from ...' on a rebuild. Ask the operator to add '$list' there. $DONT" ;;
  sandbox:override)
    set -- $detail
    echo "FIX $2 sets the launcher override '$1': the merged config decides which child Dockerfile is used (baseOnly: true uses none; dockerfile/dockerfileDir name one). Ask the operator to add '$list' to the file it names, or to decide. Also, $UNSEEN" ;;
  sandbox:unseen)
    echo "FIX no child Dockerfile at the levels this container mounts; the launcher also searches $detail and above, which it does not mount. $LAUNCH. Ask the operator to add '$list' to that file, or to take the upstream base change. $DONT" ;;
  host-apt:*)    echo "FIX sudo apt-get install -y $list" ;;
  host-dnf:*)    echo "FIX sudo dnf install -y $list" ;;
  host-brew:*)   echo "FIX brew install $list" ;;
  host-pacman:*) echo "FIX sudo pacman -S --needed $list" ;;
  *)             echo "FIX install the packages that provide: ${missing#,} (Debian names: $list)" ;;
esac
exit 0
