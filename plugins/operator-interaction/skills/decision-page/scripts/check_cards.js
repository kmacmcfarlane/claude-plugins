#!/usr/bin/env node
/* decision-page pre-publish check (operator-interaction). Run on the working copy's cards.json
   before a publish: node check_cards.js path/to/cards.json

   1. the page's own check(): the template's page-free part, loaded from ../assets/index.html,
      so this refuses exactly what the page refuses;
   2. on a file that passes, lints: a card's flat part naming an id, a count or a named thing its
      context does not introduce, in the flat part and in the medium and high levels of the
      Impact line, the TLDR and the rec line (checked against Context's summary only); a TLDR
      bullet that may carry the recommendation; a leftover what. Then the depth lints (decision
      198, the sizes in references/cards-schema.md § Size, read at each part's top level): a
      visible part (Context, the Impact line, the TLDR, the rec line) without its medium or high
      level; a level not longer than the one below it; Background, an option's detail or the
      evidence thin or long; an option but (z) with no blocks row; a card long in all; a detail
      key the page does not show. Lints are proxies: each line says how to fix it, or the thing
      may be left knowingly.

   Prints one line per problem. Exit 0 clean; 1 on a refusal, or on a file or template that
   cannot be read; 2 on lint lines only. Node built-ins only; no stack trace reaches the output. */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

const END_MARK = "/* ---- end of the page-free part";
const fail = msg => { process.stdout.write("check_cards: " + msg + "\n"); process.exit(1); };
const why = e => String((e && e.message) || e).split("\n")[0];

/* the template's page-free part: the same slice the tests load */
function loadCheck() {
  const tpl = path.join(__dirname, "..", "assets", "index.html");
  let html;
  try { html = fs.readFileSync(tpl, "utf8"); } catch (e) { fail("cannot read the template " + tpl + ": " + why(e)); }
  const start = html.indexOf("<script>"), end = html.indexOf(END_MARK);
  if (start < 0 || end < start) fail("the template has no page-free part (its script or the end-of-page-free-part marker is missing): " + tpl);
  try {
    const page = vm.runInNewContext(html.slice(start + "<script>".length, end) + "\n;({check})", {});
    if (typeof page.check !== "function") throw new Error("no check()");
    return page.check;
  } catch (e) { fail("the template's page-free part does not load: " + why(e)); }
}

/* ---- the lints ---- */
const W = {two:2, three:3, four:4, five:5, six:6, seven:7, eight:8, nine:9, ten:10, eleven:11, twelve:12};
/* slugs, hex colours, dates and times, clock times and versions are neither ids nor counts */
const strip = s => s.replace(/\[\[[0-9]+\]\]/g, "").replace(/#[0-9a-fA-F]{3,8}\b/g, "")
  .replace(/\b\d{4}-\d{2}-\d{2}(T[0-9:.]+Z?)?\b/g, "").replace(/\b\d{1,2}:\d{2}\b/g, "").replace(/\bv?\d+(\.\d+)+\b/g, "");
/* an id or label a cold reader cannot resolve: a source label (OQ3, G5), a ticket key (KAPPA-3570), a hash or item tag (7c41e0d, 2ff6) */
const ID_TOKEN = /\b[A-Z]{1,3}[0-9]+[a-z]?\b|\b[A-Z][A-Z0-9]*-[0-9]+\b|\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{4,40}\b/g;
const ids = s => strip(s).match(ID_TOKEN) || [];
/* a count: not "two-way", not a duration, size or percentage, not the first number of "N of M" */
const UNIT = "(?:seconds?|minutes?|mins?|hours?|days?|weeks?|months?|years?|percent|ms|s|kb|mb|gb|tb)";
const COUNT = new RegExp("\\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|[0-9]+)\\b(?!-)(?!\\s*" + UNIT + "\\b)(?!\\s*%)(?!\\s+of\\s+[0-9]+)", "gi");
/* an id's digits are the id lint's, not a count */
const counts = s => [...strip(s).replace(ID_TOKEN, "").matchAll(COUNT)].map(m => ({word: m[1], n: W[m[1].toLowerCase()] || Number(m[1])}));
/* a named thing: "<word> mode|setting|…"; a determiner or count word before it is dropped, leaving the bare noun */
const DET = new Set(["the","this","that","these","those","each","every","a","an","its","our","your","their","any","no","one","which","whose","same","new","old"]);
const NAMED = /\b([a-z][a-z-]*)\s+(mode|setting|review|plan|document|doc|spec|policy|flag|profile|template|track|phase|stage)\b/gi;
const named = s => [...strip(s).matchAll(NAMED)].map(m => { const w = m[1].toLowerCase(); return DET.has(w) || W[w] ? m[2].toLowerCase() : (m[1] + " " + m[2]).toLowerCase(); });
/* the broad recommendation forms the page lets through: they may be someone else's. Rec as a
   whole word and recommend…, never Recent or Records */
const REC_BROAD = /^[^A-Za-z]*(rec|recommend\w*|suggest\w*)\b|\bwe\s+suggest\b/i;

/* the flat part a cold reader reads first: what context must introduce. Not the folds, act,
   the page lede or the layer notes */
function flat(c) {
  const out = [c.t];
  for (const k of ["effect", "wait", "reach", "undo", "cost"]) out.push(c.impact[k]);
  out.push(...c.tldr);
  for (const o of c.o) out.push(o[3], o[4]);
  for (const k of ["ifleft", "roundcosts", "ifunanswered", "reason", "unknown", "norec", "dep"]) out.push(c[k]);
  return out.filter(s => typeof s === "string");
}

/* ---- the depth lints (decision 198): sizes read at each part's top level, words split on whitespace ---- */
const words = x => x == null ? 0 : Array.isArray(x) ? x.reduce((n, s) => n + words(s), 0)
  : typeof x === "object" ? Object.values(x).reduce((n, s) => n + words(s), 0)
  : String(x).split(/\s+/).filter(Boolean).length;
const LEVEL = ["summary", "medium", "high"], DETAIL_NAME = ["more detail", "full detail"];
/* the parts a card shows, by their detail key; the first four are always visible */
const PART = {context: "Context", impact: "the Impact line", tldr: "the TLDR", rec: "the rec line",
  why: "Why now", whyask: "Why ask", dep: "Depends on", evidence: "the Evidence"};
const VISIBLE = ["context", "impact", "tldr", "rec"];
const levelsOf = (c, k) => c.detail && typeof c.detail === "object" && Array.isArray(c.detail[k]) ? c.detail[k] : [];
const optLevels = (c, k) => { const o = c.detail && typeof c.detail === "object" ? c.detail.o : null; return o && typeof o === "object" && Array.isArray(o[k]) ? o[k] : []; };
const topOf = (sum, ls) => ls.length ? ls[ls.length - 1] : sum;
const row = (c, k) => c.blocks && typeof c.blocks === "object" ? c.blocks[k] || null : null;

function depth(c, say) {
  const imp = c.impact;
  const summary = {context: c.context, impact: [imp.effect, imp.wait, imp.reach, imp.undo, imp.cost], tldr: c.tldr,
    rec: [c.reason, c.unknown], why: c.why, whyask: c.whyask, dep: c.dep, evidence: c.evidence};
  /* the visible parts toggle on every card (the operator's ask), so each carries a medium and a high */
  for (const k of VISIBLE) { const n = levelsOf(c, k).length;
    if (n < 2) say("level " + k, "depth: " + PART[k] + " has no " + (n ? "high level" : "medium or high level") + ": write " + (n ? "it" : "them") + " from the sources (the operator asked for every visible part to toggle), or leave it knowingly"); }
  /* a level replaces the one below it, so it says more */
  const grow = (name, key, sum, ls) => { const ws = [words(sum), ...ls.map(words)];
    for (let i = 1; i < ws.length; i++) if (ws[i] <= ws[i - 1])
      say("grow " + key + i, "depth: " + name + " " + LEVEL[i] + " is not longer than its " + LEVEL[i - 1] + " (" + ws[i] + " words against " + ws[i - 1] + "): each level is a fuller rendition of the one below it"); };
  for (const k in PART) grow(PART[k], k, summary[k], levelsOf(c, k));
  for (const o of c.o) grow("(" + o[0] + ")'s text", "o" + o[0], o[1], optLevels(c, o[0]));
  /* the 198 sizes, at the top level: Background ~150, each option ~60-120, Evidence ~150, a card ~600-900 */
  const bg = words(topOf(c.why, levelsOf(c, "why"))) + words(topOf(c.whyask, levelsOf(c, "whyask")));
  if (bg < 60) say("bg", "depth: Background is " + bg + " words at its fullest: write Why now and Why ask near 150 together, from the record and the work behind it, or leave it knowingly on a small call; never pad");
  else if (bg > 225) say("bg", "depth: Background is " + bg + " words at its fullest: keep Why now and Why ask near 150 together");
  let optWords = 0;
  for (const o of c.o) {
    const k = o[0], top = words(topOf(o[1], optLevels(c, k))), r = row(c, k);
    if (k === "z") { optWords += top + words(o[2]); continue; }
    if (!r && !c.warn) say("row " + k, "depth: (" + k + ") has no blocks row: give it happens, who, undo and cost");
    const ow = top + (r ? words([r.happens, r.who, r.undo, r.cost]) : 0);
    optWords += ow + words(o[2]);
    if (ow < 30) say("opt " + k, "depth: (" + k + ")'s detail is " + ow + " words (its fullest text and its blocks row): write it near 60–120, what happens, undo, who and cost, from the sources; or leave it knowingly");
    else if (ow > 180) say("opt " + k, "depth: (" + k + ")'s detail is " + ow + " words (its fullest text and its blocks row): keep it near 60–120");
  }
  const ev = words(topOf(c.evidence, levelsOf(c, "evidence")));
  if (c.basis !== "none" && ev < 60) say("ev", "depth: evidence is " + ev + " words at its fullest: give the basis drill-down near 150, what was observed, inferred and assumed, with the paths and links behind each; or leave it knowingly");
  else if (ev > 225) say("ev", "depth: evidence is " + ev + " words at its fullest: keep it near 150");
  /* the card in all: the flat part and Context at their summary, the fold parts at their top level, each option's impact; not act */
  const all = words(flat(c)) + words(c.context) + bg + ev + optWords;
  if (all > 1350) say("all", "depth: the card is " + all + " words in all: keep it near 600–900; a small call gets a short card");
  if (c.detail && typeof c.detail === "object")
    for (const k of Object.keys(c.detail)) if (!(k in PART) && k !== "o")
      say("key " + k, "depth: detail." + k + " is not a part the page shows, so it is ignored: the parts are " + Object.keys(PART).join(", ") + " and o");
}

function lint(d) {
  const out = [];
  for (const c of d.cards) {
    const w = "lint: card " + c.n + ": ";
    const hasWhat = typeof c.what === "string" && c.what.trim();
    const ctx = c.context + (hasWhat ? " " + c.what : "");
    const ctxIds = new Set(ids(ctx)), ctxNums = new Set(counts(ctx).map(x => x.n)), ctxLow = ctx.toLowerCase();
    const seen = new Set(), say = (key, line) => { if (!seen.has(key)) { seen.add(key); out.push(w + line); } };
    /* the terms a text uses, against Context's summary; at is "" for the flat part, or " (part, level)" */
    const terms = (fields, at) => {
      for (const s of fields) for (const t of ids(s)) if (!ctxIds.has(t))
        say("id " + t, t + at + " is not introduced in its context: say in plain words what it is, the id after the words; or leave it if a reader of this page knows it");
      for (const s of fields) for (const x of counts(s)) if (!ctxNums.has(x.n))
        say("count " + x.n, "\"" + x.word + "\"" + at + " counts things its context does not name: say what the " + x.word + " things are, or list them, in context");
      for (const s of fields) for (const t of named(s)) if (!ctxLow.includes(t))
        say("named " + t, "\"" + t + "\"" + at + " is not glossed in its context: give it a one-line gloss in context, what it is and where it comes from");
    };
    terms(flat(c), "");
    c.tldr.forEach((b, i) => { if (REC_BROAD.test(b))
      say("tldr " + i, "tldr bullet " + (i + 1) + " may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); });
    /* the visible parts' medium and high: each steps alone, so the Context beside them may be its summary */
    const flatText = x => Array.isArray(x) ? x.flatMap(flatText) : x && typeof x === "object" ? Object.values(x).flatMap(flatText) : typeof x === "string" ? [x] : [];
    for (const k of ["impact", "tldr", "rec"]) levelsOf(c, k).forEach((r, i) => terms(flatText(r), " (" + PART[k] + ", " + DETAIL_NAME[i] + ")"));
    levelsOf(c, "tldr").forEach((bs, m) => Array.isArray(bs) && bs.forEach((b, i) => { if (REC_BROAD.test(b))
      say("tldr " + m + "." + i, "tldr bullet " + (i + 1) + " (" + DETAIL_NAME[m] + ") may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); }));
    if (hasWhat) say("what", "what present: move it into context (after the terms, before the cue) and delete it");
    depth(c, say);
  }
  return out;
}

/* ---- the run ---- */
const check = loadCheck();
const file = process.argv[2];
if (!file) fail("usage: node check_cards.js path/to/cards.json");
let text, d;
try { text = fs.readFileSync(file, "utf8"); } catch (e) { fail("cannot read " + file + ": " + why(e)); }
try { d = JSON.parse(text); } catch (e) { fail("not valid JSON: " + why(e)); }
let bad;
try { bad = check(d); } catch (e) { fail("the page's check stopped on this file: " + why(e)); }
if (bad.length) { process.stdout.write(bad.join("\n") + "\n"); process.exit(1); }
let lines;
try { lines = lint(d); } catch (e) { fail("the lints stopped on this file: " + why(e)); }
if (lines.length) { process.stdout.write(lines.join("\n") + "\n"); process.exit(2); }
process.exit(0);
