# The Otočac Status Animarum, 1710–1846

Found 13 September 2026, while checking whether question 4's stated next step —
the Otočac baptisms of Casparus Žubrinić (14 January 1767) and Toma (1768) —
could be reached now that full-resolution FamilySearch access is solved.

**It cannot. Otočac baptisms on FamilySearch begin in 1834.** The 1760s are not
in the collection at all, and no amount of better image access changes that.

But the same parish has something the archive had never looked at.

## What it is

*Croatia, Church Books, 1516–1994 → Roman Catholic → Otočac →*
**Church Census (Stanje duša) 1710–1846**, sharing one film with Marriages
1859–1872 and Deaths 1780–1836 and 1859–1872.

The film target reads:

    ŽUPA: OTOČAC · HRVATSKA — CROATIA · MATIČNA KNJIGA
    STATUS ANIMARUM 1710 – 1846 · KNJ. 1
    Microfilmed at Hrvatski državni arhiv, 2 Feb 1998

**384 images.** The census occupies roughly images 9–120; a marriage register
begins around image 124 and prose death entries run to the end. Frames carry a
printed archival page number: **HDR = image + 243** (image 30 = 273, image 70 =
313, image 110 = 353), fixed at three points.

## Why it is the right instrument

A *status animarum* is not a register of events. It is a standing list of
**households**, and its columns are exactly the ones question 4 needs:

    Pagus            the village — written vertically down the left margin
    Domus            the HOUSE NUMBER
    Nomina Familiæ   every member, with the relationship spelled out:
                       "Joannes Jurich" · "Matthæus filius detto"
                       "Anna uxor Eliæ" · "Maria filia Antonii"
    Dies/Mensis/Annus  a birth DATE for each person
    Confirmatio, Confessio / Communio   year-by-year ticks
    marginalia       "nupsit" · "adoptata ex 35 Dubravo" · "circiter 11 annos"

Question 4 asks whether Casparus Žubrinić (b. 14 Jan 1767) and Toma (b. 1768),
born a year apart and both placed at **Šumećica**, are one family. A baptism
register would give two fathers' names. **This book would give the house.** For a
zadruga question that is the better document, and it covers the right years.

## What is NOT true of it

**It is not in FamilySearch's full-text index.** Tested directly:

    GET /service/search/fulltext/search/groupNumber?ids=2121770   ->  {"ids": []}

So there is no search. It has to be read by eye.

**The village margin is not reliable for navigation.** The *Pagus* is written
sideways in the gutter, and on a good page it reads cleanly — *Novoselia* on
image 50 — but on many pages it disappears into the shadow of the binding where
the book was photographed open. Villages read off a coarse scan so far, with
varying confidence: Ulicsani, Novoselia, Sinac(?), Kuterevo Selo(?). **Not one of
them is certain enough to publish**, and Šumećica has not yet been seen.

## So what the job actually is

About **110 image-openings**, read one at a time, looking at the *Nomina
Familiæ* column for Žubrinić and at the *Pagus* margin for Šumećica. There is no
index at the front of the book and no shortcut through it. It is a sitting, not a
lookup.

**That is still a large improvement on where question 4 stood this morning**,
which was: the document that would answer it does not exist in any accessible
collection. It does exist. It is 384 images away and it has house numbers in it.

## Method notes for the next sitting

* **Scroll the thumbnail grid** rather than typing image numbers. Opening the
  grid and scrolling it three times mapped all 384 images in one go; the
  number box is slow and often does not take.
* **Drop a zoom level for overviews.** A full frame at level 13 is ~400 tiles;
  at level 10 it is 9. Survey at level 10, read at level 13.
* **Rotate the margin crop 90°** to read the vertical *Pagus* text.
* **Give every tile load a timeout.** With the Browser pane hidden the tab is
  throttled and a stalled tile will otherwise hang the whole call.
