# The household was swept, and she was left out of it

**20 September 2026.** Twice today a household was worked out of the record index, the
siblings were written into `found.psv` with their arks — and **the ancestor the sweep was
run for got no row at all.**

## Ahnentafel 7

`found.psv` has carried three children of ahnentafel 14 × 15 since this morning, each
marked *«CANDIDATE younger brother/sister of ahnentafel 7»*: **Georgius 1868**,
**Joanna 1874**, **Josephus 1876**. A fourth, **Stephanus 1861**, is quoted in
`notes/the-month-is-wrong-and-the-day-is-right.md`.

**Antonija «Tonka» Perpić — ahnentafel 7, Hedviga's maternal grandmother — had a
gravestone and four derived credits, and no entry of her own.** Her baptism was in the
same result set as her brothers':

    Birth    12 May 1859
    Baptism  15 May 1859   Krivi Put
    Father   Joannis Perpić      Mother  Luciæ Perpić
    ark 1:1:XQM9-6NQ4

**It agrees with the tree to the day** — the tree has 12 May 1859 — and a three-day gap
to baptism is ordinary here. That matters beyond this row: two other index dates in this
family **disagree with the tree by a month**, and this one is a third data point saying
the index is not careless about this household in general.

**It gives ahnentafel 15 her first document of any kind.** She had none. It does **not**
give her a maiden name: the Krivi Put index writes every mother under the father's
surname, so «Luciæ Perpić» is a convention, not her name.

## And this morning, the same thing in reverse

**Ahnentafel 21**, Maria Catharina Orešković. Both her parents had been credited from
her own baptism — Otočac, 8 September 1835 — since the day it was read. **She had
nothing.**

## Why it happens

**It is not a typo, and it is worth naming because it will happen again.** A household
sweep turns up new people, and the new people are the interesting ones. **The ancestor the
query was written for reads as «done» because their name is already familiar** — they are
in the tree, they have a page, they have a grave. The eye goes to the strangers.

## The check, and why it is not a gate

`tools/siblingcheck.py`. Every `found.psv` row positioning somebody as a **brother,
sister or sibling of ahnentafel N** is a claim that N's household has been looked at. If N
has no **hand-written** baptism row of their own, the sweep stopped short. A derived
credit does not count — being named on a child's entry is not the same as your own.

**It reports and returns 0.** Four remain, and three of them cannot be fixed:

| | | |
|---|---|---|
| **ahn 5** | Tereza Žubrinić, b. 29 Nov 1867 Otočac | **newly out of reach — see below** |
| ahn 105 | Catta Luckinić, b. 1727 | not in the index under any name |
| ahn 110 | Michael Gerkacs, b. ~1762 | ten spellings and a surname-free query, nothing |
| ahn 213 | Antonia Pekass | born in a gap the index does not hold |

**A gate that failed the build on somebody else's transcription would have to be
silenced, and a silenced gate teaches people to silence gates.** So it is a worklist, not
a contract.

## Ahnentafel 5, and a boundary worth having

Tereza Žubrinić is **Hedviga's paternal grandmother**, born **29 November 1867 at
Otočac**, and she has only a gravestone. Otočac is indexed, so she looked like a lookup.

**She is not, and the reason is a hard edge that had not been measured.** A place-only
census of the Otočac index:

| births | entries |
|---|---|
| 1700–1799 | 0 |
| 1800–1829 | 1 (a stray at Dabar, 1816) |
| 1830–1834 | 83 |
| 1835–1837 | 200 |
| 1855–1859 | 200 |
| **1860–1864** | **0** |
| **1865–1869** | **0** |
| **1870–1874** | **0** |
| **1875–1879** | **0** |

**The Otočac index runs 1830–1858 and stops.** That is the filmed book — [row 27](/worklist/)'s
*Otočac baptisms 1834–1858* — and nothing after it. **Ahnentafel 5 is outside both the
index and the film**, which puts her with the post-1894 Senj cases: reachable only
through the parish office, not through anything this archive holds.

**Her father's household is well covered and she falls off the end of it.** That is a
better answer than «not found».
