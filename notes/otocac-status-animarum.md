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
* **Rotate the margin crop +90°** to read the vertical *Pagus* text — the village
  is written **bottom-to-top**, so −90° renders it upside down and it reads as
  noise. This cost the first sitting the whole village map; see 14 September
  below.
* **Give every tile load a timeout.** With the Browser pane hidden the tab is
  throttled and a stalled tile will otherwise hang the whole call.

---

# Same film, second item: Otočac marriages 1859–1872

Read 13 September 2026 while the film was open.

The marriage register occupies roughly **images 129–147** (image 152 is the next
film target). Latin, ruled, headed *Matricula Copulatorum Rkathol. Parochiae
Otočac Anno Domini …*. Fixed points: **pag. 10 = 1862 = image 136**,
**pag. 18 = 1865 = image 140**. About 1.3 openings per year.

## Its columns — and the one it does NOT have

    Annus Mensis et dies Copulationis
    Sponsi et Sponsae:  Nomen Cognomen Conditio
                        Locus — Originis / Domicilii, with HOUSE NUMBER
                        Ritus · Aetas · Caelebs aut viduus
    Testium Nomen Cognomen Religio Status et Conditio
    Copulantis Nomen Cognomen et officium
    Observationes

**There is no parents column.** This matters for planning: the Otočac marriage
register cannot name anybody's father. It gives an **age** and a **house
number**, which identify a man but do not push a line upward. Anyone hoping this
book would break the Žubrinić wall should stop hoping — the *status animarum*
above is still the instrument for that.

## One entry read in full — and deliberately not claimed

**Image 132, entry 11. Anno 1859, die 25 Septembris.**

    Groom    Nicolaus ŽUBRINIĆ, "vicedecu…" — read as vicedecurio,
             a Military Frontier rank. Surname underlined by the scribe.
             Prozor · Catholica · aetas 24 · caelebs
    Bride    Anna DUJMOVIĆ, rustica
             Prozor · aetas 18
    Witnesses  Lucas Žubrinić et Thomas Dujmović, catholici rustici
               (a Casparus appears in the next column; not resolved)

**Aged 24 in September 1859 gives a birth between about October 1834 and
September 1835.** The archive's **ahnentafel 10 is a Nicolaus Žubrinić born
1834**. That is a good fit and it is *not* enough.

**Why this is not being published as ahnentafel 10's marriage.** The tree gives
ahn 10's wife as **Ana "Shambul" Marić**; this bride is **Anna Dujmović**. Either
the tree is wrong, or there were two wives, or — most likely on present evidence
— **this is a different Nicolaus Žubrinić**. The surname is thick on the ground
in this parish: a *Lucas* Žubrinić stands witness at this very entry. This
archive has already once announced a direct ancestor as a duplicate on exactly
this kind of name-plus-date coincidence, and the rule that came out of it applies
here: a matching given name and a matching birth year are not an identification.

What would settle it: **Tereza Žubrinić's baptism**, 29 November 1867 at Otočac,
which would name her mother. It is **not reachable** — Otočac baptisms on
FamilySearch run 1834–1858 only, and stop nine years short.

## Holdings checked the same day, for the record

    Otočac            Births 1834-1846, 1846-1858 · Deaths 1834-1858,
                      1780-1836, 1859-1872 · Marriages 1859-1872
                      · Church Census (Stanje duša) 1710-1846
    Senj              Births 1734-1894 · Deaths 1820-1858, 1859-1907
                      · Marriages 1734-1858, 1859-1920
    Krmpote-Vodice    Births 1815-1896 ONLY — no marriages, no deaths
    Brinje            Births 1888-1900 · Marriages 1888-1899 · Deaths 1888-1899

**Krmpote has no marriage register at all**, so Juraj Blažević's marriage to
Tereza Žubrinić — one of the two documents question 1b asks for — cannot be
found there. But **Krmpote births run to 1896**, and Juraj, who has *no birth
date at all* in the tree and whose children start in 1892, would fall inside
that. **His own baptism is the reachable target, and it would name his father.**
That is the next thing to do.

---

# Two corrections to the above, 14 September 2026

## The 1859 marriage is now *less* likely to be ahnentafel 10's

The Otočac marriage of **25 September 1859** gave the groom's age as **24**.
Ahnentafel 10's baptism has since been read — it was already on disk, at 4,500
pixels, in `photos/line/4502600-nicolaus-zubrinic-birth.jpg`:

> **1834, Januarii die 24, Ottocsii** — *Nicolaus, filius legitimus,
> Catholicus* — **Confiniarius, ex pago Shumechicza N° 24** — **Michaël
> Xubrinich** et **Maria uxor ejus nata Oreskovich**, Catholici.
> Godparents: *Petrus filius Francisci Xubrinich, Wigiliarum Magister
> pensionatus*, and *Maria uxor Joannis Xubrinich, Sylvarum Custos in
> Shumechicza.*

Born **24 January 1834**, he is **25** in September 1859, not 24. A year's
slack in a register age is ordinary and this does not disprove anything — but it
fails to confirm, and it is one more reason the 1859 entry stays unclaimed.

## The census target is now two house numbers, not a village

This matters more. The baptism fixes the family at **Šumećica N° 24**, and the
tree puts Toma Žubrinić (b. 1768) at **Šumećica 2**.

So the sitting at the *Status Animarum* is no longer "find Šumećica and read
it". It is:

    find Šumećica in the Pagus margin
    then find DOMUS 2 and DOMUS 24

and the book has a *Domus* column. Two numbers in one village, in a book that
lists households by number — that is a far smaller job than the one described
above, and it is the whole of question 4.

---

# Second sitting, 14 September 2026 — method gains, no answer yet

**Šumećica was not found.** What was gained:

* **A contrast filter makes the margin readable.** `__cell` now takes a canvas
  `filter` string; `contrast(2.4) brightness(1.5)` lifts the *Pagus* out of the
  binding shadow that defeated the first sitting. Overdo it — 2.6 with a tight
  crop — and the page blows to pure black and white.
* **Villages read so far**, with varying confidence:
  `#14, #22 Otočac` · `#42 Kompolje` · `#48 Novoselia` · `#64 Prozor(?)`.
  Prozor matters — it is a Žubrinić village in this archive's own gazetteer.
* **The surname is not in the Nomina column.** Image 64 reads
  *"Wolfgangus fil: defti Gregorii"*, *"Michael fil: Pauli"*,
  *"Bernardus filius Wolfgangi"* — given name and patronymic only. The family
  name sits in the margin with the *Pagus*, once per household. **So the book
  cannot be searched by surname down the wide column**, which was the plan.

**The honest position:** this is still a page-by-page read of about 110
openings, and two sittings have not cracked it. The target is now precise —
**Šumećica, Domus 2 and Domus 24** — and the tooling is better, but it needs a
dedicated run rather than the tail of a session.


---

# The sitting, 14 September 2026 — the book is navigable after all

Opened to read **Domus 2 and Domus 24 at Šumećica**, the reading that would say
whether ahnentafel 10 stayed in his father's house or moved.
**That question is not answered. What came out instead is the map of the book**,
which is worth more than one household, because it turns a 110-opening sweep
into a five-opening one.

## The film, written down for the first time

    Catalog     koha:837578 — "Matična knjiga, 1710-1872"
                Hrvatski državni arhiv u Zagrebu ·
                Rimokatolička crkva, Župa Otočac
    Film        2121770 · DGS 005498269 · 384 images
    Contents    Status animarum 1710-1846 · Vjenčani 1859-1872 ·
                Umrli 1780-1836, 1859-1872
    Viewer      /search/film/005498269

Two earlier sittings used this film without recording how to get back to it.
**The catalog search that finds it is `q.keywords`** — `q.text`, `q.anyPlace`
and `q.placeString` are all rejected by the catalog service.

## Still not full-text indexed

    GET /service/search/fulltext/search/groupNumber?ids=5498269   ->  {"ids": []}

Re-tested today against all three of `5498269`, `2121770`, `005498269`.
**Unchanged since 13 September. There is no search. It is read by eye.**

## The margin IS readable — the earlier sitting rotated it the wrong way

The last sitting recorded the *Pagus* margin as unreliable, lost in the binding
shadow. **It is not.** The fault was the rotation: the village is written
**bottom-to-top** in the gutter, so a −90° rotation renders it upside down and
it reads as noise. Rotate **+90°** and it is plain.

    crop   x 0.06 - 0.33,  y 0.13 - 0.98      (the left-hand page)
    zoom   one level down from full
    draw   translate(stripHeight, 0); rotate(+PI/2)
    filter contrast(165%) brightness(108%) grayscale(1)

Four openings stack inside one 790-wide sheet. The village name reads at a
glance.

## The village map of the census

| image | *Pagus* |
|---|---|
| 10, 15, 20 | **Ottosaz** — Otočac town |
| 25 | **Luka** |
| 30, 40, 45 | **Dubrava**, under the district heading **Biskupljak** |
| 35, 50, 55 | **Novoselia** |
| 60, 65, 70 | **Lieška** |
| 75 | not resolved |
| 80 | **Kostelievo Selo** |
| 85, 90 | **Obilje** |
| 95, 100, 101 | **Beljue** |
| **102 – 106** | **Shumechicza** |
| 107 | **Luka** again |
| 108, 109 | ***Extinctæ*** — a section of households that had died out |

**Šumećica is five openings. That is the whole village in this book**, and it is
the whole of the remaining job.

## The columns, corrected and complete

    Pagus · Pagus · N° Domus · Nomina Familiæ · Dies · Mensis · Annus
    · Ætas · Conjugium · Confirmatio · Confessio / Communio

Two *Pagus* columns, not one: the outer carries a district (*Biskupljak*), the
inner the village. **The N° Domus column sits at x ≈ 0.19 – 0.23**, immediately
right of the margin — the earlier estimate of 0.16 lands on the *Pagus*.

## What was read at the page

**Image 102 · Domus 9 · Josephus Dašović.** Georgius · Petrus filius Josephi,
27 June 1818 · Michael, 4 December 1827 · Thomas, 29 July 1831 · Josephus filius
Petri, 13 March 1846 · Maria uxor Josephi · **Anna uxor Petri nata Žunić** ·
Maria filia Petri · Joanna filia Petri.

**Image 102, lower · Nicolaus Štabinčić**, 24 November 1798, with *Michael
filius dictus Georgij*, 2 May 1802.

**Image 103 · Domus 4 · Mattheus Orehović.** Joannes · Franciscus filius dicti ·
Lucas · Petrus filius dicti · Matthæus Francisci · Matthias · Joannes filius
Matthæi · **Martha uxor Georgii nata Orehović** · Magdalena · Catharina ·
Stephana filia Francisci · Margaretha · Maria filia Georgii · Martha uxor
Francisci.

**Images 104, 105, 106** were read at survey resolution but their *Domus* digits
are not pinned and are not being written down. Heads glimpsed include a
*Valentinus*, an *Antonius*, a *Josephus Kovač*(?) and a *Franciscus
Renović*(?), with a *Rosalia … Thomæ nata Stulac* and a *Mandalena uxor
Michaelis … Dubrava* among the women.

**The Domus numbers are not in order.** Image 102 opens at **9**, image 103 at
**4**. So the book cannot be walked to a house number; every opening of the five
has to be read.

## The negative, stated carefully

**No Žubrinić household has appeared at Šumećica in the three openings read so
far, and neither Domus 2 nor Domus 24 has been seen.**

**This is not yet a finding.** Two of the five openings are unread, and a
household can run across an opening. But it is worth flagging, because if it
holds it is strange: this census carries births to **1846**, and ahnentafel 20
**Michaël Žubrinić is at «ex pago Shumechicza N° 24» in January 1834**, read off
his son's baptism. A man in the village in 1834 should be in a book current to
1846. Either he is on 104–106, or the Žubrinići sit somewhere else in this
volume — the *Extinctæ* section at 108–109 is the obvious second place to look.

## Where it stopped

FamilySearch refused the session. Image 102's own ark — fetched successfully
minutes earlier — returned **403**, and so did image 30's, still 403 after forty
seconds. **That is the block, not the blip**, by the test in
`tools/familysearch.md`, and the rule is to stop for the day.

## The next sitting is short

    images 104, 105, 106     read every N° Domus and every household head
    images 108, 109          the Extinctæ section, for Žubrinić
    then                     Domus 2 and Domus 24, whichever opening holds them

Three openings, then two. **Half an hour's work against a book that was written
off as a hundred-opening sweep this morning.**


---

# The census answered — and the answer is that it cannot answer

Read out the same day, once FamilySearch let the session back in.
**All five Šumećica openings are now read, and so is everything after them.**

## Šumećica in this book, household by household

| image | *N° Domus* | head |
|---|---|---|
| 102 | **9** | **Josephus Dašović** — Georgius · Petrus, 27 June 1818 · Michael, 4 Dec 1827 · Thomas, 29 July 1831 · Josephus *filius Petri*, 13 March 1846 · Maria *uxor Josephi* · Anna *uxor Petri nata Žunić* · Maria and Joanna *filiæ Petri* |
| 102 | **10** | **Nicolaus Štabinčić**, 24 Nov 1798, with *Michael filius dictus Georgij*, 2 May 1802 |
| 103 | **4** | **Mattheus Orehović** — fourteen people, with *Martha uxor Georgii nata Orehović* |
| 104 | — | continuation of Domus 4; the whole left page is women, no new number |
| 105 | ~**13** | a **Paulus** household — Magdalena, Catharina, Barbara, Helena, Maria, with *Rosalia … Thomæ nata Stulac* and *Mandalena uxor Michaelis … Dubrava* |
| 105 | ~**14** | a household of **Andreas · Stephanus · Elias · Petrus · Matthæus**, births 1806–1830 |
| 106 | — | **Valentinus Janežić** and **Antonius Ollar**; then **Josephus Kovačić**; then **Vincentia Orehovački** with *Francisca uxor dicti* |

**Seven or eight households. Dašović, Štabinčić, Orehović, Janežić, Ollar,
Kovačić, Orehovački.**

## The finding, and it is a negative

**There is no Žubrinić household at Šumećica in this book. There is no Domus 2
and there is no Domus 24.**

That is not a gap in the reading. Every opening of the block was read; the
*Extinctæ* section at 108–109 was read (it is one opening, photographed twice —
*Joannes Grgurin*, *Stephanus filius dicti*, and the twins *Marcus et Josephus
Georgii dicti Gemelli*); image 110 is a different village; **111 returns to
Novoselia**; and **the ruled census stops about image 112.** Images 113–119 are
later additions in another hand with **no *Pagus* column at all**, and 121
onward is blank until the marriage register.

## What that means, said plainly

The Žubrinići were demonstrably at Šumećica — **house 24 in January 1834**, on
ahnentafel 10's own baptism, and **house 2 in 1856 and 1858**, read at the page
this morning. **They are not in the parish's own household census.** The likeliest
reading is that **the ruled Šumećica block was written once, early, and never
re-made** — its households carry births into the 1840s because members were
added to existing families, not because new families were entered.

**So this book is not the instrument for question 4, and that is now known
rather than assumed.** Two sittings have been spent on it. It gave the village
map, the Frontier households of half a dozen other surnames, and a clean
negative. It will not give the Žubrinić house.

## The instrument that will

**The Otočac baptism registers, 1834–1846 and 1846–1858 — and they are indexed.**

Every baptism in those books writes the household into the *Conditio* column in
the form ***«Rusticus / Confiniarius e Šumećica N° X»***. The index gives
**ninety-three Žubrinić baptisms at Otočac between 1846 and 1860**, with both
parents named. Read the *Conditio* cell of each Šumećica one and the Žubrinić
households of the village rebuild themselves **by house number**, from a
register, for the whole span 1834–1858.

That is a better instrument than the census, it is searchable, and nobody has
opened it for this purpose. **It is the next sitting.**
