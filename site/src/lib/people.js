import register from "../data/people.json";
import ancestors from "../data/ancestors.json";
import line from "../data/line.json";

/* One person = one GEDCOM record. The tree is the authority on identity here;
   this archive's job is to say how well each record is evidenced, not to merge
   or split people behind the reader's back. */
const byId = new Map();
for (const r of register) byId.set(r.id, { ...r });
for (const a of ancestors) byId.set(a.id, { ...(byId.get(a.id) || {}), ...a, ancestor: true });
for (const s of line) byId.set(s.id, { ...(byId.get(s.id) || {}), ...s, ancestor: true, spine: true });

export const people = [...byId.values()];
export const bySlug = new Map(people.map((p) => [p.slug, p]));
export const get = (id) => byId.get(id);

export const lifespan = (p) => {
  const b = p.byear, d = p.dyear;
  if (!b && !d) return "dates unknown";
  return `${b || "?"}–${d || "?"}`;
};

/* A person is "evidenced" when the tree carries at least one source string for
   them. It is a weak test — an online tree is a witness, not a source — but it
   separates the rows that can be checked from the rows that cannot. */
export const evidenced = (p) => Array.isArray(p.sources) && p.sources.length > 0;

export const surnameGroup = (s) =>
  String(s || "").toLowerCase()
    .replace(/ž/g, "z").replace(/ć|č/g, "c").replace(/š/g, "s").replace(/đ/g, "d")
    .split("(")[0].trim()
    .replace(/^x/, "z")
    .replace(/ich$/, "ic");
