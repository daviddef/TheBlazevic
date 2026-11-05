# Roots & Routes (the tree page)

Ten views of every person in the archive who has died: hourglass, fan, whole-tree and close-family maps, Atlas map, movements, kinship, place lanes, eras,
lifespans, an Orphans tab, and the five animated views (Night sky, Ink ledger, Household, Generations, Where they lived). It is served at `/roots/`, and
bare at `/roots/view.html` for the frames in "Where they lived, and what is still missing" on a person's page (story mode).

| File | What it is | Edit by hand? |
|---|---|---|
| `tree.json` | people, parent links, years, places, routes | no, generated |
| `place_map.json` | each place string with coordinates, country and Record Atlas id | no, generated (see below) |
| `place-additions.json` | place strings decided by hand, each with its reason | yes, with a reason |
| `atlas-data.json` | the Record Atlas slice: outlines, regimes, flags, events, collections | no, generated |
| `roots.html`, `roots.embed.html` | the page, whole and as a fragment for the site layout | no, generated |
| `tree.report.json` | counts, and the 14 people whose dates are not one life | read it |
| `people.ged`, `slugs.json` | intermediates, not committed | no |

## Rebuild

```bash
python3 tools/build-tree-page.py --accept-unique   # rebuild everything and run the page's own checks
python3 tools/build-tree-page.py --check           # exit 1 if the page is older than the data it was built from
```

Needs the Record Atlas checkout (`RECORD_ATLAS`, default `~/Projects/Family Projects/Record Atlas`), read only. The skill's scripts are vendored in
`tools/tree-page/` (the family-tree-page skill, template 1.6.0), so CI and other sessions do not depend on `~/.claude`.

## What is and is not on the page

- **No living person.** The people are `site/src/data/people.json`, which holds none (living people are in `living.json`). The converter adds its floor:
  nobody with no death recorded and a birth year in the last 110 years (106 people). The page's own check fails the build on a living person's name.
- **Colour is the archive's own family** (`family` in people.json, the labels of `families.json`), not a surname spelling. Which spellings are one name is the
  Record Atlas catalogue's to say; nothing here lists them.
- **Places are never guessed.** 911 place strings come from `data/era-ground.tsv` (the town and point decided for each string as printed, with country from the
  Atlas's `geo.country_of` on the point); 21 from `place-additions.json`; the rest the Atlas names uniquely. A string that is more than one place, or names a
  country only, stays unresolved: the person is drawn at a relative's birth place (1,855 people, said on the page) or, with no relative placed, not drawn (307).
- **Estimated years are flagged**: "c. 1809" is a birth estimated from a parent, child or spouse; "1809–?" is a death not recorded.
- **Two lives that cannot be one** (died before born, or over 110 years) are not drawn and are listed in `tree.report.json` under `conflicts`.
- **The death place is the place the record states.** The converter takes a later residence as the death place; `keep_death_place` puts the recorded one back.
- **A route** (three or more places) is carried whole where the tree says "From X" on an immigration: Hedviga is Senj, Zimbabwe, Johannesburg (1975).
  "Zimbabwe" is country-level (the Atlas has no place of that name yet; the point is the centre of its outline) and is said to be so in `place-additions.json`.
