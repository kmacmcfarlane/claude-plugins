"""spin_off.py, the spin-off writer: it installs a new session's own manifest
at a pre-assigned id's store path, stamps it, records the spin-off, points this
session's ledger at it and prints the launch line - and touches nothing else
of this session. Each test names the change it is there to catch."""
import contextlib, io, json, os, shlex, stat, subprocess, sys, tempfile, time
import unittest
from unittest import mock

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)

import lib_context as L          # noqa: E402
import lineage                   # noqa: E402
import rehydrate as R            # noqa: E402
import spin_off as S             # noqa: E402

PARENT = "11111111-2222-4333-8444-555555555555"
CHILD = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
THIRD = "99999999-8888-4777-8666-555555555555"

DRAFT = """---
handoff: 1
repo: proj
session: <stamped>
written: <stamped>
head: <stamped>
branch: <stamped>
top: <stamped>
mode: handoff
by: checkpoint
---
## Doing
Building the topic's thing.

## Goal
mode: handoff — operator: "build the thing"

## Holds
None

## In flight
None

## Next
1. Start.
"""


def git(cwd, *args):
    subprocess.run(("git", "-C", cwd, "-c", "user.email=t@t", "-c", "user.name=t")
                   + args, check=True, capture_output=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = os.path.realpath(self.tmp.name)
        self.cfg = os.path.join(self.root, "cfg")
        os.mkdir(self.cfg)
        scrub = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.cfg})
        scrub.start()
        self.addCleanup(scrub.stop)
        R._top_cache.clear()
        self.repo = self.make_repo("proj", "main")
        self.draft = os.path.join(self.root, "SPINOFF.draft.md")
        self.write_draft(DRAFT)
        self.env = {"CLAUDE_CODE_SESSION_ID": PARENT,
                    "CLAUDE_SANDBOX_PROJECT_DIR": self.repo}

    def make_repo(self, name, branch):
        d = os.path.join(self.root, name)
        os.mkdir(d)
        git(d, "init", "-q", "-b", branch)
        git(d, "commit", "-q", "--allow-empty", "-m", "init")
        return d

    def write_draft(self, text, age=0):
        with open(self.draft, "w") as fh:
            fh.write(text)
        if age:
            t = time.time() - age
            os.utime(self.draft, (t, t))

    def spin(self, *extra, env=None, child=CHILD, cwd=None, prompt=None,
             topic="statusline fix"):
        argv = ["spin_off.py", "--from", self.draft, "--topic", topic]
        if prompt is not None:
            pf = os.path.join(self.root, "prompt.txt")
            with open(pf, "w", encoding="utf-8") as fh:
                fh.write(prompt)
            argv += ["--prompt-file", pf]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = S.main(argv, environ=self.env if env is None else env,
                        cwd=cwd or self.repo, child=child)
        return rc, out.getvalue().splitlines(), err.getvalue()

    def child_path(self, child=CHILD):
        return L.manifest_path(child)

    def read(self, p):
        with open(p, "rb") as fh:
            return fh.read()

    def fm(self, child=CHILD):
        with open(self.child_path(child)) as fh:
            return R.front_matter(fh.read())

    def assert_nothing_written(self, child=CHILD):
        self.assertFalse(os.path.lexists(os.path.join(L.handoff_root(), child)))
        rd = S.record_dir()
        self.assertFalse(os.path.isdir(rd) and any(
            n.endswith(".json") for n in os.listdir(rd)))
        self.assertFalse(os.path.exists(L.ledger_path(PARENT))
                         and "spin-off" in open(L.ledger_path(PARENT)).read())


class TestSpinOff(Base):
    def test_01_parent_state_and_manifest_untouched(self):
        # Kills: a call to L.mark_checkpoint; installing at the parent's path.
        L.save_state(PARENT, {"epoch": 3, "checkpoint_epoch": None})
        own = L.manifest_path(PARENT)
        os.makedirs(os.path.dirname(own), mode=0o700)
        with open(own, "w") as fh:
            fh.write(DRAFT.replace("<stamped>", PARENT, 1))
        before = (self.read(L.state_path(PARENT)), self.read(own))
        rc, out, err = self.spin()
        self.assertEqual(rc, 0, err)
        self.assertEqual((self.read(L.state_path(PARENT)), self.read(own)), before)
        self.assertFalse(L.checkpointed_this_epoch(L.load_state(PARENT)))
        self.assertEqual(out[0], f"installed {self.child_path()}")
        self.assertFalse(os.path.exists(L.state_path(CHILD)))

    def test_02_existing_child_dir_refused(self):
        # Kills: an install that accepts an existing <child>/ (exist_ok).
        os.makedirs(os.path.join(L.handoff_root(), CHILD), mode=0o700)
        rc, out, err = self.spin()
        self.assertEqual((rc, out), (2, []))
        self.assertIn("already exists", err)
        self.assertEqual(os.listdir(os.path.join(L.handoff_root(), CHILD)), [])
        self.assertFalse(os.path.isdir(S.record_dir()))
        self.assertFalse(os.path.exists(L.ledger_path(PARENT)))

    def test_03_links_refused(self):
        # Kills: a link at <child>/ written through (exist_ok, or a fresh check
        # by exists() that a dangling link passes).
        out_dir = os.path.join(self.root, "elsewhere")
        os.mkdir(out_dir)
        os.makedirs(L.handoff_root(), mode=0o700)
        home = os.path.join(L.handoff_root(), CHILD)
        for target in (out_dir, os.path.join(self.root, "dangling")):
            os.symlink(target, home)
            rc, out, err = self.spin()
            self.assertEqual((rc, out), (2, []), err)
            self.assertEqual(os.listdir(out_dir), [])
            self.assertFalse(os.path.lexists(os.path.join(self.root, "dangling")))
            os.unlink(home)
        self.assertFalse(os.path.isdir(S.record_dir()))

    def test_04_stamps(self):
        # Kills: stamping the parent's id as `session:`.
        rc, out, err = self.spin()
        self.assertEqual(rc, 0, err)
        fm = self.fm()
        self.assertEqual((fm["session"], fm["spun_from"], fm["mode"], fm["by"]),
                         (CHILD, PARENT, "handoff", "spin-off"))
        self.assertEqual(fm["top"], self.repo)
        self.assertRegex(fm["written"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(stat.S_IMODE(os.stat(self.child_path()).st_mode), 0o600)
        # Documentation: the file is the child's own by path.
        self.assertEqual(R.resolve_manifest(L.load_state(CHILD), CHILD,
                                            self.repo)[2], "own")

    def read_event(self, sid):
        return {"session_id": sid, "tool_name": "Read", "cwd": self.repo,
                "tool_input": {"file_path": self.child_path()}}

    def test_05_fallback_a_third_sessions_read_adopts(self):
        # Kills: writing `mode: continue` (a continue manifest is never adopted).
        self.assertEqual(self.spin()[0], 0)
        lineage.post_read(self.read_event(THIRD))
        ad = L.load_state(THIRD).get("manifest_adopted")
        self.assertEqual((ad or {}).get("sid"), CHILD)
        self.assertEqual(R.resolve_manifest(L.load_state(THIRD), THIRD,
                                            self.repo)[2], "adopted")

    # A command substitution, a backtick, a quote, a newline, a bidi override
    # and a zero-width joiner. The `$` is split off so this directory's label
    # scan (test_no_internal_labels) does not read `$` and `(` as a call.
    SUBST = "$" + "(touch x)"
    HOSTILE = "fix " + SUBST + " and `id` it's\nsecond line\u202e\u200dend"

    def expected(self, line, sandbox=True, session_id=True):
        toks = shlex.split(line)
        opener = toks[-1]
        head = ["cd", self.repo, "&&"]
        head += ["claude-sandbox", "--new", "--"] if sandbox else ["claude"]
        if session_id:
            head += ["--session-id", CHILD]
        head += ["--name", "proj - statusline fix", opener]
        return toks, head, opener

    def test_06_launch_line_quoting(self):
        # Kills: double quotes around a value; a newline, bidi or format
        # character left in.
        rc, out, err = self.spin(prompt=self.HOSTILE)
        self.assertEqual(rc, 0, err)
        line = out[-1]
        self.assertEqual(len(out), 3)
        self.assertNotIn("\n", line)
        toks, want, opener = self.expected(line)
        self.assertEqual(toks, want)
        self.assertTrue(opener.endswith(
            "Then: fix " + self.SUBST + " and `id` it's second lineend"), opener)
        for ch in "\u202e\u200d\n\r":
            self.assertNotIn(ch, line)
        self.assertNotIn('"', line)

    def test_06b_plain_form_without_sandbox(self):
        env = {"CLAUDE_CODE_SESSION_ID": PARENT}
        rc, out, err = self.spin("--launch-dir", self.repo, env=env)
        self.assertEqual(rc, 0, err)
        toks, want, _ = self.expected(out[-1], sandbox=False)
        self.assertEqual(toks, want)

    def opener(self, *extra):
        rc, out, err = self.spin(*extra, prompt="do it")
        self.assertEqual(rc, 0, err)
        return shlex.split(out[-1])[-1]

    def test_07_opener_clauses(self):
        # Kills: dropping the Read-in-full clause, the not-librarian clause, the
        # hand-in clause, or the no-librarian clause.
        o = self.opener("--librarian", "proj")
        self.assertIn(f"Read (the Read tool) {self.child_path()} in full first.", o)
        self.assertIn("You are not this repo's librarian", o)
        self.assertIn("hand finished branches to the librarian proj with "
                      "SendMessage, first line `hand-in from spin-off proj - "
                      "statusline fix: <branch> @ <full sha>`; wait for "
                      "`filed <id>`.", o)
        self.assertNotIn(S.NO_LIBRARIAN, o)
        os.unlink(self.child_path())
        os.rmdir(os.path.dirname(self.child_path()))
        o = self.opener()
        self.assertIn(S.NO_LIBRARIAN, o)
        self.assertNotIn("hand-in from", o)
        self.assertIn("You are not this repo's librarian", o)
        self.assertIn(f"Read (the Read tool) {self.child_path()} in full first.", o)

    def test_08_old_draft_refused(self):
        # Kills: the draft's age check removed.
        self.write_draft(DRAFT, age=31 * 60)
        rc, out, err = self.spin()
        self.assertEqual((rc, out), (2, []))
        self.assertIn("min ago", err)
        self.assert_nothing_written()

    def test_09_record_and_prune(self):
        # Kills: the prune's age comparison flipped; a prune that follows a link
        # or removes a file that is not a record.
        d = S.record_dir()
        os.makedirs(d, mode=0o700)
        old = time.time() - S.RECORD_TTL_S - 3600
        recent = time.time() - S.RECORD_TTL_S + 3600

        def put(name, t, text="{}"):
            p = os.path.join(d, name)
            with open(p, "w") as fh:
                fh.write(text)
            os.utime(p, (t, t))
            return p
        stale = put("old.json", old)
        fresh = put("young.json", recent)
        notes = put("notes.txt", old)
        outside = os.path.join(self.root, "outside.json")
        with open(outside, "w") as fh:
            fh.write("{}")
        os.utime(outside, (old, old))
        link = os.path.join(d, "link.json")
        os.symlink(outside, link)
        os.utime(link, (old, old), follow_symlinks=False)
        rc, out, err = self.spin("--librarian", "proj")
        self.assertEqual(rc, 0, err)
        self.assertFalse(os.path.exists(stale))
        for p in (fresh, notes, outside):
            self.assertTrue(os.path.exists(p), p)
        self.assertTrue(os.path.islink(link))
        rp = os.path.join(d, CHILD + ".json")
        self.assertEqual(stat.S_IMODE(os.stat(rp).st_mode), 0o600)
        with open(rp) as fh:
            rec = json.load(fh)
        self.assertEqual(set(rec), {"v", "session_id", "name", "topic", "spun_from",
                                    "parent_name", "librarian", "top", "repo",
                                    "created", "manifest"})
        self.assertEqual((rec["v"], rec["session_id"], rec["name"], rec["topic"],
                          rec["spun_from"], rec["parent_name"], rec["librarian"],
                          rec["top"], rec["repo"], rec["manifest"]),
                         (1, CHILD, "proj - statusline fix", "statusline fix",
                          PARENT, None, "proj", self.repo, "proj",
                          self.child_path()))

    def test_09b_record_dir_mode(self):
        self.assertEqual(self.spin()[0], 0)
        self.assertEqual(stat.S_IMODE(os.stat(S.record_dir()).st_mode), 0o700)

    def test_10_no_session_id_changes_nothing_else(self):
        # Kills: the flag printed whatever --no-session-id says.
        rc, out, err = self.spin(prompt="go")
        self.assertEqual(rc, 0, err)
        with_id = out[-1]
        os.unlink(self.child_path())
        os.rmdir(os.path.dirname(self.child_path()))
        rc, out, err = self.spin("--no-session-id", prompt="go")
        self.assertEqual(rc, 0, err)
        self.assertEqual(out[-1], with_id.replace(f" --session-id '{CHILD}'", ""))
        self.assertNotIn("--session-id", out[-1])

    def test_10a_default_is_one_constant(self):
        with mock.patch.object(S, "PRINT_SESSION_ID", False):
            rc, out, err = self.spin()
        self.assertEqual(rc, 0, err)
        self.assertNotIn("--session-id", out[-1])

    def test_10b_never_prints_dangerous(self):
        # Kills: a writer that adds --dangerous (always, or from its environment).
        env = dict(self.env, CLAUDE_SANDBOX_MODE="dangerous",
                   CLAUDE_SANDBOX_DANGEROUS="1", CLAUDE_SANDBOX_ARGS="--dangerous")
        for i, e in enumerate((env, {"CLAUDE_CODE_SESSION_ID": PARENT})):
            rc, out, err = self.spin("--launch-dir", self.repo, env=e,
                                     child=f"{CHILD[:-1]}{i}",
                                     prompt="never --dangerous here")
            self.assertEqual(rc, 0, err)
            toks = shlex.split(out[-1])
            self.assertNotIn("--dangerous", toks)
            self.assertNotIn("--dangerous", " ".join(toks[:-1]))

    def test_11_the_parents_own_read_adopts_it(self):
        # Documents the hazard the never-Read rule guards: a whole-file Read by
        # the spun_from session adopts the spin-off's manifest.
        self.assertEqual(self.spin()[0], 0)
        lineage.post_read(self.read_event(PARENT))
        ad = L.load_state(PARENT).get("manifest_adopted")
        self.assertEqual((ad or {}).get("sid"), CHILD)

    def test_12_bad_topics_refused_raw(self):
        # Kills: a dropped pattern check; a check moved after stripping.
        for bad in ("a/b", " lead", "x;rm", "it's", "a\u200db", "tab\there",
                    "nl\nx", "\u202eevil", "é"):
            rc, out, err = self.spin(topic=bad)
            self.assertEqual((rc, out), (2, []), repr(bad))
            self.assertIn("topic", err)
            self.assert_nothing_written()

    def test_13_stamps_come_from_the_launch_dir(self):
        # Kills: stamping head, branch and top from the cwd.
        other = self.make_repo("work", "feature-x")
        rc, out, err = self.spin("--launch-dir", self.repo, cwd=other)
        self.assertEqual(rc, 0, err)
        fm = self.fm()
        head = subprocess.run(["git", "-C", self.repo, "rev-parse", "--short",
                               "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual((fm["top"], fm["branch"], fm["head"]),
                         (self.repo, "main", head))
        self.assertEqual(shlex.split(out[-1])[1], self.repo)

    def test_14_ledger_pointer_and_gate_state_unchanged(self):
        # Kills: no ledger line; a gate write.
        L.save_state(PARENT, {"epoch": 2})
        before = self.read(L.state_path(PARENT))
        self.assertEqual(self.spin()[0], 0)
        with open(L.ledger_path(PARENT)) as fh:
            lines = fh.read().splitlines()
        self.assertIn(f"- P spin-off proj - statusline fix ({CHILD}) -> "
                      f"{self.child_path()}", lines)
        self.assertEqual(self.read(L.state_path(PARENT)), before)

    def test_15_topic_cap(self):
        # Kills: a dropped 40-character cap.
        rc, out, err = self.spin(topic="a" * 41)
        self.assertEqual((rc, out), (2, []))
        self.assert_nothing_written()
        self.assertEqual(self.spin(topic="a" * 40)[0], 0)

    def test_16_role_holds(self):
        # Kills: the role holds not added, or the lone None kept beside them.
        self.assertEqual(self.spin("--librarian", "proj")[0], 0)
        with open(self.child_path()) as fh:
            text = fh.read()
        holds = R.hold_lines(text)
        self.assertEqual(len(holds), 3, holds)
        self.assertIn("the bare name proj — proj is the single writer", holds[0])
        self.assertIn("hand branches to proj", holds[1])
        self.assertIn("writing items another session holds", holds[2])
        sec = text.split("## Holds\n", 1)[1].split("## In flight", 1)[0]
        self.assertNotIn("None", sec)

    def test_17_holds_without_a_librarian_and_without_a_section(self):
        self.write_draft(DRAFT.replace("## Holds\nNone\n\n", ""))
        self.assertEqual(self.spin()[0], 0)
        with open(self.child_path()) as fh:
            text = fh.read()
        holds = R.hold_lines(text)
        self.assertEqual(len(holds), 3, holds)
        self.assertIn("none live: the operator decides", holds[0])
        self.assertIn("none live: tell the operator", holds[1])
        self.assertLess(text.index("## Holds"), text.index("## In flight"))

    def test_18_refusals_before_install(self):
        # Kills: a missing parent-id check; the bare repo name accepted.
        for env in ({}, {"CLAUDE_CODE_SESSION_ID": "../x"}):
            rc, out, err = self.spin("--launch-dir", self.repo, env=env)
            self.assertEqual((rc, out), (2, []))
            self.assertIn("CLAUDE_CODE_SESSION_ID", err)
        rc, out, err = self.spin("--name", "proj")
        self.assertEqual((rc, out), (2, []))
        self.assert_nothing_written()

    def test_19_mode_skill_and_no_frontmatter_refused_and_removed(self):
        # Kills: a refused draft left installed.
        for text in (DRAFT.replace("by: checkpoint\n",
                                   "by: checkpoint\nmode_skill: /x:y start\n"),
                     DRAFT.split("---\n", 2)[2]):
            self.write_draft(text)
            rc, out, err = self.spin()
            self.assertEqual((rc, out), (2, []), err)
            self.assert_nothing_written()

    def test_20_parent_name_from_its_own_registry_entry_only(self):
        # Kills: a registry entry used without checking its sessionId.
        reg = os.path.join(self.cfg, "sessions")
        os.mkdir(reg)
        with open(os.path.join(reg, "4242.json"), "w") as fh:
            json.dump({"sessionId": THIRD, "name": "someone else"}, fh)
        env = dict(self.env, CLAUDE_PID="4242")
        self.assertEqual(self.spin(env=env)[0], 0)
        with open(os.path.join(S.record_dir(), CHILD + ".json")) as fh:
            self.assertIsNone(json.load(fh)["parent_name"])
        with open(os.path.join(reg, "4242.json"), "w") as fh:
            json.dump({"sessionId": PARENT, "name": "proj"}, fh)
        other = CHILD[:-1] + "f"
        rc, out, err = self.spin(env=env, child=other, prompt="go")
        self.assertEqual(rc, 0, err)
        with open(os.path.join(S.record_dir(), other + ".json")) as fh:
            self.assertEqual(json.load(fh)["parent_name"], "proj")
        self.assertTrue(shlex.split(out[-1])[-1].startswith(
            "You are a spin-off of proj in proj, on: statusline fix."))

    def test_21_cli_help_and_flag_values(self):
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "spin_off.py"),
                            "--help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        for flag in ("--from", "--topic", "--name", "--launch-dir", "--librarian",
                     "--prompt-file", "--no-session-id"):
            self.assertIn(flag, p.stdout)
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "spin_off.py"),
                            "--from", self.draft, "--topic", "--name"],
                           capture_output=True, text=True,
                           env=dict(os.environ, **self.env))
        self.assertEqual(p.returncode, 2)
        self.assert_nothing_written()

    def test_22_names_inside_the_opener_refused(self):
        # Kills: a dropped NAME_RE check (or clean() alone on --name and
        # --librarian), and a repo name with a quote let through.
        for extra in (("--name", "x'; touch p; '"),
                      ("--librarian", "a" + self.SUBST.replace("touch x", "id"))):
            rc, out, err = self.spin(*extra)
            self.assertEqual((rc, out), (2, []), extra)
            self.assert_nothing_written()
        quoted = self.make_repo("it's", "main")
        # A conforming --name, so only the repo name (in the opener and the
        # holds) is left to refuse.
        rc, out, err = self.spin("--launch-dir", quoted, "--name", "ok name")
        self.assertEqual((rc, out), (2, []))
        self.assert_nothing_written()

    CARRIED = ("HOLD dispatching any build on the statusline topic at effort xhigh "
               "or above, because the quota window is nearly spent and the operator "
               "asked to keep the reserve for reviews — until 2026-11-03T07:00Z",
               "HOLD pushing the statusline-hub branch or tagging a release of it, "
               "because the operator wants to read the review findings on the "
               "renderer change first — until decision 61 is answered")

    def test_23_carried_holds_survive_the_startup_header(self):
        # Kills: the role holds put before the carried ones.
        self.write_draft(DRAFT.replace("## Holds\nNone\n", "## Holds\n" + "".join(
            f"- {h}\n" for h in self.CARRIED)))
        self.assertEqual(self.spin("--librarian", "proj")[0], 0)
        with open(self.child_path()) as fh:
            text = fh.read()
        block = R.holds_block(text)
        for h in self.CARRIED:
            self.assertIn(h[:60], block)
        self.assertEqual(len(R.hold_lines(text)), 5)

    def test_24_frontmatter_must_read_back_as_stamped(self):
        # Kills: no read-back check after the stamp (a vertical tab splits a
        # line for the reader that the stamp's parser keeps whole).
        self.write_draft(DRAFT.replace(
            "session: <stamped>\n",
            "session: x\nnote: a\x0bmode: continue\x0bsession: EVIL\n"))
        rc, out, err = self.spin()
        self.assertEqual((rc, out), (2, []), err)
        self.assertIn("read back", err)
        self.assert_nothing_written()

    def test_25_launch_dir_with_control_or_bidi_refused(self):
        # Kills: no character check on the launch directory.
        for bad in ("a\nb", "a\u202eb"):
            d = os.path.join(self.root, bad, "proj")
            os.makedirs(d)
            rc, out, err = self.spin("--launch-dir", d)
            self.assertEqual((rc, out), (2, []), repr(bad))
            self.assertIn("launch directory", err)
            self.assert_nothing_written()


if __name__ == "__main__":
    unittest.main()
