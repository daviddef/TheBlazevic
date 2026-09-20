# Eight readings that named nobody

**20 September 2026.** `sources/readings.psv` is the archive's record of what has actually
been read off a page. It had ninety-three rows. **Eight of them credited nobody at all.**

Each carried a slug that exists in no `people.json` and no `ancestors.json`. Nothing
crashed. `coverage.py` looked the slug up, got nothing, and moved on. `datecheck.py` —
written that same morning to hold every dated citation against the tree — did
`people.get(slug)`, got `None`, and `continue`d. **The rows sat in the file looking like
evidence and graded nothing.**

## All four bad slugs are the same mistake

A **nickname** that the slug generator drops and a hand-written row keeps.

| in readings.psv | the real slug | |
|---|---|---|
| `matia-matthea-`**`matija`**`-pilipic` | `matia-matthea-pilipic` | **ahn 13** |
| `vicentius-andreas-vincent-`**`vicko`**`-pilipic` | `vicentius-andreas-vincent-pilipic` | **ahn 26** |
| `josip-anton-`**`joso`**`-papic` | `josip-anton-papic` | **ahn 6** |
| `georgius-juraj-joannis-papa-`**`jure`**`-antic` | `georgius-juraj-joannis-papa-antic-papic` | **ahn 12** |

**Every one is on the direct line.** Between them the eight rows are a baptism, two
marriages and four baptisms-of-child — including ahnentafel 13's own Karlobag baptism of
1838 and ahnentafel 12's marriage of 1885.

**A reading filed against a person who does not exist is worse than a missing reading**,
because the file looks fuller than it is.

## What it did and did not change

**It did not move the grade.** Coverage still reads 47 / 15 / 8. All four were already
graded `read` through a citation keyed on their GEDCOM id rather than their slug, which
is precisely why nobody noticed — two independent paths to «read», and only one of them
was broken.

**It did change what the tools can see.** Derived parent credits went **31 to 34**, and
`datecheck.py` can now hold those citations against the published dates, which it could
never do while the rows named nobody.

## The gate

`tools/datecheck.py` now **refuses the build** on any row whose slug names nobody —
whatever its kind, not only the dated ones it otherwise checks. It prints the nearest
real slug, because the cause is always a near-miss:

    FAIL  1 reading(s) name a person who does not exist:
          matia-matthea-matija-pilipic  (baptism 1838)  did you mean matia-matthea-pilipic?

Tested by putting a bad row back: exit 1. Removed: exit 0.

## And one real gap, found by the check that led here

The archive's rule is that **a baptism counts for the child and for both parents**.
`readingslib.py` applies it *parent-ward* — it derives parent credits from a child's
baptism row. But the sixteen hand-written `baptism-of-child` rows only ever went
parent-ward too, so a child named on their own baptism could have no row.

**Checked across all eight such pairs, and exactly one was open**: **ahnentafel 21, Maria
Catharina Orešković, Otočac, 8 September 1835**. Both her parents had been credited from
that entry since it was read — «*Marcus Oreskovich, adoptatus Sekula*» and «*Lucia uxor
ejus nata Sekula*» — and she had nothing. She has a row now.

**One case out of eight is not a systemic fault**, and it is worth saying so rather than
building a tool for it.
