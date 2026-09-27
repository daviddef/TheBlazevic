/* ONE NAME TO PUT IN A HEADING, and the recorded one kept beside it.
 *
 * Written 27 September 2026, after an audit of the eight family pages found
 * fifty-five household headings reading like this:
 *
 *   «Mate Mathias Mathæus Kalanj Matheus Matÿ Kalanj»
 *   «Joannes Juan Ivan Ive John Žubrinić»
 *   «Anica / Ana / Anna "Ana" Kalanj»
 *   «Franjo [think this is wrong] Kalanj»
 *
 * None of those is a mistake in this archive. They are the MyHeritage display
 * name, which carries every alternate spelling, every Latin form, the called
 * name in quotes and sometimes the tree-owner's own marginal note, all in one
 * field. THE TREE IS NOT TO BE EDITED, so this is a display rule and nothing
 * else: it picks one form for a heading and hands the full recorded string
 * back so the page can print it underneath. Nothing is hidden and nothing in
 * sources/ or the GEDCOM is touched.
 *
 * The rule, in order:
 *   1. A slash means the tree is offering alternatives. Take the first.
 *   2. A quoted part is the name they were called by. It is kept, because
 *      «Milka» is how a family knows a woman, but only one of them.
 *   3. Square brackets are the tree-owner talking to themselves. Dropped from
 *      the heading; still in the recorded form.
 *   4. A token repeated later in the string, or a second run of the surname,
 *      is an alias. Dropped.
 *   5. Whatever survives, keep the FIRST given name and the LAST token, which
 *      is the surname. Two names is what a heading can hold.
 *
 * It is deliberately conservative about one thing: if the rule would leave
 * nothing, or would leave a single letter, the recorded name is returned
 * unchanged. An A–Z index node is a real problem in this tree and it should
 * look like one rather than be tidied into looking like a person.
 */

const STRIP_SQUARE = /\[[^\]]*\]/g;
/* A parenthesis at the end is another spelling of the surname, not the
   surname: «Nikola Žubrinić (Xubrinic)». It goes with the recorded form. */
const STRIP_ROUND = /\([^)]*\)/g;

/** The full string as the tree records it, with whitespace normalised only. */
export const recordedName = (s) => String(s ?? "").replace(/\s+/g, " ").trim();

/** One form, fit for a heading. */
export function displayName(raw) {
  const recorded = recordedName(raw);
  if (!recorded) return "";

  let s = recorded.replace(STRIP_SQUARE, " ").replace(STRIP_ROUND, " ");

  // 1. slashed alternatives — take the first, but keep anything after the
  //    last alternative, because «Anica / Ana / Anna "Ana" Kalanj» carries the
  //    surname on the far side of the slashes.
  if (s.includes("/")) {
    const parts = s.split("/").map((x) => x.trim()).filter(Boolean);
    const tail = parts[parts.length - 1].split(/\s+/);
    // everything after the first token of the last alternative is shared tail
    s = [parts[0], ...tail.slice(1)].join(" ");
  }

  /* 2. the called name, if there is one — and only if it is ONE word.
        «"Geōrgius George"» is two more spellings of Juraj, not what anyone
        called him, and «"Jose / Pepe"» is two nicknames; a heading takes
        neither. */
  const quoted = s.match(/"([^"]+)"/);
  let called = quoted ? quoted[1].trim() : "";
  if (called.split(/[\s/]+/).filter(Boolean).length !== 1) called = "";
  s = s.replace(/"[^"]*"/g, " ");

  const tokens = s.split(/\s+/).filter(Boolean);
  if (tokens.length < 2) return recorded;

  // 4. the surname is the last token; drop an earlier run of it
  const surname = tokens[tokens.length - 1];
  const given = tokens.slice(0, -1).filter((t) => t !== surname);
  if (!given.length) return recorded;

  // 5. first given name, plus the surname
  const first = given[0];
  if (first.replace(/[^\p{L}]/gu, "").length < 2) return recorded;

  const sameWord = (a, b) =>
    a.toLowerCase().replace(/[^\p{L}]/gu, "").slice(0, 3) ===
    b.toLowerCase().replace(/[^\p{L}]/gu, "").slice(0, 3);
  const head = called && !sameWord(called, first)
    ? `${first} «${called}» ${surname}`
    : `${first} ${surname}`;
  return head;
}

/** The recorded form, but only when it says more than the heading does. */
export const alsoRecordedAs = (raw) => {
  const recorded = recordedName(raw);
  const shown = displayName(raw);
  return recorded && shown && recorded !== shown ? recorded : "";
};
