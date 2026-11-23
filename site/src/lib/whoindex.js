/* The names of "Every Name" (/who/), for the index and for its letter pages.
 *
 * ONE PAGE PER PERSON (23 November 2026): a name has no page of its own, so each entry links to the person page of that name, and a
 * name several people bear lists them all. At 3,663 names the list is too heavy for one page (the old index was 658 KB before it held a
 * single bearer), so it is split by the initial of the name: /who/ is the jump bar and the letter pages are
 * /who/names--<initial>/, with `--` in the address on purpose: a name's slug is made by collapsing every run of other characters to ONE
 * hyphen, so no name slug can ever contain two in a row, and a letter page can never be the address of a name.
 *
 * A name borne ONLY by the living is not listed: its old address redirects (it always did answer), but an index anyone can crawl is the wrong
 * place for it. A living person is counted under a name somebody who has died also bore, and is never linked from here.
 */
import { SETS, firstOf, isShared, bearersOf, SECTION_ID } from "./namesakes.js";
import { u } from "./url.js";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

export const LETTER_PREFIX = "names--";
export const initialOf = (key) => (/^[a-z]/.test(key) ? key[0] : "0-9");
export const letterSlug = (l) => LETTER_PREFIX + (l === "0-9" ? "digits" : l);
export const letterHref = (l) => u(`/who/${letterSlug(l)}/`);

const yr = (b) => { const m = /\b(1[0-9]{3}|20[0-9]{2})\b/.exec(String(b ?? "")); return m ? m[1] : ""; };

export const NAMES = [...SETS.values()]
  .filter((s) => s.persons.some((p) => !p.living))            // a name only the living bear is not listed
  .map((s) => {
    const first = firstOf(s);
    const shared = isShared(s);
    const dead = s.persons.filter((p) => !p.living);
    const nLiving = s.persons.length - dead.length;
    return {
      slug: s.key, name: s.name, n: s.persons.length + s.finds.length, initial: initialOf(s.key),
      href: u(`/people/${first.slug}/`) + (shared ? `#${SECTION_ID}` : ""),
      /* every bearer of a shared name, each a link to that person's own page, oldest first: the name as that page has it and the year born;
         the finds link to their own pages; the living are counted, not named */
      detail: shared
        ? [...bearersOf(s).filter((b) => b.kind !== "living").map((b) => `<a href="${esc(b.href)}">${esc(b.name)}${yr(b.life) ? ` (${b.kind === "find" ? "read " : "b. "}${yr(b.life)})` : ""}</a>`),
           ...(nLiving ? [`${nLiving === 1 ? "one living person" : `${nLiving} living people`}`] : [])].join("<br>")
        : "",
    };
  })
  .sort((a, b) => a.slug.localeCompare(b.slug));

export const LETTERS = [...new Set(NAMES.map((n) => n.initial))].sort((a, b) => (a === "0-9" ? 1 : b === "0-9" ? -1 : a < b ? -1 : 1));
export const namesOf = (letter) => NAMES.filter((n) => n.initial === letter);
export const SHARED = NAMES.filter((n) => n.n > 1);
