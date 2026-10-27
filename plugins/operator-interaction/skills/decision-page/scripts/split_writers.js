#!/usr/bin/env node
/* decision-page writer split (operator-interaction, 03ab F4). Splits a page's cards among card
   writers by group and dependency, as references/writers.md § The split says:

     node split_writers.js [--cap N] skeleton.json

   The skeleton is the page in outline, in page order: {layers: [[key, title, …], …], cards:
   [{n, L, dep}, …], refs: {"N": …}}. Only each layer's key, each card's n, L and dep, and the
   refs keys are read; anything else is ignored.

   1. Units: cards that share a layer are linked, and a card is linked to each [[M]] in its dep
      that is a card on the page; the linked sets, closed transitively, are the units. A [[M]]
      in refs is neither linked nor reported; any other is reported as a card to add.
   2. At or under the cap in all: one writer.
   3. A unit over the cap is cut into atoms, the sets linked by dep alone, closed transitively,
      packed in page order into pieces at or under the cap. An atom over the cap stays whole on
      a writer of its own, marked over cap: a depends chain is never cut, only same-layer links.
   4. Units and pieces are packed in page order: each writer takes the next whole one while its
      total stays at or under the cap, so small groups share a writer.

   Prints {"cap", "writers": [{"cards": [n…], "layers": [key…], "over_cap": bool}], "notes": […]},
   each writer's cards in page order. Exit 0; 1 on a skeleton it cannot read (a card with no n
   or L, an L not in layers, a repeated n, the other layer not last) or a bad --cap. Reads one
   local file, writes nothing else. Node built-ins only. */
"use strict";
const fs = require("fs");

/* the default card cap per writer: an estimate, stated with its basis in references/writers.md */
const WRITER_CAP = 15;
/* the layer of the cards in no stored group: Other decisions, always the last layer */
const OTHER = "other";

const fail = msg => { process.stdout.write("split_writers: " + msg + "\n"); process.exit(1); };

function find(parent, x) { while (parent.get(x) !== x) x = parent.get(x); return x; }
function union(parent, a, b) { const ra = find(parent, a), rb = find(parent, b); if (ra !== rb) parent.set(rb, ra); }

const SLUG = /\[\[([0-9]+)\]\]/g;
const depsOf = c => typeof c.dep === "string" ? [...c.dep.matchAll(SLUG)].map(m => Number(m[1])) : [];

function readSkeleton(d) {
  if (!d || typeof d !== "object" || Array.isArray(d)) fail("the skeleton is not a JSON object");
  if (!Array.isArray(d.layers) || !d.layers.length) fail("layers: missing");
  if (!Array.isArray(d.cards) || !d.cards.length) fail("cards: missing");
  const keys = [];
  d.layers.forEach((l, i) => {
    if (!Array.isArray(l) || typeof l[0] !== "string" || !l[0]) fail("layer " + i + ": needs [key, title, …]");
    keys.push(l[0]);
  });
  const at = keys.indexOf(OTHER);
  if (at >= 0 && at !== keys.length - 1) fail("layer other (Other decisions) must be the last layer");
  const seen = new Set();
  d.cards.forEach((c, i) => {
    if (!c || typeof c !== "object") fail("card " + i + ": not an object");
    if (!Number.isInteger(c.n) || c.n < 1) fail("card " + i + ": needs n, a whole number of 1 or more");
    if (typeof c.L !== "string" || !c.L) fail("card " + c.n + ": needs L, a layers key");
    if (!keys.includes(c.L)) fail("card " + c.n + ": L " + JSON.stringify(c.L) + " is not a layers key");
    if (c.dep !== undefined && typeof c.dep !== "string") fail("card " + c.n + ": dep must be text");
    if (seen.has(c.n)) fail("card " + c.n + ": n repeated");
    seen.add(c.n);
  });
  const refs = d.refs && typeof d.refs === "object" && !Array.isArray(d.refs) ? new Set(Object.keys(d.refs)) : new Set();
  return {keys, cards: d.cards, refs};
}

/* pack items ({cards}, in page order) into writers at or under the cap, each taking the next whole
   item while it fits; an item over the cap goes alone, marked over cap */
function pack(items, cap) {
  const out = [];
  let cur = null;
  for (const it of items) {
    if (it.cards.length > cap) { out.push({cards: it.cards.slice(), over_cap: true}); cur = null; continue; }
    if (cur && cur.cards.length + it.cards.length <= cap) cur.cards.push(...it.cards);
    else { cur = {cards: it.cards.slice(), over_cap: false}; out.push(cur); }
  }
  return out;
}

/* the sets of a union-find over the given cards, each in page order, the sets ordered by their
   first card's layer, then its position */
function sets(parent, ns, pos, layerAt) {
  const by = new Map();
  for (const n of ns) { const r = find(parent, n); if (!by.has(r)) by.set(r, []); by.get(r).push(n); }
  const all = [...by.values()].map(s => s.sort((a, b) => pos.get(a) - pos.get(b)));
  return all.sort((a, b) => (layerAt(a[0]) - layerAt(b[0])) || (pos.get(a[0]) - pos.get(b[0])));
}

function split(d, cap) {
  const {keys, cards, refs} = readSkeleton(d);
  const pos = new Map(cards.map((c, i) => [c.n, i]));
  const byN = new Map(cards.map(c => [c.n, c]));
  const layerAt = n => keys.indexOf(byN.get(n).L);
  const notes = [];
  /* the dep links between cards on the page */
  const links = [];
  for (const c of cards) for (const m of depsOf(c)) {
    if (m === c.n) continue;
    if (pos.has(m)) links.push([c.n, m]);
    else if (!refs.has(String(m)))
      notes.push("card " + c.n + " depends on [[" + m + "]], which is neither a card on this page nor a ref: add it as a card");
  }
  const ns = cards.map(c => c.n);
  let pieces;
  if (cards.length <= cap) pieces = [{cards: ns.slice(), over_cap: false}];
  else {
    /* 1. units: same-layer links and dep links */
    const unit = new Map(ns.map(n => [n, n]));
    const first = new Map();
    for (const c of cards) { if (!first.has(c.L)) first.set(c.L, c.n); else union(unit, first.get(c.L), c.n); }
    for (const [a, b] of links) union(unit, a, b);
    const items = [];
    for (const u of sets(unit, ns, pos, layerAt)) {
      if (u.length <= cap) { items.push({cards: u}); continue; }
      /* 3. a unit over the cap: atoms by dep links alone, packed into pieces */
      const atom = new Map(u.map(n => [n, n]));
      const inU = new Set(u);
      for (const [a, b] of links) if (inU.has(a) && inU.has(b)) union(atom, a, b);
      const atoms = sets(atom, u, pos, layerAt);
      for (const a of atoms) if (a.length > cap)
        notes.push("cards " + a.join(", ") + " are one depends chain of " + a.length + ", over the cap of " + cap + ": one writer, marked over cap");
      items.push(...pack(atoms.map(a => ({cards: a})), cap));
    }
    /* 4. units and pieces packed in page order */
    pieces = pack(items, cap);
  }
  const writers = pieces.map(p => {
    const cs = p.cards.slice().sort((a, b) => pos.get(a) - pos.get(b));
    const ls = keys.filter(k => cs.some(n => byN.get(n).L === k));
    return {cards: cs, layers: ls, over_cap: p.over_cap};
  });
  return {cap, writers, notes};
}

if (require.main === module) {
  const args = process.argv.slice(2);
  let cap = WRITER_CAP;
  if (args[0] === "--cap") {
    if (!/^[1-9][0-9]*$/.test(args[1] || "")) fail("--cap takes a whole number of 1 or more");
    cap = Number(args[1]);
    args.splice(0, 2);
  }
  if (args.length !== 1) fail("usage: node split_writers.js [--cap N] skeleton.json");
  let d;
  try { d = JSON.parse(fs.readFileSync(args[0], "utf8")); } catch (e) { fail("cannot read " + args[0] + ": " + String((e && e.message) || e).split("\n")[0]); }
  process.stdout.write(JSON.stringify(split(d, cap)) + "\n");
}

module.exports = {split, WRITER_CAP};
