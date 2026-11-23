/* The people who share a name, as the pages draw them (see namesets.js for which people, and why).
   One entry per other person. What each carries is what the /who/<name>/ page printed beside the same person: a person who has died is
   a name, the life span and the place; a living person is a name and a town and a country and nothing else; a register find has the
   date and place of the entry and says it was read out of a register and is not in the family tree. */
import people from "../data/people.json";
import living from "../data/living.json";
import whoFinds from "../data/who-finds.json";
import { nameSets, othersOf, firstBearer, isShared, slugify, SECTION_ID } from "./namesets.js";
import { u } from "./url.js";

export const SETS = nameSets(people, living, whoFinds);
export { SECTION_ID, slugify, isShared };

const entry = (o) => {
  if (o.kind === "find") {
    return { name: o.name, href: u(`/found/${o.slug}/`), life: o.p.date || "no date recorded", where: o.p.place || "",
             note: "Read out of a register; not in the family tree", kind: "find" };
  }
  if (o.kind === "living") {
    return { name: o.name, href: u(`/people/${o.slug}/`), life: "living — named only",
             where: [o.p.town, o.p.country].filter(Boolean).join(", "), note: "", kind: "living" };
  }
  return { name: o.name, href: u(`/people/${o.slug}/`), life: [o.p.born, o.p.died].filter(Boolean).join(" – "),
           where: o.p.bornPlace || o.p.diedPlace || "", note: "", kind: "person" };
};

/* the other people of the name of the person with this name and slug, oldest first: [] when nobody shares it */
export const othersFor = (name, slug) => {
  const set = SETS.get(slugify(name));
  return set ? othersOf(set, slug).map(entry) : [];
};

/* every bearer of a name, oldest first, for the Every Name list: the people with a page, then the finds */
export const bearersOf = (set) => othersOf(set, null).map(entry);
export const firstOf = (set) => firstBearer(set);
