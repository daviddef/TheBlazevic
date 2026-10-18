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
