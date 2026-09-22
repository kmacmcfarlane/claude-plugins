"""The segment drop dir (hook-contract.md § 11): text other tools write under
CFG/statusline-hub/segments/, read by the render with no code run - capped,
sanitised, stale or expired files dropped, the status line never broken."""
import json, os, time, unittest

import helpers
import housekeeping as H
import hub
import registry as R


class Base(helpers.Hermetic):
    def setUp(self):
        super().setUp()
        self.env.pop("COLUMNS", None)
        self._columns = os.environ.pop("COLUMNS", None)

    def tearDown(self):
        if self._columns is not None:
            os.environ["COLUMNS"] = self._columns
        super().tearDown()

    def seg_dir(self):
        return os.path.join(self.cfg, "statusline-hub", "segments")

    def segment(self, name, body=None, sid=None, raw=None, mode=0o600, age=0, **fields):
        """Write segments/<name>.json, or segments/<name>/<sid>.json (dirs 0700);
        `body` defaults to {"v": 1, **fields}; `age` seconds back-dates it."""
        d = self.seg_dir()
        for p in (os.path.dirname(d), d) + ((os.path.join(d, name),) if sid else ()):
            os.makedirs(p, mode=0o700, exist_ok=True)
            os.chmod(p, 0o700)
        path = os.path.join(d, name, sid + ".json") if sid else os.path.join(d, name + ".json")
        with open(path, "w") as f:
            f.write(raw if raw is not None else json.dumps(
                body if body is not None else dict({"v": 1}, **fields)))
        os.chmod(path, mode)
        if age:
            t = time.time() - age
            os.utime(path, (t, t))
        return path

    def line(self, payload=None, columns=None):
        if columns is not None:
            self.env["COLUMNS"] = str(columns)
        rc, out, err, _ = self.hub(payload)
        self.env.pop("COLUMNS", None)
        self.assertEqual((rc, err), (0, b""))
        self.assertTrue(out.endswith(b"\n") and out.count(b"\n") == 1, out)
        return out[:-1].decode()


class Render(Base):
    def test_no_drop_dir_leaves_the_line_as_it_was(self):
        self.manifest("a", ["echo", "gauge"])
        self.assertEqual(self.line(), "gauge")
        os.makedirs(self.seg_dir(), mode=0o700)
        self.assertEqual(self.line(), "gauge")
        self.assertEqual(self.read_sensor()["exact"]["pct"], 42.0)

    def test_segments_follow_the_hooks_in_order(self):
        self.manifest("a", ["echo", "gauge"])
        self.segment("sandbox", text="box", order=5)
        self.segment("chip", text="me", order=1)
        self.assertEqual(self.line(), "gauge  me  box")
        self.write_json(R.config_path(), {"order": ["sandbox", "a"], "separator": " | "})
        self.assertEqual(self.line(), "box | gauge | me")
        self.write_json(R.config_path(), {"disabled": ["chip"]})
        self.assertEqual(self.line(), "gauge  box")

    def test_segments_alone(self):
        self.segment("chip", text="me")
        self.assertEqual(self.line(), "me")

    def test_session_file_wins_over_the_all_sessions_file(self):
        self.segment("chip", text="everyone")
        self.segment("chip", sid="s1", text="only s1")
        self.assertEqual(self.line({"session_id": "s1"}), "only s1")
        self.assertEqual(self.line({"session_id": "s2"}), "everyone")
        # a session file that is no longer live falls back to the shared one
        self.segment("chip", sid="s1", text="gone", expires_at=time.time() - 1)
        self.assertEqual(self.line({"session_id": "s1"}), "everyone")

    def test_session_id_never_names_a_path_outside(self):
        self.segment("chip", text="shared")
        os.makedirs(os.path.join(self.seg_dir(), "chip"), mode=0o700)
        outside = os.path.join(self.cfg, "statusline-hub", "x.json")
        self.write_json(outside, {"v": 1, "text": "escaped"})
        os.chmod(outside, 0o600)
        self.assertEqual(self.line({"session_id": "../../x"}), "shared")

    def test_staleness(self):
        now = time.time()
        self.segment("a1", text="fresh")
        self.segment("a2", text="old", age=R.SEGMENT_STALE_S + 60)
        self.segment("a3", text="kept", age=R.SEGMENT_STALE_S + 60, expires_at=now + 3600)
        self.segment("a4", text="expired", expires_at=now - 1)
        self.segment("a5", text="ancient", age=R.SEGMENT_AGE_MAX_S + 60,
                     expires_at=now + 86400 * 365)
        self.segment("a6", text="bad expiry", expires_at="tomorrow")
        self.assertEqual(self.line(), "fresh  kept")

    def test_malformed_and_oversized_files_drop_only_themselves(self):
        self.manifest("a", ["echo", "gauge"])
        self.segment("b1", raw="{not json")
        self.segment("b2", raw="[1, 2]")
        self.segment("b3", text="no version", v=None)
        self.segment("b4", body={"v": 2, "text": "future"})
        self.segment("b5", body={"v": 1, "text": 42})
        self.segment("b6", text="bad order", order="1")
        self.segment("b7", text="x" * (R.SEGMENT_MAX + 10))
        self.segment("b8", text="bad fg", fg=3)
        self.segment("b9", raw="\xff\xfe")
        self.segment("ok", text="fine")
        self.assertEqual(self.line(), "gauge  fine")

    def test_text_is_sanitised_and_capped(self):
        self.segment("a", text="\x1b]0;title\x07ok \x1b[31mred\x1b[0m\x1b[2J‮txt\nline two")
        self.assertEqual(self.line(), "ok redtxt")
        self.segment("a", text="y" * 100)
        out = self.line()
        self.assertEqual(out, "y" * 39 + R.ELLIPSIS)
        self.assertEqual(R.columns(out), R.SEGMENT_COLS)
        self.segment("a", text="漢" * 30)  # wide: two columns each
        out = self.line()
        self.assertEqual(out, "漢" * 19 + R.ELLIPSIS)
        self.assertEqual(R.columns(out), 39)
        self.segment("a", text="   ")
        self.assertEqual(self.line(), "")

    def test_fg_colours_known_names_only(self):
        self.segment("a", text="warn", fg="yellow")
        self.segment("b", text="plain", fg="\x1b[5m")
        self.assertEqual(self.line(), "\x1b[33mwarn" + R.RESET + "  plain")

    def test_at_most_sixteen_providers(self):
        for i in range(R.SEGMENTS_MAX + 3):
            self.segment(f"p{i:02d}", text=str(i))
        out = self.line().split("  ")
        self.assertEqual(out, [str(i) for i in range(R.SEGMENTS_MAX)])

    def test_narrow_terminal_drops_lowest_priority_first(self):
        self.manifest("a", ["echo", "gauge"])
        self.segment("s1", text="one", priority=5)
        self.segment("s2", text="two", priority=1)
        self.segment("s3", text="three", priority=1)
        self.assertEqual(self.line(columns=200), "gauge  one  two  three")
        # 22 columns needed; 18 drops one priority-1 segment: the last shown
        self.assertEqual(self.line(columns=18), "gauge  one  two")
        self.assertEqual(self.line(columns=12), "gauge  one")
        # a display hook's text is never dropped for width
        self.assertEqual(self.line(columns=2), "gauge")

    def test_width_counts_the_health_glyph(self):
        health = os.path.join(self.cfg, "analytics", "health.json")
        self.manifest("a", ["echo", "gauge"])
        self.manifest("r", ["true"], kind="record", health_path=health)
        self.segment("s1", text="chip")
        # "gauge  chip" is 11 columns: it fits in 11 until the glyph needs 2 more
        self.assertEqual(self.line(columns=11), "gauge  chip")
        self.write_json(health, {"last_error": time.time()})
        self.assertEqual(self.line(columns=13), "gauge  chip \u26a0")
        self.assertEqual(self.line(columns=12), "gauge \u26a0")

    def test_never_runs_anything(self):
        marker = os.path.join(self.cfg, "ran")
        self.segment("a", text="$(touch ran)", command=["touch", marker])
        self.assertEqual(self.line(), "$(touch ran)")
        self.assertFalse(os.path.exists(marker))

    def test_a_fifo_or_directory_where_a_file_belongs_is_skipped(self):
        self.segment("ok", text="fine")
        os.mkfifo(os.path.join(self.seg_dir(), "fifo.json"), 0o600)
        os.makedirs(os.path.join(self.seg_dir(), "dir.json"), mode=0o700)
        rc, out, err, secs = self.hub()
        self.assertEqual((rc, out, err), (0, b"fine\n", b""))
        self.assertLess(secs, 2)

    def test_drop_dir_that_is_a_file_is_harmless(self):
        os.makedirs(os.path.dirname(self.seg_dir()), mode=0o700)
        self.write_json(self.seg_dir(), raw="not a dir")
        self.manifest("a", ["echo", "gauge"])
        self.assertEqual(self.line(), "gauge")


class Trust(Base):
    @unittest.skipIf(os.geteuid() == 0, "root bypasses the mode checks")
    def test_group_writable_file_or_dir_is_skipped(self):
        self.segment("a", text="loose", mode=0o620)
        self.segment("b", text="tight")
        self.assertEqual(self.line(), "tight")
        os.chmod(self.seg_dir(), 0o770)
        self.assertEqual(self.line(), "")

    def test_symlinks_are_not_followed(self):
        real = self.segment("real", text="real")
        os.symlink(real, os.path.join(self.seg_dir(), "link.json"))
        target = os.path.join(self.cfg, "elsewhere")
        os.makedirs(target, mode=0o700)
        self.write_json(os.path.join(target, "s.json"), {"v": 1, "text": "via link"})
        os.symlink(target, os.path.join(self.seg_dir(), "dirlink"))
        self.assertEqual(self.line(), "real")

    def test_config_dir_in_a_git_tree_shows_no_segments(self):
        repo = os.path.join(self.cfg, "repo")
        os.makedirs(os.path.join(repo, ".git"))
        self.env["CLAUDE_CONFIG_DIR"] = os.environ["CLAUDE_CONFIG_DIR"] = self.cfg = \
            os.path.join(repo, "cfg")
        self.segment("a", text="spoofed")
        self.assertEqual(self.line(), "")


class Compose(unittest.TestCase):
    def test_wrapped_output_first_segments_on_its_last_line(self):
        parts = [("gauge", None), ("chip", 0)]
        self.assertEqual(hub.fit_line(parts, "top\nbottom", "  ", None),
                         "top\nbottom  gauge  chip")
        self.assertEqual(hub.fit_line(parts, "top\nbottom", "  ", 15), "top\nbottom  gauge")
        self.assertEqual(hub.fit_line(parts, None, "  ", None), "gauge  chip")
        self.assertEqual(hub.fit_line([], "\x1b[31mred", "  ", None), "\x1b[31mred")
        self.assertEqual(hub.fit_line(parts[1:], "\x1b[31mred", "  ", None),
                         "\x1b[31mred" + R.RESET + "  chip")

    def test_reserve_counts_what_follows_the_last_line(self):
        parts = [("gauge", None), ("chip", 0)]
        self.assertEqual(hub.fit_line(parts, None, "  ", 11), "gauge  chip")
        self.assertEqual(hub.fit_line(parts, None, "  ", 11, reserve=2), "gauge")
        self.assertEqual(hub.fit_line(parts, "top\nbottom", "  ", 21, reserve=2),
                         "top\nbottom  gauge  chip")  # 19 columns + 2
        self.assertEqual(hub.fit_line(parts, "top\nbottom", "  ", 21, reserve=3),
                         "top\nbottom  gauge")

    def test_columns(self):
        self.assertEqual(R.columns("\x1b[32mab\x1b[0m"), 2)
        self.assertEqual(R.columns("é"), 1)
        self.assertEqual(R.columns("漢"), 2)


class Prune(Base):
    def test_prune_removes_what_no_render_shows(self):
        now = time.time()
        live = self.segment("live", text="x")
        kept = self.segment("kept", text="x", age=R.SEGMENT_STALE_S + 60, expires_at=now + 60)
        expired = self.segment("gone", text="x", expires_at=now - 1)
        ancient = self.segment("old", raw="{junk", age=R.SEGMENT_AGE_MAX_S + 60)
        sess = self.segment("chip", sid="s1", text="x", expires_at=now - 1)
        self.assertEqual(H.prune_segments(now), 3)
        for p in (live, kept):
            self.assertTrue(os.path.exists(p), p)
        for p in (expired, ancient, sess):
            self.assertFalse(os.path.exists(p), p)
        self.assertFalse(os.path.exists(os.path.join(self.seg_dir(), "chip")))

    def test_producer_temp_files_are_pruned_once_an_hour_old(self):
        # tempfile.mkstemp's default names, dot-prefixed as § 11 asks: not
        # prune_tmp's _TMP shape
        now = time.time()
        self.segment("chip", sid="s1", text="x", expires_at=now - 1)
        sub = os.path.join(self.seg_dir(), "chip")
        old_tmp = os.path.join(sub, ".tmpab12_cd")
        live_tmp = os.path.join(self.seg_dir(), ".chip.json.x7y8z9")
        for p, age in ((old_tmp, H.TMP_STALE_S + 60), (live_tmp, 5)):
            with open(p, "w") as f:
                f.write("{")
            os.utime(p, (now - age, now - age))
        self.assertEqual(H.prune_segments(now), 2)
        self.assertFalse(os.path.exists(old_tmp))
        self.assertFalse(os.path.exists(sub))  # the temp no longer blocks rmdir
        self.assertTrue(os.path.exists(live_tmp))  # a live producer's write

    def test_a_segment_rewritten_mid_pass_survives(self):
        now = time.time()
        for how in ("replace", "utime"):
            path = self.segment("chip", text="x", expires_at=now - 1)
            st = H._dead_segment(path, now)
            self.assertIsNotNone(st)
            if how == "replace":  # the producer's atomic write: a new inode
                tmp = self.segment("tmp", text="fresh", expires_at=now + 3600)
                os.replace(tmp, path)
            else:  # the producer keeps its file up with os.utime
                os.utime(path, ns=(st.st_mtime_ns + 10**9,) * 2)
            self.assertFalse(H._unlink_if_same(path, st), how)
            self.assertTrue(os.path.exists(path), how)

        # the same race through the whole pass: the rewrite lands between the
        # judgment and the unlink
        path = self.segment("chip", text="x", expires_at=now - 1)
        judge = H._dead_segment

        def judge_then_rewrite(p, t):
            st = judge(p, t)
            fresh = self.segment("tmp", text="fresh", expires_at=now + 3600)
            os.replace(fresh, p)
            return st

        H._dead_segment = judge_then_rewrite
        try:
            self.assertEqual(H.prune_segments(now), 0)
        finally:
            H._dead_segment = judge
        with open(path) as f:
            self.assertEqual(json.load(f)["text"], "fresh")

    def test_prune_hub_includes_segments_and_skips_untrusted_dirs(self):
        os.makedirs(os.path.join(self.cfg, "statusline-hub"), mode=0o700)
        gone = self.segment("gone", text="x", expires_at=time.time() - 1)
        H.prune_hub()
        self.assertFalse(os.path.exists(gone))
        if os.geteuid() != 0:
            gone = self.segment("gone", text="x", expires_at=time.time() - 1)
            os.chmod(self.seg_dir(), 0o777)
            self.assertEqual(H.prune_segments(), 0)
            self.assertTrue(os.path.exists(gone))


class Status(Base):
    def test_status_lists_segments_and_skips(self):
        self.segment("chip", text="me", priority=2)
        self.segment("bad", raw="{")
        rc, out, err, _ = self.hub(raw=b"", args=("--status",))
        text = out.decode()
        self.assertEqual((rc, err), (0, b""))
        self.assertIn("chip: all sessions, shows, priority 2", text)
        self.assertIn("bad.json: skipped (not JSON)", text)


if __name__ == "__main__":
    unittest.main()
