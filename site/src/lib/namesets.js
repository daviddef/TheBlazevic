/* WHO SHARES A NAME (one page per person; 23 November 2026, rolled out from Booyzen, TheBooyzen PR #36).
 *
 * Until now a NAME had a page of its own, /who/<name>/ (3,663 of them: "one person in this archive was called ...", or a list of the
 * people of a shared name), beside the PERSON's page at /people/<slug>/. David's rule: one page per person, and each person's page
 * links to the other people who carry the same name; nobody wants the shared-name pages. The name pages are gone; their addresses
 * redirect (astro.config.mjs reads whoRedirects below) and this file is the one place that says which people share a name.
 *
 * THE SET IS THE ONE THE NAME PAGES USED. It is the old /who/[slug].astro getStaticPaths, moved here unchanged in what it counts, so
 * the people listed under "Others of the same name" are exactly the people /who/ listed:
 *   - the key is the slug of the name as written: accents and case folded, every run of other characters one hyphen;
 *   - the bearers are the people of people.json (who have died) and the living of living.json (a name and a town, no dates);
 *   - and under them the register finds of src/data/who-finds.json (tools/names_index.py): people read out of a register whose name
 *     field IS a name and who are certainly dead; each has a page of its own at /found/<slug>/. A name borne only by finds has no
 *     person page and, as before, no name page.
 *
 * PURE: no imports, so astro.config.mjs can use it (it reads the JSON files itself) and so can the pages.
 */
export const slugify = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "")
  .replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase();

export const SECTION_ID = "others-of-this-name";

/* @param people  people.json rows (nobody living); @param living  living.json rows; @param finds  who-finds.json (key -> finds)
   @returns Map key -> { key, name, persons: [rows with a person page, in file order], finds: [register finds] } */
export function nameSets(people, living, finds = {}) {
  const by = new Map();
  for (const p of [...people, ...(living || [])]) {
    if (!p.name || !p.slug) continue;
    const k = slugify(p.name);
    if (!k) continue;                                  // a name with no letters or digits has no name
    if (!by.has(k)) by.set(k, { key: k, name: p.name, persons: [], finds: [] });
    by.get(k).persons.push(p);
  }
  for (const [k, rows] of Object.entries(finds || {})) if (by.has(k)) by.get(k).finds = rows;
  return by;
}

export const yearOf = (s) => { const m = /\b(1[0-9]{3}|20[0-9]{2})\b/.exec(String(s ?? "")); return m ? Number(m[1]) : null; };

/* THE FIRST BEARER of a set: the one a shared name's old address lands on. A person who is not living comes first (the page a search
   engine may show), then the earliest born (the first four-digit year in `born`), a bearer with no year after those with one, then
   slug order. Finds are never first: a find has no person page to carry the section. */
export function firstBearer(set) {
  const rank = (p) => [p.living ? 1 : 0, yearOf(p.born) ?? 99999, p.slug];
  return [...set.persons].sort((a, b) => {
    const x = rank(a), y = rank(b);
    return x[0] - y[0] || x[1] - y[1] || (x[2] < y[2] ? -1 : x[2] > y[2] ? 1 : 0);
  })[0];
}

/* a set is SHARED when more than one person bears the name (the old name page said "N different people") */
export const isShared = (set) => set.persons.length + set.finds.length > 1;

/* the old address of every name page -> where it goes now: a name one person bears -> that person's page; a shared name -> its first
   bearer's page at the "Others of the same name" section.
   `merged` is src/data/merged.json: the retired record of a person the tree held twice has no page, and its name's address (when nobody
   else bears the name) goes to the survivor. A name some person bears is the name's own redirect and wins. */
export function whoRedirects(sets, merged = [], base = "") {
  const out = {};
  for (const m of merged) {
    if (m.retired && m.retired.who && !sets.has(m.retired.who)) out[`/who/${m.retired.who}`] = `${base}/people/${m.survivor.slug}/`;
  }
  for (const [key, set] of sets) {
    const to = firstBearer(set);
    out[`/who/${key}`] = `${base}/people/${to.slug}/` + (isShared(set) ? `#${SECTION_ID}` : "");
  }
  return out;
}

const age = (e) => e.year ?? 99999;
/* the others of a name, oldest first (those with no year after, then by address): the person pages of the set except `slug`, then the
   finds. One row each: the facts the name page printed. */
export function othersOf(set, slug) {
  const rows = [
    ...set.persons.filter((p) => p.slug !== slug).map((p) => ({ kind: p.living ? "living" : "person", slug: p.slug, name: p.name, p, year: p.living ? null : yearOf(p.born) })),
    ...set.finds.map((f) => ({ kind: "find", slug: f.slug, name: f.name, p: f, year: yearOf(f.date) })),
  ];
  return rows.sort((a, b) => age(a) - age(b) || (a.kind === b.kind ? 0 : a.kind === "find" ? 1 : -1) || (a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0));
}
