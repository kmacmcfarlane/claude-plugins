#!/usr/bin/env python3
"""Install, move, or remove the claude-kit status line, idempotently.

    install_statusline.py [--user|--project|--local|--remove] [--settings PATH]

Writes `statusLine` pointing at the update-stable plugin-data path
(<config>/plugins/data/claude-kit-<marketplace>/current-hooks/statusline.py),
resolved to an ABSOLUTE path at install time: the statusline docs do not
promise env expansion in the command, so none is relied on. The symlink that
keeps that path current is maintained by this plugin's SessionStart hook.

--user   -> ~/.claude/settings.json            (default)
--project-> ./.claude/settings.json            (shared with the team - only do
            this in a repo whose collaborators want it; it overrides theirs)
--local  -> ./.claude/settings.local.json
--remove -> delete the statusLine entry from the chosen scope
"""
import argparse, json, os, sys


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
    return None


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
        sys.exit("claude-kit plugin data dir not found - is the plugin installed? "
                 "(a session must have started once so the SessionStart hook "
                 "creates the current-hooks symlink)")
    script = os.path.join(hooks, "statusline.py")
    if not os.path.exists(script):
        sys.exit(f"{script} missing - start one session with the plugin enabled "
                 f"so the symlink is created, then re-run")

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
