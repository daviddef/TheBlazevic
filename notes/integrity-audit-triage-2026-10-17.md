# Triage of the cloud integrity audit of 13 October 2026 (18 impossible dates, 7 one-sided links, 2 parent ages, 64 duplicate pairs)

17 October 2026. The audit's own files (outside this repo: `~/Downloads/audit-briefs/integrity/blazevic.md` and `integrity-blazevic.csv`) were checked against the current `site/src/data/people.json` and the archive's own checks (`tools/consistency.py` → `impossible.json`, `tools/duplicates.py` → `duplicates.json`, the kin ratchet of 6). **Nothing in the tree was changed**: every one of these is a link or a date in the shared MyHeritage GEDCOM, which feeds all six family archives and is not edited here, and none can be settled without a document.

## Why the archive's own check did not see most of them

`tools/consistency.py` takes living and held-out people out of the tree before it compares anything. The Boraš cluster below involves the mother of the family, a person with a birth year and no death, who is treated as living, so every comparison that touched her was dropped. (She is not named here: a held-out person's dates never go into a committed file.) **Of the 20 date items, only 2 (Antonia Šestan, Gregorius Žubrinić) are in `impossible.json`.** The audit found what the archive's check was blind to by construction.

## The 20 date items, checked against the current data

| Item | What the data shows | Verdict |
|---|---|---|
| Anton (1860), Ivan (1882), Antonija (1884) Blažević — mother **Tereza Pećanić** «died 1850» | The tree gives her a marriage in 1858 and children to 1884. | **Already corrected on her page** («Corrected against the register»): alive 1884 (Krmpote entry 66), dead by 26 July 1907 (Toma's death entry). The audit counts the tree's wrong date, which the page already withdraws. |
| The mother of the Boraš children born **1888–1907** (Draga 1891, Budimir 1894, Olga 1902, Kreso 1906, Zdenka 1907, Slava 1911 …), a woman the archive holds out as living because the tree gives her a birth year and no death | The birth date the tree gives her is **the same day and place as her youngest daughter's** (Zdenka Boraš), copied to the mother. A woman born that year cannot have a daughter in 1888. | **A copying error in the tree**; her real birth year is unknown (before about 1870). Accounts for 6 of the 18 items. |
| **Blazenka? Boras**, b. 1930, d. 2017, child of Joannes Ivan Boras (b. 1855, d. 1926) | Joannes Ivan was 75 at her birth and had been dead four years. Zdenka Boraš has a daughter of the same given name, **born in the same year, 1930**. | Almost certainly **the same Blazenka, wrongly hung on her grandfather** (a duplicate with a false parent link). Accounts for 3 items. |
| **Slava Boraš** (b. 1911), parent 56 | Father Joannes Ivan, 56 at the birth. | **A false alarm**: the check cannot tell a father of 56 from a mother of 56. |
| **Ante Boraš** (b. 1931), mother **Ladislava (Lada) Bilubaric** b. 11 June 1922, d. 1942 | She would have been 9. | **A wrong birth year for the mother** (probably 1912, but that is a guess). |
| **Antonija Butković** (1880–1891), father **Marko Butković** (1872–1896) | Marko would have been 8. | **A wrong father or a wrong date**; nothing here says which. |
| **Nicolaus Kraljich** (b. 29 Sep 1807), mother «Anna», b. **1809** | His mother was born two years after him; her other children are 1812, 1817, 1820. | **Her birth year is wrong** (a baptism of 1809 attached to the wrong Anna, or a slip). |
| **Stephanus Žubrinić** (b. 1833), mother **Maria, d. 1831** | Maria's children run 1822–1828, then 1833, 1836, 1844 under the same father. | **Probably a second wife not in the tree**, or Maria's death year is wrong. |
| **Stephanus Žubrinić** (b. 1769), father **Nicolai** «BEF 1769» | A hedged birth date; the child is born 1769. | **Not an error**: «before 1769» is compatible. |
| **Gregorius Žubrinić**, lifespan 111 | Born 1785, died 1896. | Already on the archive's list as a namesake mix-up. |
| **Antonia Šestan** (dies 1846, born 1847) | | Already on the archive's list (record). |
| **Franjka Grandić** (b. 1894), father Jure b. 1836 | Father of 58. | **A false alarm** (a father of 58 is possible). |

Net: **6 real data problems that need a source or a decision** (the Boraš mother, Blazenka, Lada, Marko Butković, Anna Kraljich, Maria Žubrinić), **3 already corrected or known** (Tereza, Šestan, Gregorius Žubrinić), **3 false alarms** (Slava Boraš, Franjka Grandić, Stephanus Žubrinić 1769).

## The 7 one-sided links

* **Marcus Orešković** (b. 18 April 1809) is shown as the child of **Vitus Sekula and Maria**, and as brother of Maria and Susanna Sekula; **none of those four lists him back.** A child with a different surname from his parents' (Orešković, Sekula) and no return link looks like a link made on a guess or a foster or step relationship. Not resolvable without a baptism.
* **Thomas Žubrinić Kraljcich** (b. 15 August 1806) is shown as the child of **Matthaeus Žubrinić Xubrinich and Joanna** and brother of Maria; none lists him back. The same question: a Kraljić by-name on a Žubrinić.

Both are open questions for the register, not for an edit.

## The 64 duplicate pairs

**47 of the 64 pairs already involve people in a group on `duplicates.json`** (the archive's own «The Same Person, Twice» page), so most are known candidates. The other 17 are in the audit's «low» and «medium» tiers, mostly the many Ivan Blažević entries and the Prpić, Pavelić and Žubrinić pairs sharing a spouse or a parent. None has been merged; a merge is a research decision, never made on a name alone.

## What would settle them

* **The Boraš cluster** needs a family source: the birth of Zdenka, a baptism or marriage of Joannes Ivan Boras and his wife, and the 1930 birth of Blazenka. The Senj register 1878–94 births index holds some of these children (the index runs only to 1894).
* **Kraljich and Žubrinić** items need the Senj or Karlobag baptisms of 1806–1844; the Senj baptism index (`sources/senj-baptism-index2.tsv`) has no Žubrinić/Xubrinich births in the 1830s and 1840s, so these families were baptised in a book not indexed.
* **Fixes belong at the source** (the MyHeritage tree or the shared GEDCOM), not in this archive's data, or as an explicit correction entry once a document is read.
