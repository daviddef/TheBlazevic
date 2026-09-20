# The index and the tree disagree about when Hedviga's mother was born

*20 September 2026. Found by searching the Senj baptism index by PARENTS rather
than by name, which is the query that finds a household rather than a person.*

---

## Five children of ahnentafel 6 and 7, indexed

Searching `q.fatherSurname=Papic&q.motherSurname=Prpic&q.anyPlace=Senj` returns
the household of **Josip «Joso» Papić** and **Antonija «Tonka» Prpić** — and the
index spells them both ways, *Josip × Tonka Prpić* and *Joso × Tona Perpić*, in
the same set of results.

| Child | Index | Tree | |
|---|---|---|---|
| Marija | born **11 Aug 1885**, bapt. 12 Aug | 11 AUG 1885 | agrees to the day |
| **Milka Lucia** | born **9 NOV 1886**, bapt. 17 Nov | **9 OCT 1886** | **DISAGREES — the month** |
| Anica | bapt. **3 Jul 1888** | 25 MAY 1888 | index gives no birth day |
| Josip | bapt. **1890** | 18 MAR 1890 | index gives no day |
| Božica Tonka | born **9 Dec 1891**, bapt. 13 Dec | 9 DEC 1891 | agrees to the day |

## The disagreement

**Milka Lucia Papić is ahnentafel 3** — Hedviga's mother, and after Hedviga the
most important person in this archive.

**The tree says 9 October 1886. The index says 9 November 1886**, with a baptism
on 17 November. The **day of the month is the same** and the **month is one
step out**, which is the shape of a transcription slip rather than of two
different children.

**Which is wrong is not decided here.** But two things sharpen it:

* **The index agrees with the tree to the day on two of the other four** —
  Marija 11 August 1885 and Božica 9 December 1891 — so it is not sloppy about
  this household in general.
* **A baptism eight days after a birth is ordinary** for this parish and this
  decade. A baptism on 17 November for a birth on 9 **October** would be
  thirty-nine days, which is not.

That second point leans towards the index. **It is not enough**, and today is
the day to say why: this same indexing names the wrong mother for ahnentafel
106 — *Marie* where the register plainly reads *Antonie* — and gives Zvonimir
Vukelić's mother a surname this archive read differently off the image.
**An index transcription is not evidence against an image, and here there is no
image yet.**

## What would settle it, and it is reachable

**Senj births are filmed 1878–1894**, so **1886 is inside the film**. This is
not one of the entries stranded outside the filmed range — unlike
[question 5b](/open-questions/)'s two sisters of 1895, which this same search
confirms are in neither the index nor the book.

**One page, and the archive's second-most-important birth date is settled
either way.** ark `1:1:X9D5-SHTB`.

## And her own row is deliberately not in readings.psv

The four children whose index entries **agree with the tree or add nothing
contested** are recorded in `sources/readings.psv`, each marked **INDEX ONLY,
not read from the image**.

**Milka's is not.** A reading row is this archive saying *«a document has been
read for this person»*, and what exists here is a transcription that
**contradicts the tree** about a direct ancestor's birth. Writing it in would
either assert the index over the image or bury a conflict inside a citation.
**It stays in this note until somebody opens the page.**

---

# CORRECTED, 20 September 2026 — the page had already been opened

**Everything above is right about the index and wrong about this archive.** It says «there is
no image yet», and «one page, and the archive's second-most-important birth date is settled
either way». **The page was read long ago, and it is published on this site.**

`site/src/pages/milka.astro` carries **the register image itself** —
`/photos/line/4505839-milka-lucia-birth-1886.jpg` — under the heading *Senj baptisms, page 122,
entry 96*, with the entry transcribed:

> **Milka Lucia**, *zakonita* · **born 9 October 1886, baptised 17 October** · father
> **Josip Papić, *trhonoša*** · mother **Tonka *rođ.* Prpić** · godparents **Josip Glavičić**,
> also a *trhonoša*, and **Ivka Filipović**

**The register writes the birth «1886, 9/10».** And `corrections.json` has carried the
consequence for as long: the tree's *baptism* of 19 October is a slip for the register's
**17 October**, and the archive follows the register.

## And there is a second, independent attestation

**Her marriage entry of 4 November 1907** — Senj marriages p. 294 entry 30, re-read at
**5,812 × 4,273** on 13 September 2026, ark `3:1:3QS7-L99X-175J` — gives her birth as
**«9/X»**. Roman ten. **October.**

**Two register entries, thirteen years apart, in two different hands, both say October.**

## So the conflict is settled, and the index lost

**The index is wrong by exactly one month on both of its dates** — birth and baptism alike,
9 November for 9 October and 17 November for 17 October. That is not two errors; it is one
error in the month, carried to both columns of the same entry.

**Why the mistake above happened is worth keeping.** This note was written from a household
sweep of the *index*, and it checked the five children against **the tree**. It never checked
them against **this archive's own pages**, where the answer had been sitting with the image
attached. The same sitting made the same mistake twice more — ahnentafel 21 and ahnentafel 7
both had evidence already in hand that the sweep walked past.

**Her rows are in `readings.psv` now**, both of them, marked as **read from the image** rather
than INDEX ONLY — because they were.
