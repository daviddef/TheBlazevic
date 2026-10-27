/* The ribbon cards' mini flags (27 October 2026; kit/docs/ribbon-flags.md). The flags are chosen by the kit (ribbonflags.py) and kept in
   src/data/ribbon-flags.json by tools/ribbon_flags.py, because at kit 1fa6b54 the kit's contracts for story.json and family-lines.json
   do not yet know a card's `flags` field (tools/ribbon_flags.py says why). These put them back on the cards, by position, where the
   ribbons are drawn; the kit's StoryRibbon and FamilyRibbon then draw them (FlagMini). A card whose name does not match the file's
   gets no flags (the file is stale: `npm run check:ribbonflags` fails the build first). */
import table from "../data/ribbon-flags.json";

const put = (cards, rows) =>
  (cards || []).map((c, i) => {
    const r = (rows || [])[i];
    return r && r.name === c.name && r.flags && r.flags.length ? { ...c, flags: r.flags } : c;
  });

/* the story book, with its ribbon's cards flagged */
export const storyWithFlags = (book) => ({ ...book, ribbon: { ...book.ribbon, cards: put(book.ribbon?.cards, table.story) } });

/* one family of family-lines.json, with its cards flagged */
export const familyWithFlags = (fam) => (fam && fam.cards ? { ...fam, cards: put(fam.cards, table.families[fam.id]) } : fam);
