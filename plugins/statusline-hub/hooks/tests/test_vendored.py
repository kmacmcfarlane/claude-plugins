"""Parity of the hub's other vendored copies with the statusline plugin.

owner.py carries statusline's settings-ownership code (the atomic,
formatting-preserving statusLine write, the data-dir lookup, the owner.json
marker) and housekeeping.py its sensor-record prune, both verbatim, because a
plugin may not import another plugin's code. Here each copied definition is
compared, as parsed code, with its source; every definition between a copy's
VENDORED markers must be on the list; and every name the copied functions
reach in their source is copied too, or is one the hub defines for itself on
purpose (PLUGIN, SCRIPT, classify). The tee's own copy is test_parity.py's.

Runs only in the source repo, where plugins/statusline/hooks/ sits beside this
plugin; an installed copy skips it."""
import ast, os, unittest

import helpers

SL_HOOKS = os.path.join(os.path.dirname(helpers.PLUGIN), "statusline", "hooks")
SL_OWNER = os.path.join(SL_HOOKS, "owner.py")
SL_SENSOR = os.path.join(SL_HOOKS, "sensor.py")
BESIDE = os.path.isfile(SL_OWNER) and os.path.isfile(SL_SENSOR)
OWNER = os.path.join(helpers.HOOKS, "owner.py")
HOUSEKEEPING = os.path.join(helpers.HOOKS, "housekeeping.py")

FROM_OWNER = ("MARKER", "MARKER_V", "SettingsError", "Changed", "hooks_dir", "plugin_root",
              "data_root", "data_dir", "installed_by_record", "_SH_SPECIAL", "_parse",
              "_read_text", "read_settings", "_default_mode", "atomic_write_text",
              "atomic_write_json", "_INDENT", "_ESCAPED", "_layout", "dumps_like", "_WS",
              "_MISSING", "_skip_ws", "_end_of_string", "_end_of_value", "_members", "_lead",
              "splice_key", "_splice_settings", "ReadOnly", "_crlf", "write_settings",
              "enabled_in", "read_marker", "write_marker", "_same_path",
              "ensure_hooks_symlink")
OWN_ON_PURPOSE = {"PLUGIN", "SCRIPT", "classify"}
FROM_SENSOR = ("PRUNE_DAYS", "PRUNE_EVERY_S", "TMP_STALE_S", "PRUNE_STAMP", "_TMP",
               "prune_tmp", "prune")
# names the pruning reaches in sensor.py that the hub imports from its tee copy
# (held to their source by test_parity.py)
FROM_TEE = {"safe_sid", "sensor_dir"}


def defs(path, lo=None, hi=None):
    """{name: node} of module-level functions, classes and single-name
    assignments in the file at path (only those on lines lo..hi, when given)."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    out = {}
    for n in tree.body:
        if lo is not None and not lo <= n.lineno <= hi:
            continue
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            out[n.name] = n
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and \
                isinstance(n.targets[0], ast.Name):
            out[n.targets[0].id] = n
    return out


def region(path):
    """(first, last) line numbers between the VENDORED markers."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    start = next(i for i, ln in enumerate(lines, 1) if ln.startswith("# -- VENDORED"))
    end = next(i for i, ln in enumerate(lines, 1) if ln.startswith("# -- end VENDORED"))
    return start, end


@unittest.skipUnless(BESIDE, "statusline plugin not beside this one")
class Drift(unittest.TestCase):
    def check(self, mine_path, src, names):
        mine, theirs = defs(mine_path), defs(src)
        for name in names:
            with self.subTest(name=name):
                self.assertIn(name, theirs, f"{name} is gone from {src}")
                self.assertEqual(ast.dump(mine[name]), ast.dump(theirs[name]),
                                 f"{name} drifted from {os.path.basename(src)}")
        self.assertEqual(sorted(defs(mine_path, *region(mine_path))), sorted(names))

    def test_owner_copy_matches(self):
        self.check(OWNER, SL_OWNER, FROM_OWNER)

    def test_prune_copy_matches(self):
        self.check(HOUSEKEEPING, SL_SENSOR, FROM_SENSOR)

    def reached(self, src, names, stop):
        """Names the copied definitions reach in `src`, transitively - not
        through a name in `stop`, which the hub supplies itself."""
        d = defs(src)
        todo = [x for x in names if isinstance(d.get(x), (ast.FunctionDef, ast.ClassDef))]
        seen = set()
        while todo:
            for n in ast.walk(d[todo.pop()]):
                if isinstance(n, ast.Name) and n.id in d and n.id not in seen:
                    seen.add(n.id)
                    if n.id not in stop:
                        todo.append(n.id)
        return seen - set(names)

    def test_owner_copy_is_complete(self):
        self.assertEqual(self.reached(SL_OWNER, FROM_OWNER, OWN_ON_PURPOSE), OWN_ON_PURPOSE)

    def test_prune_copy_is_complete(self):
        self.assertEqual(self.reached(SL_SENSOR, FROM_SENSOR, FROM_TEE), FROM_TEE)


if __name__ == "__main__":
    unittest.main()
