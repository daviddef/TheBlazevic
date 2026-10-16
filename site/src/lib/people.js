import register from "../data/people.json";
import ancestors from "../data/ancestors.json";
import line from "../data/line.json";

/* One person = one GEDCOM record. The tree is the authority on identity here;
   this archive's job is to say how well each record is evidenced, not to merge
   or split people behind the reader's back. */
/* TEXT THAT WAS ESCAPED BEFORE IT REACHED THE DATA. Some strings in the tree export
   carry an HTML entity as text (&scaron; for š) and some were escaped twice
   (&amp;gt; for >). A template escapes text once more on the way out, so the reader
   saw "du&scaron;a" and "&amp;gt;" in citations. Decoded here, once, on the way in:
   decoding until nothing changes, and only for the entities the tree actually uses,
   so a bare & in a URL (…?cc=2040054&wc=…) is never touched. */
const NAMED = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", scaron: "\u0161", Scaron: "\u0160",
  ccaron: "\u010d", Ccaron: "\u010c", cacute: "\u0107", Cacute: "\u0106", zcaron: "\u017e",
  Zcaron: "\u017d", dstrok: "\u0111", Dstrok: "\u0110", deg: "\u00b0", laquo: "\u00ab", raquo: "\u00bb" };
const ENT = /&(?:([A-Za-z]+)|#(\d+)|#x([0-9a-fA-F]+));/g;
export const deent = (s) => {
  if (typeof s !== "string" || !s.includes("&")) return s;
  let prev;
  do {
    prev = s;
    s = s.replace(ENT, (m, name, dec, hex) => {
      if (name) return NAMED[name] ?? m;
      const cp = dec ? parseInt(dec, 10) : parseInt(hex, 16);
      return cp > 0 && cp < 0x110000 ? String.fromCodePoint(cp) : m;
    });
  } while (s !== prev);
  return s;
};
const clean = (v) => Array.isArray(v) ? v.map(clean)
  : v && typeof v === "object" ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k, clean(x)]))
  : deent(v);

const byId = new Map();
for (const r of register) byId.set(r.id, clean(r));
for (const a of ancestors) byId.set(a.id, { ...(byId.get(a.id) || {}), ...clean(a), ancestor: true });
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
