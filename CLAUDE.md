# Blazevic Family

## Record Atlas

The shared map lives at `../Record Atlas`. Research done here is only
useful to the next person if it gets there.

Invoke the `record-atlas-feedback` skill whenever you finish a search,
open a register, write to an archive, or find a source the atlas does
not list — as you do it, not in a sweep at the end. Record the
FamilySearch waypoint, not just the film number; the skill explains why.

## Snapshots

Every reading made from a filmed or Matricula page gets a snapshot of the page kept on the site:
the image in `site/public/snaps/`, a row in `sources/snapshots.psv` (film, image number,
where on the page, viewer link, what it says, who it supports), and a link to
`/snapshots/#id` from the note and the search-register row. `tools/snapshots.py` checks the
files, people and notes exist. Readings made before 11 October 2026 are the backlog on the work
list (row 80).

## The linking standard (18 October 2026)

The twelve narrative pages (`site/standard.json`, `include`) are held to the Archive Kit's linking standard
(`kit/docs/linking-standard.md`): L1 names with an entry are linked, L2 people read from a record have an entry, L3 a
passage that cites a record links to it, L4 a scan the archive may show sits beside its passage, L5 forms nobody wrote in
full. `npm run check:standard` (last in the build, after the autolink step) prints the five counts per page and holds them
to `site/.standardfloor.json`, which may only go down; counts, never a name. Raise a number by hand, in a commit that says why.

- **L3 is the `Rec` component** (`site/src/components/Rec.astro`): wrap the words a passage already has, never reword them.
  The address comes from `site/src/data/records.json`, which `tools/build_records.py` derives from data the archive holds
  (snapshots, Trove, Matricula and FamilySearch addresses written in `searched.json`, arks in finds' and readings' citations).
  An id the table lacks stops the build; where no address is held the text stays plain. `tools/check_rec.py` checks every
  `<a data-rec>` in the build against the table and 100 record links against the source data.
- **L4 is link-only by rule** (David, 18 October 2026): FamilySearch frames and Matricula pages are never shown beside a
  passage (`scans.link_only`); the table has no plates. The scans already published on `/snapshots/` stay where they are.
- **L2: `/who/` name pages list the clean register finds** (`site/src/data/who-finds.json`, from `tools/names_index.py`).
  716 of the 861 finds have a description, not a name, in the name field and are never split by machine; splitting them is
  data work an author or a reader of the registers does, after which they flow into the index by themselves.
- What an author alone can settle (bare given names, surname-first forms, the quoted press lists, the Karlobag census
  address) is listed in `~/Downloads/audit-briefs/links/blazevic-editorial.md`.

## The "at the time" notes (18 October 2026)

A quiet line under a dated place on a deceased person's page (the Born, Baptised and Died rows and the events list): who held that ground in
that year, from the Record Atlas's region eras (kit `kit/docs/era-notes.md`). Text only, "per the Record Atlas" (or "per the Record Atlas, drawn from this
archive's own research", marked `data-era-seeded="1"`, where the Atlas era was seeded from the estate's own sovereignty file), and nothing wherever the data does not support it.

- `data/era-ground.tsv` is the decision: each place string as printed -> a region, or `-`. `data/era-towns.tsv` holds the points the kit's
  edge rule checks against the rings. `tools/build_era.py` builds `site/src/data/era-places.json` from them and `--check`s them against the data
  (a new place string in `people.json` fails the build until it has a row). `--snapshot <copy of the Atlas's context.json>` rebuilds
  `site/src/data/era-snapshot.json` (version 5) with the recorded `--unassessed allow`; refresh it deliberately and review the diff.
- Never on a living page: `check:era` (the kit's `checkera.py`) reads the built pages. The three British regions give no note before 1753 (old-style year).
- The notes are not part of a page's text for the search index or the names index (`tools/searchindex.py` skips person pages and strips `<style>`).

## The living window (25 October 2026)

Somebody born within the last 80 years with no death recorded is living: named with relationships and town and country only
(no year, no date, no record, no photograph, no structured data). The edge is ONE derived constant, `livingset.cutoff_year()`
(this year minus the kit's `LIVING_YEARS`: 1946 in 2026), imported by the generators and by `tools/livingyears.py`.

- **A public source does not release a dated person.** The kit's `living_rule.is_living` returns False for anybody who carries a
  public-source citation (FamilySearch, a passenger index), whatever their birth year; the same hole put a living man's year on the
  Mazza archive (25 October 2026). `livingset.cites_for_living` passes no citations for somebody with a birth year. The exemption belongs in the kit
  (kit gap, reported, not edited here).
- **`data/living-hold.tsv`**: people the tree flags dead with an UNDATED flag and nothing else, held as living until David confirms.
  Refused for anybody with a dated death. **`data/living-redact.tsv`**: a dead person's free text that prints a living person's year.
  **`data/living-year-allow.tsv`**: a decision, with a reason, to print a window year (a typo in the tree). **`sources/media/withheld.psv`**:
  photographs that show living people; their files are not kept.
- **`npm run check:living-years`** (`tools/livingyears.py --selftest`, in the build chain) asks what is PRINTED, not what a flag says:
  ROW-BIRTH (a data row), ROW-OPEN («<year>–?»), TXT-BDOT («b. <year>»), TXT-BORN («born in <country> after <month> <year>»), MEDIA, HOLD,
  RULE, and, with the GEDCOM beside it (local only), TREE-NAME, TREE-GIVEN («<name> in <year>»), TREE-DATE and PUBDEATH. Every rule has a
  planted fault in `--selftest`. A generated person page's Born label is the generator's: it is checked as a data row.
- A stone survey row born in the window with no death year is either printed «20??» (the survey says the death year was cut) or
  withheld (`tools/graves.py`); an index row giving a window birth is withheld (`tools/abroad.py`).
