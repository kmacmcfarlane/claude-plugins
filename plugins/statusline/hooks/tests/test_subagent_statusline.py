"""subagent_statusline.py: the agent panel's per-agent context fill, and the
plugin settings.json default that enables it."""
import json, os, re, subprocess, sys, time, unittest

from helpers import HOOKS, PLUGIN, Hermetic

RENDERER = os.path.join(HOOKS, "subagent_statusline.py")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def usage(inp, read=0, create=0, out=7):
    return {"type": "assistant", "isSidechain": True,
            "message": {"usage": {"input_tokens": inp, "cache_read_input_tokens": read,
                                  "cache_creation_input_tokens": create,
                                  "output_tokens": out}}}


class Rows(Hermetic):
    def setUp(self):
        super().setUp()
        self.proj = os.path.join(self.cfg, "projects", "p")
        os.makedirs(self.proj)
        self.transcript = os.path.join(self.proj, "sess.jsonl")
        self.subdir = os.path.join(self.proj, "sess", "subagents")

    def side(self, agent_id, lines, raw_tail=b"", mode="w"):
        os.makedirs(self.subdir, exist_ok=True)
        p = os.path.join(self.subdir, f"agent-{agent_id}.jsonl")
        with open(p, mode + "b") as f:
            for obj in lines:
                f.write((json.dumps(obj) + "\n").encode())
            f.write(raw_tail)
        return p

    def run_rows(self, tasks, columns=200, raw=None, **extra):
        payload = dict({"session_id": "sess", "transcript_path": self.transcript,
                        "cwd": self.cfg, "columns": columns, "tasks": tasks}, **extra)
        p = subprocess.run([sys.executable, RENDERER],
                           input=raw if raw is not None else json.dumps(payload),
                           capture_output=True, text=True, encoding="utf-8",
                           env=self.env, timeout=30)
        self.assertEqual((p.returncode, p.stderr), (0, ""))
        return {d["id"]: d["content"] for d in map(json.loads, p.stdout.splitlines())}

    @staticmethod
    def task(tid="a1", **kw):
        return dict({"id": tid, "name": "rev", "type": "local_agent", "status": "running",
                     "description": "Review the diff", "contextWindowSize": 200_000,
                     "tokenCount": 150_000}, **kw)

    # -- exact depth ------------------------------------------------------

    def test_exact_depth_is_the_last_usage_input_sum(self):
        self.side("a1", [usage(10, 50_000, 1_000), {"type": "user"},
                         usage(5, 80_000, 1_000)])
        rows = self.run_rows([self.task()])
        self.assertEqual(ANSI.sub("", rows["a1"]), "rev · 40% 81k/200k · Review the diff")
        self.assertIn("\x1b[32m", rows["a1"])     # 119k left on 200k: green

    def test_colour_follows_tokens_left(self):
        self.side("a1", [usage(0, 170_000)])
        self.assertIn("\x1b[31m", self.run_rows([self.task()])["a1"])  # 30k left: red

    def test_compact_boundary_resets_to_the_approximate_figure(self):
        self.side("a1", [usage(0, 150_000), {"type": "system", "subtype": "compact_boundary"}])
        row = ANSI.sub("", self.run_rows([self.task(tokenCount=20_000)])["a1"])
        self.assertIn("~10% ~20k/200k", row)
        self.side("a1", [usage(0, 30_000)], mode="a")
        row = ANSI.sub("", self.run_rows([self.task(tokenCount=20_000)])["a1"])
        self.assertIn("15% 30k/200k", row)

    def test_session_dir_named_by_session_id_is_found(self):
        self.transcript = os.path.join(self.proj, "other-name.jsonl")
        self.side("a1", [usage(0, 40_000)])
        self.assertIn("20% 40k/200k", ANSI.sub("", self.run_rows([self.task()])["a1"]))

    # -- the incremental read ---------------------------------------------

    def cache(self):
        with open(os.path.join(self.cfg, "statusline", "subagents", "sess.json")) as f:
            return json.load(f)["agents"]

    def test_second_tick_reads_only_the_appended_lines(self):
        # A line after the usage keeps it outside the TAIL_CHECK bytes.
        p = self.side("a1", [usage(0, 40_000), {"type": "user", "pad": "x" * 100}])
        self.run_rows([self.task()])
        ent = self.cache()["a1"]
        self.assertEqual(ent["off"], os.path.getsize(p))
        self.assertEqual(ent["cur"], 40_000)
        # Rewrite the already-read bytes in place (same inode, same length,
        # the tail kept): only the appended line may be read.
        with open(p, "r+b") as f:
            data = f.read()
            f.seek(0)
            f.write(data.replace(b"40000", b"99999"))
        self.side("a1", [{"type": "user"}], mode="a")
        self.assertIn("20% 40k", ANSI.sub("", self.run_rows([self.task()])["a1"]))
        self.side("a1", [usage(0, 60_000)], mode="a")
        self.assertIn("30% 60k", ANSI.sub("", self.run_rows([self.task()])["a1"]))

    def test_a_replaced_file_is_read_from_the_start(self):
        p = self.side("a1", [usage(0, 40_000), usage(0, 50_000)])
        self.run_rows([self.task()])
        os.unlink(p)
        self.side("a1", [usage(0, 20_000)])
        self.assertIn("10% 20k", ANSI.sub("", self.run_rows([self.task()])["a1"]))

    def test_a_line_without_its_newline_waits_for_the_next_tick(self):
        line = json.dumps(usage(0, 90_000)).encode()
        self.side("a1", [usage(0, 40_000)], raw_tail=line[:20])
        self.assertIn("20% 40k", ANSI.sub("", self.run_rows([self.task()])["a1"]))
        with open(os.path.join(self.subdir, "agent-a1.jsonl"), "ab") as f:
            f.write(line[20:] + b"\n")
        self.assertIn("45% 90k", ANSI.sub("", self.run_rows([self.task()])["a1"]))

    def test_budget_bounds_a_tick_and_the_next_one_continues(self):
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        pad = {"type": "user", "pad": "x" * 1000}
        p = self.side("a1", [usage(0, 10_000)] + [pad] * 50 + [usage(0, 70_000)])
        ent, done, n = R.scan(p, None, 5_000)
        self.assertFalse(done)
        self.assertLess(n, 6_200)
        self.assertEqual(ent["cur"], 10_000)
        for _ in range(20):
            ent, done, _n = R.scan(p, ent, 5_000)
            if done:
                break
        self.assertTrue(done)
        self.assertEqual((ent["cur"], ent["off"]), (70_000, os.path.getsize(p)))

    def test_unfinished_read_shows_the_approximate_figure(self):
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        old = R.BUDGET
        try:
            R.BUDGET = 10
            pad = {"type": "user", "pad": "x" * 100}
            self.side("a1", [usage(0, 40_000), pad, pad])
            got = R.depths({"session_id": "sess", "transcript_path": self.transcript,
                            "tasks": [self.task()]})
        finally:
            R.BUDGET = old
        self.assertEqual(got, {})

    def test_a_workflow_agent_one_level_down_is_found(self):
        self.subdir = os.path.join(self.proj, "sess", "subagents", "workflows", "run1")
        self.side("a1", [usage(0, 40_000)])
        self.assertIn("20% 40k", ANSI.sub("", self.run_rows([self.task()])["a1"]))

    def test_a_long_line_is_streamed_and_its_usage_found(self):
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        old = R.LINE_MAX
        try:
            R.LINE_MAX = 4096
            big = usage(0, 90_000)
            big["message"] = {"content": [{"type": "text", "text": "y" * 50_000}],
                              "usage": big["message"]["usage"]}
            p = self.side("a1", [usage(0, 10_000), big])
            ent, done, n = R.scan(p, None, 1 << 20)
            self.assertTrue(done)
            self.assertEqual((ent["cur"], ent["off"], n),
                             (90_000, os.path.getsize(p), os.path.getsize(p)))
            # The same line with no newline yet is left for the next tick.
            raw = json.dumps(big).encode()
            p = self.side("a2", [usage(0, 10_000)], raw_tail=raw)
            ent, done, n = R.scan(p, None, 1 << 20)
            self.assertEqual((ent["cur"], ent["off"]), (10_000, os.path.getsize(p) - len(raw)))
        finally:
            R.LINE_MAX = old

    def long_line_depth(self, line, line_max=4096, before=10_000):
        """The depth scan reads with `line` (bytes, no newline) after one
        ordinary usage line of `before`, LINE_MAX patched to `line_max`."""
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        old = R.LINE_MAX
        try:
            R.LINE_MAX = line_max
            p = self.side("a1", [usage(0, before)], raw_tail=line + b"\n")
            ent, done, n = R.scan(p, None, 1 << 20)
        finally:
            R.LINE_MAX = old
        self.assertTrue(done)
        self.assertEqual(ent["off"], os.path.getsize(p))
        return ent["cur"]

    @staticmethod
    def padded(marker, at, tail):
        """A line whose filler string puts `marker` (the first bytes of
        `tail`) at byte offset `at`."""
        head = b'{"type":"assistant","message":{"content":"'
        pad = at - len(head) - len(b'",')
        assert pad >= 0 and tail.startswith(marker)
        return head + b"y" * pad + b'",' + tail

    def test_a_usage_key_straddling_a_chunk_edge_is_found(self):
        tail = (b'"usage":{"input_tokens":3,"cache_read_input_tokens":40000,'
                b'"cache_creation_input_tokens":2000,"output_tokens":9}},'
                b'"toolUseResult":{"x":"' + b"z" * 5000 + b'"}}')
        for at in range(4096 - 12, 4096 + 4):     # LINE_MAX-3 and +1 among them
            line = self.padded(b'"usage"', at, tail)
            self.assertEqual(line.index(b'"usage"'), at)
            self.assertEqual(self.long_line_depth(line), 42_003, at)

    def test_usage_fields_straddling_a_chunk_edge_are_read_whole(self):
        # Pad the key so that each of the key, the colon and the digits
        # meets the edge at LINE_MAX (4096) somewhere in the sweep.
        for at in range(4096 - 40, 4096 + 4):
            tail = (b'"usage":{"input_tokens":3,"cache_read_input_tokens":123456789,'
                    b'"cache_creation_input_tokens":2}}}')
            head = b'{"type":"assistant","message":{"content":"'
            key_at = len(b'"usage":{"input_tokens":3,')
            line = head + b"y" * (at - len(head) - len(b'",') - key_at) + b'",' + tail
            self.assertEqual(line.index(b'"cache_read_input_tokens"'), at)
            self.assertEqual(self.long_line_depth(line), 123_456_794, at)

    def test_a_long_line_counts_only_message_usage(self):
        big = "z" * 6000
        # A usage elsewhere on the line - in the content, after the message,
        # at the top level - is not the message's; a line with none keeps
        # the depth before it.
        line = json.dumps({"type": "assistant",
                           "message": {"content": [{"usage": {"input_tokens": 1}}, big],
                                       "usage": {"input_tokens": 5, "cache_read_input_tokens": 70_000}},
                           "toolUseResult": {"usage": {"input_tokens": 999_999}},
                           "usage": {"input_tokens": 888_888}}).encode()
        self.assertEqual(self.long_line_depth(line), 70_005)
        line = json.dumps({"type": "user", "message": {"content": big},
                           "toolUseResult": {"usage": {"input_tokens": 999_999, "t": big}}}).encode()
        self.assertEqual(self.long_line_depth(line), 10_000)

    def test_a_usage_field_missing_is_not_borrowed_from_a_neighbour(self):
        line = json.dumps({"type": "assistant",
                           "message": {"content": "z" * 6000,
                                       "usage": {"input_tokens": 5, "cache_read_input_tokens": 70_000,
                                                 "server_tool_use": {"input_tokens": 400}},
                                       "next": {"cache_creation_input_tokens": 300_000}},
                           "cache_creation_input_tokens": 500_000}).encode()
        self.assertEqual(self.long_line_depth(line), 70_005)

    def test_the_streamed_count_matches_the_whole_line_parse(self):
        sys.path.insert(0, HOOKS)
        import random
        import subagent_statusline as R
        rnd = random.Random(7)
        keys = ["input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens",
                "output_tokens", "usage", "message"]

        def val(d):
            r = rnd.random()
            if d > 3 or r < 0.3:
                return rnd.choice(["12", "0", "-4", "3.9", "1e3", "true", "null", '"7"',
                                   '"a\\"b\\\\"', "NaN", "123456789"])
            if r < 0.5:
                return "[" + ",".join(val(d + 1) for _ in range(rnd.randint(0, 3))) + "]"
            return obj(d + 1)

        def key(k):     # sometimes escaped, which json.loads decodes
            return '"' + (k.replace("u", "\\u0075", 1) if rnd.random() < 0.2 else k) + '"'

        def obj(d):
            items = [key(rnd.choice(keys)) + ":" + val(d) for _ in range(rnd.randint(0, 5))]
            return "{" + " , ".join(items) + "}"

        cases = []
        for _ in range(400):
            cases.append(obj(0))
        cases += ['{"message":{"usage":{"input_tokens":5}}} x', '[{"message":1}]',
                  '{"message":{"usage":{"input_tokens":5,}}}', '"usage"', "7",
                  '{"message":{"usage":{"input_tokens":5},"usage":{"cache_read_input_tokens":8}}}',
                  '{"message":{"usage":{"input_tokens":5}},"message":{}}',
                  '{"message":{"content":"a\u0001b","usage":{"input_tokens":5}}}']
        for text in cases:
            line = text.encode() + b"\n"
            want = R._usage_total(line)
            for step in (1, 2, 3, 7, 64):
                u = R._UsageScan()
                for i in range(0, len(line), step):
                    u.feed(line[i:i + step])
                self.assertEqual(u.total(), want, (text, step))

    def test_least_left_to_read_goes_first(self):
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        old = R.BUDGET
        try:
            R.BUDGET = 2_000
            pad = {"type": "user", "pad": "x" * 500}
            self.side("big", [usage(0, 10_000)] + [pad] * 20)
            self.side("small", [usage(0, 40_000)])
            got = R.depths({"session_id": "sess", "transcript_path": self.transcript,
                            "tasks": [self.task("big"), self.task("small")]})
        finally:
            R.BUDGET = old
        self.assertEqual(got, {"small": 40_000})

    def test_cache_keeps_rows_not_visible_this_tick(self):
        self.side("a1", [usage(0, 40_000)])
        self.side("a2", [usage(0, 50_000)])
        self.run_rows([self.task("a1"), self.task("a2")])
        self.run_rows([self.task("a2")])
        self.assertEqual(sorted(self.cache()), ["a1", "a2"])

    # -- the approximate fallback -----------------------------------------

    def test_no_sidechain_falls_back_to_token_count_marked_approximate(self):
        row = ANSI.sub("", self.run_rows([self.task()])["a1"])
        self.assertEqual(row, "rev · ~75% ~150k/200k · Review the diff")

    def test_unsafe_id_never_names_a_path(self):
        os.makedirs(os.path.join(self.proj, "sess"), exist_ok=True)
        with open(os.path.join(self.proj, "sess", "agent-x.jsonl"), "w") as f:
            f.write(json.dumps(usage(0, 99_000)) + "\n")
        rows = self.run_rows([self.task("../x")])
        self.assertIn("~75%", ANSI.sub("", rows["../x"]))

    def test_no_window_shows_tokens_only(self):
        rows = self.run_rows([self.task(contextWindowSize=None)])
        self.assertEqual(ANSI.sub("", rows["a1"]), "rev · ~150k · Review the diff")

    def test_no_figure_keeps_the_default_row(self):
        self.assertEqual(self.run_rows([self.task(tokenCount=0)]), {})

    # -- text and width ---------------------------------------------------

    def test_payload_text_cannot_inject_escapes_or_lines(self):
        rows = self.run_rows([self.task(name="a\x1b]0;x\x07\nb‮",
                                        description="d\x1b[2Je​")])
        plain = ANSI.sub("", rows["a1"])
        self.assertNotIn("\x1b]", rows["a1"])
        self.assertNotIn("\x1b[2J", rows["a1"])
        self.assertEqual(plain, "a ]0;x b · ~75% ~150k/200k · d [2Je")

    def test_row_is_cut_to_columns(self):
        long = "word " * 40
        for cols in (30, 45, 80):
            row = ANSI.sub("", self.run_rows([self.task(description=long)], columns=cols)["a1"])
            self.assertLessEqual(len(row), cols)
            self.assertTrue(row.endswith("…"))
            self.assertTrue(row.startswith("rev · ~75%"))

    def test_too_narrow_for_the_name_shows_the_fill_alone(self):
        row = ANSI.sub("", self.run_rows([self.task()], columns=16)["a1"])
        self.assertEqual(row, "~75% ~150k/200k")

    def test_no_name_starts_with_the_fill(self):
        row = ANSI.sub("", self.run_rows([self.task(name=None)])["a1"])
        self.assertEqual(row, "~75% ~150k/200k · Review the diff")

    # -- malformed input --------------------------------------------------

    def test_malformed_input_prints_nothing(self):
        for raw in ("", "not json", "[]", '{"tasks": "x"}', '{"tasks": [1, {"id": 3}]}'):
            self.assertEqual(self.run_rows(None, raw=raw), {})

    def test_zero_columns_draws_no_rows(self):
        self.assertEqual(self.run_rows([self.task()], columns=0), {})

    def test_many_tasks_are_bounded(self):
        rows = self.run_rows([self.task(f"a{i}") for i in range(100)])
        self.assertEqual(len(rows), 64)


class SubagentCachePrune(Hermetic):
    def test_old_cache_files_are_pruned_the_current_session_kept(self):
        sys.path.insert(0, HOOKS)
        import subagent_statusline as R
        d = os.path.join(self.cfg, "statusline", "subagents")
        os.makedirs(d)
        old = time.time() - 40 * 86400
        for sid in ("keep", "gone"):
            p = os.path.join(d, sid + ".json")
            with open(p, "w") as f:
                f.write("{}")
            os.utime(p, (old, old))
        with open(os.path.join(d, "fresh.json"), "w") as f:
            f.write("{}")
        self.assertEqual(R.prune(keep="keep"), 1)
        self.assertEqual(sorted(os.listdir(d)), ["fresh.json", "keep.json"])

    def test_session_start_prunes_the_cache(self):
        d = os.path.join(self.cfg, "statusline", "subagents")
        os.makedirs(d)
        p = os.path.join(d, "gone.json")
        with open(p, "w") as f:
            f.write("{}")
        old = time.time() - 40 * 86400
        os.utime(p, (old, old))
        r = subprocess.run([sys.executable, os.path.join(HOOKS, "session_start.py")],
                           input='{"session_id": "s"}', capture_output=True, text=True,
                           env=self.env, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(p))


class PluginDefault(unittest.TestCase):
    """The plugin settings.json default names the renderer through the
    current-hooks link hooks.json keeps on this version's hooks dir."""

    def test_settings_ship_only_subagent_status_line(self):
        with open(os.path.join(PLUGIN, "settings.json")) as f:
            s = json.load(f)
        self.assertEqual(list(s), ["subagentStatusLine"])  # agent / subagentStatusLine only
        self.assertEqual(s["subagentStatusLine"]["type"], "command")

    def test_command_reaches_the_renderer_through_current_hooks(self):
        with open(os.path.join(PLUGIN, "settings.json")) as f:
            cmd = json.load(f)["subagentStatusLine"]["command"]
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", cmd)  # not expanded in plugin settings
        m = re.fullmatch(r'python3 "\$\{CLAUDE_CONFIG_DIR:-\$HOME/\.claude\}'
                         r'/plugins/data/statusline-kmacmcfarlane/current-hooks/'
                         r'([a-z_]+\.py)"', cmd)
        self.assertIsNotNone(m, cmd)
        self.assertTrue(os.path.isfile(os.path.join(HOOKS, m.group(1))))
        with open(os.path.join(HOOKS, "hooks.json")) as f:
            link = json.load(f)["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn('ln -sfn "${CLAUDE_PLUGIN_ROOT}/hooks" "${CLAUDE_PLUGIN_DATA}/current-hooks"',
                      link)
        market = os.path.join(os.path.dirname(os.path.dirname(PLUGIN)),
                              ".claude-plugin", "marketplace.json")
        if os.path.isfile(market):      # in this repo; an installed copy has none
            with open(market) as f:
                self.assertEqual(json.load(f)["name"], "kmacmcfarlane")

    def test_command_runs_the_renderer(self):
        with open(os.path.join(PLUGIN, "settings.json")) as f:
            cmd = json.load(f)["subagentStatusLine"]["command"]
        import tempfile
        with tempfile.TemporaryDirectory() as cfg:
            data = os.path.join(cfg, "plugins", "data", "statusline-kmacmcfarlane")
            os.makedirs(data)
            os.symlink(HOOKS, os.path.join(data, "current-hooks"))
            env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, HOME=cfg)
            payload = {"session_id": "s", "transcript_path": os.path.join(cfg, "t.jsonl"),
                       "columns": 80, "tasks": [{"id": "a1", "tokenCount": 1000,
                                                 "contextWindowSize": 200_000}]}
            p = subprocess.run(["sh", "-c", cmd], input=json.dumps(payload),
                               capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual((p.returncode, p.stderr), (0, ""))
        self.assertEqual(json.loads(p.stdout)["id"], "a1")


if __name__ == "__main__":
    unittest.main()
