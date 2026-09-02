#!/usr/bin/env python3
"""Install, move, or remove the claude-kit status line, idempotently.

    install_statusline.py [--user|--project|--local|--remove] [--settings PATH]

Writes `statusLine` pointing at the update-stable plugin-data path
(<config>/plugins/data/claude-kit-<marketplace>/current-hooks/statusline.py),
resolved to an ABSOLUTE path at install time: the statusline docs do not
promise env expansion in the command, so none is relied on. The symlink that
keeps that path current is maintained by this plugin's SessionStart hook; if it
does not exist yet (a session started before the plugin loaded, so the hook
never fired), this script creates it the same way the hook does.

--user   -> ~/.claude/settings.json            (default)
--project-> ./.claude/settings.json            (shared with the team - only do
            this in a repo whose collaborators want it; it overrides theirs)
--local  -> ./.claude/settings.local.json
--remove -> delete the statusLine entry from the chosen scope
"""
import argparse, json, os, re, sys


def plugin_root():
    # <root>/skills/install-statusline/scripts/install_statusline.py
    p = os.path.abspath(__file__)
    for _ in range(3):
        p = os.path.dirname(p)
    return os.path.dirname(p)


def data_hooks_dir():
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    if d:
        return os.path.join(d, "current-hooks")
    cfg = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
    base = os.path.join(cfg, "plugins", "data")
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            if name.startswith("claude-kit-"):
                return os.path.join(base, name, "current-hooks")
    # Fresh install: no data dir yet. Derive its name from the cache path this
    # script runs from (plugins/cache/<marketplace>/claude-kit/<version>/...).
    m = re.search(r"/plugins/cache/([^/]+)/claude-kit/", os.path.abspath(__file__))
    if m:
        return os.path.join(base, "claude-kit-" + m.group(1), "current-hooks")
    return None


def ensure_hooks_symlink(hooks):
    """Create current-hooks as the SessionStart hook would (ln -sfn), covering
    sessions that started before the plugin loaded so the hook never fired."""
    if os.path.isdir(hooks):  # resolves already; SessionStart keeps it current
        return
    src = os.path.join(plugin_root(), "hooks")
    if not os.path.isdir(src):
        return
    os.makedirs(os.path.dirname(hooks), exist_ok=True)
    tmp = hooks + ".tmp"
    try:
        if os.path.lexists(tmp):
            os.remove(tmp)
        os.symlink(src, tmp)
        os.replace(tmp, hooks)  # atomic, also replaces a dangling symlink
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--user", action="store_true")
    scope.add_argument("--project", action="store_true")
    scope.add_argument("--local", action="store_true")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--settings", help="explicit settings file path")
    a = ap.parse_args()

    if a.settings:
        path = a.settings
    elif a.project:
        path = os.path.join(".claude", "settings.json")
    elif a.local:
        path = os.path.join(".claude", "settings.local.json")
    else:
        cfg = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
        path = os.path.join(cfg, "settings.json")

    d = {}
    if os.path.exists(path):
        d = json.load(open(path))

    if a.remove:
        removed = d.pop("statusLine", None)
        json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
        hooks = data_hooks_dir()
        if hooks:
            try:
                os.remove(os.path.join(os.path.dirname(hooks), "statusline-installed.json"))
            except OSError:
                pass
        print(f"removed statusLine from {path}" if removed else f"no statusLine in {path}")
        return

    hooks = data_hooks_dir()
    if not hooks:
        sys.exit("claude-kit plugin data dir not found and not derivable from "
                 "this script's path - is the plugin installed?")
    ensure_hooks_symlink(hooks)
    script = os.path.join(hooks, "statusline.py")
    if not os.path.exists(script):
        sys.exit(f"{script} missing - could not create the current-hooks "
                 f"symlink (plugin hooks dir not found next to this script); "
                 f"start one session with the plugin enabled, then re-run")

    prev = d.get("statusLine")
    cmd = f"python3 {json.dumps(script)}"
    d["statusLine"] = {"type": "command", "command": cmd}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False)
    # Marker for the SessionStart self-heal: a settings write by a session
    # launched BEFORE this install serializes its stale in-memory snapshot and
    # drops this entry (live-fired 2026-08-31 via /plugin). The heal restores it.
    marker = os.path.join(os.path.dirname(hooks), "statusline-installed.json")
    json.dump({"settings": os.path.abspath(path), "command": cmd},
              open(marker, "w"), indent=2)
    print(f"{'updated' if prev else 'installed'} statusLine in {path}\n  -> {script}")
    print("WARNING: sessions already running hold a pre-install settings snapshot; "
          "a /plugin toggle or model/effort change there will clobber this entry "
          "on write. The claude-kit SessionStart hook now self-heals it at the "
          "next session start.")


main()
