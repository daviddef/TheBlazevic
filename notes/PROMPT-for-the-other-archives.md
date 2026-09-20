# A prompt to send every other family session

*Written 21 September 2026 after two faults were found here that every archive in
the estate is likely to share. Copy the block below verbatim into each session.*

---

Two faults were found in the Blažević archive today that are almost certainly in
yours too. Please check both, **measure before you change anything**, and report
the numbers back even if they come out zero — a zero that has been measured is
worth having and a zero that has been assumed is not.

**1. IS YOUR PUBLICATION SCOPE A SURNAME TEST OR A DESCENT TEST?**

Mine published a person when `fold(surname)` was one of a fixed list of family
surnames, plus anyone on the direct ancestral line. **That is how a family is
FILED. It is not what a family IS.** A daughter's children take their father's
name and vanish from the archive, though they are blood.

The case that exposed it: the root person's **aunt** married a man whose surname
was not on the list. Her five children — **the root person's first cousins** —
appeared nowhere on the site.

Measure it like this. Walk **up** from your root person to every ancestor, then
**down** through every descendant of those ancestors. That set is the cognatic
kindred: everyone related to your root by blood. Compare it with the set your
build actually publishes.

    Mine: 72 ancestors → kindred of 1,134 → 258 blood relatives out of scope,
    of whom 234 were publishable once the living rule had run.
    Published people went 1,226 → 1,460.

If yours is non-zero, consider publishing `surname in list OR in kindred`. Two
cautions from doing it here:

  * **Return blood only.** A spouse who married in should NOT come with it
    unless their own surname is already on your list. The husband in my case is
    still unpublished while all five of his children are published, and that is
    the correct boundary for a descent test.
  * **Widening scope pulls new surnames and new places into your data**, and
    anything that links `/<surname>/` or `/places/<slug>/` will start pointing
    at pages that do not exist. Mine emitted 61 dead links from one page that
    had always assumed every surname it saw had a family page. Check your build
    after, not before.

**2. DOES YOUR AUTO-LINKER ACTUALLY LINK ANYTHING?**

Mine had been silently missing the commonest name in the archive for as long as
it has existed, and a reader found it by looking at a page full of names and no
links. Three separate causes, all worth checking:

  * **ACCENTS.** The index is built from the TREE's spelling and the prose is
    written in the ARCHIVE's. My tree holds an ancestor as `Blazevic` and every
    page writes `Blažević`. The matcher was case-insensitive and **not**
    accent-insensitive, so `z` and `ž` were two letters and the name never
    linked once. Fold accents on **both sides**. Fold **per character** so the
    fold is length-preserving — `String.normalize("NFD")` plus a mark-strip
    *shortens* the string, and every offset after the first accent is then
    wrong. Handle the letters that do not decompose at all: **đ, ð, ł, ø, ß**.
  * **SLASH-JOINED SURNAMES.** My builder split alternatives in the GIVEN name
    and not in the SURNAME, so `Tereza Žubrinić` — the form every page actually
    writes — was absent while two forms nobody writes were present.
  * **INLINE QUOTED NICKNAMES.** A tree that holds `Ljubomir "Ljubo" Blažević`
    yields no `Ljubomir Blažević` unless you strip the quoted part and offer
    both.

**Check it end to end rather than by reading the code**: build, then grep a
built page for `class="wholink"` — or whatever your linker marks — and count.
Zero on a page full of names is the symptom.

**AND A RULE THAT SHOULD SURVIVE ALL OF THIS.** Do not link a name held by more
than one person. Mine has eighteen men called Ivan Blažević; linking one of them
would be the merge-on-a-name error these archives exist to document. If widening
the index makes a name ambiguous, the right outcome is that it stops linking.

**If you publish living people under a `named-bare` policy**, apply the living
rule in the TOOL that writes the data, not in the template — so a living
person's dates never enter the JSON at all. I built a page for a family with
survivors today and the rule stripped two birth years before they could reach
a file. A template guard would have shipped them into the search index.
