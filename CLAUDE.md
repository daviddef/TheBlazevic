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
