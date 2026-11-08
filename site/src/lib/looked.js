/* «WHERE WE HAVE LOOKED» for one person: the input of the kit's #looked section (kit/lib/personlooked.js), built from site/src/data/looked.json, which
   tools/build_looked.py writes from the search register, the Roots & Routes Atlas place data and the Record Atlas surname catalogue (the file's own header
   says what it matches and what it leaves out). A row reaches a person by TAG: the surname family and a place the person's own record names. Never by
   person. Nothing here reads a living person: the page passes only a person who has died, and a row carries sources, surnames and places only.

   lookedFor(p) -> null | { rows, places, names, span }; null when the person has no matching search and no place the archive holds books for. */
import looked from "../data/looked.json";
import { gedYear } from "./storyFamily.js";

const fold = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
/* the same tokens tools/build_looked.py place_tokens makes: each comma part, a trailing house number removed, folded */
const tokens = (s) => String(s || "").split(",").map((x) => fold(x.trim().replace(/\s+\d+[a-z]?$/i, ""))).filter(Boolean);
const rank = { covered: 0, unknown: 1, missed: 2 };

export const OUTCOMES = {
  yield: { label: "Yielded", cls: "found" }, partial: { label: "Partly", cls: "partial" }, nothing: { label: "Nothing", cls: "nil" },
  blocked: { label: "Blocked", cls: "blocked" }, pending: { label: "Not yet", cls: "notyet" },
};

export function personPlaceKeys(p) {
  const strings = [p.bornPlace, p.baptisedPlace, p.diedPlace, p.burial, ...(p.events || []).map((e) => e.place), ...((p.rel && p.rel.spouses) || []).map((r) => r.marriedPlace)];
  const seen = [];
  for (const s of strings) for (const t of tokens(s)) if (looked.places[t] && !seen.includes(t)) seen.push(t);
  return seen;
}

export function lookedFor(p) {
  const keys = new Set([looked.surnameKey[fold(p.surname)], looked.surnameKey[fold(p.family)]].filter(Boolean));
  const placeKeys = personPlaceKeys(p);
  if (!placeKeys.length) return null;
  const rows = [];
  for (const r of looked.rows) {
    if (r.placeOnly) {   // wanted at a place, not a search for a name: anyone at the place is shown it, in the «not looked yet» box
      if (r.places.some((x) => placeKeys.includes(x))) rows.push({ ...r, places: r.places.filter((x) => placeKeys.includes(x)) });
      continue;
    }
    const k = r.surnames.filter((x) => keys.has(x));
    if (!k.length || !r.places.some((x) => placeKeys.includes(x))) continue;
    const out = { id: r.id, src: r.src, volume: r.volume, years: r.years, span: r.span, what: r.what, when: r.when, outcome: r.outcome, surnames: k,
      places: r.places.filter((x) => placeKeys.includes(x)), href: r.href, volumes: r.volumes };
    if (r.nil) {   // the worst verdict among the person's surname keys: a covered nil only if every key was covered
      const vs = k.map((x) => r.nil[x] || ["unknown"]).sort((a, b) => rank[b[0]] - rank[a[0]]);
      out.nil = { status: vs[0][0], missed: vs[0].slice(1) };
    }
    rows.push(out);
  }
  const matched = new Set(rows.filter((r) => !r.placeOnly).flatMap((r) => r.places));
  const places = placeKeys.filter((k) => matched.has(k) || looked.places[k].held).map((k) => {
    const pl = looked.places[k];
    return { key: k, name: pl.name, volumes: pl.volumes, catalogued: pl.catalogued || 0, held: pl.held || null, atlas: pl.volumes.length > 0 };
  });
  if (!places.length) return null;
  const names = keys.size ? [...keys].map((k) => looked.labels[k]) : [String(p.surname || "").replace(/\s*[("].*$/, "").trim()].filter(Boolean);
  const by = gedYear(p.born || p.byear), dy = gedYear(p.died || p.dyear);
  const span = by != null ? [by, dy != null ? dy : by + 80] : null;
  return { rows: rows.filter((r) => r.places.some((x) => places.some((pl) => pl.key === x))), places, names, span };
}
