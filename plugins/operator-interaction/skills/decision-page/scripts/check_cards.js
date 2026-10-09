#!/usr/bin/env node
/* decision-page pre-publish check (operator-interaction). Run on the working copy's cards.json
   before a publish: node check_cards.js path/to/cards.json

   1. the page's own check(): the template's page-free part, loaded from ../assets/index.html,
      so this refuses exactly what the page refuses;
   2. on a file that passes, lints, each line saying how to fix it, or that the thing may be left
      knowingly:
      - ids: a machine-readable id anywhere the page shows text (every card field and level, act,
        the page title, the lede, the layer titles and notes, refs), whatever Context says; the
        page is the reader's only context. Backtick spans, https links and slugs are not ids;
      - terms: a count or a named thing in the flat part, or in the medium and high levels of the
        Impact, the TLDR and the rec line, that Context's summary does not introduce;
      - the TLDR: a bullet that may carry the recommendation, at every level, headings, bullets
        and sub-bullets in reading order; a leftover what;
      - shapes: summaries a sentence or two (the TLDR one or two bullets, an Impact facet a line),
        medium terse bullets with a sub-bullet or two, high headed sections; the Impact's medium
        one bullet per facet;
      - a card Impact effect that reads as the recommended option's alone;
      - depth (decision 198, the sizes in references/cards-schema.md § Size, read at each part's
        top level; levels are optional on every part, decision 201): a level not longer than the
        one below it; Background, an option's detail or the evidence thin where it carries
        levels, or long; an option but (z) with no blocks row; a card long in all; a detail key
        the page does not show.
      Lints are proxies.

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
/* neither ids nor counts: backtick spans (a path, command or name the operator types), https links,
   slugs, hex colours (never a #tag after an id noun: item #4151 stays), dates and times, clock times
   and versions */
const ID_NOUN = "(?:work item|item|commit|ticket|decision|answer|card)s?";
const strip = s => s.replace(/`[^`]*`/g, " ").replace(/https:\/\/\S+/g, " ").replace(/\[\[[0-9]+\]\]/g, "")
  .replace(new RegExp("(?<!\\b" + ID_NOUN + "\\s+)#[0-9a-fA-F]{3,8}\\b", "gi"), "")
  .replace(/\b\d{4}-\d{2}-\d{2}(T[0-9:.]+Z?)?\b/g, "").replace(/\b\d{1,2}:\d{2}\b/g, "").replace(/\bv?\d+(\.\d+)+\b/g, "");
/* an id or label a cold reader cannot resolve: a source label (OQ3, G5), a ticket key (KAPPA-3570), a hash or item tag (7c41e0d, 2ff6) */
const ID_TOKEN = /\b[A-Z]{1,3}[0-9]+[a-z]?\b|\b[A-Z][A-Z0-9]*-[0-9]+\b|\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{4,40}\b/g;
/* a work-item id: kebab-case, three or more segments, a four-hex suffix holding a digit */
const KEBAB_ID = /\b[a-z0-9]+(?:-[a-z0-9]+){2,}-(?=[0-9a-f]{0,3}[0-9])[0-9a-f]{4}\b/g;
/* an id after a noun: work item 4151, commit 8ea8a3c, item #4151; a year is not one (item 2026) */
const NOUN_ID = /\b(?:work item|item|commit|ticket)s?\s+#?((?=[0-9a-f]*[0-9])[0-9a-f]{4,40})\b/gi;
/* a decision by number: decision 151, answer 201; not "answer 2 questions", "card 3 of 5" or a duration */
const UNIT = "(?:seconds?|minutes?|mins?|hours?|days?|weeks?|months?|years?|percent|ms|s|kb|mb|gb|tb)";
const DECISION_ID = new RegExp("\\b(decision|answer|card)s?\\s+#?(\\d+)\\b(?!\\s+of\\s+\\d)(?!\\s*" + UNIT + "\\b)(\\s+[a-z]+)?", "gi");
const YEAR = /^(19|20)\d\d$/;
/* every id in a text: [token, a decision number or null] */
function ids(s) {
  const t = strip(s), out = [];
  for (const m of t.matchAll(ID_TOKEN)) out.push([m[0], null]);
  for (const m of t.matchAll(KEBAB_ID)) out.push([m[0], null]);
  for (const m of t.matchAll(NOUN_ID)) if (!(/^\d+$/.test(m[1]) && YEAR.test(m[1]))) out.push([m[0].replace(/\s+/g, " "), null]);
  for (const m of t.matchAll(DECISION_ID)) {
    /* "answer" followed by a word is the verb: answer 2 questions */
    if (m[1].toLowerCase() === "answer" && m[3]) continue;
    out.push([(m[0].slice(0, m[0].length - (m[3] || "").length)).replace(/\s+/g, " "), m[2]]);
  }
  /* a bracketed tag: a four-digit token in ( … ) that is not a year, nor a number before a unit (1500 ms) */
  for (const m of t.matchAll(/\(([^()]{1,60})\)/g)) {
    const toks = m[1].split(/[\s,;]+/).filter(Boolean);
    toks.forEach((tok, i) => { if (/^\d{4}$/.test(tok) && !YEAR.test(tok) && !new RegExp("^" + UNIT + "$", "i").test(toks[i + 1] || ""))
      out.push(["(" + tok + ")", null]); });
  }
  const seen = new Set();
  return out.filter(([x]) => !seen.has(x) && seen.add(x));
}
const ID_ALL = [ID_TOKEN, KEBAB_ID, NOUN_ID, new RegExp(DECISION_ID.source.replace("(\\s+[a-z]+)?", ""), "gi")];
const unId = s => ID_ALL.reduce((t, r) => t.replace(r, " "), strip(s));
/* a count: not "two-way", not a duration, size or percentage, not the first number of "N of M" */
const COUNT = new RegExp("\\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|[0-9]+)\\b(?!-)(?!\\s*" + UNIT + "\\b)(?!\\s*%)(?!\\s+of\\s+[0-9]+)", "gi");
/* an id's digits are the id lint's, not a count */
const counts = s => [...unId(s).matchAll(COUNT)].map(m => ({word: m[1], n: W[m[1].toLowerCase()] || Number(m[1])}));
/* a named thing: "<word> mode|setting|…"; a determiner or count word before it is dropped, leaving the bare noun */
const DET = new Set(["the","this","that","these","those","each","every","a","an","its","our","your","their","any","no","one","which","whose","same","new","old"]);
const NAMED = /\b([a-z][a-z-]*)\s+(mode|setting|review|plan|document|doc|spec|policy|flag|profile|template|track|phase|stage)\b/gi;
const named = s => [...strip(s).matchAll(NAMED)].map(m => { const w = m[1].toLowerCase(); return DET.has(w) || W[w] ? m[2].toLowerCase() : (m[1] + " " + m[2]).toLowerCase(); });
/* the broad recommendation forms the page lets through: they may be someone else's. Rec as a
   whole word and recommend…, never Recent or Records */
const REC_BROAD = /^[^A-Za-z]*(rec|recommend\w*|suggest\w*)\b|\bwe\s+suggest\b/i;

/* the flat part a cold reader reads first: what context must introduce, for counts and named things */
function flat(c) {
  const out = [c.t];
  for (const k of ["effect", "wait", "reach", "undo", "cost"]) out.push(c.impact[k]);
  out.push(...c.tldr);
  for (const o of c.o) out.push(o[3], o[4]);
  for (const k of ["ifleft", "roundcosts", "ifunanswered", "reason", "unknown", "norec", "dep"]) out.push(c[k]);
  return out.filter(s => typeof s === "string");
}
/* every text in a value, in reading order: a section's heading, then each bullet and its sub-bullets */
const textsOf = x => typeof x === "string" ? [x] : Array.isArray(x) ? x.flatMap(textsOf)
  : x && typeof x === "object" ? ("h" in x ? [x.h, ...textsOf(x.b)] : "t" in x ? [x.t, ...textsOf(x.sub || [])] : Object.values(x).flatMap(textsOf)) : [];

/* ---- the shape lints (the level shapes: summary a sentence or two, medium terse bullets, high sections) ---- */
const words = x => x == null ? 0 : Array.isArray(x) ? x.reduce((n, s) => n + words(s), 0)
  : typeof x === "object" ? Object.values(x).reduce((n, s) => n + words(s), 0)
  : String(x).split(/\s+/).filter(Boolean).length;
/* sentences: a stop (. ! ?) then whitespace then a capital, digit, backtick, [ or (; backtick spans,
   links, e.g., i.e., etc., vs. and the dots of a version or decimal never end one */
const sentences = s => String(s).replace(/`[^`]*`/g, "x").replace(/https:\/\/\S+/g, "u")
  .replace(/\b(e\.g|i\.e|etc|vs|cf)\./gi, "$1").replace(/(\d)\.(\d)/g, "$1$2")
  .split(/(?<=[.!?])\s+(?=[A-Z0-9`\[(])/).filter(x => x.trim()).length;
const isSecs = v => Array.isArray(v) && v.length > 0 && v.every(x => x && typeof x === "object" && !Array.isArray(x) && "h" in x);
const TERSE = 14, SUB_CAP = 2, MEDIUM_CAP = 6;
const LEVEL = ["summary", "medium", "high"], DETAIL_NAME = ["more detail", "full detail"];
/* the parts a card shows, by their detail key; the first four are always visible */
const PART = {context: "Context", impact: "the Impact line", tldr: "the TLDR", rec: "the rec line",
  why: "Why now", whyask: "Why ask", dep: "Depends on", evidence: "the Evidence"};
const FACETS = ["effect", "wait", "reach", "undo", "cost"];
const levelsOf = (c, k) => c.detail && typeof c.detail === "object" && Array.isArray(c.detail[k]) ? c.detail[k] : [];
const optLevels = (c, k) => { const o = c.detail && typeof c.detail === "object" ? c.detail.o : null; return o && typeof o === "object" && Array.isArray(o[k]) ? o[k] : []; };

function shapes(c, say) {
  const sh = (key, line) => say("shape " + key, "shape: " + line);
  const terse = (where, s) => { const n = words(s), k = sentences(s);
    if (k > 1 || n > TERSE) sh(where, where + " is " + (k > 1 ? k + " sentences" : n + " words") + ": keep a bullet at this level a terse fragment, one point in about " + TERSE + " words; full sentences belong at full detail"); };
  /* the visible summaries, always */
  const cs = sentences(c.context), cw = words(c.context);
  if (cs > 2 || cw > 60) sh("ctx", "Context's summary is " + (cs > 2 ? cs + " sentences" : cw + " words") + ": keep it to one or two sentences, about 60 words, with the terms the card uses; move the rest to its levels, or leave it knowingly");
  if (c.tldr.length > 2) sh("tldr n", "the TLDR has " + c.tldr.length + " bullets: keep it to one or two terse bullets");
  c.tldr.forEach((b, i) => terse("TLDR bullet " + (i + 1), b));
  for (const k of FACETS) if (typeof c.impact[k] === "string" && words(c.impact[k]) > 16)
    sh("imp " + k, "Impact " + k + " is " + words(c.impact[k]) + " words: keep each facet on its line to about 16; its detail goes in the Impact's levels");
  /* a fold part's summary, where the part carries levels (a part with none is a small call's whole text) */
  const fold = (name, key, sum, ls) => { if (ls.length && sum != null && sentences(textsOf(sum).join(" ")) > 2)
    sh("sum " + key, name + "'s summary is " + sentences(textsOf(sum).join(" ")) + " sentences: keep it to one or two; its levels carry the rest"); };
  for (const k of ["why", "whyask", "dep", "evidence"]) fold(PART[k], k, c[k], levelsOf(c, k));
  for (const o of c.o) fold("(" + o[0] + ")'s text", "o" + o[0], o[1], optLevels(c, o[0]));
  /* medium, terse bullets with a sub-bullet or two; high, headed sections */
  const medium = (name, m) => {
    if (typeof m === "string") return sh(name + " m", name + " more detail is prose: write it as terse bullets, with a sub-bullet or two where they help");
    if (isSecs(m)) return sh(name + " m", name + " more detail is in sections: save sections for full detail, and write more detail as terse bullets");
    if (m.length > MEDIUM_CAP) sh(name + " mn", name + " more detail has " + m.length + " bullets: keep it to about " + MEDIUM_CAP);
    m.forEach((b, i) => { const t = typeof b === "string" ? b : b.t, sub = typeof b === "string" ? [] : b.sub || [];
      terse(name + " more detail bullet " + (i + 1), t);
      if (sub.length > SUB_CAP) sh(name + " sub " + i, name + " more detail bullet " + (i + 1) + " has " + sub.length + " sub-bullets: give a bullet one or two, or split it");
      sub.forEach((x, j) => terse(name + " more detail bullet " + (i + 1) + "." + (j + 1), x)); });
  };
  const high = (name, h) => { if (!isSecs(h)) sh(name + " h", name + " full detail is not in sections: give full detail as headed sections with bullets"); };
  for (const k of ["context", "tldr", "rec", "why", "whyask", "dep", "evidence"]) {
    const ls = levelsOf(c, k);
    if (ls[0] != null) medium(PART[k], ls[0]);
    if (ls[1] != null) high(PART[k], ls[1]);
  }
  for (const o of c.o) { const ls = optLevels(c, o[0]);
    if (ls[0] != null) medium("(" + o[0] + ")'s text", ls[0]);
    if (ls[1] != null) high("(" + o[0] + ")'s text", ls[1]); }
  /* the Impact's medium: one bullet per facet, the options in its sub-bullets; its high renders as facet sections */
  const im = levelsOf(c, "impact")[0];
  if (im && typeof im === "object") for (const k of FACETS) { const v = im[k]; if (v == null) continue;
    const at = "the Impact's more detail, " + k;
    if (Array.isArray(v)) { sh("imp m " + k, at + ", is a list: give each facet one bullet, and put the options in its sub-bullets"); continue; }
    const t = typeof v === "string" ? v : v.t, sub = typeof v === "string" ? [] : v.sub || [];
    terse(at, t);
    if (sub.length > SUB_CAP) sh("imp sub " + k, at + ", has " + sub.length + " sub-bullets: give a facet one or two; where it differs across more than two options, group them ((a) and (b): …)");
    sub.forEach((x, j) => terse(at + ", sub-bullet " + (j + 1), x));
  }
}

/* ---- the rec-only effect lint: the card's Impact is the decision's across its options ---- */
const STOP = new Set("a an the and or of to in on for is are be it its this that from with by at as no not one any who what can".split(" "));
const toks = s => new Set((String(s).toLowerCase().replace(/\[\[[0-9]+\]\]/g, "").match(/[a-z0-9]+/g) || []).filter(w => !STOP.has(w) && w.length > 2));
const share = (e, r) => { const E = toks(e), R = toks(r); if (!E.size) return 0; let n = 0; for (const w of E) if (R.has(w)) n++; return n / E.size; };
function recOnly(c, say) {
  if (!c.rec) return;
  const optText = o => [o[2], o[3], o[4], ((c.blocks && c.blocks[o[0]]) || {}).happens || ""].join(" ");
  const r = c.o.find(o => o[0] === c.rec), others = c.o.filter(o => o[0] !== c.rec && o[0] !== "z");
  const effects = [["", c.impact.effect], ...levelsOf(c, "impact").map((l, i) => [" (" + DETAIL_NAME[i] + ")", l && typeof l === "object" ? textsOf(l.effect).join(" ") : ""])];
  for (const [at, e] of effects) {
    if (!e) continue;
    const sr = share(e, optText(r)), so = Math.max(0, ...others.map(o => share(e, optText(o))));
    if ((e.match(/\([a-y]\)/g) || []).length < 2 && sr >= 0.4 && sr - so >= 0.25)
      say("rec-only" + at, "impact: the effect" + at + " reads as the recommended option's (\"" + e.slice(0, 60) + "\"): say what the decision changes across its options; each option's effect is in its blocks row");
  }
}

/* ---- the depth lints (decision 198): sizes read at each part's top level, words split on whitespace ---- */
const topOf = (sum, ls) => ls.length ? ls[ls.length - 1] : sum;
const row = (c, k) => c.blocks && typeof c.blocks === "object" ? c.blocks[k] || null : null;

function depth(c, say) {
  const imp = c.impact;
  const summary = {context: c.context, impact: [imp.effect, imp.wait, imp.reach, imp.undo, imp.cost], tldr: c.tldr,
    rec: [c.reason, c.unknown], why: c.why, whyask: c.whyask, dep: c.dep, evidence: c.evidence};
  /* a level replaces the one below it, so it says more */
  const grow = (name, key, sum, ls) => { const ws = [words(sum), ...ls.map(words)];
    for (let i = 1; i < ws.length; i++) if (ws[i] <= ws[i - 1])
      say("grow " + key + i, "depth: " + name + " " + LEVEL[i] + " is not longer than its " + LEVEL[i - 1] + " (" + ws[i] + " words against " + ws[i - 1] + "): each level is a fuller rendition of the one below it"); };
  for (const k in PART) grow(PART[k], k, summary[k], levelsOf(c, k));
  for (const o of c.o) grow("(" + o[0] + ")'s text", "o" + o[0], o[1], optLevels(c, o[0]));
  /* the 198 sizes, at the top level: Background ~150, each option ~60-120, Evidence ~150, a card ~600-900.
     Levels scale with the decision (201): a part with none may stay short, so thin is linted only where
     the writer gave levels; long is linted everywhere */
  const bg = words(topOf(c.why, levelsOf(c, "why"))) + words(topOf(c.whyask, levelsOf(c, "whyask")));
  const bgLv = levelsOf(c, "why").length + levelsOf(c, "whyask").length > 0;
  if (bgLv && bg < 60) say("bg", "depth: Background is " + bg + " words at its fullest: write Why now and Why ask near 150 together, from the record and the work behind it, or leave it knowingly; never pad");
  else if (bg > 225) say("bg", "depth: Background is " + bg + " words at its fullest: keep Why now and Why ask near 150 together");
  let optWords = 0;
  for (const o of c.o) {
    const k = o[0], top = words(topOf(o[1], optLevels(c, k))), r = row(c, k);
    if (k === "z") { optWords += top + words(o[2]); continue; }
    if (!r && !c.warn) say("row " + k, "depth: (" + k + ") has no blocks row: give it happens, who, undo and cost");
    const ow = top + (r ? words([r.happens, r.who, r.undo, r.cost]) : 0);
    optWords += ow + words(o[2]);
    if (optLevels(c, k).length && ow < 30) say("opt " + k, "depth: (" + k + ")'s detail is " + ow + " words (its fullest text and its blocks row): write it near 60–120, what happens, undo, who and cost, from the sources; or leave it knowingly");
    else if (ow > 180) say("opt " + k, "depth: (" + k + ")'s detail is " + ow + " words (its fullest text and its blocks row): keep it near 60–120");
  }
  const ev = words(topOf(c.evidence, levelsOf(c, "evidence")));
  if (levelsOf(c, "evidence").length && c.basis !== "none" && ev < 60) say("ev", "depth: evidence is " + ev + " words at its fullest: give the basis drill-down near 150, what was observed, inferred and assumed, with the paths and links behind each; or leave it knowingly");
  else if (ev > 225) say("ev", "depth: evidence is " + ev + " words at its fullest: keep it near 150");
  /* the card in all: the flat part and Context at their summary, the fold parts at their top level, each option's impact; not act */
  const all = words(flat(c)) + words(c.context) + bg + ev + optWords;
  if (all > 1350) say("all", "depth: the card is " + all + " words in all: keep it near 600–900; a small call gets a short card");
  if (c.detail && typeof c.detail === "object")
    for (const k of Object.keys(c.detail)) if (!(k in PART) && k !== "o")
      say("key " + k, "depth: detail." + k + " is not a part the page shows, so it is ignored: the parts are " + Object.keys(PART).join(", ") + " and o");
}

/* ---- the id lint: no machine-readable id anywhere the page shows text; the page is the reader's only context ---- */
const idLine = ([t, n], at) => t + " looks like an id (" + at + "): "
  + (n ? "name the decision by its slug [[" + n + "]]" : "name the thing by its short name or title, a decision by its slug [[N]]")
  + "; the page is the reader's only context; leave it if it is a term the reader knows (S3, UTF-8)";
/* the texts a card shows, by part: everything but rev, n, L and the option letters */
function cardTexts(c) {
  const out = [];
  const put = (at, v) => { for (const s of textsOf(v)) out.push([at, s]); };
  for (const k of ["t", "context", "what", "class", "why", "whyask", "dep", "ifleft", "roundcosts", "ifunanswered", "reason", "unknown", "norec", "evidence"]) put(k, c[k]);
  put("impact", c.impact); put("tldr", c.tldr);
  for (const o of c.o) put("(" + o[0] + ")", o.slice(1));
  if (c.blocks && typeof c.blocks === "object") for (const k in c.blocks) put("blocks (" + k + ")", c.blocks[k]);
  if (c.act && typeof c.act === "object") for (const k in c.act) put("act (" + k + ")", c.act[k]);
  if (c.detail && typeof c.detail === "object") for (const k in c.detail)
    if (k === "o" && c.detail.o && typeof c.detail.o === "object") { for (const x in c.detail.o) put("detail.o." + x, c.detail.o[x]); }
    else put("detail." + k, c.detail[k]);
  return out;
}
function pageIds(d, out) {
  const say = line => out.push("lint: page: " + line), seen = new Set();
  const look = (at, s) => { if (typeof s === "string") for (const x of ids(s)) if (!seen.has(at + x[0])) { seen.add(at + x[0]); say(idLine(x, at)); } };
  const pg = d.page && typeof d.page === "object" ? d.page : {};
  look("the page title", pg.title); look("the lede", pg.lede);
  for (const l of d.layers) { look("layer " + l[0] + "'s title", l[1]); look("layer " + l[0] + "'s note", l[2]); }
  for (const k in (d.refs || {})) { const r = d.refs[k] || {};
    look("refs " + k + " short", r.short); look("refs " + k + " q", r.q);
    if (typeof r.a === "string") for (const x of ids(r.a))
      say("refs " + k + " a holds " + x[0] + ", which looks like an id: if these are the operator's own words, leave them as given; otherwise name the thing"); }
}

function lint(d) {
  const out = [];
  pageIds(d, out);
  for (const c of d.cards) {
    const w = "lint: card " + c.n + ": ";
    const hasWhat = typeof c.what === "string" && c.what.trim();
    const ctx = c.context + (hasWhat ? " " + c.what : "");
    const ctxNums = new Set(counts(ctx).map(x => x.n)), ctxLow = ctx.toLowerCase();
    const seen = new Set(), say = (key, line) => { if (!seen.has(key)) { seen.add(key); out.push(w + line); } };
    for (const [at, s] of cardTexts(c)) for (const x of ids(s)) say("id " + x[0], idLine(x, at));
    /* the terms a visible text uses, against Context's summary; at is "" for the flat part, or " (part, level)" */
    const terms = (fields, at) => {
      for (const s of fields) for (const x of counts(s)) if (!ctxNums.has(x.n))
        say("count " + x.n, "\"" + x.word + "\"" + at + " counts things its context does not name: say what the " + x.word + " things are, or list them, in context");
      for (const s of fields) for (const t of named(s)) if (!ctxLow.includes(t))
        say("named " + t, "\"" + t + "\"" + at + " is not glossed in its context: give it a one-line gloss in context, what it is and where it comes from");
    };
    terms(flat(c), "");
    c.tldr.forEach((b, i) => { if (REC_BROAD.test(b))
      say("tldr " + i, "tldr bullet " + (i + 1) + " may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); });
    /* the visible parts' medium and high: each steps alone, so the Context beside them may be its summary */
    for (const k of ["impact", "tldr", "rec"]) levelsOf(c, k).forEach((r, i) => terms(textsOf(r), " (" + PART[k] + ", " + DETAIL_NAME[i] + ")"));
    /* a TLDR level's headings, bullets and sub-bullets, numbered in reading order as the page numbers them */
    levelsOf(c, "tldr").forEach((bs, m) => textsOf(bs).forEach((b, i) => { if (REC_BROAD.test(b))
      say("tldr " + m + "." + i, "tldr bullet " + (i + 1) + " (" + DETAIL_NAME[m] + ") may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); }));
    if (hasWhat) say("what", "what present: move it into context (after the terms, before the cue) and delete it");
    shapes(c, say);
    recOnly(c, say);
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
