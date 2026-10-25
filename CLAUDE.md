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

- **The kit carries the rule (341af33, 25 October 2026).** `living_rule.is_living` no longer lets a public-source citation or a
  bare death flag release anybody born inside the window. `tools/livingset.py` passes `undated_dead=True` for a DEAT event that is
  only `Y` (no date, no place, no cause or note, no burial: `death_evidence() == "flag"`) and `recorded_dead` for a real record.
  `cites_for_living` is kept working beside the kit and is redundant; delete it once the kit gate has run clean for a release.
  The one person whose status changed was a tree typo (a birth year after the parents' deaths): withheld as living on 25 October, he
  is deceased again since 26 October (below). The correction text that still quotes the tree's year is registered in `data/living-year-allow.json`.
- **Two records kept beside the tree, never in it (26 October 2026; applied by `gedcom.apply_overlays` on every `load()`).**
  `data/tree-corrections.tsv` (id|event|tree year|corrected year|source): a typing slip in a YEAR, corrected for publication, day and
  month kept; the event's note says so and the source is the archive's own correction note in `corrections.json`; a row whose tree
  year no longer matches stops the build. `tools/consistency.py` reads the tree AS EXPORTED (`load(corrected=False)`) so
  /impossible/ still reports what the tree says (who is living is decided on the corrected tree). `data/death-confirmations.tsv`
  (id|source|grade): a death the tree records with a place and no date, confirmed by the family; the source and grade are printed
  on the death event, no date is invented, and it is a RECORDED death for the kit (take the hold in `living-hold.tsv` out in the same
  commit). Current rows: one corrected birth year (Georgius Prpić, 1962 to 1862), one confirmed death (Robert, family
  confirmation by David, 25 October 2026). Ivan Anton Defranceski (the second of the name) is NOT changed: the Defranceschi archive
  records a death in 2026; this archive holds none.
- **A third record kept beside the tree: a merge the owner confirms (25 October 2026).** `data/tree-merges.tsv`
  (surviving id|retired id|source|grade), applied by `gedcom.apply_merges` after the overlays and before the parent links.
  The first row: Georgius Prpić (survivor: the better-sourced, with the day and the register of his birth) and Jure Perpic
  (the Croatian form of Georgius; died 1882) are ONE man, confirmed by the tree's owner (the source on the row names him). The retired person leaves the
  people, every family names the survivor (a child listed twice in a family is listed once: he is no longer his own
  brother), the facts are folded in (an empty or flag-only event is filled, a plain date made exact by the other record's
  date of the same year, both citations kept; a different date, place, cause or sex STOPS the build: nothing is chosen
  silently), the retired name is kept as `alt_names` / `merged` («Also recorded as» on the page), and
  `site/src/data/merged.json` (written by `build_site_data.py`, read by `astro.config.mjs`) turns the retired
  `/people/<slug>/` and, where nobody else bears the name, `/who/<slug>/` into Astro redirect stubs. The slug stays in
  `person-slugs.json` for ever. `load(corrected=False)` applies none of it. The merge is written up on /corrections/ (the
  entry for the survivor in `corrections.json`). Regenerate with `python3 tools/regen.py` (and `tools/ancestry.py` for
  `data/surname-*.tsv`), then rebuild the search index. Nothing is merged on a resemblance: /duplicates/ still only reports.
- **`npm run check:living` also runs the kit's printed-year gate** (`--years --config standard.json --strict-allow`): its registry is
  `data/living-year-allow.json` (`{allow:[{text, why, file?}]}`, a reason of 8 characters or more; the text is matched in the RAW
  built file, so a snippet inside HTML carries its tags), named in `site/standard.json` under `living_years`. It runs beside
  `tools/livingyears.py`, which keeps its own registry (`data/living-year-allow.tsv`).
- **`data/living-hold.tsv`**: people the tree records dead with a place and no date, held as living until David confirms (empty now: confirm with `data/death-confirmations.tsv`).
  Refused for anybody with a dated death. (A bare flag needs no hold: the kit keeps such a person living.) **`data/living-redact.tsv`**: a dead person's free text that prints a living person's year.
  **`data/living-year-allow.tsv`**: a decision, with a reason, to print a window year (a typo in the tree). **`sources/media/withheld.psv`**:
  photographs that show living people; their files are not kept.
- **`npm run check:living-years`** (`tools/livingyears.py --selftest`, in the build chain) asks what is PRINTED, not what a flag says:
  ROW-BIRTH (a data row), ROW-OPEN («<year>–?»), TXT-BDOT («b. <year>»), TXT-BORN («born in <country> after <month> <year>»), MEDIA, HOLD,
  RULE, and, with the GEDCOM beside it (local only), TREE-NAME, TREE-GIVEN («<name> in <year>»), TREE-DATE and PUBDEATH. Every rule has a
  planted fault in `--selftest`. A generated person page's Born label is the generator's: it is checked as a data row.
- A stone survey row born in the window with no death year is either printed «20??» (the survey says the death year was cut) or
  withheld (`tools/graves.py`); an index row giving a window birth is withheld (`tools/abroad.py`).
