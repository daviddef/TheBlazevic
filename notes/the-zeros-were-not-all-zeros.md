# The zeros were not all zeros

**20 September 2026.** `sources/familysearch/indexed.psv` is the table every register
row on the work list plans against: an indexed book is a search box, an unindexed one is
a sitting. Seven parishes in it said **NOTHING**. Three of the seven were wrong, and the
reason they were wrong is the same fault that hid ahnentafel 52 for three sittings.

## The fault

**Every zero in that file was produced by naming a surname.** The file says so itself —
«NOTHING, under Antić, Papić, Jelličić and Lončarić», «under Blažević and Tomljanović»,
«under Car and Antić». Two surnames per parish, nothing came back, zero recorded.

Hours earlier the same day, ahnentafel 52's baptism turned up at Karlobag filed under
**«Piberich»** — a surname that occurs exactly once in the parish and is one clerk's
reading of one hand. **If a surname can hide a person, it can hide a parish.**

## The re-test

A probe that names **no surname at all**: `q.anyPlace` plus a date window, counting only
the rows whose *returned* place string actually matches the parish.

**Controls first.** Karlobag and Senj return **100 of 100** in every window from 1700 to
1899. The instrument works.

| Parish | Was | Is |
|---|---|---|
| **Bribir** | NOTHING | **80+ indexed deaths** (1843–1855) and baptisms to 1876 |
| **Selce** | NOTHING | **five baptisms**, 1803–1844 |
| **Ledenice** | NOTHING | **four entries in two centuries** — 1748, 1749, 1845, 1888 |
| Brinje | NOTHING | zero confirmed |
| Sinac | NOTHING | zero confirmed |
| Gospić | NOTHING | zero confirmed |
| Smokvica | NOTHING | zero confirmed **for our Smokvica** |

**The Selce row indicts its own method.** It recorded a zero «under Antić» — and one of
the five entries the place-only probe returns is **«Margaritam ANTICH, 7 Nov 1844»**. The
surname it searched was sitting in the results it did not get.

## Two ways the new probe lies, both caught here rather than published

**It returns the wrong village.** *Bribir* is two places — ours in Primorsko-goranska and
one near Šibenik, two hundred kilometres away — and on a wide window the Šibenik one
outranks ours **593 to 7**. *Smokvica* returned ten burials at **Smokvica near Koper, in
Slovenia**. **Always read the place string back; never trust the query you sent.**

**It has false negatives of its own.** A place-only probe of **Krmpote returned zero in
every window** — and this archive found an indexed Krmpote-Vodice baptism of 1895 by
surname earlier the same day. The Krmpote row stands. **Neither probe is authoritative
alone**, and a zero from either means «not found by this instrument», not «not there».

## What came out of it, and what did not

**Ledenice gave a date to somebody already in the tree.** «Marija Milka, 16 May 1888,
Luka Kalanj × Kata», ark `1:1:XQM9-8KKX`. `marija-milka-kalanj` carries the bare year
**1888** and a citation to the image; the index supplies the **day**. Filed `INDEX ONLY`.
The index calls her mother *Kata Kalanj* where the tree has *Kata Miletić* — the indexer
has given the mother the father's surname, which is a convention rather than a conflict.

**Selce did not give a sibling to ahnentafel 12, though it looked for a moment as if it
had.** «Margaritam Antich, 7 Nov 1844, father **Josephi Antich**» — and ahnentafel 24 is
Josephum Antić of Selce. **The mother is «Margaritæ» and ahnentafel 24's wife is Maria
Jelličić.** He died in 1850 and she outlived him to 1882, so there was no second
marriage. A different household. She is in `found.psv` to be ruled out, because the next
reader will meet her first.

**Bribir is a correction with no one to spend it on.** The archive has **no person at
Bribir** — the eighty indexed deaths are real and useless here. Recorded because the
table is shared with the sister archives, and it was telling all of them a false zero.

## What does not change

**The headline holds.** The indexing is a **Karlobag–Otočac–Senj** phenomenon: Hedviga's
mother's side is searchable and her father's side is not. Smokvica is still zero, Krmpote
before 1880 is still zero, and Ledenice's four entries in two hundred years are not a
register — **row 33 stays a film read in practice.**

What changes is that «unindexed» was too strong for three parishes, and **one of them,
Selce, holds ahnentafel 12, 24 and 25.**
