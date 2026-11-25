# Senj register capture: how every image is read and every entry written down (opened 25 November 2026)

This is the working method for the end-to-end walks in `senj-books-plan.md`. It was set while reading Senj births 1859-1877
(`9R2D-JW5`, Latin printed table, svezak V, Povijesni arhiv Rijeka 275 (K4) 498), and applies to every Senj book.

## What is read, from where

- Local private copies of the leaves only: `Family Projects/_scans/<WAYPOINT>/NNNN.jpg` (never committed, never copied into a site or the Atlas).
- One image is one opening (two pages, a left and a right half of the printed table). An entry is one table row and runs across both pages.
- Make the two page crops with the helper (they are 2000 px tall, which is the size that reads the cursive reliably):

      OUT=<your folder> bash <scratchpad>/jw5/prep.sh N      # writes $OUT/NNNNL.jpg and $OUT/NNNNR.jpg

  and look at both with the Read tool. Zoom (crop the original with `sips -c H W --cropOffset Y X`, then `--resampleHeight 1800`) on every
  cell you cannot settle, on every surname in the watch list, and on every number in the entry-number column. A whole-image view (`sips -Z 1500`)
  is only for covers, targets, blanks and a rotated or shifted opening.

## The table, one file per book (`sources/senj-entries-<WAYPOINT>.tsv`), tab-separated, one header line

`vol`, `image`, `pages` (the printed page numbers seen on the opening, e.g. `1-2`, empty if none is printed), `entry` (the "Numerus currens" as written;
empty if lost, and then say so in `conf`), `born` and `baptised` (ISO `YYYY-MM-DD` when day, month and year are all read; otherwise what is read, e.g.
`1859-01`; empty if none), `child` (given name(s) as written), `legit` (`legitima`/`legitimus`/`illegitima` as written), `parents` (the whole parents cell,
copied as written, line breaks as ` / `), `father`, `mother` (each as written, mother with her maiden name if the cell gives one; empty if not given),
`occupation` (as written, Latin or other), `religion` (the "Religio" column as written, `Romano catholica` or what it says), `house` (place and house number as written), `godparents` (the whole cell as written, ` / ` for line breaks),
`baptiser` (name and office as written), `obs` (the "Observationes" cell as written, and any marginal or later-hand note, each marked `[later hand]` when it is),
`conf` (the reading's confidence, see below), `note` (what the page itself shows: a pasted slip, a torn corner, a second exposure, a correction written over a
number or date).

- **Names are copied as written.** No modernising ("Joannes" stays "Joannes", "Franz" stays "Franz"), no joining of spellings, no choosing between two
  forms. The Atlas catalogues decide what is the same name, later and elsewhere.
- **A reading that is not settled is left out of the cell**, and the cell shows `[…]` where the unreadable word was. Never guess, never write a
  question mark in a cell, and never fill a cell from a neighbouring entry or from what the family tree says. `conf` then names the cell and what
  is unsettled (`child:a; father:b surname 2nd letter; godparents:c second name`). Grades: `a` read at plate level without doubt; `b` read, one letter
  or word weighed against the same scribe's hand elsewhere; `c` partly read, the cell holds only what is settled.
- Characters: write Croatian letters as the page has them (Č Ć Š Ž Đ and also the old forms). Where the scribe writes `v` for `n` or `u` for `n`,
  copy what is on the page and say it in `conf`; the reading of Perkonić/Perković is a known trap of this hand.
- **Every entry gets a row**, in the order of the page, even when almost nothing is legible (then the row says what is, and `conf` says `c`).
  A row is never written for an entry that was not looked at. An empty row cell means the table cell is empty on the page; `[…]` means it is not.
- **Living people**: nothing in a register of 1859-1877 is a living person, but later hand notes (`+ u Senju 14.VIII.1936`) are copied as they stand.

### The header line, and one example row (image 5, the first entry of the opening; all other columns follow the same way)

```
vol	image	pages	entry	born	baptised	child	legit	parents	father	mother	occupation	religion	house	godparents	baptiser	obs	conf	note
9R2D-JW5	5	1-2	7	1859-01-24	1859-01-24	Maria	legitima	Josephus Horvat faber ferrarius, / Josepha nata Sandrini	Josephus Horvat	Josepha nata Sandrini	faber ferrarius	Romano catholica	Segnia Nro 415	Franciscus Frica faber lignarius, viduus / et Maria Slatanić vidua, ambo Rom: catholici	Joannes Ivšić cooperator loci	Proles ista propter instans periculum mortis domi sub Nro 415 baptisata est.	child:a; father:a; godparents:b surname Frica	number cut by the page edge, a second figure written below it
```

## Watch list: zoom these regardless of how sure the first reading feels

Any name that starts or reads like Blažević (Blasevich, Blaschevich, Blaževich, Blažević), Kosina, Žubrinić (Zubrinich, Xubrinich), Perpić/Prpić (Perpich,
Prpich, Perkonić/Perković), Tomljanović, Franceschi/Franceskini/Defranceschi/Franchesini, Uroda/Vroda, Šojat/Soyat, Papić, Bevandić, Orešković, Dobrila.
Zoom to the level where each letter is clear, read it against the same scribe's hand on the same page, and give `conf`. Near-names you actually read
(Blažina, Blažić, Blažetić, Blažanin...) are written exactly as they are; they are never changed to the watch name.

## Special images

- Film slate, resolution target, cover, endpaper, blank page: logged in the ledger as such (`kind` = `slate`, `target`, `cover`, `endpaper`, `blank`), no rows.
- A second exposure of the previous opening, or a rotated or shifted frame: logged, and rows are written only for entries not already captured
  (cross-reference the earlier image in `note`).
- A printed title or a handwritten summary page (year totals, an index): copied as text into the ledger's `text` field, not into the table.
- A pasted slip over an entry, a torn corner, a correction: read what can be read, say what is covered in `note`.

## The per-image ledger (`sources/senj-walk-ledger-<WP>.json`, same shape as the existing ones)

`images["N"] = {"passes": ["1"], "kind": "entries", "entries": 6, "first": 7, "last": 13, "note": "..."}`. An image is only listed when both of its pages were read and
every entry on it has a row. The book is "walked" only when every image of the book is listed and the table is checked (no image without rows unless it is a
target, cover, blank or second exposure). Until then the search-register row says what was read (`pages`) and `walked: false`.

## Checks before a part is handed in

- Every image number in the part's range appears in the ledger part, and every `entries` count equals the number of rows for that image.
- Entry numbers run on from image to image (the scribe's numbers continue; an irregular number is zoomed, copied and noted, never renumbered).
- Born/baptised dates run on in order within a page; an out-of-order date is zoomed and noted.
- No cell holds a guess. No `?`.
