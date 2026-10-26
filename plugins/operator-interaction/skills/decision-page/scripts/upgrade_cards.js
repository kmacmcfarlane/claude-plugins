#!/usr/bin/env node
/* decision-page upgrader (operator-interaction): older page data to decision-page/5, format only, every rev kept.

     node upgrade_cards.js IN OUT [--questions QMAP] [--only LIST] [--records DIR]

   IN is a cards.json in one of three shapes, told apart card by card by their fields and stamps:
     1. legacy shipped: options as arrays (o), with blocks, act, detail.o, warn and unknown beside them;
     2. the kit (the live page's working shape, v4 or v5 layout): options as objects with no format stamp,
        pros/cons as the inline lines and prosT/consT as the table rows, assume, background, attachments;
     3. already decision-card/5 (stamped): passed through as it is.
   A file whose envelope is already decision-page/5 is copied to OUT byte for byte ("already decision-page/5");
   it still honours --only (OUT then holds the set's cards) and --records (the set's records written).
   Every rev is kept byte for byte: an answer counts only when its rev equals its card's exactly. Every n must be a
   whole number of 1 or more, used once; it names the record file.

   --questions QMAP  a JSON object {"N": "the question"}: each upgraded card's q (the headline's question). A card
                     that carries its own q keeps it.
   --only LIST       a file of decision numbers, one a line: only those cards are upgraded and written; every other
                     card in IN is left out of OUT, unchecked.
   --records DIR     also writes DIR/<N>.json per card: the card record, without the page-only L and dep.

   All or nothing: any card it cannot fully map (no q, a field it does not know, an unknown scope level, unequal
   assumption lists, a writer marker, a newer stamp) stops the run: exit 1, every problem listed with its card,
   nothing written. On success it prints a line per card (rev kept byte for byte, or new) and every
   value it moved with a note, and exits 0. It reads JSON and writes JSON; it never evaluates content.
   Writes: OUT's directory is made, OUT is written first, then each record; every file goes to a temp name in its
   own directory and is renamed over its target, so a failed write leaves no half-written file. A record file it
   will replace is named before it is replaced.
   Exit 2: usage, a file that cannot be read or parsed, or a write that fails (one plain line). Node built-ins only. */
"use strict";
const fs = require("fs"), path = require("path");

const PAGE_FORMAT = "decision-page/5", CARD_FORMAT = "decision-card/5";
const NONE = new Set(["", "none", "none.", "n/a", "n/a.", "-", "–", "—"]);
const isNone = v => v == null || (typeof v === "string" && NONE.has(v.trim().toLowerCase()));
const isObj = v => !!v && typeof v === "object" && !Array.isArray(v);
const isStr = v => typeof v === "string";
const REV_SECONDS = /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/;
const REV_MINUTES = /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z$/;
const LETTER = /^[a-z]$/;
/* a decision number: a whole number of 1 or more (it names a record file under --records) */
const isPosInt = v => typeof v === "number" && Number.isInteger(v) && v >= 1;
const nowUtc = () => new Date().toISOString().replace(/\.[0-9]+Z$/, "Z");
const stampOf = (v, name) => { const m = isStr(v) ? v.match(/^([a-z-]+)\/([0-9]+)$/) : null; return m && m[1] === name ? Number(m[2]) : null; };

function usage(msg) { process.stdout.write("upgrade_cards: " + msg + "\nusage: node upgrade_cards.js IN OUT [--questions QMAP] [--only LIST] [--records DIR]\n"); process.exit(2); }
function readJson(f, what) {
  let t;
  try { t = fs.readFileSync(f, "utf8"); } catch (e) { usage("cannot read " + what + " " + f); }
  try { return JSON.parse(t); } catch (e) { usage(what + " " + f + " is not valid JSON: " + String(e.message).split("\n")[0]); }
}

/* ---- the rev: kept byte for byte (an answer counts only when its rev equals the card's exactly; the minute form is
   one the record reads); anything else the rev pattern refuses gets a new one */
function upgradeRev(rev, note) {
  if (isStr(rev) && (REV_SECONDS.test(rev) || REV_MINUTES.test(rev))) { note.rev = "rev kept"; return rev; }
  note.rev = "new rev (was " + JSON.stringify(rev) + ")";
  return nowUtc();
}

/* ---- shape 1: legacy shipped (c06b's legacy -> 5 map, page rows) ---- */
const LEGACY_KNOWN = new Set(["n", "L", "t", "label", "rev", "impact", "tldr", "context", "what", "why", "whyask", "class",
  "warn", "blocks", "act", "dep", "rec", "norec", "o", "basis", "reason", "unknown", "evidence", "detail", "ifleft",
  "roundcosts", "ifunanswered", "stakes", "q", "raised"]);
const DETAIL_PARTS = new Set(["context", "tldr", "impact", "rec", "why", "whyask", "evidence", "dep"]);

function dropEffect(lv) { if (!isObj(lv)) return lv; const x = Object.assign({}, lv); delete x.effect; return x; }

/* the old card-level effect's clause for option k: "(b) …" up to the next "; (" or its end */
function effectClause(effect, k) {
  if (!isStr(effect)) return null;
  const m = effect.match(new RegExp("\\(" + k + "\\)\\s*([^;]+?)(?=;\\s*\\([a-z]\\)|$)"));
  return m ? m[1].trim() : null;
}

function fromLegacy(c, bad, note) {
  const out = {};
  for (const k of Object.keys(c)) if (!LEGACY_KNOWN.has(k)) bad.push("field " + k + " is not one the legacy shape has: nothing maps it");
  if (!Array.isArray(c.o)) { bad.push("o is not a list of options"); return out; }
  const blocks = isObj(c.blocks) ? c.blocks : {}, act = isObj(c.act) ? c.act : {};
  const dto = isObj(c.detail) && isObj(c.detail.o) ? c.detail.o : {};
  for (const k of ["n", "L", "t", "label", "context", "tldr", "what", "why", "whyask", "class", "dep", "rec", "norec",
    "basis", "reason", "evidence", "ifleft", "roundcosts", "ifunanswered", "q", "raised"]) if (k in c) out[k] = c[k];
  if (c.warn === true) out.oneway = true;
  if (isStr(c.unknown) && !isNone(c.unknown)) out.open = [c.unknown];
  if (isObj(c.impact)) { out.impact = dropEffect(c.impact); if ("effect" in c.impact) note.moved.push("impact.effect dropped (no card-level effect)"); }
  if ("stakes" in c) note.moved.push("stakes dropped (the Impact's undo and reach carry it)");
  out.options = [];
  for (const o of c.o) {
    if (!Array.isArray(o) || o.length !== 5 || !o.every(isStr)) { bad.push("an option is not [letter, full, impact, title, one line]"); continue; }
    const [k, full, imp, title, one] = o;
    /* the letter is checked before anything is built from it (a regex, a key) */
    if (!LETTER.test(k)) { bad.push("an option letter " + JSON.stringify(k) + " is not one letter a-z"); continue; }
    const b = isObj(blocks[k]) ? blocks[k] : null;
    const x = {k, title};
    if (!isNone(one)) x.line = one;
    if (!isNone(full)) x.text = full;
    let effect = b && isStr(b.happens) && !isNone(b.happens) ? b.happens : (!isNone(imp) ? imp : null);
    if (effect == null && k !== "z") { effect = effectClause(c.impact && c.impact.effect, k); if (effect) note.moved.push("(" + k + ")'s effect seeded from the old card-level effect"); }
    if (effect != null) x.effect = effect;
    else if (k !== "z") bad.push("(" + k + ") has no effect of its own, and the old card-level effect names none for it");
    if (b) {
      if ("who" in b && !isNone(b.who)) x.reach = b.who;
      for (const f of ["undo", "cost"]) if (f in b && (f === "undo" || !isNone(b[f]))) x[f] = b[f];
      if (b.oneway === true) x.oneway = true;
    }
    if (Array.isArray(act[k])) x.act = act[k];
    if (Array.isArray(dto[k])) x.detail = dto[k];
    out.options.push(x);
  }
  if (isObj(c.detail)) {
    const d = {};
    for (const k of Object.keys(c.detail)) {
      if (k === "o") continue;
      if (!DETAIL_PARTS.has(k)) { bad.push("detail." + k + " is not a part a card has"); continue; }
      d[k] = k === "impact" && Array.isArray(c.detail.impact) ? c.detail.impact.map(dropEffect) : c.detail[k];
    }
    if (Object.keys(d).length) out.detail = d;
  } else if (c.detail != null) out.detail = c.detail;
  return out;
}

/* ---- shape 2: the kit (its SCHEMA.md as built: v4 with assume.unknown, v5 with open) ---- */
const KIT_KNOWN = new Set(["n", "rev", "L", "t", "label", "oneway", "tldr", "dep", "context", "what", "finding", "scope",
  "likelihood", "best", "open", "assume", "impact", "ifleft", "ifunanswered", "roundcosts", "rec", "norec", "options",
  "act", "background", "attached", "rejected", "why", "whyask", "class", "detail", "evidence", "warn", "q", "raised"]);
const KIT_OPTION = new Set(["k", "text", "line", "pros", "cons", "plan", "effect", "reach", "undo", "oneway", "cost", "prosT", "consT"]);
const SCOPE = {"shapes the work": "shapes", "required": "required", "outside the criteria": "outside"};
const MARKER = "@@WRITE";

function hasMarker(v) { return isStr(v) ? v.includes(MARKER) : Array.isArray(v) ? v.some(hasMarker) : isObj(v) ? Object.values(v).some(hasMarker) : false; }
function lettersPhrase(ls) { const xs = ls.map(l => "(" + l + ")"); return xs.length < 2 ? xs.join("") : xs.slice(0, -1).join(", ") + " or " + xs[xs.length - 1]; }

function fromKit(c, bad, note) {
  const out = {};
  for (const k of Object.keys(c)) if (!KIT_KNOWN.has(k)) bad.push("field " + k + " is not one the kit's schema names: nothing maps it");
  if (hasMarker(c)) bad.push("a writer marker (" + MARKER + ") is still in it: fill it or delete it first");
  for (const k of ["n", "L", "t", "label", "tldr", "context", "best", "ifleft", "ifunanswered", "roundcosts", "rec", "norec",
    "class", "q", "raised"]) if (k in c) out[k] = c[k];
  if (c.oneway === true || c.warn === true) out.oneway = true;
  /* why now and why ask: the Background fold's (answer 338); a top-level pair only where the fold lacks one */
  const bg = isObj(c.background) ? c.background : {};
  for (const k of ["why", "whyask"]) { const v = isStr(bg[k]) ? bg[k] : c[k]; if (isStr(v)) out[k] = v; }
  /* the dependency line: written as text with slugs */
  if (isStr(c.dep)) out.dep = c.dep;
  else if (isObj(c.dep)) {
    if (!Number.isInteger(c.dep.n)) bad.push("dep has no decision number n");
    else { const ls = Array.isArray(c.dep.letters) ? c.dep.letters : [];
      out.dep = ls.length ? "only if [[" + c.dep.n + "]] is " + lettersPhrase(ls) : "after [[" + c.dep.n + "]] is answered, whatever its answer"; }
  }
  /* what: text, a list of items, or {intro, items} */
  const item = it => isStr(it) ? {name: it} : isObj(it) ? Object.assign({name: it.name}, "is" in it ? {about: it.is} : {}, "per" in it ? {per: it.per} : {}) : null;
  if (isStr(c.what)) out.what = c.what;
  else if (Array.isArray(c.what)) out.items = c.what.map(item);
  else if (isObj(c.what)) { if (isStr(c.what.intro)) out.what = c.what.intro; if (Array.isArray(c.what.items)) out.items = c.what.items.map(item); }
  if (out.items && out.items.some(x => !x || !isStr(x.name))) bad.push("what holds an item with no name");
  if (isObj(c.finding)) {
    const f = {};
    if ("what" in c.finding) f.mechanism = c.finding.what;
    if ("where" in c.finding) f.where = c.finding.where;
    if ("code" in c.finding) f.excerpt = c.finding.code;
    out.finding = f;
  }
  if (isObj(c.scope)) {
    const lv = SCOPE[c.scope.k];
    if (!lv) bad.push("scope level " + JSON.stringify(c.scope.k) + " is not one the record has (shapes the work, required, outside the criteria)");
    else out.scope = {level: lv, says: c.scope.text};
  }
  if (isObj(c.likelihood)) {
    const b = c.likelihood.basis;
    if (b === "observed") out.likelihood = {kind: "observed", seen: c.likelihood.text};
    else if (!isStr(b) || !b.trim()) { out.likelihood = {kind: "evidence", seen: c.likelihood.text}; note.moved.push("likelihood with no basis read as evidence"); }
    else { out.likelihood = {kind: "evidence", seen: "(" + b + ") " + c.likelihood.text}; note.moved.push("likelihood basis " + JSON.stringify(b) + " kept at the head of seen"); }
  }
  /* open questions: v5's open, or v4's assume.unknown, none dropped */
  const open = [].concat(Array.isArray(c.open) ? c.open : [], isObj(c.assume) && Array.isArray(c.assume.unknown) ? c.assume.unknown : []).filter(x => !isNone(x));
  if (open.length) out.open = open;
  if (isObj(c.assume)) {
    const a = c.assume;
    if ("basis" in a) out.basis = a.basis;
    if ("reason" in a) out.reason = a.reason;
    const as = Array.isArray(a.assumptions) ? a.assumptions : [], tw = Array.isArray(a.tripwires) ? a.tripwires : [];
    if (as.length !== tw.length) bad.push("assume has " + as.length + " assumptions and " + tw.length + " tripwires: each assumption needs its own");
    else if (as.length) out.assume = as.map((r, i) => ({rests: r, tw: tw[i]}));
  }
  if (isObj(c.impact)) { out.impact = dropEffect(c.impact); if ("effect" in c.impact) note.moved.push("impact.effect dropped (no card-level effect)"); }
  /* evidence: a top-level one first, then each evidence attachment in order, one flat list */
  const ev = [];
  if (isStr(c.evidence)) ev.push(c.evidence); else if (Array.isArray(c.evidence)) ev.push(...c.evidence);
  const att = [];
  for (const x of Array.isArray(c.attached) ? c.attached : []) {
    if (!isObj(x)) { bad.push("an attachment is not an object"); continue; }
    if (x.kind === "evidence") {
      /* the record's evidence is a flat list of text: an attachment id is dropped, and a link to it would break */
      if (isStr(x.id) && x.id) {
        const all = JSON.stringify(c);
        if (all.includes("[[att:" + x.id + "|") || all.includes("[[att:" + x.id + "]]")) bad.push("a link names evidence attachment " + JSON.stringify(x.id) + ", whose id the record's evidence list drops");
        else note.moved.push("evidence attachment id " + JSON.stringify(x.id) + " dropped");
      }
      const t = isStr(x.title) && x.title.trim() ? x.title.trim() + " — " : "";
      if (isStr(x.body)) ev.push(t + x.body);
      else if (Array.isArray(x.body)) x.body.forEach((b, i) => ev.push((i ? "" : t) + b));
      else bad.push("an evidence attachment's body is neither text nor a list");
    } else {
      /* an own-key copy onto a null-prototype object: a "__proto__" key stays a plain key, never a prototype */
      const y = Object.create(null);
      for (const k of Object.keys(x)) y[k] = x[k];
      if (x.kind === "example" && "mode" in y) { y.form = y.mode; delete y.mode; }
      att.push(y);
    }
  }
  if (ev.length) out.evidence = ev;
  if (att.length) out.attached = att;
  if (Array.isArray(c.rejected)) out.rejected = c.rejected.map(r => ({t: r && r.bold, why: r && r.bullets}));
  /* the options: the name trap (the kit's pros/cons are the one-line texts, prosT/consT the table rows) */
  const act = isObj(c.act) ? c.act : {};
  out.options = [];
  for (const o of Array.isArray(c.options) ? c.options : []) {
    if (!isObj(o)) { bad.push("an option is not an object"); continue; }
    if (!isStr(o.k) || !LETTER.test(o.k)) { bad.push("an option letter " + JSON.stringify(o.k) + " is not one letter a-z"); continue; }
    for (const k of Object.keys(o)) if (!KIT_OPTION.has(k)) bad.push("(" + o.k + ") field " + k + " is not one the kit's schema names");
    if (!isStr(o.text) || !o.text.trim()) { bad.push("(" + o.k + ") has no text: the kit's text is the option's title"); continue; }
    const x = {k: o.k, title: o.text};
    for (const k of ["line", "effect", "reach", "undo", "cost", "plan"]) if (k in o && !(k !== "undo" && isNone(o[k]))) x[k] = o[k];
    if (o.oneway === true) x.oneway = true;
    if ("pros" in o) x.pro = o.pros;
    if ("cons" in o) x.con = o.cons;
    if ("prosT" in o) x.pros = o.prosT;
    if ("consT" in o) x.cons = o.consT;
    if (Array.isArray(act[o.k])) x.act = act[o.k];
    out.options.push(x);
  }
  for (const k of Object.keys(act)) if (!out.options.some(o => o.k === k)) bad.push("act (" + k + ") names no option");
  if (isObj(c.detail)) {
    const d = {};
    for (const k of Object.keys(c.detail)) {
      if (k === "o") { const o = c.detail.o; if (isObj(o)) for (const l in o) { const x = out.options.find(y => y.k === l); if (x) x.detail = o[l]; else bad.push("detail.o." + l + " names no option"); } continue; }
      if (!DETAIL_PARTS.has(k)) { bad.push("detail." + k + " is not a part a card has"); continue; }
      d[k] = k === "impact" && Array.isArray(c.detail.impact) ? c.detail.impact.map(dropEffect) : c.detail[k];
    }
    if (Object.keys(d).length) out.detail = d;
  }
  return out;
}

/* ---- one card: which shape, then its map ---- */
function upgradeCard(c, qmap) {
  const bad = [], note = {moved: []};
  if (!isObj(c)) return {bad: ["not an object"], note};
  const f = stampOf(c.format, "decision-card");
  if (c.format != null) {
    if (f === 5) { note.rev = "already " + CARD_FORMAT + ", passed through"; return {card: c, bad, note}; }
    if (f !== null && f > 5) return {bad: ["in a newer format (" + c.format + "): never downgraded"], note};
    return {bad: ["format " + JSON.stringify(c.format) + " is not one the upgrader reads"], note};
  }
  let out;
  if (Array.isArray(c.o)) { note.shape = "legacy"; out = fromLegacy(c, bad, note); }
  else if (Array.isArray(c.options)) {
    note.shape = isObj(c.assume) && "unknown" in c.assume ? "kit (v4)" : "kit";
    out = fromKit(c, bad, note);
  } else return {bad: ["neither options as arrays (o) nor as objects (options): a shape the upgrader cannot place"], note};
  /* the question: the card's own, else the headline's from --questions */
  if (!isStr(out.q) || !out.q.trim()) {
    const q = qmap ? qmap[String(c.n)] : null;
    if (isStr(q) && q.trim() && !/[\r\n]/.test(q)) out.q = q.trim();
    else bad.push("no q: give its question in --questions");
  }
  const rev = upgradeRev(c.rev, note);
  /* the carried-over marker: the shape it came from and the rev it kept, beside rev and never touching it. A writer
     who revises the card gives it a new rev, so the marker no longer matches and the card is checked as new */
  const card = Object.assign({format: CARD_FORMAT, n: out.n, rev, upgraded: {from: note.shape, rev}}, out);
  card.n = c.n;
  return {card, bad, note};
}

function main() {
  const args = process.argv.slice(2), opt = {};
  const pos = [];
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--questions" || a === "--records" || a === "--only") { if (i + 1 >= args.length) usage(a + " needs a value"); opt[a.slice(2)] = args[++i]; }
    else if (a.startsWith("--")) usage("unknown option " + a);
    else pos.push(a);
  }
  if (pos.length !== 2) usage("give IN and OUT");
  const [inFile, outFile] = pos;
  const d = readJson(inFile, "the input");
  const qmap = opt.questions ? readJson(opt.questions, "the question map") : null;
  if (qmap != null && !isObj(qmap)) usage("the question map must be an object {\"N\": \"question\"}");
  let only = null;
  if (opt.only) {
    let t;
    try { t = fs.readFileSync(opt.only, "utf8"); } catch (e) { usage("cannot read the set " + opt.only); }
    only = new Set();
    for (const line of t.split(/\r?\n/)) { const s = line.trim(); if (!s) continue; if (!/^[0-9]+$/.test(s)) usage("the set holds " + JSON.stringify(s) + ", not a decision number"); only.add(Number(s)); }
  }
  if (!isObj(d) || !Array.isArray(d.cards)) { process.stdout.write("upgrade_cards: " + inFile + " has no cards list: not a cards.json it can place\n"); process.exit(1); }
  const pf = stampOf(d.format, "decision-page");
  if (d.format != null && pf !== 5) {
    process.stdout.write("upgrade_cards: " + inFile + ": format " + JSON.stringify(d.format) + (pf !== null && pf > 5 ? " is newer than this upgrader: never downgraded" : " is not one it reads") + "\n");
    process.exit(1);
  }
  const v5 = pf === 5;
  const problems = [], lines = [], cards = [], seenN = new Set();
  for (const c of d.cards) {
    const n = isObj(c) ? c.n : undefined;
    if (only && !only.has(n)) continue;
    const w = "card " + (isPosInt(n) ? n : JSON.stringify(n === undefined ? null : n));
    /* the number names the record file: a whole number of 1 or more, once each, checked before anything is written */
    if (!isPosInt(n)) { problems.push(w + ": n must be a whole number of 1 or more"); continue; }
    if (seenN.has(n)) { problems.push(w + ": number used twice"); continue; }
    seenN.add(n);
    if (v5) {
      /* already decision-page/5: each card passes through as it is; a card not stamped is a file the upgrader cannot place */
      if (stampOf(c.format, "decision-card") !== 5) { problems.push(w + ": not stamped " + CARD_FORMAT + " in a " + PAGE_FORMAT + " file"); continue; }
      cards.push(c);
      lines.push(w + ": already " + CARD_FORMAT + ", passed through");
      continue;
    }
    const r = upgradeCard(c, qmap);
    if (r.bad.length) { for (const b of r.bad) problems.push(w + ": " + b); continue; }
    cards.push(r.card);
    lines.push(w + ": " + (r.note.shape ? r.note.shape + ", " : "") + r.note.rev + (r.note.moved.length ? "; " + r.note.moved.join("; ") : ""));
  }
  if (only) for (const n of only) if (!d.cards.some(c => isObj(c) && c.n === n)) problems.push("card " + n + ": in the set, not in " + inFile);
  if (problems.length) {
    process.stdout.write(problems.join("\n") + "\nupgrade_cards: " + problems.length + " problem" + (problems.length === 1 ? "" : "s") + "; nothing written\n");
    process.exit(1);
  }
  /* a slug to a card left out of the set: the writer gives it a refs entry, or the page refuses it */
  const kept = new Set(cards.map(c => String(c.n))), refs = isObj(d.refs) ? d.refs : {};
  const slugs = new Set();
  const scan = v => { if (isStr(v)) { for (const m of v.matchAll(/\[\[([0-9]+)\]\]/g)) slugs.add(m[1]); } else if (Array.isArray(v)) v.forEach(scan); else if (isObj(v)) Object.values(v).forEach(scan); };
  cards.forEach(scan);
  for (const s of slugs) if (!kept.has(s) && !(s in refs)) lines.push("note: [[" + s + "]] is named but is neither a card here nor a ref: give it a refs entry or its card");
  /* what is written: OUT (a decision-page/5 file with no set is copied byte for byte; with --only, its envelope
     holds the set's cards), then one record per card under --records */
  let outBytes, tail;
  if (v5 && !only) { outBytes = fs.readFileSync(inFile); tail = inFile + ": already " + PAGE_FORMAT + ", copied as it is"; }
  else {
    const outDoc = {format: PAGE_FORMAT};
    for (const k of Object.keys(d)) if (k !== "format") outDoc[k] = k === "cards" ? cards : d[k];
    outBytes = JSON.stringify(outDoc, null, 2) + "\n";
    tail = outFile + ": " + cards.length + " card" + (cards.length === 1 ? "" : "s") + ", " + PAGE_FORMAT + (v5 ? " (already; the set only)" : "");
  }
  const records = opt.records ? cards.map(c => {
    const r = Object.assign({}, c); delete r.L; delete r.dep;
    if (isObj(r.detail) && "dep" in r.detail) { r.detail = Object.assign({}, r.detail); delete r.detail.dep; }
    return [path.join(opt.records, c.n + ".json"), JSON.stringify(r, null, 2) + "\n"];
  }) : [];
  /* said before anything is replaced */
  for (const [p] of records) if (fs.existsSync(p)) lines.push("note: " + p + " exists and will be replaced");
  if (lines.length) process.stdout.write(lines.join("\n") + "\n");
  /* each file written to a temp name in its own directory, then renamed over its target, so a failed write
     leaves no half-written file; a write error is one plain line and exit 2 */
  let at = outFile;
  const put = (target, bytes) => {
    at = target;
    const tmp = path.join(path.dirname(target), "." + path.basename(target) + ".tmp-" + process.pid);
    try { fs.writeFileSync(tmp, bytes); fs.renameSync(tmp, target); }
    catch (e) { try { fs.unlinkSync(tmp); } catch (_) { /* no temp file was made */ } throw e; }
  };
  try {
    fs.mkdirSync(path.dirname(path.resolve(outFile)), {recursive: true});
    put(outFile, outBytes);
    if (opt.records) {
      at = opt.records;
      fs.mkdirSync(opt.records, {recursive: true});
      for (const [p, bytes] of records) put(p, bytes);
    }
  } catch (e) {
    process.stdout.write("upgrade_cards: cannot write " + at + ": " + String((e && e.message) || e).split("\n")[0] + "\n");
    process.exit(2);
  }
  process.stdout.write(tail + "\n");
}
main();
