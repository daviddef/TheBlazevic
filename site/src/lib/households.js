/* The couples of one surname, out of the register.

   Written when the family pages got their households, and put here rather
   than in the page because the families index wants the same count and
   this estate has spent a fortnight lifting duplicated logic out of
   templates. Two callers, one definition of what a household is.

   A HOUSEHOLD IS A COUPLE, SO IT IS COUNTED ONCE. When both spouses carry
   the surname — which happens constantly in Smokvica, where the Blaževići
   married each other — the same marriage appears under each of them, and
   the pair is keyed on both ids so it is kept once.

   A person with neither spouse nor child is not a household and is left
   to the list of everyone of the name. */
import { people, surnameGroup } from "./people.js";

const BY_ID = new Map(people.map((p) => [p.id, p]));

export function householdsOf(keys, onSpine = new Set()) {
  const rows = people
    .filter((p) => keys.includes(surnameGroup(p.surname)))
    .sort((a, b) => (a.byear || 9999) - (b.byear || 9999));

  const seen = new Set();
  const out = [];
  for (const p of rows) {
    const rel = p.rel || {};
    const spouses = rel.spouses || [];
    const kids = rel.children || [];
    if (!spouses.length && !kids.length) continue;
    const sp = spouses[0] || null;
    const key = [p.id, sp ? sp.id : ""].sort().join("|");
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({
      head: p.name,
      headHref: p.slug ? `/people/${p.slug}/` : null,
      spouse: sp ? sp.name : "",
      spouseHref: sp && sp.slug ? `/people/${sp.slug}/` : null,
      married: (sp && sp.married) || "",
      born: p.byear ? String(p.byear) : "",
      where: p.bornPlace || p.diedPlace || "",
      children: kids.map((c) => {
        const full = BY_ID.get(c.id) || {};
        return {
          name: c.name,
          href: c.slug ? `/people/${c.slug}/` : null,
          living: !!full.living,
          dates: [c.born, c.died].filter(Boolean).join("–") || "",
          /* The child this archive came down through — read off the spine
             by id, so it is the spine's own answer and not a name match. */
          line: onSpine.has(c.id),
        };
      }),
    });
  }
  return out;
}

/* Perpic folds into Prpic, as everywhere else here. */
export const familyKeys = (slug) => ({ prpic: ["prpic", "perpic"] }[slug] || [slug]);
