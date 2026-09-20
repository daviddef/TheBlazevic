# Searching the index by PARENTS rebuilds a household, and the by-name is the key

*Work list rows 24 and 54, 20 September 2026.*

---

## The query that changes what the index is for

Every earlier sitting searched this index **by person** — a surname, a given
name, a year. That finds an individual if you already know enough about them.

**Searching by PARENTS finds a household.**

    q.fatherGivenName=Michaele&q.fatherSurname=Gergacs
      &q.motherGivenName=Lucia&q.anyPlace=Karlobag

returns six children at once, and the archive had **one** of them.

## Ahnentafel 110 × 111 — Michael Gerkacs and Lucia Tomljanović

| | |
|---|---|
| Magdalena | **11 March 1787** |
| **Maria** | **August 1789** — **ahnentafel 55** |
| Magdalena | **January 1792** — *the second of that name* |
| Catharina | **25 November 1794** |
| Bartholomæus | **17 August 1797** |
| Mathias | **23 February 1801** |

**Ahnentafel 55's own baptism was not in this archive.** It held her marriage of
1807 and her death of 1834 and not the entry she was christened on. The index
gives the month without the day; the tree says **11 August 1789**, and the index
does not contradict it.

**And it names ahnentafel 111.** Lucia Tomljanović is one of the twenty-four
direct ancestors with no document of any kind — she is placed at *Montani
Stanište*, which is not a parish and never was. She is named here, in a
register, six times.

**The two Magdalenas** are either a necronym — the first child died and the name
was given again, which this archive has documented elsewhere — or the index
holding one child twice, which it demonstrably does: Caetano Bacchi's 1779
baptism carries two different arks.

## Ahnentafel 106 × 107 — and the by-name did exactly what row 54 predicted

Row 54 said: *«look for the by-name. Two of the four are already known under one
— Smojver vulgò Vukić — and the Karlobag indexes file households under the
nadimak.»*

**They do.** This couple's children are indexed under **both** names:

| Under **Vukich** | | Under **Smojver** | |
|---|---|---|---|
| Maria | 6 May 1776 | *(no given name)* | 23 February 1782 |
| Josephus Franciscus | August 1777 | Vincentia Lucia | 5 December 1788 |
| Anna Oliva | 25 September 1785 | | |

Plus **ahnentafel 53, Oliva Maria, 11 March 1781**, which this archive read off
the image in September — and whose entry is the proof that the two surnames are
one couple: *«ex Vincentio, et Oliva Smoyver, **vulgò Vukić**, Conjugibus»*.

**A searcher who queries only Smojver finds two of these five children.** The
house name is not a spelling variant to be folded away; it is a second index
key, and the register says so itself.

## What is recorded and what is not

The ten children are in `sources/found.psv` as people the tree does not have.
**Ahnentafel 55's baptism is in `readings.psv`, marked INDEX ONLY**, because
nobody has opened the page — and this same indexing has already been caught
today naming the wrong mother for ahnentafel 106 and giving Zvonimir Vukelić's
mother a surname the archive read differently off the film.

**The index finds the page. The page settles the fact.**

---

# Two more households, and two things the index disagrees with the tree about

## Ahnentafel 42 × 43 — Marcus Orešković and Lucia Sekula, Otočac

**This couple is indexed under both surnames too**, and the tree already knew:
it carries two of their children as *«Orešković Oreskovic **Sekula**»*. So
*«Marcus Sekula × Lucia»* and *«Marcus Oresković × Lucia Sekula»* are one
household, and a searcher who queries one surname finds half the children.

**Two children the tree does not have**: **Michael, 26 September 1841**, and
**Paulus, 29 June 1846**.

**Paulus is a twin.** *Petrus*, whom the tree does have, was baptised **the same
day to the same parents** — arks `QKMK-SQMV` and `QKMK-SQML`. This archive's
duplicate detector has a tier for *«same day, same parents»* and treats it as
near-conclusive evidence of one person entered twice. **Here it is two boys**,
and the reason to believe that is the reason the tier exists at all: the
discriminator is whether anything else separates them, and two different given
names on two different arks do.

**And the sexes are swapped.** The tree has *Francisca* in **1840** and
*Franciscus* in **1844**. The index has **Franciscus 5 March 1840** and
**Francisca 3 June 1844** — the same two years, the same parents, the opposite
sexes. One of the two is wrong and this archive does not know which.

## Ahnentafel 26 × 27 — Vicentius Pilipić and Matia Uroda, Karlobag

**Two children the tree does not have**: **Maria Catharina, 25 January 1834** —
four years before ahnentafel 13 — and **Georgius, 18 November 1841**. The
index also confirms *Josephus, 14 October 1835*, whom the tree carries as
*Joso*.

## And one household the index cannot reach

**Ahnentafel 40 × 41, Toma Žubrinić and Marija Findrić.** Their child
ahnentafel 20 was born in **1811** and the Otočac index begins at **1834**.
The query returns forty other Žubrinić households at Otočac and not theirs.
**That is coverage, not spelling**, and no amount of surname variation fixes it.
