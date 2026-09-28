#!/usr/bin/env python3
"""The data was fine, the build dropped it, nothing refused.

Asked directly on 28 September 2026: are all findings in the site — visuals,
trees, stories, updated? Checking rather than asserting found a real instance.
Ursula Sedej — Johann Kozina's second wife, the woman who was later
`posestnica` of the house — had been fully written into `/kosina/`'s prose
across four commits, and was never added to `tools/kosina.py`'s CARNIOLAN
table, the hand-typed list that `kosina.json` and the page's own stat line are
built from. The count said "6 read out of the parish registers" while the
prose directly below it was describing a 7th. She was in `sources/found.psv`
the whole time. Nothing refused the build; it was simply never asked to check.

A sibling archive (via a cross-session message from the estate's landing
session, 28 September 2026) had already met this exact fault once, at Mazza,
and reported that five archives independently ported the lesson into their
own `check:evidence`-style gate, each in their own architecture. This is
this archive's version, and it targets the one place the fault could recur.

WHY IT IS ONLY ONE PLACE. Everywhere else, a found.psv row reaches a browsable
page by construction rather than by memory: `readingsdata.py` builds
`readings.bySlug` from every row of `sources/readings.psv` and every
`/people/<slug>/` page consults it directly; `/found/<slug>/` is generated
from `found.json` itself, one page per row, so a row cannot exist without a
page; and the eight core family pages call `descentOf()` in
`site/src/lib/households.js`, which pulls in every found.psv row whose
surname matches the family — a computed join, not a list anyone maintains.

Kosina is not one of the eight surnames, so `/kosina/` cannot use that join.
`tools/kosina.py`'s CARNIOLAN and HOUSEHOLD tables are hand-typed instead, and
say why in their own comment: "a claim about people ... should be legible as
one, not inferred from a string that might drift." That is the right call —
a page this dense in correction and retraction should not be quietly
regenerated — but a hand-typed list has no mechanism to notice when
`found.psv` grows a new row that belongs in it. This does not replace the
hand-typed list. It watches it.

WHAT IT CHECKS, AND THE DISTINCTION IT DOES NOT BLUR. Not "does this person
have a page anywhere" — every found.psv row already does, and that is checked
by construction, not by this file. This checks a different thing: does a
person the household's OWN relation text names — "SECOND WIFE of Johann
Kozina", "DAUGHTER of Johann Kozina and Ursula Sedej" — actually appear IN
the household this archive's flagship narrative page tells the story of. A
`/found/<slug>/` page a reader would only reach by searching is not the same
as appearing in the household table of the page written to be read start to
finish.

THE METHOD, AND WHY IT IS NARROW ON PURPOSE. A given name alone is too common
to mean anything — "Maria" matches a third of this archive's rows. Requiring
a Kos-/Koz- surname stem to ALSO appear in the same relation sentence is what
keeps it to zero false positives against the current file, tested by hand
before this was written rather than after: it does not flag a single Žubrinić
or Antić row that happens to share a first name with someone in the
household. The surname itself is allowed to vary — Kosina, Kozina, Kosinar,
Kosiner are the same clerks' hands on the same family, which is the whole
subject of the page's own "Kosina, or Kozina" section — so the stem, not the
exact spelling, is what is matched.

EXCLUDED, AND WHY, ON THE LINE RATHER THAN IN A COMMENT ABOVE THE LIST. Some
found.psv rows name a household member and are correctly NOT in the
household — a deliberate narrative choice, not an oversight. Add the row
name here with the reason, the way notescheck.py's NOT_FOR_READERS does it.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOUND = os.path.join(ROOT, "sources", "found.psv")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kosina as K  # noqa: E402

# A found.psv row that names a household member and is deliberately NOT
# itself in the household. Each line is a decision, not a gap.
EXCLUDED = {
    "Marija \"Mina\" Kozina":
        "the same woman as «Maria Kozina of 1859», who IS in the household. "
        "Two found.psv rows by design — one for each line of evidence that "
        "found her, the marriage register and the baptismal index — and "
        "/kosina/ tells the story of both converging on one identity. Both "
        "slugs are linked from the page's own prose.",
}

KOZ_STEM = re.compile(r"\bKos\w*|\bKoz\w*", re.I)


def household_names():
    return {t[0] for t in K.CARNIOLAN} | {t[0] for t in K.HOUSEHOLD}


def given_names(names):
    out = set()
    for n in names:
        first = n.split()[0].strip("\"")
        if len(first) > 2:
            out.add(first)
    return out


def rows():
    for line in open(FOUND, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = [x.strip() for x in line.split("|")]
        if len(f) < 3:
            continue
        yield f[0], f[2]  # name, relation


def main():
    household = household_names()
    given = given_names(household)
    bad = []
    for name, relation in rows():
        if name in household or name in EXCLUDED:
            continue
        if not KOZ_STEM.search(relation):
            continue
        hits = [g for g in given if re.search(r"\b" + re.escape(g) + r"\b", relation)]
        if hits:
            bad.append(
                "%s: relation names %s, who is in tools/kosina.py's household "
                "— but this row is not there, and not in EXCLUDED with a "
                "reason. «%s»"
                % (name, " and ".join(hits), relation[:90]))

    if bad:
        print("\n  FAIL  household  %d found.psv row(s) name a household "
              "member and are not accounted for" % len(bad))
        for b in bad:
            print("          " + b)
        print("        Add the person to tools/kosina.py, or to EXCLUDED in "
              "tools/householdcheck.py with the reason.")
        sys.exit(1)
    print("  ok    household  %d found.psv row(s) checked, %d household "
          "member(s), 0 unaccounted, %d excluded by name"
          % (sum(1 for _ in rows()), len(household), len(EXCLUDED)))


if __name__ == "__main__":
    main()
