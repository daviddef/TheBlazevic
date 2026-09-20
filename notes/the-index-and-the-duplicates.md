# What one register entry says about two tree records

*Work list row 40, 20 September 2026. The first use of the baptism index on the
duplicate groups, which have been waiting on a register since the row was
written.*

---

## The test

A live duplicate group is **two tree records that may be one person**. The
register settles it in one question: **is there one baptism entry, or two?**

Four groups fall inside the Otočac index's window of 1834–1858. Two of them
answer.

## Andreas Žubrinić, 1844 — one entry, and one of the two records is a fragment

| | Born | Place | Parents |
|---|---|---|---|
| `andreas-zubrinic` | **13 NOV 1844** | Otočac | Michael Žubrinić × Catharina |
| `andreas-zubrinic-xubrinich` | NOV 1844 | *(none)* | Michael Žubrinić Xubrinich × Catharina |

**The index holds exactly one baptism**: *13 November 1844, Otočac, «Michaël
Žubrinić × Catharina»* · `1:1:QKMK-S6M9`.

Same father's given name, same mother's given name, same month — and **one copy
has the day and the place while the other has neither**. That is the shape this
archive already recognises from **Danijel Kalanj** and from **pava / Paulina
Boras**: *one record entered twice, one copy complete and one partial.*

## Alexander Žubrinić, 1839 — and the register does not give the mother a surname

| | Born | Parents |
|---|---|---|
| `alexander-zubrinic` | 14 MAR 1839 | Michael Žubrinić × **Magdalena Oreskovic** |
| `alexander-zubrinic-2` | 14 MAR 1839 | Michael «Miko» Žubrinić × **Magdalena Mande Draženović** |

**The index holds exactly one baptism**: *14 March 1839, Otočac, «Michael
Žubrinić × **Magdalena**»* · `1:1:QKMK-STYY` — **and the mother has no
surname in it.**

This row has stood since 15 September as *«two boys, born the same day, to two
different Michaels»*, and `tools/duplicates.py` grew a function —
`parent_surnames()` — specifically so that *Orešković* and *Draženović* would
keep them apart.

**But those two surnames are not in the register.** The entry names the mother
**Magdalena** and stops. Whatever supplied *Orešković* to one record and
*Draženović* to the other, it was not this baptism.

**So the discriminator is doing its job on data that is not evidence.** That
does not make them one boy — it means the reason given for their being two does
not come from a document, and the archive should stop repeating it as though it
did.

## What this does not prove, and it matters

**The index is not complete.** The clearest measure of that is Karlobag, where
the entire **Luckinić** holding is **seven entries** for a family documented
across generations, and where ahnentafel 105's own 1727 baptism is absent
although her father's other children are there.

**So "the index holds one entry" is not "the register holds one entry."** It is
evidence and it points one way in both cases, and in the Alexander case it does
something stronger than point: **it removes the grounds for the opposite
conclusion.**

**Two of the four were not answered.** *Lucia Žubrinić 1835* returns nothing at
Otočac at all. *Magdalena Žubrinić 1847* returns one entry, to **Philippus ×
Maria Begović**, which is neither of the tree's pair.
