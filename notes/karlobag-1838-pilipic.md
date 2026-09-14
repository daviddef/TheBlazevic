# Karlobag, 18 September 1838 — ahnentafel 13, and two trades in a port town

Read 14 September 2026 from `photos/line/4502630-matia-birth.jpg`,
**4,500 × 3,470**. A dense Latin baptismal register, *Anno Domini 1838*, the
entry boxed by whoever uploaded it.

> *[Die 18ª Se]ptemb. — M. R. D. Cooperator **Carolus Perzevich** baptisavit
> **Mattheam** filiam legitimam **Cammeralis nauclerō Vincentii Pilipich** et
> **Mattheæ Uroda** conjugum hujus Civitatis. Patrini fuerunt **Antonius
> Kuchulian**, obequitator(?) …, et **Oliva filia dicti Josephi Pilipich
> mercatoris**.*

**Ahnentafel 13 confirmed** — Matia Pilipić, 18 September 1838, the tree's exact
date, daughter of **ahnentafel 26 and 27**. She is the *"Matia rodjena Filipić"*
of the Senj marriage of 1885.

## Two occupations the archive did not have

**Ahnentafel 26, Vicentius Pilipić: *Cammeralis nauclerus*** — a **chamber
shipmaster**, that is a master mariner in imperial service. Karlobag is a port,
and this is the first time anyone in this family is recorded working at sea
rather than on land.

**Ahnentafel 52, Josephus Pilipić: *mercator*** — a **merchant**. His daughter
**Oliva** stands godmother, which makes the baby's godmother her own paternal
aunt, named for her grandmother Oliva Maria Smojver.

Both fit the shape this archive had already noticed at Karlobag — a parish of
*Dominus* honorifics, a Giustiniani godfather, a Pro-Colonel, a Captain and a
Baron von Holstein. **The Pilipići are town people of some standing**, and that
is a different social world from the Krmpote *seljaci* and the Otočac
*Confiniarii* on the other branches.

*Not resolved:* the godfather Antonius Kuchulian's title, read as *obequitator*,
which would be a mounted courier or patrol. Left as read rather than translated
with confidence.

---

# And the scanned backlog is now clear

The coverage tool marked **12 people on the direct line as *scanned*** — an
image attached, nothing read out. All twelve are now accounted for:

    ahn 12, 14        the 1885 Senj marriage    read at full resolution, 13 Sept
    ahn 25            1809 baptism · 1835 marriage   read 14 Sept
    ahn 27            1810 Karlobag baptism     read 14 Sept
    ahn 42, 43        1835 Orešković baptism    already read — /frontier
    ahn 48, 49        1835 marriage · 1806 baptism   read 14 Sept
    ahn 50, 51        1835 marriage             read 14 Sept
    ahn 106           1754 Smojver baptism      already read — notes 10 Sept
    ahn 214           1779 Bacchi baptism       already read — notes 10 Sept
    ahn 13            1838 Karlobag baptism     read 14 Sept — this one

**Four of the twelve had already been read** and the tool did not know. So
*scanned* does not mean "unread"; it means **"has an image and no swept register
row"**, which is a different thing. The real backlog was eight, and it is now
none.

That is worth fixing rather than remembering: `tools/coverage.py` decides the
state from the data alone and has no way to learn that a page or a note has read
a document. Until it can, **the number on `/coverage` overstates how much is
unread.**
