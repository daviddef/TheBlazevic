# Research of 22 November 2026, second stretch: the loose ends, and one slow read at Karlobag

Items 26–30 of the 30-item list (the loose ends from the week's pull requests), and the first FamilySearch read of items 15–25.
The FamilySearch pane was signed in (catalogue status 200); the Lerena and Defranceski sessions said in writing that they were
not reading FamilySearch, so this session was the one sweeper. Nothing was entered, no limit met.

## 26. The ark-and-image check

**Offline part, done.** 332 FamilySearch arks in `sources/` and `notes/` sit within 160 characters of an «image N» or «frame N».
69 of them are in the film maps under `sources/familysearch/` (an image-number-to-ark map for Karlobag, Otočac and Selce). Compared
with those maps, every Karlobag ark agrees with its claimed number, and the Selce arks that look as if they disagree (304 against 18,
340 against 54, 397 against 111) are the one offset already explained on 22 November: film frame minus 286 is the volume image.
**Not done:** the other roughly 260 arks have no map, so each would have to be opened to learn what number the viewer shows. That is a
bounded job (one catalogue listing per waypoint gives the ark order, the way `fetch-arks.js` does) but it is a FamilySearch read, and
it also needs a decision about which numbering a citation means (the Karlobag citations count the whole film, the Selce
snapshots count the volume). It is left as the first job for a sweep session.

## 27. The 14 GED-NAME findings

Run with the GEDCOM beside the build (`tools/livingcheck.py`, then `--advisory`); the whole check passes, and the 14 are advisory only,
by the gate's own design. The list, by page: `/roots/` and `/roots/view.html` (one finding each), and one finding each on twelve
person pages: George Augustus Kolbe, Gregorie Pickerd, John Peckard, Ricardo Juan Carlos Lerena, Elizabeth Price, Pablo Armando
Robert Paul Lerena, Price (the surname page), John Gerson Eliezar Kolbe, Margaret Anne Degenfeld, Samuel Charles Sneyd, Richard
Price and Willem Hermanus Booyzen. All are the shared tree's English, South African and Uruguayan lines, not the Croatian ones.
**Not resolved:** the check does not print the living name it found, so which living person each page names was not read off here,
and nothing was rewritten. To close each one somebody has to open the page beside the tree and either give the person the
name-and-family-only treatment or remove the name; it is a decision about those pages, not a research result.

## 28. Vladimira Boras, and a year that was not printed but could be worked out

She is on the living list correctly (the tree records no death for her), and on `/corrections/` her name appears only as a
relation in a record about her mother, unlinked. **What was wrong is the line beside it:** the mother's entry gave her own birth
year and then her age at this daughter's birth and the gap since her first child, which is a way of printing the daughter's
birth year without writing it, and no gate reads for arithmetic. Changed in `site/src/data/corrections.json` (the record line
only): the line now says only that the tenth child comes decades after the nine others. The explanation beside it gives no
year for her and stays. No other text in `corrections.json`, `questions.json`, `worklist.json` or `who-finds.json` names any of
the 34 living people. The general lesson, for the living gates: a printed age or a «years after» beside a dead parent's year
is a living person's year; `tools/livingyears.py` does not look for that.

## 29. Why no era flags show on the corrections page

Not a gap in this archive's data. The era snapshot assesses only: 1951–1986 for the Croatian places (Yugoslavia), 1924–1936 for
Otočac as well, and for Brisbane 1843–1854, 1865–1896 and 1907–1990. The years the corrections page actually names are almost all
1700–1900 (Selce, Otočac, Karlobag, Krivi Put, Senj), which the snapshot leaves silent by decision (the Military Frontier and the
Kvarner are contested or have no flag in the kit's table). So no flag is missing here; to get one, the kit or the Atlas would have
to assess those eras. Nothing was added to `flag-countries.json`.

## 30. What's new «Corrected» cards: the two versions

`corrections.json` (164 rows) has no dates, so What's new counts them and draws no cards. Version A, the present one: nothing
changes. Version B: the 29 hand-written entries on the corrections page already carry a day each; passing them to the pulse as
dated rows would draw 29 «Corrected» cards and move the corrected count from 164 to 193, and each card would link to its
`c-<day>-<hash>` anchor. That is a ruling for David; nothing was built for B.

## Items 15–25: the first read

**Row 25 (Selce deaths): nothing to read.** What it still owns is the baptism of Margarita Drozović (born about 1776–81). The
Selce births volume begins in 1778 and was already read to 1783 without her, so she was baptised before it begins or elsewhere;
the one source that would name her parents' house is the *Status Animarum*, which is not on the films this archive holds.

**Row 54 (Karlobag births): image 53 read slowly, no Smojver or Vukić.** The baptism of ahnentafel 212, Josiph Smojver Vukić
(b. 1730–31), was last looked for in strips at 2–3x. Both pages of image 53 (book pages 94 and 95, entries from March 1730 to
March 1732) were read in three strips each at about 4x, entry by entry, for Smojver, Smoyver, Smoiver, Vukić and Vukich in any role.
None. The clerk (Pop Andrija Kolikar, a Latin entry pasted in for a gentleman's son on 6 October 1730) enters some months out of
order, which is why 1730 and 1731 follow each other twice on the one image. Search register: `fs/karlobag-births-1730-1732-smojver-slow-read-2026-11-22`.
This is a nil for one image, not for the man: an «Osip Smojver» is a father at Karlobag in 1733.

**Not started.** Rows 24, 26, 4, 29, 31, 33, 27, 32, 83 and 6 each need a long, careful read of a register; none was begun
today. Sensible order, from what the rows say is left: row 54's other unread images (the neighbours of image 53), rows 29 and 31
(Senj and Krivi Put baptisms, which rows 29 and 31 say have reachable entries), then row 4 (the Senj marriage of
ahnentafel 12 and 13).
