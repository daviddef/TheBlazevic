# Novi Vinodolski is indexed to 1899, and the coverage table said 1850s

**20 September 2026.** Marking the first coverage table *superseded* raised a question it
had not occurred to anybody to ask: **the new table was built fresh rather than from the
old one, so anything the old one held and the new one did not had simply vanished.**

Checked. **One parish had: Crikvenica.** Restored.

## And checking it turned up something better

Chasing Crikvenica meant measuring the parishes around it, and **Novi Vinodolski — the
book with the largest reach in this archive — is indexed far more widely than the table
said.** The table recorded *baptism, probed 1680s 1850s*. A place-only census:

| births | entries | what they are |
|---|---|---|
| 1650–1749 | **300 of 300** | baptisms |
| 1750–1799 | **300 of 300** | baptisms |
| 1800–1829 | **300 of 300** | baptisms |
| 1830–1859 | **300 of 300** | baptisms |
| 1860–1879 | **300 of 300** | baptisms **and burials** |
| 1880–1899 | **300 of 300** | baptisms **and burials** |

**Dense in every window from 1651 to 1899**, and **burials are indexed too, from 1860** —
about a quarter of the rows in the last two windows, and none before.

**This is Klenovica's parish.** `parishes.psv` gives Novi Vinodolski as
*novi vinodolski, klenovica, povile*, and **101 of this archive's people are at
Klenovica**. A book that was recorded as sampled in two decades is in fact searchable
across two and a half centuries.

## A fifth child, and the one whose scan nobody had

`corrections.json` records **four** Kalanj baptisms «sitting unattached in the family's own
photo library» — Ana 1894, Franciska 1896, Zora 1898, Ivan 1900, all of Martin Kalanj and
Marija Peričić.

**The index holds five.**

    5 Aug 1893   Rozalia Kalanj    Martin Kalanj × Maria Peričić    XQMQ-QY3Q
    May 1894     Ana Kalanj        Martin Kalanj × Marija Perčić    XQMQ-431T
    29 Aug 1896  Francika Kalanj   Martin Kalanj × Marijo Peričić   XQMQ-C14Q
    Apr 1898     Zora Kalanj       Martin Kalanj × Marija Peričić   XQMQ-8DTK
    Mar 1900     Ivan Kalanj       Martin Kalanj × Marija Peričić   XQMQ-431C

**`rozalia-kalanj` is in the tree**, born 4 July 1893, with exactly those parents — and had
**no reading of any kind**, because hers is the one scan that was not in the photo library.
The four that were there got read; the fifth was never looked for.

**And her entry does not sit quietly.** The tree gives her birth as **4 July** and the index
her baptism as **5 August** — a month, where her four siblings' entries put days between the
two. Filed `INDEX ONLY` and flagged, because that gap is a reason to open the page rather
than something to write down and move past.

## Crikvenica, restored and demoted in the same breath

It is **densely indexed 1750–1858 and zero from 1860**. But its 448 surnames are
Crikvenica-town names — **Czar, Lovrich, Skiljan, Ivancsich, Xuppan, Pohmajević** — and
**not one Kalanj or Perković** in 1,800 sampled rows.

**That is because Klenovica is not in this parish.** The archive's own `parishes.psv` gives
Crikvenica as *crikvenica, selce jadranovo*; Klenovica belongs to Novi Vinodolski. An hour
was spent probing the wrong book on the strength of a place string in the tree, and the
gazetteer had the answer the whole time. **Cheap, and worth writing down so nobody repeats
it.**

## Two old claims that do not reproduce

**«Novi Vinodolski: 4 death».** A census of 1,800 rows returns baptisms and burials and
**no deaths**. Burials are a different event and are dated from 1860.

**«Senj also under the Latin place string SENIA».** `q.anyPlace=Senia` returns **nothing**.
Either it was never right or it has been normalised away.

**Neither is recorded as a correction**, because a probe that fails to reproduce a result is
not the same as a probe that disproves it. They are noted and left.

---

## And then the opening closed, which is worth recording as carefully as an opening

A densely indexed parish holding 101 of this archive's people looked like the best lead of
the day. **It is not, and the reason is the caveat this table has carried from the start:
presence is not completeness.**

**The Kalanj surname appears FIVE times in the whole Novi Vinodolski index** — eight
spellings tried, *Kalanj · Kalain · Kallayn · Kalanja · Kalanic · Kalany · Calanj · Kalan*,
as surname and as father's surname — and all five are the one household of Martin Kalanj
and Marija Peričić, 1893 to 1900. **Nothing earlier. Nothing else.**

**It is not the surname-blindness that caught this archive out at Karlobag.** Tested the
way that fault is tested — given names only, no surname:

* *father Josephus × mother Rosalia, 1855–1870* — **0**. That is Martin's and Anica's
  household, and their baptisms are quoted in `corrections.json` from the page itself.
* *father Josip × mother Rozalija, 1855–1870* — 21 rows, **not one a Kalanj**.
* *Josephus, 1824–1828* — 24 Novi Vinodolski baptisms, dense and legible: Sokolić,
  Krišković, Maričić, Petrinović, Mudrovčić, Karlović, Potočnjak, Piskulić, Radetić **and
  Peričić**. **No Kalanj.**

**Peričić is in the index and Kalanj is not**, in the same parish and the same decade. So
this is not a spelling failure and not a coverage failure. **The index for this parish
simply does not hold this family before 1893.**

## And the village is invisible

**«Klenovica» never appears as a place string.** A query for it returns **Cres, Hreljin,
Lopar, Ravna Gora** — fuzzy matches on other parishes entirely. *Povile* the same. Every
row in this parish is filed as **«Novi Vinodolski»**, 200 of 200 in the 1800–1860 sample,
one string and no other.

**So: search Novi Vinodolski, never Klenovica** — and expect the parish and not the village
in anything that comes back.

## What that leaves

**The 101 Klenovica people are a film read, not a lookup**, in a parish whose index is
dense for everybody except them. `parishes.psv` gives the films as **baptisms 1650–1900,
marriages 1674–1859, deaths 1704–1899** — so the book is there, and it is
[row 32](/worklist/)'s.

**The five indexed entries are still worth having**: they gave Rozalia 1893, whom nobody
had. But they are the end of what the search box can do here, not the beginning.
