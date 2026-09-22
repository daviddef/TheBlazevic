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

/* EVERY PERSON OF ONE SURNAME, AS A DESCENT ROW.
 *
 * The households builder above answers «which couples does this surname
 * have», and it skips anybody with neither a spouse nor a child — which on
 * Papić is fifty-nine of a hundred and sixteen people. Asked for on 22
 * September: the family page should list EVERYONE the archive holds of the
 * name, tree people and register-only people together, in the same shape
 * the front page uses.
 *
 * So this returns one Descent row per PERSON, oldest first. A person with a
 * marriage gets their wife or husband in the right-hand column and their
 * children beneath; a person with neither still gets a row, because being
 * unmarried is not a reason to be missing from the list of your own family.
 *
 * SIBLINGS COME FROM EACH SIDE'S OWN RECORD, never from the other's, so the
 * two columns say what each person's family actually is.
 */
export function descentOf(keys, onSpine = new Set(), found = []) {
  const BY_ID2 = new Map(people.map((p) => [p.id, p]));
  const ours = people
    .filter((p) => keys.includes(surnameGroup(p.surname)))
    .sort((a, b) => (a.byear || 9999) - (b.byear || 9999));

  const card = (x) => {
    const full = BY_ID2.get(x.id) || {};
    return {
      name: x.name,
      href: x.slug ? `/people/${x.slug}/` : null,
      dates: [x.born, x.died].filter(Boolean).join("–") || "",
      line: onSpine.has(x.id),
    };
  };

  const rows = ours.map((p) => {
    const rel = p.rel || {};
    const sp = (rel.spouses || [])[0] || null;
    const spouseRec = sp && sp.id ? BY_ID2.get(sp.id) : null;
    const hers = spouseRec && spouseRec.rel ? spouseRec.rel.siblings || [] : [];
    return {
      gen: undefined,
      era: [p.byear, p.dyear].filter(Boolean).join(" → ") || undefined,
      name: p.name,
      href: p.slug ? `/people/${p.slug}/` : "",
      born: p.born || (p.byear ? String(p.byear) : ""),
      died: p.died || (p.dyear ? String(p.dyear) : ""),
      trade: (p.occupations || []).map((o) => o.what).filter(Boolean)[0] || "",
      place: p.bornPlace || p.diedPlace || "",
      spouse: sp ? sp.name : "",
      spouseHref: sp && sp.slug ? `/people/${sp.slug}/` : null,
      spouseBorn: sp && sp.born ? String(sp.born) : "",
      spouseAlt: sp ? "" : "no marriage recorded for them",
      children: (rel.children || []).map(card),
      hisSiblings: (rel.siblings || []).map(card),
      herSiblings: hers.map(card),
      hisLabel: String(p.name).split(" ")[0] + "’s",
      herLabel: sp ? String(sp.name).split(" ")[0] + "’s" : "Theirs",
      sources: (p.sources || []).map((s) => ({ label: String(s).split(" — ")[0] })),
      confidence: (p.sources || []).length ? "in the family tree" : "",
    };
  });

  /* AND THE PEOPLE THE TREE HAS NEVER HEARD OF. They were read out of a
     register, they have a page under /found/ since 22 September, and they
     belong in the list of their own family rather than in a separate table
     further down the page. The pill says which side of that line they fall
     on, because it is a fact about the tree and not about the evidence. */
  const mine = found.filter((r) => keys.includes(surnameGroup(String(r.name).split(" ").pop())));
  for (const r of mine) {
    rows.push({
      name: r.name,
      href: r.slug ? `/found/${r.slug}/` : "",
      era: r.date || undefined,
      born: r.event === "baptism" || r.event === "birth" ? r.date || "" : "",
      died: r.event === "death" || r.event === "burial" ? r.date || "" : "",
      place: r.place || "",
      spouse: "",
      spouseAlt: "",
      confidence: "parish register · not yet in the family tree",
      note: r.relation ? `${r.relation}.` : "",
      sources: r.citation ? [{ label: r.citation }] : [],
      children: [], hisSiblings: [], herSiblings: [],
    });
  }
  return rows;
}
