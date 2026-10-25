# Triage of the cloud integrity audit of 13 October 2026 (18 impossible dates, 7 one-sided links, 2 parent ages, 64 duplicate pairs)

17 October 2026 (corrected the same day). The audit's own files (outside this repo: `~/Projects/Family Projects/_from Downloads/audit-briefs/integrity/blazevic.md` and `integrity-blazevic.csv`) were checked against the current `site/src/data/people.json` and the archive's own records: `tools/consistency.py` → `impossible.json` (published at /impossible/), the hand-written `corrections.json`, and `tools/duplicates.py` → `duplicates.json`. **Nothing in the tree was changed**: every item is a link or a date in the shared MyHeritage GEDCOM, which feeds all six family archives and is not edited here.

**A correction to this note's first version.** It said the archive's own check missed the Boraš cluster because the mother is held out as living. That was wrong: she was born in 1907, which is not living by the 80-year rule, and the check did not drop her. The audit's items are keyed by the child's page; the archive's check is keyed by the parent's. Matching on the parent, **every one of the audit's date findings except one is already on /impossible/**, and the Boraš ones are already explained in `corrections.json`.

## The 20 date and age items against what the archive already holds

| Audit item (child → parent) | What /impossible/ and the corrections hold | Verdict |
|---|---|---|
| Anton, Ivan, Antonija Blažević → Tereza Pećanić «died 1850» | On /impossible/ (hedged) and **corrected on her page**: alive 1884, dead by 26 July 1907. | Known, corrected. |
| Boraš children born 1888–1907 → the wife Vladimira, «born 12 December 1907» (6 items) | On /impossible/ (generation); `corrections.json` says it is **one wrong link** and that her birth date is **copied from her daughter Zdenka's** (the same day). | Known and explained; needs a family source to repair. |
| Blazenka? Boraš → Joannes Ivan Boraš (b. 1855, d. 1926; «75 at her birth, four years dead») | On /impossible/ (record). | Known. Probably a granddaughter hung on her grandfather; unproved. |
| Slava Boraš → Joannes Ivan, 56 | The check lists only the mother-side; a father of 56 is possible. | False alarm. |
| Ante Boraš → Ladislava (Lada) Bilubaric, b. 1922 | On /impossible/ (generation, age 9). | Known; the mother's birth year is wrong (probably 1912, unproved). |
| Antonija Butković → Marko Butković (b. 1872, she b. 1880) | On /impossible/ (age 8). | Known; wrong father or wrong date. |
| Nicolaus Kraljich (b. 1807) → mother Anna «b. 1809» | On /impossible/ (age 3 against her child of 1812). | Known; Anna's birth year is wrong. |
| Stephanus Žubrinić (b. 1833) → mother Maria, d. 1831 | On /impossible/ (record). | Known; probably a second wife not in the tree: the Otočac index has a Michael Žubrinić with a wife **Catharina** and children with the same given names ([note](zubrinic-michael-miko-second-wife-index.md)); not proved. |
| Stephanus Žubrinić (b. 1769) → Nicolai «BEF 1769» | On /impossible/ (hedged). | Not an error: «before 1769» is compatible. |
| Gregorius Žubrinić, lifespan 111 | On /impossible/ (namesake). | Known. |
| Antonia Šestan, died 1846 before born 1847 | On /impossible/ (record). | Known. |
| Franjka Grandić → Jure Grandić (b. 1836, she b. 1894) | Not listed. | A false alarm (a father of 58). |

**Net: the audit found nothing the archive's own check had not already found, apart from two advisory father-age alarms that are not errors.** The kin ratchet stays at 6.

## The 7 one-sided links

* **Marcus Orešković** (b. 18 April 1809) is shown as the child of **Vitus Sekula and Maria**, and as brother of Maria and Susanna Sekula; **none of those four lists him back.** A child whose surname differs from his parents' and with no return link looks like a guess, a foster or a step relationship. Not resolvable without a baptism.
* **Thomas Žubrinić Kraljcich** (b. 15 August 1806) is shown as the child of **Matthaeus Žubrinić Xubrinich and Joanna** and brother of Maria; none lists him back. The same question: a Kraljić by-name on a Žubrinić.

Both need a baptism, not an edit.

## The 64 duplicate pairs

**47 of the 64 pairs already involve people in a group on `duplicates.json`** (the archive's own «The Same Person, Twice» page). The other 17 are in the audit's «low» and «medium» tiers, mostly the many Ivan Blažević entries and the Prpić, Pavelić and Žubrinić pairs that share a spouse or a parent. None has been merged; a merge is a research decision, never made on a name alone.

## What would settle them

* The Boraš cluster: a family source for Joannes Ivan Boraš's real wife, the birth of Zdenka, and the 1930 Blazenka.
* The Kraljich and Žubrinić items: the Senj or Karlobag baptisms of 1806–1844 (the Senj baptism index `sources/senj-baptism-index2.tsv` has no Žubrinić/Xubrinich births in the 1830s–40s, so they were baptised in a book that is not indexed).
* Fixes belong at the source (the MyHeritage tree or the shared GEDCOM), or as an explicit correction entry once a document is read.
