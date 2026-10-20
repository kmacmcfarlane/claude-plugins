"""The decision page's code block draws an excerpt verbatim, escaped, and never parsed.

An excerpt (`{text, lang?, src?}`, `references/cards-schema.md` § An excerpt) is the page's
first multi-line text: code, a log, a diff or test output. The finding body and the excerpt
attachment render through it. Its text is data, never markup and never instructions, so
these tests feed it hostile excerpts:

- an HTML tag (`</script>`, `<img onerror>`), quotes and entities come out escaped;
- a backtick, a `[[N]]` slug, an `https://` link and a code fence show as typed;
- line breaks and tabs are kept, CRLF read as one break, one trailing break dropped;
- a control or bidirectional character shows as a visible U+ tag;
- the text read back out of the block equals the text put in;
- `excerptProblem` refuses a malformed excerpt, and an injected `lang` never reaches the page.

`codeBlock`, `excerptProblem` and their helpers are loaded from `assets/index.html`'s page-free
part and run under node. Each check is also run against a mutated template (the text passed
through the page's mark renderer, or left unescaped), so a check that cannot fail does not pass
for one.

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import html
import json
import re
import subprocess
import sys
import unittest

from test_impact import NODE, page_free_script


def setUpModule():
    if not NODE:
        print("WARNING: node is not installed: the decision page's code-block tests "
              "(DecisionPageExcerpt) are skipped, so the excerpt renderer's escaping went "
              "untested", file=sys.stderr)


HARNESS = r"""
const xs = JSON.parse(require("fs").readFileSync(0, "utf8"));
REFS = {"41": {short: "upload limits", q: "q", a: "a", when: "w"}};
process.stdout.write(JSON.stringify(xs.map(x => ({p: excerptProblem(x), h: excerptProblem(x) ? "" : codeBlock(x)}))));
"""

# the one line that draws the text; the mutants swap its escaping out
TEXT_LINE = "const xcText=t=>esc(xcLines(t).join(\"\\n\"))"


def run(xs, script=None):
    src = (script or page_free_script()) + HARNESS
    out = subprocess.run([NODE, "-e", src], input=json.dumps(xs), capture_output=True,
                         text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr)
    return json.loads(out.stdout)


def body(h):
    """The inner HTML of the block's <code>."""
    m = re.search(r'<pre class="xpre"[^>]*><code>(.*)</code></pre></figure>$', h, re.S)
    assert m, h
    return m.group(1)


def read_back(h):
    """The text a reader sees: the markup-free body, its U+ tags back to their characters."""
    b = re.sub(r'<span class="xcc" title="U\+([0-9A-F]{4,6})">U\+\1</span>',
               lambda m: chr(int(m.group(1), 16)), body(h))
    return None if "<" in b else html.unescape(b)


HOSTILE = [
    "</script><script>alert(1)</script>",
    '<img src=x onerror="alert(1)">',
    "<a href=\"javascript:alert(1)\">x</a> & 'q' \"d\" &lt;",
    "see `rm -rf /` and [[41]] at https://example.com/a?b=1&c=2",
    "```js\nalert(1)\n```\n~~~\n````",
    "\nfirst line blank\n\tindented\r\nwindows\rold mac\n",
    "abc\u202eevil\u2066x\u200b\u0000\u0007y",
    "tag\U000e0001\U000e007f\U000e0100\U000e01ef\ufff9\ufffb\u034f\u115f\u1160\u3164\uffa0\u17b4\u17b5\u180b\u180fend",
]
# the invisible and bidirectional characters above: each must show as a U+ tag, never raw
INVISIBLE = set(HOSTILE[-2] + HOSTILE[-1]) - set("abcevilxytagend")


@unittest.skipUnless(NODE, "node is not installed")
class DecisionPageExcerpt(unittest.TestCase):

    def problems(self, script=None):
        """Every way the renderer fails the rules, over the hostile set."""
        out = []
        res = run([{"text": t, "lang": "js", "src": "src/up.py:40-52 at the merge base"}
                   for t in HOSTILE], script)
        for t, r in zip(HOSTILE, res):
            h = r["h"]
            if r["p"]:
                out.append("refused %r: %s" % (t, r["p"]))
                continue
            b = body(h)
            for bad in ("<script", "<img", "<a ", "<a>", "<code>", "slug", "<button"):
                if bad in b:
                    out.append("%r renders %s" % (t, bad))
            raw = sorted("U+%04X" % ord(c) for c in INVISIBLE if c in b)
            if raw:
                out.append("%r leaves %s raw" % (t, ", ".join(raw)))
            norm = t.replace("\r\n", "\n").replace("\r", "\n")
            norm = norm[:-1] if norm.endswith("\n") else norm
            if read_back(h) != norm:
                out.append("%r reads back as %r" % (t, read_back(h)))
        return out

    def test_hostile_excerpts_render_as_text(self):
        self.assertEqual(self.problems(), [])

    def test_mutants_fail(self):
        script = page_free_script()
        self.assertEqual(script.count(TEXT_LINE), 1)
        # the text through the page's mark renderer: backticks, slugs and links come alive
        marked = script.replace(TEXT_LINE, "const xcText=t=>fmtD(xcLines(t).join(\"\\n\"))")
        self.assertTrue(self.problems(marked))
        # the text unescaped: tags come alive
        raw = script.replace(TEXT_LINE, "const xcText=t=>String(xcLines(t).join(\"\\n\"))")
        self.assertTrue(self.problems(raw))
        # the control class without its astral ranges: tag characters slip through raw
        ctrl = script.count("\\u{E0000}-\\u{E007F}")
        self.assertEqual(ctrl, 1)
        narrow = script.replace("\\u{E0000}-\\u{E007F}", "")
        self.assertTrue(self.problems(narrow))

    def test_script_close_and_onerror_escaped(self):
        h = run([{"text": HOSTILE[0]}, {"text": HOSTILE[1]}])
        self.assertIn("&lt;/script&gt;&lt;script&gt;", h[0]["h"])
        self.assertNotIn("</script", h[0]["h"].lower())
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", h[1]["h"])

    def test_lines_and_tabs_kept(self):
        h = run([{"text": "a\r\n\tb\rc\n"}, {"text": "\nx"}])
        self.assertEqual(body(h[0]["h"]), "a\n\tb\nc")
        self.assertIn('data-lines="3"', h[0]["h"])
        # a leading break follows <code>, not <pre>, so the HTML parser keeps it
        self.assertEqual(body(h[1]["h"]), "\nx")
        self.assertIn('<pre class="xpre" tabindex="0" aria-label="Excerpt"><code>\n', h[1]["h"])

    def test_control_characters_shown(self):
        h = run([{"text": "a\u202eb\u200bc\u0000"}])[0]["h"]
        for u in ("U+202E", "U+200B", "U+0000"):
            self.assertIn('<span class="xcc" title="%s">%s</span>' % (u, u), h)
        self.assertNotIn("\u202e", h)

    def test_caption(self):
        h = run([{"text": "x"}, {"text": "x", "lang": "diff"},
                 {"text": "x", "src": "<b>[[41]]</b> `y` https://example.com"}])
        self.assertNotIn("figcaption", h[0]["h"])
        self.assertIn('<figcaption class="xch"><span class="pill cls">diff</span></figcaption>',
                      h[1]["h"])
        cap = h[2]["h"]
        self.assertIn("&lt;b&gt;[[41]]&lt;/b&gt; `y` https://example.com", cap)
        for bad in ("<b>", "slug", "<code>`", "<a "):
            self.assertNotIn(bad, cap.split("<pre")[0])
        self.assertIn('aria-label="Excerpt: &lt;b&gt;[[41]]&lt;/b&gt; `y` https://example.com"', cap)

    def test_problems(self):
        good = [{"text": "x"}, {"text": "a\nb", "lang": "c++", "src": "a.c:1-2"},
                {"text": "x", "lang": None, "src": None}]
        bad = [None, "text", ["x"], {}, {"text": ""}, {"text": "  \n"}, {"text": 3},
               {"text": "x", "lang": "\"><script>"}, {"text": "x", "lang": "a b"},
               {"text": "x", "lang": "x" * 25}, {"text": "x", "lang": 3},
               {"text": "x", "src": "a\nb"}, {"text": "x", "src": ""}, {"text": "x", "src": 3}]
        res = run(good + bad)
        self.assertEqual([r["p"] for r in res[:len(good)]], [""] * len(good))
        for x, r in zip(bad, res[len(good):]):
            self.assertTrue(r["p"], x)
            self.assertEqual(r["h"], "", x)

    def test_injected_lang_never_reaches_the_page(self):
        # a caller that skipped the check still gets an escaped label
        src = page_free_script() + r"""
process.stdout.write(JSON.stringify(codeBlock({text: "x", lang: '"><script>alert(1)</script>'})));
"""
        out = subprocess.run([NODE, "-e", src], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        h = json.loads(out.stdout)
        self.assertNotIn("<script", h)
        self.assertIn("&quot;&gt;&lt;script&gt;", h)


if __name__ == "__main__":
    unittest.main()
