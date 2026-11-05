/* WHAT EVERY PERSON PAGE NEEDS TO TELL A LIFE, built once for the 4,488 pages (a page's frontmatter runs once per page, so a map made there is made
   4,488 times). Nothing here is written for a person: it is the archive's own people.json read in the tree shape the kit's story functions take
   (kit/lib/personstory.js: byId[id] = { id, given, sur, sex, by, dy, bp, line, href, father, mother, kids, spouse }).

   - `bySlug`, `hasPage`: the published people and everyone with a page, a living person included (a living page is a name, relationships, a town and
     a country); a card links only where there is a page.
   - `drawn`: the ids Roots & Routes draws (public/roots-links.json, written by tools/build-tree-page.py); "Where they lived" is offered only for those.
   - `TREE_BY`: the line of fathers, for the story's first stop. A parent is the father only where the record holds the sex M and the mother only where
     it holds F: a parent whose sex is not recorded fills neither slot, and is drawn as "Parent" on the family row. Sex is never inferred from a name or
     from the order the tree lists the parents.
   - `gedYear`: the year a GEDCOM date phrase holds. */
import { people } from "./people.js";
import living from "../data/living.json";
import rootsLinks from "../../public/roots-links.json";
import { u } from "./url.js";

export const gedYear = (v) => { const m = /\b(1[0-9]\d\d|20\d\d|[5-9]\d\d)\b/.exec(String(v ?? "")); return m ? Number(m[1]) : null; };

export const bySlug = new Map(people.map((q) => [q.slug, q]));
export const hasPage = new Set([...bySlug.keys(), ...living.map((q) => q.slug)]);
export const livingSlugs = new Set(living.map((q) => q.slug));
export const drawn = new Set(rootsLinks.people || []);

/* a date phrase that is not a plain date (ABT, EST, CAL, BEF, AFT, BET … AND …, free text) is an estimate: the card draws «c. 1750» */
const PLAIN = /^\s*(\d{1,2} )?([A-Za-z]{3,9} )?\d{4}\s*$/;
const estimated = (v) => v != null && v !== "" && !PLAIN.test(String(v));
const sexOf = (s) => (s === "M" ? "m" : s === "F" ? "f" : "u");
export const TREE_BY = (() => {
  const by = {};
  for (const p of people) {
    const dead = p.deathRecorded === true || !!(p.died || p.dyear || p.diedPlace || p.burial);
    by[p.id] = { id: p.id, given: p.given || "", sur: p.surname || "", sex: sexOf(p.sex), by: gedYear(p.born || p.byear), bye: estimated(p.born || p.byear), dy: gedYear(p.died || p.dyear), dye: estimated(p.died || p.dyear),
      dead, bp: p.bornPlace ? p.bornPlace.split(",")[0].trim() : "", line: 1, href: u(`/people/${p.slug}/`), father: null, mother: null, kids: [], spouse: [] };
  }
  for (const p of people) {
    for (const r of (p.rel && p.rel.parents) || []) {
      const q = r.id && by[r.id];
      if (!q) continue;
      if (q.sex === "m" && !by[p.id].father) by[p.id].father = q.id;
      else if (q.sex === "f" && !by[p.id].mother) by[p.id].mother = q.id;
    }
  }
  return by;
})();
