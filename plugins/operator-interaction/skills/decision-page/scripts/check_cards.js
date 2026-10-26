#!/usr/bin/env node
/* decision-page pre-publish check (operator-interaction). Run on the working copy's cards.json
   before a publish, or on one card record before it is raised:

     node check_cards.js path/to/cards.json
     node check_cards.js --record path/to/record.json

   1. the page's own check(): the template's page-free part, loaded from ../assets/index.html,
      so this refuses exactly what the page refuses (decision-page/5, each card a decision-card/5
      record plus L and dep). With --record, the card checks alone (no layer, no slug check), and
      the page-only L and dep refused in a record;
   2. on a file that passes, lints, each line saying how to fix it, or that the thing may be left
      knowingly:
      - ids: a machine-readable id anywhere the page shows text (every card field and level, act,
        the page title, the lede, the layer titles and notes, refs), whatever Context says; the
        page is the reader's only context. Backtick spans, https links and slugs are not ids;
      - terms: a count or a named thing in the flat part, or in the medium and high levels of the
        Impact and the TLDR, that Context's summary (with its bundle's shared context)
        does not introduce;
      - groups: a bundle (a layer with shared context) holding fewer than two cards;
      - the TLDR: a bullet that may carry the recommendation, at every level, headings, bullets
        and sub-bullets in reading order; a leftover what;
      - the Background fold's summary: the first sentence of why past BGSUM_CAP words;
      - shapes: summaries a sentence or two (the TLDR one or two bullets, an Impact facet a line),
        medium terse bullets with a sub-bullet or two, high headed sections; the Impact's medium
        one bullet per facet;
      - an Impact reach that reads as the recommended option's alone;
      - the mechanism: an option's effect of a bare label, MECH_MIN words or fewer (rule 268);
      - the system: a process phrase (a review comment, another round, your time, a blocked
        session) in an option's effect or reach, or the Impact's reach, which describe the thing
        the work builds (rule 259);
      - depth (decision 198, the sizes in references/cards-schema.md § Size, read at each part's
        top level; levels are optional on every part, decision 201): a level not longer than the
        one below it; Background, an option's detail or the evidence thin where it carries
        levels, or long; an option but (z) with no reach; a card long in all; a detail key the
        page does not show; what a new card owes (why, whyask, reason) missing; a card with a
        recommendation and no assumptions (assume);
      - one-way options: a ⚠ card with no option flagged oneway; a flagged option while the
        Impact carries no undo;
      - trade-offs: an option but (z) with no one-line pro or con (the inline Pros and Cons rows);
        a recommended option with no con; a card with two or more real options and none.
      Lints are proxies.

   Prints one line per problem. Exit 0 clean; 1 on a refusal, or on a file or template that
   cannot be read; 2 on lint lines only. Node built-ins only; no stack trace reaches the output. */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

const END_MARK = "/* ---- end of the page-free part";
const fail = msg => { process.stdout.write("check_cards: " + msg + "\n"); process.exit(1); };
const why = e => String((e && e.message) || e).split("\n")[0];

/* the template's page-free part: the same slice the tests load */
function loadPage() {
  const tpl = path.join(__dirname, "..", "assets", "index.html");
  let html;
  try { html = fs.readFileSync(tpl, "utf8"); } catch (e) { fail("cannot read the template " + tpl + ": " + why(e)); }
  const start = html.indexOf("<script>"), end = html.indexOf(END_MARK);
  if (start < 0 || end < start) fail("the template has no page-free part (its script or the end-of-page-free-part marker is missing): " + tpl);
  try {
    const page = vm.runInNewContext(html.slice(start + "<script>".length, end) + "\n;({check, recordProblems, bgFirst, assumeOf, proCon})", {});
    if (typeof page.check !== "function" || typeof page.recordProblems !== "function" || typeof page.bgFirst !== "function"
      || typeof page.assumeOf !== "function" || typeof page.proCon !== "function") throw new Error("no check(), recordProblems(), bgFirst(), assumeOf() or proCon()");
    return page;
  } catch (e) { fail("the template's page-free part does not load: " + why(e)); }
}

/* ---- the lints ---- */
const W = {two:2, three:3, four:4, five:5, six:6, seven:7, eight:8, nine:9, ten:10, eleven:11, twelve:12};
/* neither ids nor counts: backtick spans (a path, command or name the operator types), https links,
   slugs, hex colours (never a #tag after an id noun: item #4151 stays), dates and times, clock times
   and versions */
const ID_NOUN = "(?:work item|item|commit|ticket|decision|answer|card)s?";
/* the source labels the page's cards declare ({id, name}), each passing only with its short name beside it:
   F7 (oversize upload). Set by lint() from the file it checks */
let DECLARED = [];
const reEsc = x => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const declare = cards => cards.map(c => c.label).filter(l => l && typeof l === "object" && typeof l.id === "string" && typeof l.name === "string")
  .map(l => new RegExp("(?<![A-Za-z0-9])" + reEsc(l.id) + "\\s*\\(\\s*" + reEsc(l.name.trim()).replace(/\s+/g, "\\s+") + "\\s*\\)", "gi"));
const unlabel = s => DECLARED.reduce((t, r) => t.replace(r, " "), s);
const strip = s => unlabel(s).replace(/`[^`]*`/g, " ").replace(/https:\/\/\S+/g, " ").replace(/\[\[[0-9]+\]\]/g, "")
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
/* every id in a text, one per mention: [token, a decision number or null]. Where two patterns match
   the same words (commit abc123 is a noun id and a hex tag), the longest match stands */
function ids(s) {
  const t = strip(s), found = [];
  const add = (tok, n, at, len) => found.push({tok, n, at, end: at + len});
  for (const m of t.matchAll(ID_TOKEN)) add(m[0], null, m.index, m[0].length);
  for (const m of t.matchAll(KEBAB_ID)) add(m[0], null, m.index, m[0].length);
  for (const m of t.matchAll(NOUN_ID)) if (!(/^\d+$/.test(m[1]) && YEAR.test(m[1]))) add(m[0].replace(/\s+/g, " "), null, m.index, m[0].length);
  for (const m of t.matchAll(DECISION_ID)) {
    /* "answer" followed by a word is the verb: answer 2 questions */
    if (m[1].toLowerCase() === "answer" && m[3]) continue;
    const len = m[0].length - (m[3] || "").length;
    add(m[0].slice(0, len).replace(/\s+/g, " "), m[2], m.index, len);
  }
  /* a bracketed tag: a four-digit token in ( … ) that is not a year, nor a number before a unit (1500 ms) */
  for (const m of t.matchAll(/\(([^()]{1,60})\)/g)) {
    const toks = [...m[1].matchAll(/[^\s,;]+/g)];
    toks.forEach((x, i) => { const tok = x[0];
      if (/^\d{4}$/.test(tok) && !YEAR.test(tok) && !new RegExp("^" + UNIT + "$", "i").test(toks[i + 1] ? toks[i + 1][0] : ""))
        add("(" + tok + ")", null, m.index + 1 + x.index, tok.length); });
  }
  const kept = [];
  for (const f of found.sort((x, y) => (y.end - y.at) - (x.end - x.at)))
    if (!kept.some(k => f.at < k.end && k.at < f.end)) kept.push(f);
  const seen = new Set();
  return kept.sort((x, y) => x.at - y.at).filter(f => !seen.has(f.tok) && seen.add(f.tok)).map(f => [f.tok, f.n]);
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

/* the options, objects in letter order */
const opts = c => Array.isArray(c.options) ? c.options : [];
const IMP = ["wait", "reach", "undo", "cost"];
/* the flat part a cold reader reads first: what context must introduce, for counts and named things. The basis
   reason is not in it: it sits in the closed Assumptions fold */
function flat(c) {
  const out = [c.t];
  for (const k of IMP) out.push(c.impact[k]);
  out.push(...c.tldr);
  for (const o of opts(c)) out.push(o.title, o.line);
  for (const k of ["ifleft", "roundcosts", "ifunanswered", "norec", "dep"]) out.push(c[k]);
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
/* the Background fold's summary (answer 338): the first sentence of why, read by the page's own bgFirst, so the
   lint and the closed fold measure the same text */
const BGSUM_CAP = 25;
const LEVEL = ["summary", "medium", "high"], DETAIL_NAME = ["more detail", "full detail"];
/* the parts a card shows, by their detail key; the first four are always visible */
const PART = {context: "Context", impact: "the Impact line", tldr: "the TLDR", rec: "the basis line",
  why: "Why now", whyask: "Why ask", dep: "Depends on", evidence: "the Evidence"};
const levelsOf = (c, k) => c.detail && typeof c.detail === "object" && Array.isArray(c.detail[k]) ? c.detail[k] : [];
const optLevels = o => Array.isArray(o.detail) ? o.detail : [];

function shapes(c, say) {
  const sh = (key, line) => say("shape " + key, "shape: " + line);
  const terse = (where, s) => { const n = words(s), k = sentences(s);
    if (k > 1 || n > TERSE) sh(where, where + " is " + (k > 1 ? k + " sentences" : n + " words") + ": keep a bullet at this level a terse fragment, one point in about " + TERSE + " words; full sentences belong at full detail"); };
  /* the visible summaries, always */
  const cs = sentences(c.context), cw = words(c.context);
  if (cs > 2 || cw > 60) sh("ctx", "Context's summary is " + (cs > 2 ? cs + " sentences" : cw + " words") + ": keep it to one or two sentences, about 60 words, with the terms the card uses; move the rest to its levels, or leave it knowingly");
  if (c.tldr.length > 2) sh("tldr n", "the TLDR has " + c.tldr.length + " bullets: keep it to one or two terse bullets");
  c.tldr.forEach((b, i) => terse("TLDR bullet " + (i + 1), b));
  for (const k of IMP) if (typeof c.impact[k] === "string" && words(c.impact[k]) > 16)
    sh("imp " + k, "Impact " + k + " is " + words(c.impact[k]) + " words: keep each facet on its line to about 16; its detail goes in the Impact's levels");
  const bgs = words(page.bgFirst(c));
  if (bgs > BGSUM_CAP) say("bgsum", "shape: the Background fold's summary, the first sentence of why, is " + bgs + " words: keep it to about " + BGSUM_CAP + "; rewrite the sentence shorter, never cut it, or leave it knowingly");
  /* a fold part's summary, where the part carries levels (a part with none is a small call's whole text) */
  const fold = (name, key, sum, ls) => { if (ls.length && sum != null && sentences(textsOf(sum).join(" ")) > 2)
    sh("sum " + key, name + "'s summary is " + sentences(textsOf(sum).join(" ")) + " sentences: keep it to one or two; its levels carry the rest"); };
  for (const k of ["why", "whyask", "dep", "evidence"]) fold(PART[k], k, c[k], levelsOf(c, k));
  for (const o of opts(c)) fold("(" + o.k + ")'s text", "o" + o.k, o.text, optLevels(o));
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
  for (const o of opts(c)) { const ls = optLevels(o);
    if (ls[0] != null) medium("(" + o.k + ")'s text", ls[0]);
    if (ls[1] != null) high("(" + o.k + ")'s text", ls[1]); }
  /* the Impact's medium: one bullet per facet, the options in its sub-bullets; its high renders as facet sections */
  const im = levelsOf(c, "impact")[0];
  if (im && typeof im === "object") for (const k of IMP) { const v = im[k]; if (v == null) continue;
    const at = "the Impact's more detail, " + k;
    if (Array.isArray(v)) { sh("imp m " + k, at + ", is a list: give each facet one bullet, and put the options in its sub-bullets"); continue; }
    const t = typeof v === "string" ? v : v.t, sub = typeof v === "string" ? [] : v.sub || [];
    terse(at, t);
    if (sub.length > SUB_CAP) sh("imp sub " + k, at + ", has " + sub.length + " sub-bullets: give a facet one or two; where it differs across more than two options, group them ((a) and (b): …)");
    sub.forEach((x, j) => terse(at + ", sub-bullet " + (j + 1), x));
  }
}

/* ---- the rec-only lint: the card's Impact is the decision's across its options. With no card-level effect
   (v5), it reads the Impact's reach, at every level: a reach that shares its words with the recommended option
   and with no other reads as that option's alone, and belongs on it. Undo and cost may name one option by design;
   they are not read ---- */
const STOP = new Set("a an the and or of to in on for is are be it its this that from with by at as no not one any who what can".split(" "));
const toks = s => new Set((String(s).toLowerCase().replace(/\[\[[0-9]+\]\]/g, "").match(/[a-z0-9]+/g) || []).filter(w => !STOP.has(w) && w.length > 2));
const share = (e, r) => { const E = toks(e), R = toks(r); if (!E.size) return 0; let n = 0; for (const w of E) if (R.has(w)) n++; return n / E.size; };
function recOnly(c, say) {
  if (!c.rec) return;
  const optText = o => [o.title, o.line, o.effect, o.reach, o.cost].filter(s => typeof s === "string").join(" ");
  const r = opts(c).find(o => o.k === c.rec), others = opts(c).filter(o => o.k !== c.rec && o.k !== "z");
  if (!r || !others.length) return;
  const vals = [["", c.impact.reach], ...levelsOf(c, "impact").map((l, i) => [" (" + DETAIL_NAME[i] + ")", l && typeof l === "object" ? textsOf(l.reach).join(" ") : ""])];
  for (const [at, e] of vals) {
    if (!e || typeof e !== "string") continue;
    const sr = share(e, optText(r)), so = Math.max(0, ...others.map(o => share(e, optText(o))));
    if ((e.match(/\([a-y]\)/g) || []).length < 2 && sr >= 0.4 && so === 0)
      say("rec-only" + at, "impact: the reach" + at + " reads as the recommended option's (\"" + e.slice(0, 60) + "\"): say who or what any option reaches; the option's own reach is on the option");
  }
}

/* ---- the system lint (rule 259): Effect and Reach describe the thing the work builds, never the process, which
   is the Wait. Phrases, not bare words: "the code review checklist", "a comment in the hook" and "a round-trip"
   are system effects. Read: the Impact's reach, at every level; each option's effect and reach but (z)'s. Never
   the wait; never a round ask (ifleft or roundcosts), whose system is the round ---- */
const PROCESS = /\breview comments?\b|\b(another|next|a|review) round\b(?!-)|\byour (attention|time)\b|\b(held|waits?|waiting) (for|on|until) (you|review|the operator)\b|\bblocked session\b|\bsession (is )?blocked\b/i;
function systemOnly(c, say) {
  if (c.ifleft != null || c.roundcosts != null) return;
  const at = [["the reach", c.impact.reach]];
  levelsOf(c, "impact").forEach((l, i) => { if (l && typeof l === "object") at.push(["the reach (" + DETAIL_NAME[i] + ")", textsOf(l.reach).join(" ")]); });
  for (const o of opts(c)) if (o.k !== "z") at.push(["(" + o.k + ")'s effect", o.effect], ["(" + o.k + ")'s reach", o.reach]);
  for (const [where, s] of at) { const m = typeof s === "string" ? s.match(PROCESS) : null;
    if (m) say("process " + where, "impact: " + where + " names the process (\"" + m[0] + "\"): Effect and Reach describe the system the work builds, its code, data, users and deploys; move the process effect to wait, or leave it knowingly when the system the work builds is itself a review or a process"); }
}

/* ---- the mechanism lint (rule 268): each option's effect says how it happens, who meets it and when, and the
   before and after. A proxy: it catches only the bare label, an effect of MECH_MIN words or fewer; never (z)'s,
   and never a no-change statement ---- */
const MECH_MIN = 4;
const NO_CHANGE = /^[^A-Za-z]*(no|nothing|none|unchanged)\b/i;
function mech(c, say) {
  for (const o of opts(c)) { if (o.k === "z") continue;
    const e = o.effect, n = words(e);
    if (typeof e === "string" && e.trim() && n <= MECH_MIN && !NO_CHANGE.test(e))
      say("mech " + o.k, "impact: (" + o.k + ")'s effect is " + n + " words (\"" + e.trim() + "\"): say its mechanism, how it happens, who meets it and when, and the before and after; or leave it knowingly"); }
}

/* ---- the depth lints (decision 198): sizes read at each part's top level, words split on whitespace ---- */
const topOf = (sum, ls) => ls.length ? ls[ls.length - 1] : sum;

function depth(c, say) {
  const imp = c.impact;
  const summary = {context: c.context, impact: IMP.map(k => imp[k]), tldr: c.tldr,
    rec: [c.reason], why: c.why, whyask: c.whyask, dep: c.dep, evidence: c.evidence};
  /* a level replaces the one below it, so it says more */
  const grow = (name, key, sum, ls) => { const ws = [words(sum), ...ls.map(words)];
    for (let i = 1; i < ws.length; i++) if (ws[i] <= ws[i - 1])
      say("grow " + key + i, "depth: " + name + " " + LEVEL[i] + " is not longer than its " + LEVEL[i - 1] + " (" + ws[i] + " words against " + ws[i - 1] + "): each level is a fuller rendition of the one below it"); };
  for (const k in PART) grow(PART[k], k, summary[k], levelsOf(c, k));
  for (const o of opts(c)) grow("(" + o.k + ")'s text", "o" + o.k, o.text, optLevels(o));
  /* what a new card owes, which the page does not refuse so an upgraded older card renders with nothing invented */
  const missing = ["why", "whyask"].filter(k => !(typeof c[k] === "string" && c[k].trim()));
  if (missing.length) say("bg", "depth: " + missing.join(" and ") + " missing: a new card says why now and why it is asked (the Background fold); leave it knowingly only on an upgraded older card");
  if (!(typeof c.reason === "string" && c.reason.trim()))
    say("reason", "depth: reason missing: a new card gives the one-clause reason for its rec (or for its basis word, with no rec); leave it knowingly only on an upgraded older card");
  /* the Assumptions fold (the v5 layout): a recommendation names what it rests on, each with its tripwire. The
     assumptions counted are the ones the page shows (its own assumeOf: one whose rests is none is not shown) */
  const as = page.assumeOf(c);
  if (c.rec && !as.length)
    say("assume", "depth: no assumptions: a card with a recommendation names what the call rests on, each with its tripwire, the sign that would change it (assume: [{rests, tw}], shown in the Assumptions fold); a small call may leave it knowingly");
  /* the 198 sizes, at the top level: Background ~150, each option ~60-120, Evidence ~150, a card ~600-900.
     Levels scale with the decision (201): a part with none may stay short, so thin is linted only where
     the writer gave levels; long is linted everywhere */
  const bg = words(topOf(c.why, levelsOf(c, "why"))) + words(topOf(c.whyask, levelsOf(c, "whyask")));
  const bgLv = levelsOf(c, "why").length + levelsOf(c, "whyask").length > 0;
  if (!missing.length && bgLv && bg < 60) say("bg", "depth: Background is " + bg + " words at its fullest: write Why now and Why ask near 150 together, from the record and the work behind it, or leave it knowingly; never pad");
  else if (bg > 225) say("bg", "depth: Background is " + bg + " words at its fullest: keep Why now and Why ask near 150 together");
  let optWords = 0;
  for (const o of opts(c)) {
    const top = words(topOf(o.text, optLevels(o)));
    if (o.k === "z") { optWords += top + words(o.effect); continue; }
    if (!(typeof o.reach === "string" && o.reach.trim()) && c.oneway !== true)
      say("row " + o.k, "depth: (" + o.k + ") has no reach: give it who or what it reaches, its undo where it is one-way or costly, and its cost where it has one");
    const ow = top + words([o.effect, o.reach, o.undo, o.cost]);
    optWords += ow;
    if (optLevels(o).length && ow < 30) say("opt " + o.k, "depth: (" + o.k + ")'s detail is " + ow + " words (its fullest text and its effect, reach, undo and cost): write it near 60–120, from the sources; or leave it knowingly");
    else if (ow > 180) say("opt " + o.k, "depth: (" + o.k + ")'s detail is " + ow + " words (its fullest text and its effect, reach, undo and cost): keep it near 60–120");
  }
  const ev = words(topOf(c.evidence, levelsOf(c, "evidence")));
  if (levelsOf(c, "evidence").length && c.basis !== "none" && ev < 60) say("ev", "depth: evidence is " + ev + " words at its fullest: give the basis drill-down near 150, what was observed, inferred and assumed, with the paths and links behind each; or leave it knowingly");
  else if (ev > 225) say("ev", "depth: evidence is " + ev + " words at its fullest: keep it near 150");
  /* the card in all: the flat part and Context at their summary, the fold parts at their top level (the basis reason
     among them), each option's detail and its inline Pros and Cons rows; not act */
  const pc = opts(c).reduce((n, o) => n + words(page.proCon(o).map(r => r[1])), 0);
  const all = words(flat(c)) + words(c.context) + bg + ev + words(topOf(c.reason, levelsOf(c, "rec"))) + words(as) + optWords + pc;
  if (all > 1350) say("all", "depth: the card is " + all + " words in all: keep it near 600–900; a small call gets a short card");
  if (c.detail && typeof c.detail === "object")
    for (const k of Object.keys(c.detail)) if (!(k in PART))
      say("key " + k, "depth: detail." + k + " is not a part the page shows, so it is ignored: the parts are " + Object.keys(PART).join(", ") + ", and each option's own detail");
}

/* ---- the one-way lints: the page refuses an option flagged oneway without its undo; these catch what it lets
   through ---- */
function oneway(c, say) {
  const flagged = opts(c).filter(o => o.oneway === true).map(o => o.k);
  if (c.oneway === true && !flagged.length)
    say("oneway", "oneway: a ⚠ one-way card has no option flagged one-way: set oneway: true, with its undo, on each option one-way or costly to undo; or leave it knowingly on a card the operator has answered");
  if (flagged.length && !(typeof c.impact.undo === "string" && c.impact.undo.trim()))
    say("oneway impact", "oneway: (" + flagged.join(", ") + ") is flagged one-way but the Impact carries no undo: name it there, (" + flagged[0] + ") and how it is undone, or that it cannot be");
}

/* ---- the trade-offs lint (302's feedback, F4): each option but (z) shows its one-line Pros and Cons under it. It reads
   the rows the page shows (its own proCon: a none one is not shown). A card with two or more real options and none
   gets one line; otherwise each option missing a row gets its own, and a recommended option with no con its own ---- */
function tradeoffs(c, say) {
  const real = opts(c).filter(o => o.k !== "z");
  const rows = o => new Set(page.proCon(o).map(r => r[0]));
  if (real.length >= 2 && real.every(o => !rows(o).size)) {
    say("tradeoffs", "shape: none of the card's " + real.length + " options but (z) carries its pros and cons: give each a one-line pro and con (pro, con: the inline Pros and Cons rows), or leave it knowingly on an upgraded older card");
    return;
  }
  for (const o of real) { const r = rows(o), isRec = c.rec === o.k;
    if (isRec && !r.has("Cons"))
      say("tradeoffs rec", "shape: the recommended option (" + o.k + ") has no con: say what choosing it costs or risks on its Cons row (con), so the recommendation is weighed; or leave it knowingly");
    const miss = [r.has("Pros") ? "" : "pro", r.has("Cons") || isRec ? "" : "con"].filter(Boolean);
    if (miss.length)
      say("tradeoffs " + o.k, "shape: (" + o.k + ") has no " + miss.join(" and no ") + ": give it a one-line " + miss.join(" and ") + " (its inline " + miss.map(m => m === "pro" ? "Pros" : "Cons").join(" and ") + " row), or leave it knowingly on an upgraded older card");
  }
}

/* ---- the source label's short name: plain words, about 2 to 6 ---- */
function labelName(c, say) {
  const l = c.label;
  if (l && typeof l === "object" && typeof l.name === "string" && words(l.name) > 6)
    say("shape label", "shape: the label " + l.id + "'s short name is " + words(l.name) + " words: keep it to about 2–6 plain words");
}

/* ---- the id lint: no machine-readable id anywhere the page shows text; the page is the reader's only context ---- */
const idLine = ([t, n], at) => t + " looks like an id (" + at + "): "
  + (n ? "name the decision by its slug [[" + n + "]], with its card or a refs entry" : "name the thing by its short name or title, a decision by its slug [[N]]")
  + "; the page is the reader's only context; leave it if it is a term the reader knows (S3, UTF-8)";
/* the texts a card shows, by part: everything the page renders but rev, n, L and the option letters */
function cardTexts(c) {
  const out = [];
  const put = (at, v) => { for (const s of textsOf(v)) out.push([at, s]); };
  if (c.label && typeof c.label === "object") put("label", c.label.name);
  for (const k of ["t", "context", "what", "class", "why", "whyask", "dep", "ifleft", "roundcosts", "ifunanswered", "reason", "norec", "evidence", "open"]) put(k, c[k]);
  for (const k of IMP) put("impact", c.impact[k]);
  put("tldr", c.tldr);
  if (Array.isArray(c.assume)) for (const a of c.assume) if (a && typeof a === "object") put("assume", [a.rests, a.tw]);
  for (const o of opts(c)) {
    for (const k of ["title", "line", "text", "effect", "reach", "undo", "cost", "pro", "con"]) put("(" + o.k + ")", o[k]);
    if (Array.isArray(o.act)) put("act (" + o.k + ")", o.act);
    if (Array.isArray(o.detail)) put("detail (" + o.k + ")", o.detail);
  }
  if (c.detail && typeof c.detail === "object") for (const k in c.detail)
    put("detail." + k, k === "impact" && Array.isArray(c.detail.impact) ? c.detail.impact.map(l => l && typeof l === "object" ? IMP.map(f => l[f]) : l) : c.detail[k]);
  return out;
}
function pageIds(d, out) {
  const say = line => out.push("lint: page: " + line), seen = new Set();
  const look = (at, s) => { if (typeof s === "string") for (const x of ids(s)) if (!seen.has(at + x[0])) { seen.add(at + x[0]); say(idLine(x, at)); } };
  const pg = d.page && typeof d.page === "object" ? d.page : {};
  look("the page title", pg.title); look("the lede", pg.lede);
  for (const l of d.layers) { look("the title of layer " + l[0], l[1]); look("the note of layer " + l[0], l[2]);
    look("the shared context of layer " + l[0], l[3]);
    /* a bundle groups two or more item cards (rule 263) */
    const n = d.cards.filter(c => c.L === l[0]).length;
    if (typeof l[3] === "string" && l[3].trim() && n < 2)
      say("group " + l[0] + " holds " + n + " card" + (n === 1 ? "" : "s") + ": a bundle (a layer with shared context) groups two or more item cards; give a lone item its own Context and a plain layer, or leave it knowingly"); }
  for (const k in (d.refs || {})) { const r = d.refs[k] || {};
    look("refs " + k + " short", r.short); look("refs " + k + " q", r.q);
    if (typeof r.a === "string") for (const x of ids(r.a))
      say("refs " + k + " a holds " + x[0] + ", which looks like an id: if these are the operator's own words, leave them as given; otherwise name the thing"); }
}

/* the card lints, one card; w opens each line ("lint: card 41: "), sh is its bundle's shared context */
function lintCard(c, w, sh, out) {
  const hasWhat = typeof c.what === "string" && c.what.trim();
  /* an item card in a bundle may lean on its group's shared context (rule 263) */
  const ctx = c.context + (hasWhat ? " " + c.what : "") + (typeof sh === "string" ? " " + sh : "");
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
  /* the visible parts' medium and high: each steps alone, so the Context beside them may be its summary. The basis
     line's levels are in the closed Assumptions fold, so they are not read */
  for (const k of ["impact", "tldr"]) levelsOf(c, k).forEach((r, i) => terms(k === "impact" && r && typeof r === "object" ? textsOf(IMP.map(f => r[f])) : textsOf(r), " (" + PART[k] + ", " + DETAIL_NAME[i] + ")"));
  /* a TLDR level's headings, bullets and sub-bullets, numbered in reading order as the page numbers them */
  levelsOf(c, "tldr").forEach((bs, m) => textsOf(bs).forEach((b, i) => { if (REC_BROAD.test(b))
    say("tldr " + m + "." + i, "tldr bullet " + (i + 1) + " (" + DETAIL_NAME[m] + ") may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); }));
  if (hasWhat) say("what", "what present: move it into context (after the terms, before the cue) and delete it");
  shapes(c, say);
  recOnly(c, say);
  systemOnly(c, say);
  mech(c, say);
  depth(c, say);
  oneway(c, say);
  tradeoffs(c, say);
  labelName(c, say);
}

function lint(d) {
  const out = [];
  DECLARED = declare(d.cards);
  pageIds(d, out);
  for (const c of d.cards) lintCard(c, "lint: card " + c.n + ": ", (d.layers.find(l => l[0] === c.L) || [])[3], out);
  return out;
}

/* ---- the run ---- */
const page = loadPage();
const args = process.argv.slice(2);
const record = args[0] === "--record";
const file = record ? args[1] : args[0];
if (!file || args.length !== (record ? 2 : 1)) fail("usage: node check_cards.js path/to/cards.json, or node check_cards.js --record path/to/record.json");
let text, d;
try { text = fs.readFileSync(file, "utf8"); } catch (e) { fail("cannot read " + file + ": " + why(e)); }
try { d = JSON.parse(text); } catch (e) { fail("not valid JSON: " + why(e)); }
let bad;
try { bad = record ? page.recordProblems(d) : page.check(d); } catch (e) { fail("the page's check stopped on this file: " + why(e)); }
if (bad.length) { process.stdout.write(bad.join("\n") + "\n"); process.exit(1); }
let lines = [];
try {
  if (record) { DECLARED = declare([d]); lintCard(d, "lint: record " + d.n + ": ", null, lines); }
  else lines = lint(d);
} catch (e) { fail("the lints stopped on this file: " + why(e)); }
if (lines.length) { process.stdout.write(lines.join("\n") + "\n"); process.exit(2); }
process.exit(0);
