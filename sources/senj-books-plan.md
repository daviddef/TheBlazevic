# Senj and its neighbours on FamilySearch: the end-to-end plan (opened 25 November 2026)

David's order (25 November 2026): get the books done end to end, Senj first, then the neighbouring parishes ("do them all").
Method: the shared `familysearch-volume-sweep` skill. One FamilySearch sweeper per account; the Defranceski session also reads
on the same account, so ask before starting and send one "pane free" at the end of each book or sitting.

## What "done" means here

- Every image of the book is read, both pages, at full size, including second exposures (Senj births image 32 is a second photograph of Str. 23)
  and covers/targets (logged as such). The per-image ledger (`ledger.py FILE next` is the resume rule) is the receipt.
- Every entry is captured in a table, one file per book: `sources/senj-entries-<WAYPOINT>.tsv` (a volume's images, once per book), with the columns
  volume, image, printed page, entry no., born, baptised/married/died, name, legitimate, father (as written), mother (as written, maiden name),
  occupation, house/place, godparents/witnesses, baptiser, later notes, reading confidence. Names are copied as written; a reading that is not
  settled is left out of the cell and said in the confidence column, never guessed. Nothing is typed into the table about living people.
- Only then does the search-register row say `walked: true`. Until then it says what was read (`pages`) and `walked: false`.

## The control files (this PR)

- `sources/senj-walk-ledger.json` (marriages and deaths 1734-1858, 592 images, all read; the 1790-91 Latin block, images 139-142 onward, still to be reread at higher zoom).
- `sources/senj-walk-ledger-JWL.json` (births 1878-1894, 269 images): pass 1 done for images 25-33 and 70-71 only (both pages, every entry).
  The 17 October sweep (images 158-166, 170, 206-239 except 207-208, 260-263) was read by a child's name, so it does not count as a read of every entry.
- `sources/senj-walk-ledger-JW5.json` (births 1859-1877, 399 images): images 317 and 363-364 only.
- Ledgers for the other Senj books are opened when their image counts are measured (step 3 below).

## The order

Setup: (1) agree the pane with the Defranceski session; (2) probe each book for a machine transcript or Image Index (the transcript-scan mode finds
hit leaves fast but never supports "walked"); (3) measure the image count of every waypoint and save its ark list; (4) the capture table above.

Senj: (5) `9RK1-W3P` marriages and deaths 1734-1858, 592 images, reread the Latin block and close; (6) `9R2D-JWL` births 1878-1894, 269; (7) `9R2D-JW5` births 1859-1877, 399;
(8) `9R2D-K6D` deaths 1859-1907; (9) `9R2D-N3F` marriages 1859-1920; (10) `9R2M-L27` births 1756-1858; (11) `9RK1-T3F` births 1734-1756;
(12) test the 16 October baptism-index sweep against the walked pages; (13) re-find ten tree people with known Senj baptisms as a control; (14) publish each closed book to the Atlas.

Neighbours (by people in the tree): Krivi Put births 1847-1884, marriages 1871-1894, deaths 1878-1934 and the missing roll; Otočac (`9RK1-N3B`, `9RK1-Y4C`, `9R2D-16X`, `9R2W-823`,
plan in `otocac-walk-plan.md`); Sv. Juraj kod Senja 1697-1852; Senjska Draga 1858-1900; Selce 1778-1886; Novi Vinodolski and Klenovica 1650-1900; Krmpote-Vodice 1879-1896;
Karlobag 1691-1861 and its census; Prozor 1704-1857; Jablanac and Brinje; Vratnik.

## Rules that do not bend

Never enter credentials (David signs in); a sign-out (401), block or rate limit is a stop, written down with the next image. Zoom before naming. A nil names the exact terms typed
(Atlas catalogue, `terms` then `cover`). Surname and given-name forms met go to the Atlas catalogues, not into this archive. Snapshot every reading (`sources/snapshots.psv`).
A finding is not done until it is told in the archive's files and, where it names a person the tree holds, linked to their page.
