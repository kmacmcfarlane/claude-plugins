#!/usr/bin/env node
/* decision-page pre-publish check (operator-interaction). Run on the working copy's cards.json
   before a publish, or on one card record before it is raised:

     node check_cards.js path/to/cards.json
     node check_cards.js --record path/to/record.json

   1. the page's own check(): the template's page-free part, loaded from ../assets/index.html,
      so this refuses exactly what the page refuses (decision-page/5, each card a decision-card/5
      record plus L and dep). With --record, the card checks alone (no layer, no slug check), and
      the page-only L and dep refused in a record;
   1a. the attachment refusals, the runner's own (F3): a [[att:id|label]] link to an id the card does not attach,
      or a [[att: that is not that form (the page shows its label as plain text); and a secret in an attachment or
      in the Finding's excerpt (a private key block, a token with a known prefix, a password, token or secret
      assignment with a long value), named by where it is and its key, never its value. SECRET_PATTERNS are the
      ones the skill's grep step runs without node;
   1b. the set refusal, the runner's own (never the page's, so an older published page still renders): a
      card whose title, first TLDR bullet, or an option's title or line (but (z)'s) counts two or more
      things, with no items or fewer items than the largest count (the What part lists every item of a
      set, F6). A card the upgrader carried over with its rev kept, and a count of 100 or more, get it as
      the set lint instead; a count in what with no items of its length gets the count lint;
   2. on a file that passes, lints, each line saying how to fix it, or that the thing may be left
      knowingly:
      - the set: an items list of another length than the count; a carried-over card's set;
      - ids: a machine-readable id anywhere the page shows text (every card field and level, act,
        the page title, the lede, the layer titles and notes, refs, the What part and its items, the Finding but its
        excerpt, the Scope, the Likelihood and Best response?, the Rejected alternatives, each attachment but its
        excerpt-shaped body), whatever Context says; the page is the reader's only context. Backtick spans, https links and slugs are
        not ids, and a source label a card or its finding declares passes with its short name beside it;
      - terms: a count or a named thing in the flat part, or in the medium and high levels of the
        Impact and the TLDR, that Context's summary (with its bundle's shared context, and the What
        part: its text and its items) does not introduce; a count in the places that say what is
        decided points to items; the Finding's title and mechanism are read too (F7), the Scope's says (F8), and the
        Likelihood's seen and Best response? (F9), each rejected alternative's title (F2), and each attachment's
        title (F3), which the Attached fold's summary shows;
      - attachments (F3): more than ATT_CAP on a card, or an excerpt-shaped body past XC_LINES lines or XC_BYTES
        bytes;
      - groups: a bundle (a layer with shared context) holding fewer than two cards;
      - the dependency order (03ab F7): a card placed before a card in its own layer that its dep names (deporder,
        no line start); a pair in a dep cycle is skipped, and a target on another layer or in refs is never read;
      - the TLDR: a bullet that may carry the recommendation, at every level, headings, bullets
        and sub-bullets in reading order;
      - the Background fold's summary: the first sentence of why past BGSUM_CAP words;
      - shapes: summaries a sentence or two (the TLDR one or two bullets, an Impact facet a line),
        medium terse bullets with a sub-bullet or two, high headed sections; the Impact's medium
        one bullet per facet;
      - an Impact reach that reads as the recommended option's alone; an item's per that gives the
        recommended option's outcome alone;
      - the mechanism: an option's effect, or the Finding's mechanism, of a bare label, MECH_MIN words or fewer (rule 268);
      - the likelihood (F9, answer 267 (a), widened): a shown seen that is a bare no data, holds an estimate word, a
        percentage with no bracketed source after it, opens on a carried-over basis word ("(estimated) "), or, on an
        observed one, ends on no bracketed source; a likelihood with no shown best on a new card (not one the upgrader
        carried over with its rev);
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
        a recommended option with no con; a card with two or more real options and none; a pro or
        con past PROCON_CAP words;
      - the plan (F5): an option with no plan in brief (the first part of its view); a plan past
        PLAN_CAP words; an option with both plan and text, whose text is not shown.
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
    const page = vm.runInNewContext(html.slice(start + "<script>".length, end) + "\n;({check, recordProblems, bgFirst, assumeOf, proCon, planOf, prosCons, itemsOf, perOf, findingOf, scopeOf, likelihoodOf, bestOf, rejectedOf, rejWhy, attachedOf})", {});
    if (typeof page.check !== "function" || typeof page.recordProblems !== "function" || typeof page.bgFirst !== "function"
      || typeof page.assumeOf !== "function" || typeof page.proCon !== "function" || typeof page.planOf !== "function"
      || typeof page.prosCons !== "function" || typeof page.itemsOf !== "function" || typeof page.perOf !== "function"
      || typeof page.findingOf !== "function" || typeof page.scopeOf !== "function" || typeof page.likelihoodOf !== "function"
      || typeof page.bestOf !== "function" || typeof page.rejectedOf !== "function" || typeof page.rejWhy !== "function"
      || typeof page.attachedOf !== "function")
      throw new Error("no check(), recordProblems(), bgFirst(), assumeOf(), proCon(), planOf(), prosCons(), itemsOf(), perOf(), findingOf(), scopeOf(), likelihoodOf(), bestOf(), rejectedOf(), rejWhy() or attachedOf()");
    return page;
  } catch (e) { fail("the template's page-free part does not load: " + why(e)); }
}

/* ---- the lints ---- */
const W = {two:2, three:3, four:4, five:5, six:6, seven:7, eight:8, nine:9, ten:10, eleven:11, twelve:12};
/* neither ids nor counts: backtick spans (a path, command or name the operator types), https links,
   slugs, hex colours (never a #tag after an id noun: item #4151 stays), dates and times, clock times
   and versions */
const ID_NOUN = "(?:work item|item|commit|ticket|decision|answer|card)s?";
/* the source labels the page's cards declare ({id, name}), a card's own and its finding's (F7), each passing only with
   its short name beside it: F7 (oversize upload). Set by lint() from the file it checks */
let DECLARED = [];
const reEsc = x => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const declare = cards => cards.flatMap(c => [c.label, c.finding && typeof c.finding === "object" ? c.finding.label : null]).filter(l => l && typeof l === "object" && typeof l.id === "string" && typeof l.name === "string")
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
/* a four-digit year (2027) counts nothing */
const counts = s => [...unId(s).matchAll(COUNT)].filter(m => !(/^[0-9]+$/.test(m[1]) && YEAR.test(m[1])))
  .map(m => ({word: m[1], n: W[m[1].toLowerCase()] || Number(m[1])}));
/* a named thing: "<word> mode|setting|…"; a determiner or count word before it is dropped, leaving the bare noun; the s of a possessive is no qualifier */
const DET = new Set(["the","this","that","these","those","each","every","a","an","its","our","your","their","any","no","one","which","whose","same","new","old"]);
const NAMED = /\b([a-z][a-z-]*)\s+(mode|setting|review|plan|document|doc|spec|policy|flag|profile|template|track|phase|stage)\b/gi;
/* NAMED matches do not overlap: when a function word leads one ("to plan" in "to plan mode"), the noun it used up
   can still head the real name, so read on from the second word */
const NAMED_NEXT = /^\s+(mode|setting|review|plan|document|doc|spec|policy|flag|profile|template|track|phase|stage)\b/i;
const named = s => { const t = strip(s); return [...t.matchAll(NAMED)].flatMap(m => { const w = m[1].toLowerCase();
  const possessive = w === "s" && m.index > 0 && /['’]/.test(t[m.index - 1]);
  if (!possessive && FUNC.has(w)) { const nx = t.slice(m.index + m[0].length).match(NAMED_NEXT);
    return nx ? [(m[2] + " " + nx[1]).toLowerCase()] : []; }
  return possessive ? [] : [DET.has(w) || W[w] ? m[2].toLowerCase() : (m[1] + " " + m[2]).toLowerCase()]; }); };
/* over an option's view (its plan and its table's points, prose where the nouns are often verbs: "to plan", "and
   review", "reaches review"), a match is dropped when its first word is a function word or a verb form, as DET
   drops a determiner, and the bare noun left is not read: only a qualified name ("content mode") fires. A verb form
   is a third-person -es ("reaches"); -ed and -ing stay, since they qualify real names ("the staging phase", "a managed
   setting"). The s of a possessive ("the maintainer's plan") is no qualifier either */
const FUNC = new Set(["to", "and", "or", "nor", "but", "of", "for", "without", "with", "then", "than", "so", "as", "at", "by", "in",
  "on", "from", "into", "onto", "per", "via", "if", "when", "until", "before", "after", "while"]);
const VERB_FORM = /(?:es)$/;
const namedView = s => { const t = strip(s); return [...t.matchAll(NAMED)].flatMap(m => { const w = m[1].toLowerCase();
  const possessive = w === "s" && m.index > 0 && /['’]/.test(t[m.index - 1]);
  return possessive || DET.has(w) || W[w] || FUNC.has(w) || VERB_FORM.test(w) ? [] : [(m[1] + " " + m[2]).toLowerCase()]; }); };
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
/* the places that say what is decided (F6, the set check): the title, the TLDR's first bullet (what is decided; a
   count in its second goes to the count lint), and each option's title and line, but (z)'s, which says what waiting
   costs */
function decided(c) {
  const out = [c.t, c.tldr[0]];
  for (const o of opts(c)) if (o.k !== "z") out.push(o.title, o.line);
  return out.filter(s => typeof s === "string");
}
/* the What part's texts, as the page shows them: what, then each item's name, where, about and per */
const whatTexts = c => [c.what, ...page.itemsOf(c).flatMap(x => [x.name, x.where, x.about, ...page.perOf(x).map(p => p[1])])]
  .filter(s => typeof s === "string");
/* the Finding's texts a cold reader reads (F7): its title and its mechanism, as the page shows them; its label is
   glossed by its own short name, where is a location and the excerpt is verbatim, so none of those is read for terms */
const findingTexts = c => { const f = page.findingOf(c); return f ? [f.title, f.mechanism].filter(s => typeof s === "string") : []; };
/* the Scope's text as the page shows it (F8): its says; the level is one of three fixed words */
const scopeTexts = c => { const s = page.scopeOf(c); return s && typeof s.says === "string" ? [s.says] : []; };
/* the Likelihood's texts as the page shows them (F9): its seen, then Best response?; the kind is one of two fixed words */
const likelihoodTexts = c => { const l = page.likelihoodOf(c), b = page.bestOf(c); return l ? [l.seen, b].filter(s => typeof s === "string" && s) : []; };
/* the Rejected alternatives fold's texts as the page shows them (F2): each shown alternative's title, then its shown
   reasons */
const rejectedTexts = c => page.rejectedOf(c).flatMap(r => [r.t, ...page.rejWhy(r)]);
/* the Attached fold's texts as the page shows them (F3), but an excerpt-shaped body (verbatim data, never read for ids
   or terms, as the Finding's excerpt is not): each shown attachment's title and source line, then its body's text */
const XC_KINDS = new Set(["excerpt", "preview"]);
const depTexts = x => !x || typeof x !== "object" ? [] : [x.name, x.rel, x.note, ...(Array.isArray(x.kids) ? x.kids.flatMap(depTexts) : [])];
const attTexts = a => {
  const b = a.body, xc = XC_KINDS.has(a.kind) || (a.kind === "example" && a.form === "mock");
  const body = xc ? [] : a.kind === "table" || a.kind === "matrix" ? (b && typeof b === "object" ? [...(b.cols || []), ...(Array.isArray(b.rows) ? b.rows.flat() : [])] : [])
    : a.kind === "steps" || a.kind === "checks" ? (Array.isArray(b) ? b.flatMap(x => x && typeof x === "object" ? [x.t, x.d] : []) : [])
    : a.kind === "depmap" ? (Array.isArray(b) ? b.flatMap(depTexts) : []) : [].concat(b);
  return [a.title, a.src, a.pointer, ...body].filter(x => typeof x === "string");
};
const attachedTexts = c => page.attachedOf(c).flatMap(attTexts);
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
/* the parts a card shows, by their detail key; the first four are always visible. The dependency line (dep) is
   static, with no levels (03ab F3), so it is no part here: an older card's detail.dep lints key */
const PART = {context: "Context", impact: "the Impact line", tldr: "the TLDR", rec: "the basis line",
  why: "Why now", whyask: "Why ask", evidence: "the Evidence"};
const levelsOf = (c, k) => c.detail && typeof c.detail === "object" && Array.isArray(c.detail[k]) ? c.detail[k] : [];
const optLevels = o => Array.isArray(o.detail) ? o.detail : [];
/* an option's prose, the summary its levels step from: its plan in brief (F5), or, on an older option with none,
   its text. The page reads the same (its planOf) */
const optProse = o => page.planOf(o) || o.text;
/* an option's view, as the page shows it (F5): its plan in brief, then the points of its Pros | Cons table */
const viewTexts = o => [page.planOf(o), ...page.prosCons(o).flatMap(r => r[1])].filter(Boolean);

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
  for (const k of ["why", "whyask", "evidence"]) fold(PART[k], k, c[k], levelsOf(c, k));
  /* an older option's text; a plan in brief is 2-4 sentences by design, and the plan lint sizes it */
  for (const o of opts(c)) if (!page.planOf(o)) fold("(" + o.k + ")'s text", "o" + o.k, o.text, optLevels(o));
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
  for (const k of ["context", "tldr", "rec", "why", "whyask", "evidence"]) {
    const ls = levelsOf(c, k);
    if (ls[0] != null) medium(PART[k], ls[0]);
    if (ls[1] != null) high(PART[k], ls[1]);
  }
  for (const o of opts(c)) { const ls = optLevels(o), name = "(" + o.k + ")'s " + (page.planOf(o) ? "plan" : "text");
    if (ls[0] != null) medium(name, ls[0]);
    if (ls[1] != null) high(name, ls[1]); }
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
  /* an item's per (F6) is its outcome under each option: one that names the recommended option alone reads as the
     recommendation's; one naming (z) beside it also says what waiting does, and passes */
  page.itemsOf(c).forEach((x, i) => { const ks = page.perOf(x).map(p => p[0]);
    if (ks.length === 1 && ks[0] === c.rec)
      say("rec-only item " + (i + 1), "impact: item " + (i + 1) + " (" + x.name + ")'s per gives only the recommended option's outcome: give its outcome under each option, or leave per out when every option leaves it the same"); });
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
  /* the Finding says how it happens too (F7): a mechanism of a bare label is the finding's name, not its mechanism */
  const f = page.findingOf(c), fm = f ? f.mechanism : null;
  if (typeof fm === "string" && words(fm) <= MECH_MIN)
    say("mech finding", "impact: the finding's mechanism is " + words(fm) + " words (\"" + fm.trim() + "\"): say how it happens, who meets it and when; or leave it knowingly");
}

/* ---- the likelihood lint (F9, answer 267 (a), widened): the Likelihood's line gives the strongest concrete fact, else
   the evidence there is; never a bare no data, never an estimated probability, and a percentage only as an observed
   share with its source. Proxies over the shown seen (the page's own likelihoodOf); a lint, never a refusal, so a
   carried-over card renders ---- */
const LK_NO_DATA = /^\W*(no (data|records?|information)( (available|yet|so far|found))?|unknown|not known|none known|tbd)\W*$/i;
const LK_ESTIMATE = /\b(likely|unlikely|probab(ly|le|ility|ilities)|chances?|odds|maybe|perhaps|almost certain(ly)?|guess(ed)?|presumabl[ey])\b/i;
/* quoted text (a log line, a message as written) is not the writer's estimate: read the line without it */
const unquoted = s => s.replace(/`[^`]*`|"[^"]*"|“[^”]*”/g, " ");
/* a share: "%", "percent", or a ratio in words ("nine in ten", "one in 40") */
const LK_SHARE = /%|\bper\s?cent\b|\b\w+ in (?:ten|a hundred|\d+)\b/gi;
/* the first share with no source: none in a bracket after it, and not inside a bracket that also holds a word
   ("(CI history, 7.5%)"); null when every share is sourced */
const unsourcedShare = s => {
  for (const m of s.matchAll(LK_SHARE)) {
    const at = m.index, end = at + m[0].length;
    if (s.slice(end).includes("(")) continue;
    const open = s.lastIndexOf("(", at), shut = s.lastIndexOf(")", at);
    if (open > shut) { const close = s.indexOf(")", end), inner = s.slice(open + 1, close < 0 ? s.length : close);
      if (/[A-Za-z]{2,}/.test(inner.replace(m[0], " "))) continue; }
    return m[0];
  }
  return null;
};
/* an observed fact's source, in brackets at the end */
const LK_SOURCE_END = /\([^()]+\)\W*$/;
/* the upgrader's carried-over basis word at the head of an evidence seen: "(estimated) …", never "(observed) " */
const LK_CARRIED = /^\s*\((?!observed\))[a-z]+\)\s/;
function likelihoodLint(c, say) {
  const l = page.likelihoodOf(c);
  if (!l) return;
  const s = l.seen, fix = "name the event, then the strongest fact (a count with its window and source), else the evidence there is and what would settle it";
  if (LK_NO_DATA.test(s))
    say("likelihood no-data", "impact: the likelihood says only \"" + s.trim() + "\": " + fix + "; a bare no data is never the line");
  const e = unquoted(s).match(LK_ESTIMATE);
  if (e) say("likelihood estimate", "impact: the likelihood holds an estimate (\"" + e[0] + "\"): give an observed fact instead, or the evidence there is; or leave it knowingly");
  const p = unsourcedShare(s);
  if (p) say("likelihood percent", "impact: the likelihood gives a share (\"" + p + "\") with no source in brackets beside it: a percentage is an observed share, with its source and window; or leave it knowingly");
  if (l.kind === "evidence" && LK_CARRIED.test(s))
    say("likelihood carried", "impact: the likelihood opens on a carried-over basis word (\"" + s.trim().match(/^\([^)]*\)/)[0] + "\"): " + fix + ", and drop the word");
  if (l.kind === "observed" && !LK_SOURCE_END.test(s))
    say("likelihood source", "impact: an observed likelihood ends on no source in brackets: give where the fact comes from, (the provider's status page); or leave it knowingly");
  /* Best response? (answer 339 (a)): owed by a new card beside its likelihood; one the upgrader carried over may lack it */
  if (!page.bestOf(c) && !carried(c))
    say("best", "impact: the likelihood has no best: say on Best response? whether acting here is the most important response to that failure, and if not, what is; or leave it knowingly on a card carried over by the upgrader");
}

/* the Finding's words in the card in all: its title, where and mechanism; never its excerpt, which has its own size */
const findingWords = c => { const f = page.findingOf(c); return f ? [f.title, f.where, f.mechanism].filter(s => typeof s === "string") : []; };
/* ---- the depth lints (decision 198): sizes read at each part's top level, words split on whitespace ---- */
const topOf = (sum, ls) => ls.length ? ls[ls.length - 1] : sum;

function depth(c, say) {
  const imp = c.impact;
  const summary = {context: c.context, impact: IMP.map(k => imp[k]), tldr: c.tldr,
    rec: [c.reason], why: c.why, whyask: c.whyask, evidence: c.evidence};
  /* a level replaces the one below it, so it says more */
  const grow = (name, key, sum, ls) => { const ws = [words(sum), ...ls.map(words)];
    for (let i = 1; i < ws.length; i++) if (ws[i] <= ws[i - 1])
      say("grow " + key + i, "depth: " + name + " " + LEVEL[i] + " is not longer than its " + LEVEL[i - 1] + " (" + ws[i] + " words against " + ws[i - 1] + "): each level is a fuller rendition of the one below it"); };
  for (const k in PART) grow(PART[k], k, summary[k], levelsOf(c, k));
  for (const o of opts(c)) grow("(" + o.k + ")'s " + (page.planOf(o) ? "plan" : "text"), "o" + o.k, optProse(o), optLevels(o));
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
    const top = words(topOf(optProse(o), optLevels(o)));
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
     among them), the What part (its text and its items), the Finding (not its excerpt), the Scope, the Likelihood and Best response?, the Rejected alternatives fold, each option's detail (its plan or text at its top level, and its facets), its inline Pros and Cons
     rows and the points of its view's Pros | Cons table; not act, and not the attachments (F3), which keep their own size */
  const pc = opts(c).reduce((n, o) => n + words(page.proCon(o).map(r => r[1])) + words(page.prosCons(o).map(r => r[1])), 0);
  const all = words(flat(c)) + words(c.context) + words(whatTexts(c)) + bg + ev + words(findingWords(c)) + words(scopeTexts(c)) + words(likelihoodTexts(c)) + words(rejectedTexts(c)) + words(topOf(c.reason, levelsOf(c, "rec"))) + words(as) + optWords + pc;
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
const PROCON_CAP = 25;
function tradeoffs(c, say) {
  const real = opts(c).filter(o => o.k !== "z");
  /* a row is one line: a pro or con past the cap is a paragraph, which belongs in pros or cons */
  for (const o of real) for (const [l, v] of page.proCon(o)) { const n = words(v);
    if (n > PROCON_CAP) say("tradeoffs long " + o.k + l, "shape: (" + o.k + ")'s " + (l === "Pros" ? "pro" : "con") + " is " + n + " words: keep its " + l + " row to one line, about " + PROCON_CAP + " words; the points in full go in " + (l === "Pros" ? "pros" : "cons")); }
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

/* ---- the plan lint (F5): an option's view opens on its Plan in brief, what choosing it sets in motion, 2-4
   sentences. It reads the page's own planOf, so a none plan counts as missing. (z) gives one too: what deciding
   later sets in motion. A card with no plan on any option gets one line ---- */
const PLAN_CAP = 100;
function plan(c, say) {
  const os = opts(c), miss = os.filter(o => !page.planOf(o)).map(o => o.k);
  for (const o of os) { const n = words(page.planOf(o));
    if (n > PLAN_CAP) say("plan long " + o.k, "depth: (" + o.k + ")'s plan is " + n + " words: keep its Plan in brief to 2–4 sentences, about " + PLAN_CAP + " words at most; its fuller renditions go in its levels (detail)"); }
  /* a view opens on the plan: an option's text beside it is never shown */
  for (const o of os) if (page.planOf(o) && typeof o.text === "string" && o.text.trim())
    say("plan text " + o.k, "depth: (" + o.k + ") has both plan and text; text is not shown: its view opens on the plan, so put what text says in the plan or its levels (detail), and drop text");
  if (!miss.length) return;
  if (miss.length === os.length && os.length > 1)
    say("plan", "depth: none of the card's " + os.length + " options carries its plan in brief: give each, (z) too, a plan (2–4 sentences, what choosing it sets in motion), the first part of its view; or leave it knowingly on an upgraded older card, whose view shows its text instead");
  else for (const k of miss)
    say("plan " + k, "depth: (" + k + ") has no plan: give it a Plan in brief (plan: 2–4 sentences, what choosing it sets in motion), the first part of its view; or leave it knowingly on an upgraded older card, whose view shows its text instead");
}

/* ---- the attachments' size (F3, the attachments proposal's limits): at most ATT_CAP on a card; an excerpt-shaped body
   about XC_LINES lines or XC_BYTES bytes at most, a longer one cut with the cut said where it is ---- */
const ATT_CAP = 6, XC_LINES = 80, XC_BYTES = 4096;
function attachedSize(c, say) {
  const as = page.attachedOf(c);
  if (as.length > ATT_CAP) say("attached", "depth: the card carries " + as.length + " attachments: keep it to about " + ATT_CAP + "; point to the rest from one summary, or leave it knowingly");
  /* a source line: src, else an excerpt-shaped body's own src, as the page shows it */
  const shownSrc = v => typeof v === "string" && !!v.trim() && !["none", "n/a", "-"].includes(v.trim().toLowerCase());
  as.forEach((a, i) => { const b = a.body;
    if (a.kind !== "example" && !shownSrc(a.src) && !(isExcerptObj(b) && shownSrc(b.src)))
      say("attached src " + i, "depth: attachment " + (i + 1) + " (" + a.title + ") has no source line: say in src where it came from (a path and range at a commit, a command and when it ran, the full text's place, where it was cited); or leave it knowingly");
    if (!(XC_KINDS.has(a.kind) || (a.kind === "example" && a.form === "mock")) || !b || typeof b.text !== "string") return;
    const n = b.text.replace(/\r\n?/g, "\n").replace(/\n$/, "").split("\n").length, bytes = Buffer.byteLength(b.text, "utf8");
    if (n > XC_LINES || bytes > XC_BYTES)
      say("attached " + i, "depth: attachment " + (i + 1) + " (" + a.title + ") is " + n + " lines, " + bytes + " bytes: keep an excerpt to about " + XC_LINES + " lines or " + XC_BYTES + " bytes; cut it and say in the text where the cut is and where the rest is, or leave it knowingly"); });
}

/* ---- the source label's short name: plain words, about 2 to 6 ---- */
function labelName(c, say) {
  /* the card's label, else its finding's (F7): either is shown with its short name */
  const l = c.label || (c.finding && c.finding.label);
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
  page.itemsOf(c).forEach((x, i) => put("item " + (i + 1), [x.name, x.where, x.about, ...page.perOf(x).map(p => p[1])]));
  /* the Finding as the page shows it: its label with its short name (a declared label passes), title, where and
     mechanism; never its excerpt, verbatim data whose src names a commit by design */
  { const f = page.findingOf(c);
    if (f) put("finding", [f.label && typeof f.label === "object" && typeof f.label.id === "string" ? f.label.id + " (" + f.label.name + ")" : null,
      f.title, f.where, f.mechanism].filter(s => typeof s === "string")); }
  put("scope", scopeTexts(c));
  put("likelihood", likelihoodTexts(c));
  put("rejected", rejectedTexts(c));
  put("attached", attachedTexts(c));
  if (Array.isArray(c.assume)) for (const a of c.assume) if (a && typeof a === "object") put("assume", [a.rests, a.tw]);
  for (const o of opts(c)) {
    for (const k of ["title", "line", "text", "plan", "effect", "reach", "undo", "cost", "pro", "con", "pros", "cons"]) put("(" + o.k + ")", o[k]);
    if (Array.isArray(o.act)) put("act (" + o.k + ")", o.act);
    if (Array.isArray(o.detail)) put("detail (" + o.k + ")", o.detail);
  }
  if (c.detail && typeof c.detail === "object") for (const k in c.detail)
    put("detail." + k, k === "impact" && Array.isArray(c.detail.impact) ? c.detail.impact.map(l => l && typeof l === "object" ? IMP.map(f => l[f]) : l) : c.detail[k]);
  return out;
}
const LEDE_REPO = /\brepo(s|sitory|sitories)?\b/i;
function pageIds(d, out) {
  const say = line => out.push("lint: page: " + line), seen = new Set();
  const look = (at, s) => { if (typeof s === "string") for (const x of ids(s)) if (!seen.has(at + x[0])) { seen.add(at + x[0]); say(idLine(x, at)); } };
  const pg = d.page && typeof d.page === "object" ? d.page : {};
  look("the page title", pg.title); look("the lede", pg.lede);
  /* excerpts on a page (an excerpt-shaped attachment, a Finding's excerpt): its lede names the repos they come from, so the
     operator knows what a share would expose. A heuristic: the lede holds the word repo, repos, repository or
     repositories */
  const xc = d.cards.some(c => (c.finding && typeof c.finding === "object" && c.finding.excerpt != null)
    || page.attachedOf(c).some(a => XC_KINDS.has(a.kind) || (a.kind === "example" && a.form === "mock")));
  if (xc && !(typeof pg.lede === "string" && LEDE_REPO.test(pg.lede)))
    say("lede names no repo, though the page shows excerpts: say in the lede which repos they come from (e.g. 'excerpts from the <name> repo'), so a share's reach is known; or leave it knowingly");
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
  /* an item card in a bundle may lean on its group's shared context (rule 263); the What part, after Context,
     introduces too: its text, and a set's items, whose number is itself named by the list */
  const items = page.itemsOf(c);
  const ctx = [c.context, ...whatTexts(c), typeof sh === "string" ? sh : ""].join(" ");
  const ctxNums = new Set(counts(ctx).map(x => x.n)), ctxLow = ctx.toLowerCase();
  if (items.length) ctxNums.add(items.length);
  const seen = new Set(), say = (key, line) => { if (!seen.has(key)) { seen.add(key); out.push(w + line); } };
  for (const [at, s] of cardTexts(c)) for (const x of ids(s)) say("id " + x[0], idLine(x, at));
  /* the terms a visible text uses, against Context's summary; at is "" for the flat part, or " (part, level)" */
  const terms = (fields, at, namer = named, fix = "say what the WORD things are, or list them, in context", withCounts = true) => {
    if (withCounts) for (const s of fields) for (const x of counts(s)) if (!ctxNums.has(x.n))
      say("count " + x.n, "\"" + x.word + "\"" + at + " counts things its context does not name: " + fix.replace("WORD", x.word));
    for (const s of fields) for (const t of namer(s)) if (!ctxLow.includes(t))
      say("named " + t, "\"" + t + "\"" + at + " is not glossed in its context: give it a one-line gloss in context, what it is and where it comes from");
  };
  /* a count where the card says what is decided names a set: its items belong in the What part (F6) */
  terms(decided(c), "", named, "list the WORD things in items, the What part, one each with its name; or say what they are in context");
  terms(flat(c), "");
  /* the Finding, never folded, after What (F7): its title and mechanism */
  terms(findingTexts(c), " (the finding)");
  /* the Scope, never folded, after the Finding (F8): its says */
  terms(scopeTexts(c), " (the scope)");
  /* the Likelihood and Best response?, never folded, after the Scope (F9). An observed count in seen is the fact the
     line exists to give (how often the event happens, with its window and source), not a set Context must name: seen
     is read for named things only; Best response? is read whole */
  { const l = page.likelihoodOf(c), b = page.bestOf(c);
    if (l) terms([l.seen], " (the likelihood)", named, undefined, false);
    if (b) terms([b], " (the likelihood)"); }
  /* the Rejected alternatives fold (F2), the last bottom fold: its titles, which its summary shows; the reasons sit in
     the closed fold, as the other folds' text does */
  terms(page.rejectedOf(c).map(r => r.t), " (rejected alternatives)");
  /* the Attached fold (F3): its titles, which its summary shows; the rest sits in the closed fold */
  terms(page.attachedOf(c).map(a => a.title), " (attached)");
  attachedSize(c, say);
  /* the Pros and Cons rows are visible too, though not in the flat part's budget: the cold read covers them */
  terms(opts(c).flatMap(o => page.proCon(o).map(r => r[1])), " (pros and cons)");
  /* and each option's view (F5), which picking the option opens: its plan in brief and its Pros | Cons table */
  terms(opts(c).flatMap(viewTexts), " (an option's view)", namedView);
  c.tldr.forEach((b, i) => { if (REC_BROAD.test(b))
    say("tldr " + i, "tldr bullet " + (i + 1) + " may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); });
  /* the visible parts' medium and high: each steps alone, so the Context beside them may be its summary. The basis
     line's levels are in the closed Assumptions fold, so they are not read */
  for (const k of ["impact", "tldr"]) levelsOf(c, k).forEach((r, i) => terms(k === "impact" && r && typeof r === "object" ? textsOf(IMP.map(f => r[f])) : textsOf(r), " (" + PART[k] + ", " + DETAIL_NAME[i] + ")"));
  /* a TLDR level's headings, bullets and sub-bullets, numbered in reading order as the page numbers them */
  levelsOf(c, "tldr").forEach((bs, m) => textsOf(bs).forEach((b, i) => { if (REC_BROAD.test(b))
    say("tldr " + m + "." + i, "tldr bullet " + (i + 1) + " (" + DETAIL_NAME[m] + ") may carry the recommendation: the options mark it; say what is decided instead, or leave it if it reports someone else's"); }));
  /* the set check's lint: a list of another length, or a carried-over card's set (its refusal is setProblems') */
  const sc = setCheck(c);
  if (sc && !sc.refuse) say("set", "shape: " + sc.text);
  /* a count in what (F6): the What part says what is decided, so a count there names a set its items list */
  if (typeof c.what === "string") { const nOpts = opts(c).filter(o => o.k !== "z").length;
    for (const x of setCounts(c.what, nOpts)) if (x >= 2 && x !== items.length)
      say("count " + x, "what counts " + x + " things its items do not list" + (items.length ? " (items lists " + items.length + ")" : "") + ": list each in items, one each with its name; or leave it knowingly when the count names something else"); }
  shapes(c, say);
  recOnly(c, say);
  systemOnly(c, say);
  mech(c, say);
  likelihoodLint(c, say);
  depth(c, say);
  oneway(c, say);
  tradeoffs(c, say);
  plan(c, say);
  labelName(c, say);
}

/* ---- the dependency order (03ab F7, answer 307 (a)): inside a group, each card after every card it depends on.
   A card's dep names its targets as slugs; a target that is a card in the same layer and comes later in cards fires,
   once per target. A target on another layer, in refs, or in another repo (no slug) is never read; a pair in a dep
   cycle (the target reaches the card back through the page's own deps) is skipped, its members ordered by the
   precedence alone ---- */
const depsOf = c => typeof c.dep !== "string" ? []
  : [...new Set([...c.dep.matchAll(/\[\[([0-9]+)\]\]/g)].map(m => m[1]))];
function depOrder(d) {
  const at = new Map(d.cards.map((c, i) => [String(c.n), i]));
  const edges = new Map(d.cards.map(c => [String(c.n), depsOf(c).filter(m => at.has(m))]));
  const reaches = (from, to) => { const seen = new Set(), todo = [from];
    while (todo.length) { const x = todo.pop(); if (x === to) return true;
      if (!seen.has(x)) { seen.add(x); todo.push(...(edges.get(x) || [])); } }
    return false; };
  return c => { const me = String(c.n), i = at.get(me);
    return (edges.get(me) || []).filter(m => { const t = d.cards[at.get(m)];
      return t.L === c.L && at.get(m) > i && !reaches(m, me); }); };
}
function deporder(c, late, say) {
  for (const m of late(c))
    say("deporder " + m, "depends on [[" + m + "]], which comes after it in its group; move it after"); }

function lint(d) {
  const out = [];
  DECLARED = declare(d.cards);
  pageIds(d, out);
  const late = depOrder(d);
  for (const c of d.cards) {
    const w = "lint: card " + c.n + ": ";
    lintCard(c, w, (d.layers.find(l => l[0] === c.L) || [])[3], out);
    const seen = new Set();
    deporder(c, late, (key, line) => { if (!seen.has(key)) { seen.add(key); out.push(w + line); } }); }
  return out;
}

/* ---- the set check (F6, b78c): a card about a set cannot pass without its items named. A count of two or more
   where the card says what is decided needs its items. Refused when there are none, or fewer than the largest count;
   any other mismatch (a list of another length) is a lint. A card the upgrader carried over (its upgraded.rev equal to
   its rev: format only, rev kept) gets the lint in place of the refusal, so a lazy upgrade stays seamless; once a
   writer revises it with a new rev, it is refused like any card. The runner's alone: the page's check() never
   refuses it, so an older published page still renders ---- */
/* a numeral (digits or a word) labels one thing, never counts a set, when it comes right after a singular label
   noun from a closed list (LABEL_HEAD: principle, step, tier, option, …), or after a plural one before the text's
   end, punctuation, a function word or a verb and its object: principle 3, Phase 2 plan, step 2 of the guide, tier
   three, Option two first, issues 7 breaks the build. After any other word it counts: "Retire 3 plugins this
   quarter", "Delete three", "Archive 5 in this round", "the three pages", "fix items 3 broken links" */
const LABEL_NUM = /([A-Za-z]+)\s+$/;
const LABEL_HEAD = /^(?:principle|step|tier|option|phase|stage|rule|finding|item|issue|answer|decision|question|section|chapter|part|level|round|wave|track|version|row|line|card|page|figure|table|note|point|criterion|requirement|ticket|case|test|example|layer|group|slot|lane|sprint|milestone)s?$/i;
const COUNT_DET = new Set([...DET, "all", "both", "only", "first", "last", "other", "of", "between", "on", "in", "at",
  "to", "for", "from", "with", "after", "before", "by", "over", "under", "up", "top", "remaining", "next", "final"]);
const OBJ_DET = new Set(["the", "a", "an", "this", "that", "these", "those", "its", "their", "our", "your", "his", "her"]);
const FUNC_AFTER = new Set(["of", "and", "or", "nor", "to", "in", "on", "at", "by", "for", "from", "with", "into", "onto", "per",
  "via", "as", "if", "but", "not", "so", "than", "then", "now", "only", "first", "already", "also", "again", "still",
  "says", "said", "say", "is", "are", "was", "were", "be", "been", "has", "had", "have", "does", "did", "do", "will",
  "would", "can", "could", "may", "might", "must", "should", "which", "that", "this", "these", "those", "it", "its",
  "the", "a", "an", "when", "while", "before", "after", "under", "over", "until", "since"]);
const isLabelNum = (t, m) => { const p = t.slice(0, m.index).match(LABEL_NUM);
  if (!p || COUNT_DET.has(p[1].toLowerCase()) || !LABEL_HEAD.test(p[1])) return false;
  if (!/s$/i.test(p[1])) return true;
  const rest = t.slice(m.index + m[1].length), nx = rest.match(/^\s+([A-Za-z]+)(?:\s+([A-Za-z]+))?/);
  return !rest.trim() || /^\s*[.,;:!?)\]—–]/.test(rest) || (!!nx && FUNC_AFTER.has(nx[1].toLowerCase()))
    || (!!nx && /s$/i.test(nx[1]) && !!nx[2] && OBJ_DET.has(nx[2].toLowerCase())); };
/* a version or a code: a numeral right after a capitalised word that is not the text's first word (Drop Python 2
   support, Use Node 22, HTTP 404), whatever follows it */
const afterName = (t, m) => { const p = t.slice(0, m.index).match(LABEL_NUM);
  return !!p && /^[A-Z]/.test(p[1]) && !!t.slice(0, p.index).trim(); };
const MONTH = "(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)";
/* a date: a numeral next to a month name (26 October, October 26) */
const nearMonth = (t, m) => new RegExp("\\b" + MONTH + "\\.?\\s*$", "i").test(t.slice(0, m.index))
  || new RegExp("^\\s+" + MONTH + "\\b", "i").test(t.slice(m.index + m[1].length));
/* a list of labels: numerals in a run, "findings 3, 4 and 7", "issues 12, 14" */
const inNumList = (t, m) => /^[0-9]+$/.test(m[1]) && (/^\s*(?:,|and|or)\s*[0-9]+\b/.test(t.slice(m.index + m[1].length))
  || /\b[0-9]+\s*(?:,|and|or)\s*$/.test(t.slice(0, m.index)));
/* not a set's count: N times; a range (3-5, pages 3-5, 1350 to 900 words); a number after a slash (HTTP/2) or a
   currency sign ($30); a setting's value after "to" or "at" with no plural noun after it (set the timeout to 30); N
   of the …, a part of a set named elsewhere; a quantity of a unit (2 spaces, 600 words, two rounds) */
const SET_UNIT = "(?:rounds?|spaces?|words?|characters?|chars?|lines?|columns?|bytes?|tokens?|sentences?|bullets?|px|em|rem|pt|times)";
const notSetCount = (t, m) => { const before = t.slice(0, m.index), after = t.slice(m.index + m[1].length);
  return /[-–/$£€]\s*$/.test(before) || /\b(?:to|and)\s+$/.test(before) && /\d\s*$/.test(before.replace(/\s*(?:to|and)\s+$/, ""))
    || /\b(?:to|at)\s+$/i.test(before) && !/^\s+[A-Za-z]+s\b/.test(after)
    || /^\s*[-–]\s*\w/.test(after) || /^\s+to\s+[0-9]+\b/.test(after) || new RegExp("^(?:\\s*(?:to|and|-|–)\\s*[0-9a-z]+)?\\s+" + SET_UNIT + "\\b", "i").test(after)
    || /^\s+of\s+(?:the|these|those|its|our|your|their|them)\b/i.test(after) && !/\b(?:all|both|each)\s+$/i.test(before); };
/* "both" before a plural noun counts two (Retire both plugins); "both" alone, "both options", or "both" before a
   function word ending in s (Treat both as …) does not */
const BOTH = /\bboth\s+([A-Za-z]+s)\b/gi;
/* a sentence about the options themselves: a count equal to the real options' is the options, not a set */
const ABOUT_OPTIONS = /\b(?:options?|which of|which one|between|one of|either)\b/i;
/* a count of 100 or more (a status code, a size) is never refused: SET_BIG and over is linted only */
const SET_BIG = 100;
const setCounts = (s, nOpts) => { const t = unId(s);
  return [...t.matchAll(COUNT)].filter(m => !(/^[0-9]+$/.test(m[1]) && YEAR.test(m[1])) && !isLabelNum(t, m)
    && !afterName(t, m) && !nearMonth(t, m) && !inNumList(t, m) && !notSetCount(t, m))
    .map(m => W[m[1].toLowerCase()] || Number(m[1]))
    .concat([...t.matchAll(BOTH)].filter(m => !/^options$/i.test(m[1]) && !FUNC_AFTER.has(m[1].toLowerCase())).map(() => 2))
    .filter(x => !(x === nOpts && ABOUT_OPTIONS.test(t))); };
/* a card the upgrader carried over, format only: its marker names the rev it kept */
const carried = c => !!c.upgraded && typeof c.upgraded === "object" && c.upgraded.rev === c.rev;
/* the set check on one card: null, or {refuse, text} */
function setCheck(c) {
  const n = page.itemsOf(c).length, nOpts = opts(c).filter(o => o.k !== "z").length, seen = new Set();
  for (const s of decided(c)) for (const x of setCounts(s, nOpts)) if (x >= 2) seen.add(x);
  if (!seen.size) return null;
  const max = Math.max(...seen), short = n < max;
  if (!short && seen.has(n)) return null;
  /* refused only short of a count under SET_BIG; short of a bigger one alone, linted */
  const small = [...seen].filter(x => x < SET_BIG), refuse = !!small.length && n < Math.max(...small) && !carried(c);
  return {refuse, text: "a set not listed in items: it counts " + [...seen].join(" and ") + " things where it says what is decided"
    + (n ? ", but items lists " + n : ", and there are no items") + ": " + (short
      ? "list each in items (the What part: {name, where, about, per}), so the operator can name every item it acts on"
        + (carried(c) ? "; carried over by the upgrader with its rev, so linted, and refused once revised with a new rev" : "")
      : "make the count and the list agree, or leave it knowingly when the count names something else")};
}
function setProblems(c, w) { const s = setCheck(c); return s && s.refuse ? [w + ": " + s.text] : []; }

/* ---- the attachment refusals (F3): the runner's own, so an older published page still renders ---- */
/* a link to an attachment: [[att:id|label]], the id one the card attaches. The page shows any other as its label, or
   as written; here it is refused. Every text of the card is read, but excerpts (verbatim data, never parsed) */
const ATT_LINK_AT = /\[\[att:/g, ATT_LINK_FULL = /^\[\[att:([a-z0-9-]+)\|[^\]\r\n]+\]\]/;
const isExcerptObj = v => v && typeof v === "object" && !Array.isArray(v) && typeof v.text === "string" && Object.keys(v).every(k => k === "text" || k === "lang" || k === "src");
const stringsAt = (v, at, out) => { if (typeof v === "string") out.push([at, v]);
  else if (Array.isArray(v)) v.forEach((x, i) => stringsAt(x, at + "[" + i + "]", out));
  else if (v && typeof v === "object" && !isExcerptObj(v)) for (const k of Object.keys(v)) stringsAt(v[k], at ? at + "." + k : k, out);
  return out; };
function attLinkProblems(c, w) {
  const ids = new Set(page.attachedOf(c).map(a => a.id).filter(x => typeof x === "string")), out = [];
  for (const [at, s] of stringsAt(c, "", [])) for (const m of s.matchAll(ATT_LINK_AT)) {
    const f = s.slice(m.index).match(ATT_LINK_FULL);
    if (!f) out.push(w + ": " + at + " has a link to an attachment not written [[att:id|label]]: the id in lower-case letters, digits and -, then | and the words the link shows");
    else if (!ids.has(f[1])) out.push(w + ": " + at + " links attachment " + f[1] + ", which the card does not attach: give that attachment its id, or drop the link");
  }
  return out;
}
/* a secret in an attachment (any of its text, excerpts included) or in the Finding's excerpt: refused, never a lint.
   Each pattern is POSIX ERE as well as JavaScript, case-insensitive, read a line at a time: the decision-page skill's
   grep step runs these same patterns over cards.json where there is no node. The problem names where it is and,
   for an assignment, its key: never the value. The grep reads cards.json as JSON, where a line break, a tab or a
   character outside ASCII before a token is an escape (\n, \t, \u201c): a token's left boundary takes those too. The
   assignment's quantifiers are bounded, so a long line cannot make it backtrack. The patterns are a net, not a proof: a value holding a backslash, quote or space in its first 16 characters, a key running more than 80 characters past its keyword, or more than 80 spaces around its = or : passes both; the cold read's item 6 is the check for those. */
const SECRET_PATTERNS = [
  ["a private key block", "-----BEGIN[ A-Z]*PRIVATE KEY-----"],
  ["a GitHub token", "(^|[^A-Za-z0-9]|\\\\[nrtbf]|\\\\u[0-9A-Fa-f]{4})(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}"],
  ["a GitHub token", "github_pat_[A-Za-z0-9_]{30,}"],
  ["a GitLab token", "glpat-[A-Za-z0-9_-]{20,}"],
  ["a Slack token", "xox[abprs]-[A-Za-z0-9-]{10,}"],
  ["an AWS access key", "(^|[^A-Za-z0-9]|\\\\[nrtbf]|\\\\u[0-9A-Fa-f]{4})AKIA[0-9A-Z]{16}"],
  ["a Google API key", "AIza[0-9A-Za-z_-]{35}"],
  ["an API key", "(^|[^A-Za-z0-9]|\\\\[nrtbf]|\\\\u[0-9A-Fa-f]{4})sk-[A-Za-z0-9_-]{20,}"],
  ["an assignment of a secret", "[A-Za-z0-9_-]{0,40}(password|passwd|secret|token|api[_-]?key|access[_-]?key)[A-Za-z0-9_-]{0,80}.?.? {0,80}[:=] {0,80}.?.?[A-Za-z0-9_./+=-]{16,}"],
];
/* the key an assignment names, echoed only when it cannot be part of the value: a name of at most 41 characters that,
   with its keyword taken out, holds no run of 8 or more letters and digits; else null, and the problem names only the
   keyword it holds, leaving <name> for the writer to fill with the real key */
const safeKey = m => { const k = (m[0].match(/^[A-Za-z0-9_-]+/) || [""])[0];
  return /^[A-Za-z_][A-Za-z0-9_-]{0,40}$/.test(k) && !/[A-Za-z0-9]{8,}/.test(k.replace(m[1], "-")) ? k : null; };
const SECRET_RE = SECRET_PATTERNS.map(([name, ere]) => [name, new RegExp(ere, "i")]);
function secretProblems(c, w) {
  const out = [], look = (at, v) => { const all = (o, p) => { if (typeof o === "string") o.split(/\r\n?|\n/).forEach((line, i) => {
      for (const [name, re] of SECRET_RE) { const m = line.match(re); if (!m) continue;
        const asg = name === "an assignment of a secret", key = asg ? safeKey(m) : "";
        out.push(w + ": " + p + " line " + (i + 1) + " looks like it holds a secret (" + name + (key ? ", key " + key : asg ? ", its key holds " + m[1] : "") + "): never its value on the page; say where it is kept and under which key, [redacted: key " + (key || "<name>") + " in <where it is kept>]");
        break; } });
    else if (Array.isArray(o)) o.forEach((x, i) => all(x, p + "[" + i + "]"));
    else if (o && typeof o === "object") for (const k of Object.keys(o)) all(o[k], p + "." + k); };
    all(v, at); };
  if (Array.isArray(c.attached)) c.attached.forEach((a, i) => look("attached " + (i + 1), a));
  if (c.finding && typeof c.finding === "object" && c.finding.excerpt != null) look("finding.excerpt", c.finding.excerpt);
  return out;
}
const attRefusals = (c, w) => [...attLinkProblems(c, w), ...secretProblems(c, w)];

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
try {
  DECLARED = declare(record ? [d] : d.cards);
  bad = record ? [...attRefusals(d, "record " + d.n), ...setProblems(d, "record " + d.n)]
    : d.cards.flatMap(c => [...attRefusals(c, "card " + c.n), ...setProblems(c, "card " + c.n)]);
} catch (e) { fail("the attachment and set checks stopped on this file: " + why(e)); }
if (bad.length) { process.stdout.write(bad.join("\n") + "\n"); process.exit(1); }
let lines = [];
try {
  if (record) { DECLARED = declare([d]); lintCard(d, "lint: record " + d.n + ": ", null, lines); }
  else lines = lint(d);
} catch (e) { fail("the lints stopped on this file: " + why(e)); }
if (lines.length) { process.stdout.write(lines.join("\n") + "\n"); process.exit(2); }
process.exit(0);
