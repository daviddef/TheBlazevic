# Otočac on FamilySearch: the end-to-end walk for Žubrinić (plan and control, opened 10 November 2026)

David's order (10 November 2026): walk every Otočac book on FamilySearch end to end and show every Žubrinić and their
relations across them. Method: the shared `familysearch-volume-sweep` skill. One FamilySearch sweeper per account:
the Lerena session reads on the same account, so ask before starting and again before resuming.

## Terms to type (Atlas catalogue, `surname_variants.py terms Zubrinic`, 10 November 2026)

Same family: Xubrinic, Xubrinić, Xubrinich, Žubrinić, Zubrinic, Žubrinic. Seen on this line's records: Zubrinić, Zubrinich.
Also met in this archive's own notes and NOT yet in the catalogue (add with evidence at the end of the walk, do not
assume): Dubrinić, Bubrinić (an index misreading), Subrinich. Read the page for any such form; log it as seen.

## The volumes (Atlas `fs-volumes.json`, place `otocac`) and what is already read

| # | Waypoint | Contents | Already read | To walk |
|---|---|---|---|---|
| 1 | `9RK1-N3B:391644801,391674001,391979302` | Births 1834-1846 (film 5482656) | images 8-27 for Marić/Šumbul; spot reads 16, 43-47 | all images, for Žubrinić |
| 2 | `9RK1-Y4C:391644801,391674001,391979401` | Births 1846-1858 + Deaths 1834-1858 (film 5482657, 218 images; beyond ~219 is Pakrac) | deaths 140-217 for Kraljić; 15 Michael-father baptisms by index; 117, 147-152, 167 | all 218 images |
| 3 | `9R2D-16X:391644801,391674001,391979501` | Census 1710-1846 (9-122), Marriages 1859-1872 (~129-147), Deaths 1780-1836 (156-332), Deaths 1859-1872 (336-379), film 5498269, 384 images | census whole (14 Sept); deaths 1780-1836 whole (15 Sept); marriages verified, one entry read; deaths 1859-72 reduced scale for Kraljić | marriages 1859-72 and deaths 1859-72 at full size; a Žubrinić-table pass over the census and the 1780-1836 deaths, which were read for other questions |
| 4 | `9R2W-823` | Marriages and Deaths 1918 | nothing | look, probably out of scope |

Not on FamilySearch at all: Otočac baptisms before 1834, marriages 1834-1858, anything 1710-1780 except the census.

## Control

`sources/otocac-walk-ledger-N3B.json`, `-Y4C.json`, `-16X.json` (skill `ledger.py`; resume rule `ledger.py FILE next`).
Findings go into `sources/otocac-zubrinic-table.tsv` (volume, image, side, date, event, person, father, mother, spouse,
village and house number, godparents/witnesses, spelling as written, reading confidence). One row per Žubrinić or
relation named in an entry; mothers' maiden names, godparents and witnesses count.

## Status

- 10 November 2026: nothing walked yet. Lerena session is reading (Florida baptism book) and asked me to hold; I made no
  FamilySearch image request. Resume when it messages that it has stopped.
- 10 November 2026 (later): the Lerena session released FamilySearch; David signed in and ordered the walk. First pass done by page-crop readers over the whole of N3B (births 1834-46, images 1-73), Y4C (births 1846-58 and deaths 1834-58, images 1-217) and X16 marriages 1859-72 (129-152), deaths 1780-1836 (153-332) and deaths 1859-72 (336-379); the census (X16 9-122) only through its alphabetical index (123-125) and the household pages the index points to (see below). A second pass over the left-page line ends of the 1780-1836 deaths (the first crop cut them) is done for images 153-332. Findings: `sources/otocac-zubrinic-table.tsv` (1279 rows, one per mention; events in `sources/otocac-events.tsv`), near-names in `sources/otocac-zubrinic-near.tsv`.
- Gaps, stated plainly: Y4C deaths Nrus 12-29 (Feb-10 May 1852, book pp. 189-190) are not on the film between the openings 187|188 and 191|192; the readings are by reader, and only the 165 medium and low rows were re-read at full zoom (see the next entry); the 1114 high-confidence rows are first-pass readings; the 1780-1836 deaths carry no mothers' maiden names or godparents; census household pages read only for the houses the index gives.
- 10 November 2026 (full-zoom check): every one of the 165 medium and low rows (59 N3B, 36 Y4C, 70 X16; 123 page-sides) was re-read at level 13 by page-crop readers, top and bottom half of each side, and the verdict written in the table's `verified` column (the reader's spelling and remark are appended to the note; the 165 rows are also in `sources/otocac-zoom-checks.tsv`). Result: 117 CONFIRMED, 8 CONFIRMED-STEM (the stem Žubrin-/Xubrin- is clear, the ending is lost under a column rule, the page edge or a flourish), 11 LOOK-ALIKE (another name: Zubesich, Hrabrov, Dubrinić, Žubčić types; kept in the table with `verified` = LOOK-ALIKE and not counted, and entered in `sources/otocac-zubrinic-near.tsv`), 29 UNSETTLED (letters lost or an initial not settled between Ž and D; not counted as certain). The readers also listed 167 Žubrinić-type names on the same page-sides that were not among the items: 135 already in the table (by date, within four days), 3 not matched by date (two are probably table lines 194 and 198 with a different day, one is Magdalena, godmother, Feb 1844, which may mean the table's dates for lines 207-210 are a month out: check), 22 another name (added to the near-names file) and 7 unsettled; all are in `sources/otocac-zoom-extras.tsv` with the table line they match. The events file's `status` is `zoom_confirmed` / `zoom_stem` / `zoom_unsettled` / `zoom_lookalike` for the 142 events with at least one zoomed row (the rest stay `read_by_reader` or `unsettled`). Not done: the high-confidence rows were not re-zoomed; the images are about 1400 px wide, so some initials (Ž against D, X against K) stay open at any zoom.
- Not "walked" in the Atlas sense: no volume is closed (`walked` stays false) until the table's hits are zoom-verified and the unread cells are cleared.
