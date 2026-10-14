"""The decision page's progress bar sticks to the top of the viewport once scrolled past.

Read from `skills/decision-page/assets/index.html` as text (no node needed):

- the `.bar` rule holds `position:sticky`, `top:0`, a background from the colour tokens and
  a z-index, so cards scroll under it in either theme;
- the bar is a direct child of `.wrap`, not of `header`: a sticky element sticks only inside
  its parent, so inside the header it would scroll away with it;
- no ancestor of the bar (`html`, `body`, `.wrap`) sets `overflow`, which would stop it
  sticking to the viewport (a grouped selector such as `html,body` counts for each);
- a ResizeObserver keeps the scroll padding at the bar's height, so a card opened from a
  slug is not hidden under it (`scroll-padding-top` in the CSS is the fallback).

Each check runs on the real page (no problems) and on a mutated copy (a problem).

Run from the plugin dir: python3 -m unittest discover -s tests -q
"""

import re
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "skills" / "decision-page" / "assets" / "index.html"


def rules(html):
    """{selector: declarations} for each top-level rule in the page's <style> block."""
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    out = {}
    for sels, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        for sel in sels.split(","):
            out[sel.strip()] = out.get(sel.strip(), "") + ";" + body
    return out


def decls(body):
    return {k.strip(): v.strip() for k, _, v in
            (d.partition(":") for d in body.split(";") if ":" in d)}


def sticky_problems(html):
    out = []
    r = rules(html)
    bar = decls(r.get(".bar", ""))
    if bar.get("position") != "sticky":
        out.append(".bar is not position:sticky")
    if bar.get("top") not in ("0", "0px"):
        out.append(".bar has no top:0")
    if not bar.get("background", "").startswith("var(--"):
        out.append(".bar has no token background")
    if "z-index" not in bar:
        out.append(".bar has no z-index")
    for sel in ("html", "body", ".wrap"):
        if any(k.startswith("overflow") and k != "overflow-wrap" for k in decls(r.get(sel, ""))):
            out.append(sel + " sets overflow")
    if not re.search(r'new ResizeObserver\(.*?scrollPaddingTop.*?offsetHeight', html):
        out.append("no ResizeObserver keeps the scroll padding at the bar's height")
    body = html.split("</style>", 1)[1]
    header = re.search(r"<header>.*?</header>", body, re.S)
    if header and 'class="bar"' in header.group(0):
        out.append("the bar sits inside header")
    if not re.search(r'<div class="wrap">\s*<header>.*?</header>\s*<div class="bar">', body, re.S):
        out.append("the bar is not a child of .wrap right after the header")
    return out


class StickyBar(unittest.TestCase):
    def setUp(self):
        self.html = PAGE.read_text()

    def test_page(self):
        self.assertEqual(sticky_problems(self.html), [])

    def test_not_sticky(self):
        bad = self.html.replace("position:sticky;", "", 1)
        self.assertIn(".bar is not position:sticky", sticky_problems(bad))

    def test_no_background(self):
        bad = self.html.replace("z-index:5;background:var(--bg);", "z-index:5;", 1)
        self.assertIn(".bar has no token background", sticky_problems(bad))

    def test_overflow_ancestor(self):
        bad = self.html.replace(".wrap{", ".wrap{overflow:hidden;", 1)
        self.assertIn(".wrap sets overflow", sticky_problems(bad))

    def test_grouped_overflow(self):
        bad = self.html.replace("body{", "html,body{overflow-x:hidden}\nbody{", 1)
        self.assertIn("html sets overflow", sticky_problems(bad))

    def test_no_resize_observer(self):
        bad = self.html.replace("new ResizeObserver", "new Thing", 1)
        self.assertIn("no ResizeObserver keeps the scroll padding at the bar's height",
                      sticky_problems(bad))

    def test_bar_in_header(self):
        bar = re.search(r'  <div class="bar">.*?</div>\n', self.html, re.S).group(0)
        bad = self.html.replace(bar, "", 1).replace("  </header>", bar + "  </header>", 1)
        self.assertIn("the bar sits inside header", sticky_problems(bad))


if __name__ == "__main__":
    unittest.main()
