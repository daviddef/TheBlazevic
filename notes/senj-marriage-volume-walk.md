# The Senj marriage and death volume (9RK1-W3P): every image read once, 13–14 October 2026

The volume is FamilySearch waypoint **9RK1-W3P**, roll 290 of the Archive of Croatia in Zagreb (project YU00001), **592 images**. It is not one book but a bundle of interleaved sequences, so the only complete method was every image, both pages. The control file is `sources/senj-walk-ledger.json` (one entry per image, every hit, what is still owed), driven by `tools/senjwalk.py`. **All 592 images have been read once; the strip pass (images 10–79) and the second passes (images 58–67, 139–151, 177–206, the abbreviated 1820–30 death lines, the Croatian 1849–51 lines, the Pilepich/Perpich pages 472–473 and 475, and 505R) were done on 14–15 October 2026. The volume is read as completely as these registers allow, and what is left is listed under «What is still owed»** — see «What is still owed».

## What is in the volume (a map, by image)

| images | what | notes |
|---|---|---|
| 1–9 | roll leader, title cards (item 1) | |
| 10–206 | **item 1 — marriages 1734–1819** (Latin prose, then numbered entries) | 10–79 read through a narrow window (strip pass owed); 139–151 (1790–94) and 177–206 (1805–19) small cursive |
| 207–208 | title card, item 2 | |
| 209–381 | **item 2 — marriages 1820–1858** | a bundle of interleaved sequences: the Cathedral parish, B.M.V., the military; Croatian entries 1849–51 |
| 382–525 | **item 3 — deaths 1820–1848** («Protocollum mortuorum») | arranged by the **initial of the surname**: a one-line «obiit …» entry for 1820–c.1830, then tabular pages (Anno, Nomen, Aetas, Morbus, Sacramenta, Locus sepulturae, Sepeliens, N°); A to Z, ending at 519L; 520–521 Z continues; 524–525 end of the item and the title card of item 4 |
| 526–588 | **item 4 — deaths 1849–1858** | chronological, with the entry numbers of each year: Croatian prose (1849–50, «dana … preminu …»), Latin from January 1851, each entry written out in full from February 1855 («obdormivit in Domino … filius legitimus [occupation of the father]»), the house number («sub Hao domali N») from February 1858; the cooperators Sladovich, Khreskovich, Lukovich, Verhovac, Bušić, Biankini |
| 589–592 | end of roll 290: END, the title card again, the film leader (**«NASTAVAK na filmu 291»** — it continues on roll 291), a resolution chart, END OF ROLL | |

The film continues on **roll 291**, which is not part of this volume.

## How it was read

One page per screenshot, at about page scale, then a crop of every hit at the same scale kept as a snapshot (the image in `site/public/snaps/`, a row in `sources/snapshots.psv`, a found person). Names were read as written («Perpich», «Krepotich», «Wukellich») and are recorded as the page spells them; where a looped hand makes a surname doubtful it is marked «read with a query» in the snapshot. A death entry names a person at the end of life with usually no parents; the found-person text says so and never guesses a link. Very common Senj surnames (Lončarić, Antić, Jurčić, Butković, Barac) are kept as page-scale **seen rows** (`tools/senjwalk_seen.py`), with no found person.

**The death register was read after the marriage register had been completed, in the order of the book**, initial by initial (B, K, O, P, S, T, V, Z carry most of the families), and the Croatian-and-Latin chronological register page by page. 272 readings, 321 people, 39 seen rows.

## What it holds for the families researched

By family, with every reading's date, image and snapshot. «m.» is a marriage entry, «d.» a death entry. None is joined to a line of this archive: the volume is a **place** (Senj) where these surnames lived and died, and no entry here names a parent of a person in the tree.

### Vukelić (44)

- 7 January 1764 m. — Tome Vukelić witness 1764 (image 71R; [snapshot](/snapshots/#senj-marriage-1764-01-andrea-deskovic-ursula-witness-tome-vukelic))
- December 1765 m. — Mihovil Vukelić groom 1765 (image ; [snapshot](/snapshots/#senj-marriage-1765-12-mihovil-vukelic-bride-widow-of-mikula-tomjenovic-magdalena))
- 18 June 1766 m. — Tome Vukelić witness 1766 (image 76L; [snapshot](/snapshots/#senj-marriage-1766-06-jurja-sayfon-maru-witness-tome-vukelic))
- 15 November 1766 m. — Ilija Vukelić of Sv Juraj groom 1766 (image 77L; [snapshot](/snapshots/#senj-marriage-1766-11-iliya-vukelic-of-sv-jurja-widow-vicenca))
- 10 May 1824 d. — Widow Vukelić aged 70 died Senj May 1824 (image 511R; [snapshot](/snapshots/#senj-death-1824-05-widow-vukelich))
- 12 August 1824 d. — Joannes Vukelić son of Petrus died Senj August 1824 (image 511R; [snapshot](/snapshots/#senj-death-1824-08-joannes-son-of-petrus-vukelich))
- 4 June 1825 d. — Petrus Vukelić aged 70 died Senj June 1825 (image 512L; [snapshot](/snapshots/#senj-death-1825-06-dominus-petrus-vukelich-aged-70))
- 5 February 1826 m. — Franciscus Thian groom of 1826 with a Vukelić bride of Sveti Juraj (image 347L; [snapshot](/snapshots/#senj-marriage-1826-02-franciscus-thian-maria-vukelich-of-st-georgen))
- 5 February 1826 m. — Maria Vukelić of Sveti Juraj bride of Franciscus Thian 1826 (image 347L; [snapshot](/snapshots/#senj-marriage-1826-02-franciscus-thian-maria-vukelich-of-st-georgen-bride))
- 26 July 1826 d. — Thomas Vukelić infant died Senj July 1826 (image 512L; [snapshot](/snapshots/#senj-death-1826-07-thomas-son-of-georgius-vukelich-aged-8-months))
- 10 January 1827 d. — Lucas Vukelić died Senj January 1827 (image 512L; [snapshot](/snapshots/#senj-death-1827-01-lucas-vukelich))
- 19 May 1828 d. — Juliana Vukelić infant died Senj May 1828 (image 512L; [snapshot](/snapshots/#senj-death-1828-05-juliana-daughter-of-dr-stephanus-vukelich))
- 22 June 1834 d. — Ursula Vukelić aged 12 died Senj June 1834 (image 513R; [snapshot](/snapshots/#senj-death-1834-06-ursula-daughter-of-laurentius-vukelich-aged-12))
- 9 January 1836 d. — Joannes Vukelić aged 77 died Senj January 1836 (image 513R; [snapshot](/snapshots/#senj-death-1836-01-joannes-vukelich-aged-77))
- 14 January 1836 d. — Maria Vukelić widow aged 70 died Senj January 1836 (image 513R; [snapshot](/snapshots/#senj-death-1836-01-maria-widow-vukelich-aged-70))
- 9 August 1836 d. — Lucas Vukelić aged 22 died Senj August 1836 (image 514L; [snapshot](/snapshots/#senj-death-1836-08-lucas-vukelich-of-st-georgius-aged-22))
- 26 August 1836 d. — Joannes Vukelić infant died Senj August 1836 (image 514L; [snapshot](/snapshots/#senj-death-1836-08-joannes-son-of-lucas-and-cecilia-vukelich-aged-5-days))
- January 1841 m. — Georgius Vukelić widower mariner of St Georgen groom of 1841 (image 362R; [snapshot](/snapshots/#senj-marriage-1841-01-georgius-vukelich-widower-of-st-georgen-hellena))
- 13 January 1844 d. — Josephus Gasparus Vukelić infant died Senj January 1844 (image 515R; [snapshot](/snapshots/#senj-death-1844-01-josephus-gasparus-vukelich-aged-8-days))
- 10 February 1844 d. — Anna Vukelić aged 34 died Senj February 1844 (image 515R; [snapshot](/snapshots/#senj-death-1844-02-anna-vukelich-aged-34))
- 22 June 1847 d. — Joannes Vukelić aged 67 died Senj June 1847 (image 516R; [snapshot](/snapshots/#senj-death-1847-06-joannes-vukellich-aged-67))
- 7 October 1847 d. — Rosalia Vukelić aged 18 died Senj October 1847 (image 516R; [snapshot](/snapshots/#senj-death-1847-10-rosalia-vukellich-aged-18))
- 19 February 1849 m. — Jure Vukelić sailor witness at Senj marriage of 1849 (image 329L; [snapshot](/snapshots/#senj-marriage-1849-02-josip-rubicic-widower-witness-jure-vukelic))
- 2 August 1849 d. — Kathe Vukelić aged 36 died Senj August 1849 (image 533L; [snapshot](/snapshots/#senj-death-1849-08-kathe-vukelic-aged-36))
- 6 October 1849 d. — Lovre Vukelić aged 77 died Senj October 1849 (image 534R; [snapshot](/snapshots/#senj-death-1849-10-lovre-vukellich-aged-77))
- 16 February 1850 d. — Maria Vukelić aged 8 died Senj February 1850 (image 536R; [snapshot](/snapshots/#senj-death-1850-02-maria-wukellich-aged-8))
- 20 December 1850 d. — Magdalena Vukelić infant died Senj December 1850 (image 547R; [snapshot](/snapshots/#senj-death-1850-12-magdalena-vukellic-aged-5-months))
- 25 May 1851 m. — Vitus Vukelić tailor groom of 1851 from Kosinj (image 363L; [snapshot](/snapshots/#senj-marriage-1851-05-vitus-vukellich-antonia-dvoich))
- 25 May 1851 m. — Antonia Dvoić bride of Vitus Vukelić 1851 (image 363L; [snapshot](/snapshots/#senj-marriage-1851-05-vitus-vukellich-antonia-dvoich-bride))
- 19 August 1851 m. — Joannes Vukelić of Gospić groom of 1851 (image 363R; [snapshot](/snapshots/#senj-marriage-1851-08-joannes-vukelich-of-gospic-francisca-tomjanovich))
- October 1851 d. — Anna Vukelić infant died Senj October 1851 (image 550R; [snapshot](/snapshots/#senj-death-1851-10-anna-vukellic-aged-1))
- 29 April 1852 m. — Blasius Rossi groom of 1852 at Senj whose mother was née Vukelić (image 331L; [snapshot](/snapshots/#senj-marriage-1852-04-blasius-rossi-mother-anna-nee-vukelic))
- 10 June 1852 d. — Joannes Vukelić theology student aged 26 died Senj June 1852 (image 553R; [snapshot](/snapshots/#senj-death-1852-06-joannes-wukelic-cleric-aged-26))
- 16 January 1853 d. — Antonius Vukelić customs watchman aged 32 died Senj January 1853 (image 555R; [snapshot](/snapshots/#senj-death-1853-01-antonius-vukellic-vigil-finantialis-aged-32))
- 30 May 1853 d. — Adolphus Vukelić infant died Senj May 1853 (image 557L; [snapshot](/snapshots/#senj-death-1853-05-adolphus-son-of-antonius-vukellic-aged-1))
- 4 January 1854 d. — Theresia Vukelić widow aged 72 died Senj January 1854 (image 559L; [snapshot](/snapshots/#senj-death-1854-01-theresia-widow-vukellic-aged-72))
- 5 April 1854 d. — Catharina Vukelić infant died Senj April 1854 (image 561L; [snapshot](/snapshots/#senj-death-1854-04-catharina-daughter-of-joannes-vukellic-aged-1))
- 27 May 1854 d. — Ursula Vukelić widow aged 75 died Senj May 1854 (image 561R; [snapshot](/snapshots/#senj-death-1854-05-ursula-widow-vukellic-aged-75))
- 18 September 1854 d. — Franciscus Vukelić aged 19 died Senj September 1854 (image 563L; [snapshot](/snapshots/#senj-death-1854-09-franciscus-vukelic-aged-19))
- 10 April 1856 d. — Carolus Vukelić aged 1 died Senj April 1856 (image 575L; [snapshot](/snapshots/#senj-death-1856-04-carolus-son-of-centurion-petrus-vukelic-aged-1y6m))
- 16 May 1856 d. — Leopoldina Vukelić aged 2 died Senj May 1856 (image 575L; [snapshot](/snapshots/#senj-death-1856-05-leopoldina-daughter-of-centurion-petrus-vukelic-aged-2))
- 15 January 1857 d. — Joanna Vukelić aged 2 died Senj January 1857 (image 578L; [snapshot](/snapshots/#senj-death-1857-01-joanna-daughter-of-joannes-vukelic-aged-2y6m))
- 13 April 1857 d. — Franciscus Vukelić aged 2 died Senj April 1857 (image 579L; [snapshot](/snapshots/#senj-death-1857-04-franciscus-son-of-matthaeus-vukelic-aged-2))
- 22 June 1857 d. — Fridericus Vukelić aged 5 died Senj June 1857 (image 581L; [snapshot](/snapshots/#senj-death-1857-06-fridericus-son-of-centurion-petrus-vukelic-aged-5))

### Babić (41)

- 29 April 1748 m. — Katarina Babić of Sv Juraj bride 1748 (image 45L; [snapshot](/snapshots/#senj-marriage-1748-04-jou-rokovic-of-lovran-katarina-daughter-of-matiya-babic))
- February 1766 m. — Mate Babić groom 1766 (image 75R; [snapshot](/snapshots/#senj-marriage-1766-02-matu-babic-katarina-daughter-of-jure-sablic))
- autumn 1814 m. — Georgius Babić groom 1814 (image 196R; [snapshot](/snapshots/#senj-marriage-1814-autumn-georgius-babic-citizen-of-sv-juraj-mathia-butkovic))
- June 1815 m. — Joanna Babić bride 1815 (image 198R; [snapshot](/snapshots/#senj-marriage-1815-06-franciscus-jurcic-joanna-babic))
- autumn 1815 m. — Franciscus Babić of Novigrad groom 1815 (image 199L; [snapshot](/snapshots/#senj-marriage-1815-autumn-franciscus-babic-of-novigrad-doima-babic))
- 23 October 1831 m. — Antonia Babić of Novigrad bride of 1831 (image 255L; [snapshot](/snapshots/#senj-marriage-1831-10-christophorus-gerzanich-antonia-babich-novigrad-bride))
- 23 January 1842 m. — Antonius Babić of Senj groom of 1842 (image 226L; [snapshot](/snapshots/#senj-marriage-1842-01-antonius-babich-maria-calanich))
- 6 February 1842 m. — Laurentius Babić of Senj groom of 1842 (image 226L; [snapshot](/snapshots/#senj-marriage-1842-02-laurentius-babich-anna-kuppar))
- 1847 m. — Franciscus Babić of Senj groom of 1847 (image 228R; [snapshot](/snapshots/#senj-marriage-1847-franciscus-babich-maria-bajsich))
- 1847 m. — Maria Bajsich bride of Babić 1847 (image 228R; [snapshot](/snapshots/#senj-marriage-1847-franciscus-babich-maria-bajsich-bride))
- 6 March 1848 m. — Stephanus Babić of Senj groom of 1848 (image 229L; [snapshot](/snapshots/#senj-marriage-1848-03-stephanus-babich-catharina-ostoman))
- 6 March 1848 m. — Catharina Ostoman bride of Babić 1848 (image 229L; [snapshot](/snapshots/#senj-marriage-1848-03-stephanus-babich-catharina-ostoman-bride))
- 28 November 1850 m. — Ante Babić bride of 1850 at Senj (image ; [snapshot](/snapshots/#senj-marriage-1850-11-croatian-entry-bride-ante-daughter-of-jure-babic))
- 7 July 1850 d. — Maria Babić aged 7 died Senj July 1850 (image 542L; [snapshot](/snapshots/#senj-death-1850-07-maria-babic-aged-7))
- 29 September 1850 d. — Michael Babić infant died Senj September 1850 (image 545R; [snapshot](/snapshots/#senj-death-1850-09-michael-babic-aged-7-days))
- 24 November 1850 d. — Anton Babić aged 3 died Senj November 1850 (image 547L; [snapshot](/snapshots/#senj-death-1850-11-anton-babic-aged-3))
- 13 July 1851 m. — Christophorus Babić mariner groom of 1851 with a bride of Ledenice (image 375R; [snapshot](/snapshots/#senj-marriage-1851-07-christophorus-babich-catharina-stillin-of-ledenice))
- 13 July 1851 m. — Catharina Stillin of Ledenice bride of Christophorus Babić 1851 (image 375R; [snapshot](/snapshots/#senj-marriage-1851-07-christophorus-babich-catharina-stillin-of-ledenice-bride))
- 1 March 1851 d. — Johannes Babić customs watchman aged 54 died Senj March 1851 (image 548L; [snapshot](/snapshots/#senj-death-1851-03-johannes-babic-vigil-finantialis-aged-54))
- 6 October 1851 d. — Stephanus Babić aged 30 died Senj October 1851 (image 550L; [snapshot](/snapshots/#senj-death-1851-10-stephanus-babic-aged-30))
- 21 November 1852 m. — Joannes Babić mariner groom of 1852 whose mother was née Jurčić (image 376L; [snapshot](/snapshots/#senj-marriage-1852-11-joannes-babic-mother-maria-nee-jurcic-jacoba-fabris))
- 21 November 1852 m. — Jacoba Fabris bride of Joannes Babić 1852 (image 376L; [snapshot](/snapshots/#senj-marriage-1852-11-joannes-babic-mother-maria-nee-jurcic-jacoba-fabris-bride))
- 5 May 1853 d. — Vincentius Babić aged 41 died Senj May 1853 (image 556R; [snapshot](/snapshots/#senj-death-1853-05-vincentius-babic-aged-41))
- 16 April 1854 d. — Vincentius Babić infant died Senj April 1854 (image 561R; [snapshot](/snapshots/#senj-death-1854-04-vincentius-son-of-martha-babic-aged-12-months))
- 31 January 1855 d. — Georgius Babić veteran aged 78 died Senj January 1855 (image 564L; [snapshot](/snapshots/#senj-death-1855-01-georgius-babic-aged-78))
- 20 July 1855 d. — Joannes Babić porter died Senj July 1855 (image 567R; [snapshot](/snapshots/#senj-death-1855-07-joannes-babic-bajulus))
- 31 July 1855 d. — Jacobus Babić aged 4 died Senj July 1855 (image 569L; [snapshot](/snapshots/#senj-death-1855-07-jacobus-son-of-georgius-babic-aged-4))
- 1 August 1855 d. — Antonius Babić aged 2 died Senj August 1855 (image 569R; [snapshot](/snapshots/#senj-death-1855-08-antonius-son-of-georgius-babic-aged-2))
- 23 August 1855 d. — Josepha Babić aged 10 died Senj August 1855 (image 570L; [snapshot](/snapshots/#senj-death-1855-08-josepha-daughter-of-laurentius-babic-aged-10))
- 27 August 1855 d. — Ursula Babić aged 3 died Senj August 1855 (image 570R; [snapshot](/snapshots/#senj-death-1855-08-ursula-daughter-of-franciscus-babic-aged-3))
- 27 August 1855 d. — Maria Babić aged 6 died Senj August 1855 (image 570R; [snapshot](/snapshots/#senj-death-1855-08-maria-daughter-of-franciscus-babic-aged-6))
- 28 August 1855 d. — Francisca Romana Babić aged 4 died Senj August 1855 (image 571L; [snapshot](/snapshots/#senj-death-1855-08-francisca-romana-daughter-of-franciscus-babic-aged-4))
- 29 August 1855 d. — Maria Babić aged 2 died Senj August 1855 (image 571L; [snapshot](/snapshots/#senj-death-1855-08-maria-daughter-of-franciscus-babic-aged-2))
- 20 July 1856 m. — Casparus Paulus Babić mariner groom of 1856 (image 358R; [snapshot](/snapshots/#senj-marriage-1856-07-casparus-paulus-babich-maria-of-bescanensis))
- 20 July 1856 m. — Maria of Bescan bride of Casparus Paulus Babić 1856 (image 358R; [snapshot](/snapshots/#senj-marriage-1856-07-casparus-paulus-babich-maria-of-bescanensis-bride))
- 29 June 1856 d. — Francisca Babić servant died Senj June 1856 (image 575R; [snapshot](/snapshots/#senj-death-1856-06-francisca-babic-servant))
- 14 August 1856 d. — Maria Babić aged 2 died Senj August 1856 (image 576R; [snapshot](/snapshots/#senj-death-1856-08-maria-daughter-of-gregorius-babic-aged-2y6m))
- 20 December 1856 d. — Theresia Babić aged 14 died Senj December 1856 (image 577R; [snapshot](/snapshots/#senj-death-1856-12-theresia-daughter-of-augustinus-babic-aged-14))
- 10 February 1857 m. — Catharina widow of Stephanus Babić bride of 1857 (image 260R; [snapshot](/snapshots/#senj-marriage-1857-02-antonius-gerbac-widower-catharina-widow-of-stephanus-babich-bride))
- 26 March 1857 d. — Maria Babić aged 5 died Senj March 1857 (image 579L; [snapshot](/snapshots/#senj-death-1857-03-maria-daughter-of-laurentius-babic-aged-5y6m))
- 30 May 1858 m. — Antonius Babić witness at Senj marriage of 1858 (image 283R; [snapshot](/snapshots/#senj-marriage-1858-05-martinus-kirn-witness-antonius-babich))

### Krmpotić (30)

- 13 October 1739 m. — Marko Tomičić of Krmpote (image 23L; [snapshot](/snapshots/#senj-marriage-1739-10-marko-tomicic-of-krmpote))
- 1765 m. — Pernich of Krmpote groom of 1765 (image 74L; [snapshot](/snapshots/#senj-marriage-1765-pernich-of-krmpote-widow-of-vid-sojat))
- August 1790 m. — Martha Filipović of Krmpote bride 1790 (image 141R; [snapshot](/snapshots/#senj-marriage-1790-08-georgius-tomljan-otocac-soldier-martha-filipovic-of-krmpote-bride))
- 23 January 1822 m. — Michael Krmpotić widower of Senj groom of 1822 (image 276R; [snapshot](/snapshots/#senj-marriage-1822-01-michael-krmpotich-widower-witness-franciscus-zubrinich))
- 23 January 1822 m. — Stanislava widow bride of Krmpotić 1822 (image 276R; [snapshot](/snapshots/#senj-marriage-1822-01-michael-krmpotich-widower-witness-franciscus-zubrinich-bride))
- 16 September 1824 d. — Marcus Krmpotić infant died Senj September 1824 (image 439L; [snapshot](/snapshots/#senj-death-1824-09-marcus-son-of-marcus-and-francisca-krmpotich-aged-1))
- 2 September 1825 d. — Maria Krmpotić daughter of Michael of St Salvator died Senj 1825 (image 439L; [snapshot](/snapshots/#senj-death-1825-09-maria-daughter-of-michael-krmpotich-of-st-salvator))
- 28 November 1828 m. — Simon Samarsia groom of 1828 with a Krmpotić bride (image ; [snapshot](/snapshots/#senj-marriage-1828-11-simon-samarsia-bride-mathia-krmpotich))
- 28 November 1828 m. — Mathia Krmpotić bride of Samarsia 1828 (image ; [snapshot](/snapshots/#senj-marriage-1828-11-simon-samarsia-bride-mathia-krmpotich-bride))
- 18 May 1830 m. — Michael Krmpotić widower of Senj groom of 1830 (image 277L; [snapshot](/snapshots/#senj-marriage-1830-05-michael-krmpotich-widower-54-antonia-tomlanovich-widow))
- 18 May 1830 m. — Antonia widow bride of Krmpotić 1830 (image 277L; [snapshot](/snapshots/#senj-marriage-1830-05-michael-krmpotich-widower-54-antonia-tomlanovich-widow-bride))
- 15 March 1831 d. — Nicolaus Krmpotić of St Salvator died Senj March 1831 (image 440R; [snapshot](/snapshots/#senj-death-1831-03-michael-krmpotich-aged-14-and-nicolaus-krmpotich-aged-48-of-st-salvator))
- 1832 m. — Franciscus Aloysius Kovačić widower groom of 1832 with Krmpotić witness (image 277R; [snapshot](/snapshots/#senj-marriage-1832-franciscus-aloysius-kovacich-widower-witness-krmpotich))
- 4 February 1833 m. — Petrus Tomaić soldier groom of 1833 with a Krmpotić bride of St Salvator (image 348R; [snapshot](/snapshots/#senj-marriage-1833-02-petrus-tomaich-soldier-helena-krmpotich-of-st-salvator))
- 4 February 1833 m. — Helena Krmpotić of St Salvator bride of Petrus Tomaić 1833 (image 348R; [snapshot](/snapshots/#senj-marriage-1833-02-petrus-tomaich-soldier-helena-krmpotich-of-st-salvator-bride))
- 24 June 1833 m. — Petrus Vukelić widower of Krasno groom of 1833 with a Krmpotić widow (image 360R; [snapshot](/snapshots/#senj-marriage-1833-06-petrus-vukelich-widower-of-krasno-martha-krmpotich-widow))
- 24 June 1833 m. — Martha Krmpotić widow bride of Petrus Vukelić 1833 (image 360R; [snapshot](/snapshots/#senj-marriage-1833-06-petrus-vukelich-widower-of-krasno-martha-krmpotich-widow-bride))
- 16 February 1834 d. — Anna Krmpotić born at St Salvator died Senj February 1834 (image 439L; [snapshot](/snapshots/#senj-death-1834-02-anna-krmpotich-born-at-st-salvator-aged-30))
- 16 February 1835 d. — Helena Krmpotić aged 90 died Senj February 1835 (image 443L; [snapshot](/snapshots/#senj-death-1835-02-helena-krmpotich-aged-90))
- 15 October 1838 d. — Paulus Butković watchman of Krmpote died Senj 1838 (image 389L; [snapshot](/snapshots/#senj-death-1838-10-paulus-butkovich-vigil-of-krmpote-aged-26))
- 28 December 1844 d. — Joanna Krmpotić aged 60 died Senj December 1844 (image 452R; [snapshot](/snapshots/#senj-death-1844-12-joanna-krmpotich-aged-60))
- 19 June 1853 m. — Franciscus Samarzia widower soldier groom of 1853 with a Krmpotić bride (image 366L; [snapshot](/snapshots/#senj-marriage-1853-06-franciscus-samarzia-widower-maria-krmpotich))
- 19 June 1853 m. — Maria Krmpotić bride of Franciscus Samarzia 1853 (image 366L; [snapshot](/snapshots/#senj-marriage-1853-06-franciscus-samarzia-widower-maria-krmpotich-bride))
- 6 March 1853 d. — Alexander Krmpotić newborn died Senj March 1853 (image 556L; [snapshot](/snapshots/#senj-death-1853-03-alexander-son-of-georgius-krmpotic-aged-9-days))
- 6 October 1853 d. — Antonius Krmpotić aged 70 died Senj October 1853 (image 558L; [snapshot](/snapshots/#senj-death-1853-10-antonius-krmpotic-aged-70))
- 20 September 1855 d. — Margarita Krmpotić mendicant of Krmpote died Senj September 1855 (image 572L; [snapshot](/snapshots/#senj-death-1855-09-margarita-krmpotic-mendicant-of-krmpote))
- April 1856 m. — Jacobus Žerković widower groom of 1856 with a Krmpotić widow bride (image 375L; [snapshot](/snapshots/#senj-marriage-1856-04-jacobus-zerkovic-widower-of-st-georgen-josepha-widow-krmpotich))
- April 1856 m. — Josepha Krmpotić widow bride of Jacobus Žerković 1856 (image 375L; [snapshot](/snapshots/#senj-marriage-1856-04-jacobus-zerkovic-widower-of-st-georgen-josepha-widow-krmpotich-bride))
- 25 August 1856 d. — Thomas Vukelić Grenzer of Krmpote aged 26 died Senj August 1856 (image 576R; [snapshot](/snapshots/#senj-death-1856-08-thomas-vukelic-confiniarius-of-krmpote-aged-26))
- 8 January 1858 d. — Gregorius Krmpotić Grenzer aged 75 died Senj January 1858 (image 582R; [snapshot](/snapshots/#senj-death-1858-01-gregorius-krmpotic-confiniarius-aged-75))

### Tomljanović (29)

- 18 February 1738 m. — Klara Tomljanović bride 1738 (image 18L; [snapshot](/snapshots/#senj-marriage-1738-02-antonio-speranci-klara-daughter-of-vule-tomjanovic))
- 1738 m. — Pave Tomljanović witness 1738 (image 20R; [snapshot](/snapshots/#senj-marriage-1738-12-pera-stabar-klara-witness-pave-tomjanovic))
- 14 May 1739 m. — Antonia Tomljanović bride 1739 (image 22R; [snapshot](/snapshots/#senj-marriage-1739-05-francisca-bexilva-antonia-daughter-of-jule-tomjanovic))
- 2 October 1739 m. — Pave Tomljanović canon officiating priest 1739 (image 23R; [snapshot](/snapshots/#senj-marriage-1739-10-franu-parskovic-klara-celebrant-pop-pave-tomjanovic-canon))
- 1741 m. — Perica Tomljanović canon celebrant 1741 (image 27R; [snapshot](/snapshots/#senj-marriage-1741-11-franu-roxanic-widow-celebrated-by-canon-perica-tomjanovic))
- 18 January 1742 m. — Pero Tomljanović groom 1742 (image 28R; [snapshot](/snapshots/#senj-marriage-1742-01-pero-tomjanovic-margarita-celebrated-by-his-brother-pop-marko-tomjanovic))
- 13 October 1751 m. — Jure Tomljanović groom 1751 (image 51L; [snapshot](/snapshots/#senj-marriage-1751-10-jure-tommyanovic-widower-mandalena))
- January 1754 m. — Anton Tomljanović named in an entry of 1754 (image 58R; [snapshot](/snapshots/#senj-marriage-1754-01-anton-tomljanovic-named-in-entry-58r-top))
- 24 April 1762 m. — Petar Tomljanović canon celebrant 1762 (image 69L; [snapshot](/snapshots/#senj-marriage-1762-04-canon-petar-tomljanovic-celebrant))
- September 1764 m. — Petar Tomljanović canon celebrant 1764 (image 72R; [snapshot](/snapshots/#senj-marriage-1764-09-canon-petar-tomljanovic-celebrates))
- August 1790 m. — Georgius Tomljan soldier of the Otočac regiment groom 1790 (image 141R; [snapshot](/snapshots/#senj-marriage-1790-08-georgius-tomljan-otocac-soldier-martha-filipovic-of-krmpote))
- February 1831 d. — Gregorius Tomljanović son of Antonius died Senj February 1831 (image 505R; [snapshot](/snapshots/#senj-death-1831-02-gregorius-son-of-antonius-tomljanovic))
- 31 March 1832 d. — Clara Tomljanović widow aged 60 died Senj March 1832 (image 505R; [snapshot](/snapshots/#senj-death-1832-03-clara-widow-tomljanovic-aged-60))
- 25 February 1834 d. — Mattia Tomljanović infant died Senj February 1834 (image 506R; [snapshot](/snapshots/#senj-death-1834-02-mattia-daughter-of-matthias-tomljanovich-one-day))
- 8 April 1834 d. — Maria Tomljanović widow aged 60 died Senj April 1834 (image 506R; [snapshot](/snapshots/#senj-death-1834-04-maria-widow-tomljanovich-aged-60))
- 27 August 1837 m. — Georgius Tomjanović groom of 1837 with a Smojver bride of Jablanac (image 349L; [snapshot](/snapshots/#senj-marriage-1837-08-georgius-tomjanovich-vincentia-smojver-of-jablanac))
- 27 August 1837 m. — Vincentia Smojver of Jablanac bride of Georgius Tomjanović 1837 (image 349L; [snapshot](/snapshots/#senj-marriage-1837-08-georgius-tomjanovich-vincentia-smojver-of-jablanac-bride))
- 22 February 1842 d. — Lucas Tomljanović infant died Senj February 1842 (image 507R; [snapshot](/snapshots/#senj-death-1842-02-lucas-son-of-matthias-tomljanovich-aged-4-months))
- 19 April 1843 d. — Mathias Tomljanović infant died Senj April 1843 (image 508L; [snapshot](/snapshots/#senj-death-1843-04-mathias-tomljanovich-aged-3))
- 2 February 1845 m. — Bartholomaeus Tomjanović groom of 1845 with a Smojver bride of Jablanac (image 350R; [snapshot](/snapshots/#senj-marriage-1845-02-bartholomaeus-tomjanovich-lucia-smojver-of-jablanac))
- 2 February 1845 m. — Lucia Smojver of Jablanac bride of Bartholomaeus Tomjanović 1845 (image 350R; [snapshot](/snapshots/#senj-marriage-1845-02-bartholomaeus-tomjanovich-lucia-smojver-of-jablanac-bride))
- 6 December 1846 d. — Margaritha Tomljanović aged 9 died Senj December 1846 (image 509L; [snapshot](/snapshots/#senj-death-1846-12-margaritha-tomljanovich-aged-9))
- 5 December 1847 d. — Virginia Tomljanović aged 4 died Senj December 1847 (image 509L; [snapshot](/snapshots/#senj-death-1847-12-virginia-tomljanovich-aged-4))
- 1848 d. — Maria Tomljanović aged 57 died Senj 1848 (image 509R; [snapshot](/snapshots/#senj-death-1848-maria-tomljanovich-aged-57))
- 19 August 1851 m. — Francisca Tomjanović bride of Joannes Vukelić 1851 (image 363R; [snapshot](/snapshots/#senj-marriage-1851-08-joannes-vukelich-of-gospic-francisca-tomjanovich-bride))
- 17 September 1855 d. — Georgius Tomljanović of Krmpote aged 57 died Senj September 1855 (image 572L; [snapshot](/snapshots/#senj-death-1855-09-georgius-tomljanovic-confiniarius-of-krmpote-aged-57))
- 15 November 1855 d. — Joannes Tomljanović aged 2 died Senj November 1855 (image 572R; [snapshot](/snapshots/#senj-death-1855-11-joannes-son-of-philippus-tomljanovic-aged-2y6m))
- 24 February 1856 d. — Petrus Tomljanović aged 2 died Senj February 1856 (image 574L; [snapshot](/snapshots/#senj-death-1856-02-petrus-son-of-bartholomeus-tomljanovic-aged-2))
- 2 June 1858 d. — Matthaeus Tomljanović retired watchman aged 54 died Senj June 1858 (image 585R; [snapshot](/snapshots/#senj-death-1858-06-matthaeus-tomljanovic-provisionatus-vigil-aged-54))

### Other (28)

- 2 December 1736 m. — Matia Urolla of Zastva (image 13R; [snapshot](/snapshots/#senj-marriage-1736-12-matia-urolla-of-zastva))
- 7 February 1767 m. — Pop Fabre Vuklić celebrant 1767 (image 78L; [snapshot](/snapshots/#senj-marriage-1767-02-bernardo-frakasa-antonija-pop-fabre-vuklic))
- 2 July 1820 m. — Joannes Malik soldier groom of 1820 at Senj (image ; [snapshot](/snapshots/#senj-marriage-1820-07-joannes-malik-soldier-customs-bride-francisca-spalj))
- 1821 m. — Thomas Orichovich groom of 1821 at Senj (image 309R; [snapshot](/snapshots/#senj-marriage-1821-10-thomas-orichovich-maria-sbarich))
- 1821 m. — Maria Sbaich bride of Orichovich 1821 (image 309R; [snapshot](/snapshots/#senj-marriage-1821-10-thomas-orichovich-maria-sbarich-bride))
- 1823 m. — Lucia Lončarić bride of Savretić 1823 (image 335L; [snapshot](/snapshots/#senj-marriage-1823-georgius-savretic-lucia-lonaric-witnesses-joannes-laurentius-boras-bride))
- 23 October 1831 m. — Christophorus Gerzanich groom of 1831 at Senj (image 255L; [snapshot](/snapshots/#senj-marriage-1831-10-christophorus-gerzanich-antonia-babich-novigrad))
- 25 November 1832 m. — Martinus Lenack groom of 1832 at Senj (image 269R; [snapshot](/snapshots/#senj-marriage-1832-11-martinus-lenack-anna-loncarich))
- 25 November 1832 m. — Anna Lončarić bride of Lenack 1832 (image 269R; [snapshot](/snapshots/#senj-marriage-1832-11-martinus-lenack-anna-loncarich-bride))
- 7 April 1833 d. — Franciscus ab Oresnovich vice-colonel died Senj April 1833 (image 469R; [snapshot](/snapshots/#senj-death-1833-04-franciscus-ab-oresnovich-vice-colonel-aged-58))
- 29 September 1844 m. — Aloysius Rubelli groom of 1844 at Senj (image 328L; [snapshot](/snapshots/#senj-marriage-1844-09-aloysius-rubelli-justina-lukatelli))
- 1845 m. — Georgius Haas groom of 1845 at Senj (image 264L; [snapshot](/snapshots/#senj-marriage-1845-georgius-haas-francisca-loncarich))
- 1845 m. — Francisca Lončarić bride of 1845 (image 264L; [snapshot](/snapshots/#senj-marriage-1845-georgius-haas-francisca-loncarich-bride))
- 16 February 1846 m. — Mathias Jurcić of Senj groom of 1846 (image 272R; [snapshot](/snapshots/#senj-marriage-1846-02-mathias-jurcic-laurentia-antic-of-lukovo))
- 16 February 1846 m. — Laurentia Antić of Lukovo bride of 1846 (image 272R; [snapshot](/snapshots/#senj-marriage-1846-02-mathias-jurcic-laurentia-antic-of-lukovo-bride))
- February 1848 d. — Zuppan woman aged 66 died Senj February 1848 (image 523L; [snapshot](/snapshots/#senj-death-1848-02-zuppan-woman-aged-66))
- 28 May 1849 m. — Joso Antić witness at Senj marriage of 1849 (image 281R; [snapshot](/snapshots/#senj-marriage-1849-05-croatian-entry-mihovil-kriskovic-maria-basic-witness-joso-antic))
- 9 June 1850 m. — Tereza Čačić of Senj bride of 1850 (image 221R; [snapshot](/snapshots/#senj-marriage-1850-06-gergo-blazevic-of-krmpote-terezia-cacic-bride))
- 27 October 1850 m. — Philip Kruk groom of 1850 at Senj (image 282L; [snapshot](/snapshots/#senj-marriage-1850-10-philip-kruk-helena-loncarich-croatian-entry))
- 27 October 1850 m. — Helena Lončarić bride of Kruk 1850 (image 282L; [snapshot](/snapshots/#senj-marriage-1850-10-philip-kruk-helena-loncarich-croatian-entry-bride))
- 29 December 1850 m. — Luka Pukavina groom of 1850 at Senj with a Čačić bride (image 329L; [snapshot](/snapshots/#senj-marriage-1850-12-luka-pukavina-catharina-cacic-mother-tomljanovic))
- 29 December 1850 m. — Catharina Čačić bride of Pukavina 1850 (image 329L; [snapshot](/snapshots/#senj-marriage-1850-12-luka-pukavina-catharina-cacic-mother-tomljanovic-bride))
- 21 August 1853 m. — Jacobus Lenac groom of 1853 at Senj (image 290L; [snapshot](/snapshots/#senj-marriage-1853-08-jacobus-lenac-maria-butkovic-witnesses-babich-perpic))
- 10 February 1857 m. — Antonius Gerbac widower of Starigrad groom of 1857 (image 260R; [snapshot](/snapshots/#senj-marriage-1857-02-antonius-gerbac-widower-catharina-widow-of-stephanus-babich))
- 30 May 1858 m. — Lucas Glavicsich of Senj groom of 1858 (image 260R; [snapshot](/snapshots/#senj-marriage-1858-05-lucas-glavicsich-maria-tomlenovich-of-karlobag))
- 30 May 1858 m. — Maria Tomljenović of Karlobag bride of 1858 (image 260R; [snapshot](/snapshots/#senj-marriage-1858-05-lucas-glavicsich-maria-tomlenovich-of-karlobag-bride))
- August 1858 m. — Franciscus Vincentius Gerzic of Senj groom of 1858 (image 261L; [snapshot](/snapshots/#senj-marriage-1858-08-franciscus-vincentius-gerzic-martha-loncarich-widow))
- August 1858 m. — Martha Lončarić widow of Linić bride of 1858 (image 261L; [snapshot](/snapshots/#senj-marriage-1858-08-franciscus-vincentius-gerzic-martha-loncarich-widow-bride))

### Prpić / Perpić (18)

- 9 October 1788 m. — Antonia Prpić daughter of Matte (image 136R; [snapshot](/snapshots/#senj-marriage-1788-10-marko-salanic-antonia-prpic))
- 29 February 1820 d. — Joannes Perpić newborn died Senj February 1820 (image 472R; [snapshot](/snapshots/#senj-death-1820-02-joannes-son-of-franciscus-perpic-after-emergency-baptism))
- 6 October 1834 d. — Andreas Perpić aged 70 died Senj October 1834 (image 475R; [snapshot](/snapshots/#senj-death-1834-10-andreas-perpic-aged-70))
- 22 September 1836 d. — Maria Perpić widow aged 63 died Senj September 1836 (image 476R; [snapshot](/snapshots/#senj-death-1836-09-maria-widow-perpich-aged-63))
- 25 March 1837 d. — Apollonia Perpić widow aged 45 died suddenly Senj March 1837 (image 476R; [snapshot](/snapshots/#senj-death-1837-03-apollonia-widow-perpich-aged-45-died-suddenly))
- 6 March 1840 d. — Franciscus Perpić aged 48 died Senj March 1840 (image 477R; [snapshot](/snapshots/#senj-death-1840-03-franciscus-perpich-aged-48))
- 20 April 1841 d. — Maria Perpić aged 48 died Senj April 1841 (image 478R; [snapshot](/snapshots/#senj-death-1841-04-maria-perpich-aged-48-and-1841-06-vitus-perpich-aged-2))
- 31 July 1842 d. — Josephus Perpić frontier soldier aged 61 died Senj July 1842 (image 479L; [snapshot](/snapshots/#senj-death-1842-07-josephus-perpich-aged-61-confiniarius))
- 5 December 1844 d. — Augustinus Perpić infant died Senj December 1844 (image 479R; [snapshot](/snapshots/#senj-death-1844-12-augustinus-perpic-aged-1))
- 16 December 1845 m. — Joannes Perpich groom of 1845 at Senj (image 319R; [snapshot](/snapshots/#senj-marriage-1845-12-joannes-perpich-francisca-lenac))
- 16 December 1845 m. — Francisca Lenac bride of Perpich 1845 (image 319R; [snapshot](/snapshots/#senj-marriage-1845-12-joannes-perpich-francisca-lenac-bride))
- February 1847 d. — Antonia Perpić aged 35 died Senj February 1847 (image 482L; [snapshot](/snapshots/#senj-death-1847-01-maria-pilepich-aged-9-months-and-1847-02-antonia-perpich-aged-35-bride))
- 1848 d. — Josephus Perpić aged 50 died Senj 1848 (image 482R; [snapshot](/snapshots/#senj-death-1848-josephus-perpich-aged-50))
- 1848 d. — Franciscus Perpić aged 25 died Senj 1848 faded (image 482R; [snapshot](/snapshots/#senj-death-1848-franciscus-perpich-aged-25-faded))
- 1 July 1849 d. — Martin Perpić aged 34 died Senj July 1849 (image 532R; [snapshot](/snapshots/#senj-death-1849-07-martin-perpsich-aged-34))
- 6 February 1853 m. — Franciscus Prpić groom of 1853 at Senj (image 321R; [snapshot](/snapshots/#senj-marriage-1853-02-franciscus-perpic-anna-brozincevic))
- 6 February 1853 m. — Anna Maria Theresia Brozinčević bride of Prpić 1853 (image 321R; [snapshot](/snapshots/#senj-marriage-1853-02-franciscus-perpic-anna-brozincevic-bride))
- 27 June 1854 d. — Theresia Perpić infant died Senj June 1854 (image 562R; [snapshot](/snapshots/#senj-death-1854-06-theresia-daughter-of-franciscus-perpic-aged-10-months))

### Orešković (14)

- 24 June 1783 m. — Juraj Orešković adjutant of the Otočac regiment (image 118L; [snapshot](/snapshots/#senj-marriage-1783-06-juraj-oreskovic-adjutant-catharina-milanes))
- 22 June 1827 d. — Georgius Orešković drowned at sea aged 20 died Senj June 1827 (image 468R; [snapshot](/snapshots/#senj-death-1826-27-andreas-oreskovich-aged-68-and-georgius-oreskovich-drowned-aged-20))
- 9 May 1832 m. — Valentinus Savretić groom of 1832 with an Orešković widow bride (image 336L; [snapshot](/snapshots/#senj-marriage-1832-05-valentinus-savretic-widow-maria-oreskovic))
- 9 May 1832 m. — Maria Orešković widow bride of Savretić 1832 (image 336L; [snapshot](/snapshots/#senj-marriage-1832-05-valentinus-savretic-widow-maria-oreskovic-bride))
- 8 May 1833 d. — Clara Orešković child of Formosus died Senj May 1833 (image 469R; [snapshot](/snapshots/#senj-death-1833-35-children-of-formosus-oreskovich-clara-juliana-carolina))
- 26 August 1836 d. — Franciscus Orešković child of Formosus died Senj August 1836 (image 470L; [snapshot](/snapshots/#senj-death-1836-37-franciscus-maria-ludomilla-children-of-formosus-oreskovich))
- 26 November 1843 m. — Joannes Thian groom of 1843 with an Orešković bride (image 350R; [snapshot](/snapshots/#senj-marriage-1843-11-joannes-thian-maria-oreskovich))
- 26 November 1843 m. — Maria Orešković bride of Joannes Thian 1843 (image 350R; [snapshot](/snapshots/#senj-marriage-1843-11-joannes-thian-maria-oreskovich-bride))
- 20 January 1848 d. — Mathia Orešković aged 80 died Senj January 1848 (image 470R; [snapshot](/snapshots/#senj-death-1848-01-mathia-oreskovich-aged-80))
- 9 September 1849 m. — Mathe Thian groom of 1849 with an Orešković bride (image 351L; [snapshot](/snapshots/#senj-marriage-1849-09-mathe-thian-maria-oreskovich-croatian-entry))
- 9 September 1849 m. — Marija Orešković bride of Mathe Thian 1849 (image 351L; [snapshot](/snapshots/#senj-marriage-1849-09-mathe-thian-maria-oreskovich-croatian-entry-bride))
- 27 July 1849 d. — Formoz Orešković aged 54 died Senj July 1849 (image 533L; [snapshot](/snapshots/#senj-death-1849-07-formoz-oriskovic-aged-54))
- 15 August 1851 d. — Catharina Orešković aged 26 died Senj August 1851 (image 549R; [snapshot](/snapshots/#senj-death-1851-08-catharina-oreskovic-aged-26))
- 10 April 1853 m. — Maria Magličić bride of Ignatius Turkalj 1853 whose mother was an Orešković (image 352R; [snapshot](/snapshots/#senj-marriage-1853-04-ignatius-turkalj-maria-maglich-mother-oreskovich-bride))

### Belobarbić (14)

- 13 December 1849 d. — Petar Belobarbić aged 68 died Senj December 1849 (image 535R; [snapshot](/snapshots/#senj-death-1849-12-petar-belobarbich-aged-68))
- 18 November 1849 m. — Ivan Belobarbić groom 1849 (image 345R; [snapshot](/snapshots/#senj-marriage-1849-11-ivan-belobarbic-vincenca-gregoric))
- 31 August 1852 m. — Michael Belobarbić groom of 1852 with a bride of Novi in Vinodol (image 376L; [snapshot](/snapshots/#senj-marriage-1852-08-michael-belobarbic-francisca-petrinovic-of-novi))
- 31 August 1852 m. — Francisca Petrinović of Novi bride of Michael Belobarbić 1852 (image 376L; [snapshot](/snapshots/#senj-marriage-1852-08-michael-belobarbic-francisca-petrinovic-of-novi-bride))
- 22 May 1852 d. — Maria Belobarbić newborn died Senj May 1852 (image 553R; [snapshot](/snapshots/#senj-death-1852-05-maria-daughter-of-michael-belobarbic-one-day))
- 8 February 1854 d. — Joannes Belobarbić newborn died Senj February 1854 (image 560L; [snapshot](/snapshots/#senj-death-1854-02-son-of-belobarbic-baptised-joannes-in-need))
- 2 March 1854 d. — Ana Belobarbić infant died Senj March 1854 (image 560R; [snapshot](/snapshots/#senj-death-1854-03-ana-daughter-of-antonius-belobarbic-aged-4-months))
- 6 December 1854 d. — Josephus Belobarbić infant died Senj December 1854 (image 564L; [snapshot](/snapshots/#senj-death-1854-12-josephus-son-of-georgius-belobarbic-aged-1y6m))
- 14 August 1855 d. — Antonius Belobarbić aged 14 died Senj August 1855 (image 570L; [snapshot](/snapshots/#senj-death-1855-08-antonius-son-of-antonius-belobarbic-aged-14))
- 3 January 1856 d. — Wolfgangus Belobarbić infant died Senj January 1856 (image 573R; [snapshot](/snapshots/#senj-death-1856-01-wolfgangus-son-of-georgius-belobarbic-aged-1y))
- 22 February 1856 d. — Vincentia Belobarbić wife of Georgius aged 28 died Senj February 1856 (image 574L; [snapshot](/snapshots/#senj-death-1856-02-vincentia-wife-of-georgius-belobarbic-aged-28))
- 22 March 1857 d. — Vincentia Belobarbić infant died Senj March 1857 (image 579L; [snapshot](/snapshots/#senj-death-1857-03-vincentia-daughter-of-antonius-belobarbic-aged-2-months))
- 9 May 1857 d. — Matthaeus Belobarbić aged 7 died Senj May 1857 (image 579R; [snapshot](/snapshots/#senj-death-1857-05-matthaeus-son-of-georgius-belobarbic-aged-7))
- 25 November 1858 d. — Andreas Belobarbić newborn died Senj November 1858 (image 588L; [snapshot](/snapshots/#senj-death-1858-11-andreas-son-of-michael-belobarbic-newborn))

### Blažević (13)

- 14 February 1754 m. — Anna Blažević bride of Josip Kosović 1754 (image 59L; [snapshot](/snapshots/#senj-marriage-1754-02-josip-kosovic-anna-daughter-of-the-late-ivan-blazevic))
- March 1768 m. — Anna widow of Mate Blažević (image 82R; [snapshot](/snapshots/#senj-marriage-1768-03-anna-widow-of-mate-blazevic))
- 23 January 1769 m. — Mate Blažević of Senj groom of 1769 (image 84L; [snapshot](/snapshots/#senj-marriage-1769-01-mate-blazevic-marries-a-widow))
- February 1779 m. — Lorne Blažević groom of 1779 (image 104R; [snapshot](/snapshots/#senj-marriage-1779-02-lorne-blazevic-franica-fobber))
- 1802–1812 m. — Fabianus Blažević witness at Senj 1802-1812 (image 193R; [snapshot](/snapshots/#senj-witness-fabianus-blazevich-1802-1812))
- 18 August 1812 m. — Vincentia Blažević widow bride of 1812 (image 194L; [snapshot](/snapshots/#senj-marriage-1812-08-petrus-bozijan-widow-vincentia-blazevich))
- 24 January 1830 d. — Margaritha Blažević died Senj January 1830 (image 384L; [snapshot](/snapshots/#senj-death-1830-01-margaritha-blazevich-aged-50))
- 7 August 1830 d. — Francisca Blažević died Senj August 1830 (image 384L; [snapshot](/snapshots/#senj-death-1830-08-francisca-blazevich-aged-70))
- 17 [?]bris 1832 m. — Fabianus Blažević widower tailor of Senj groom of 1832 (image 222R; [snapshot](/snapshots/#senj-marriage-1832-xbris-fabianus-blazevich-widower-tailor-margaritha))
- 18 September 1840 d. — Margaritha Blažević died Senj September 1840 (image 390L; [snapshot](/snapshots/#senj-death-1840-09-margaritha-blazevich-aged-50))
- April 1842 d. — Jacobus Blažević aged 10 died Senj April 1842 (image 391R; [snapshot](/snapshots/#senj-death-1842-04-jacobus-blazevich-aged-10))
- 27 March 1844 d. — Fabianus Blažević widower aged 74 died Senj March 1844 (image 392R; [snapshot](/snapshots/#senj-death-1844-03-fabianus-blazevich-widower-aged-74))
- 9 June 1850 m. — Georgius Blažević son of Ivan of Krmpote groom of 1850 (image 221R; [snapshot](/snapshots/#senj-marriage-1850-06-gergo-blazevic-of-krmpote-terezia-cacic))

### Butković (13)

- 18 October 1735 m. — Katarina Butković of Ledenice bride 1735 (image 10R; [snapshot](/snapshots/#senj-marriage-1735-10-stipe-bukvic-katarina-daughter-of-mikula-butkovic-of-ledenice))
- 13 February 1736 m. — Franjo Butković of Karlobag groom 1736 (image 12L; [snapshot](/snapshots/#senj-marriage-1736-02-franjo-butkovic-of-karlobag-mara))
- 12 June 1746 m. — Mate Butković groom of Brinje 1746 (image 39L; [snapshot](/snapshots/#senj-marriage-1746-06-mate-butkovic-of-brinje))
- 3 August 1750 m. — Matiya Butković of Savil bride 1750 (image 50L; [snapshot](/snapshots/#senj-marriage-1750-08-frano-kulbiric-maria-daughter-of-mike-butkovic-of-savil))
- December 1763 m. — Jura Butković witness 1763 (image 71R; [snapshot](/snapshots/#senj-marriage-1763-12-mate-kohe-margarita-witness-jura-butkovic))
- 24 November 1764 m. — Matija widow of Anton Butković bride 1764 (image 73L; [snapshot](/snapshots/#senj-marriage-1764-11-juraj-verbanic-widow-of-anton-butkovic-matija))
- March 1767 m. — Ivan Butković witness 1767 (image 79L; [snapshot](/snapshots/#senj-marriage-1767-03-toma-carofiglio-margarita-witness-ivan-butkovic))
- July 1851 m. — Vincentius mariner groom of 1851 with a Butković bride of Ledenice (image ; [snapshot](/snapshots/#senj-marriage-1851-07-vincentius-bride-lucia-butkovich-of-ledenice))
- July 1851 m. — Lucia Butković of Ledenice bride of 1851 (image ; [snapshot](/snapshots/#senj-marriage-1851-07-vincentius-bride-lucia-butkovich-of-ledenice-bride))
- 21 August 1853 m. — Maria Butković bride of Lenac 1853 (image 290L; [snapshot](/snapshots/#senj-marriage-1853-08-jacobus-lenac-maria-butkovic-witnesses-babich-perpic-bride))
- 11 September 1855 d. — Anna Butković maidservant aged 16 died Senj September 1855 (image 571R; [snapshot](/snapshots/#senj-death-1855-09-anna-butkovic-servant-aged-16))
- 18 August 1857 d. — Maria Butković aged 5 died Senj August 1857 (image 581R; [snapshot](/snapshots/#senj-death-1857-08-maria-daughter-of-georgius-butkovic-aged-5y6m))
- 23 December 1858 d. — Simeon Butković aged 1 died Senj December 1858 (image 588R; [snapshot](/snapshots/#senj-death-1858-12-simeon-son-of-georgius-butkovic-aged-1y6m))

### Pilipić (13)

- July 1824 d. — Matthaeus Pilipić child died Senj July 1824 (image 473L; [snapshot](/snapshots/#senj-death-1824-07-matthaeus-son-of-joannes-pilipic))
- September 1826 d. — Stephana Pilipić daughter of Joannes died Senj September 1826 (image 473L; [snapshot](/snapshots/#senj-death-1826-09-stephana-daughter-of-joannes-pilipic))
- November 1826 d. — Nicolaus Pilipić aged 3 died Senj November 1826 (image 473L; [snapshot](/snapshots/#senj-death-1826-11-nicolaus-son-of-antonius-pilipic-aged-3))
- June 1827 d. — Francisca Pilipić daughter of Franciscus died Senj June 1827 (image 473L; [snapshot](/snapshots/#senj-death-1827-06-francisca-daughter-of-franciscus-pilipic))
- 1830 d. — Anna Pilipić aged 1 died Senj 1830 (image 473R; [snapshot](/snapshots/#senj-death-1830-anna-daughter-of-joannes-pilipic-aged-1))
- 16 June 1831 d. — Catharina widow Pilipić aged 86 died Senj June 1831 (image 474R; [snapshot](/snapshots/#senj-death-1831-32-catharina-widow-pilipich-aged-86-and-franciscus-son-of-andreas-pilipich-aged-6))
- 28 September 1833 d. — Anna Pilipić daughter of Vitus died Senj September 1833 (image 475L; [snapshot](/snapshots/#senj-death-1833-anna-daughter-of-vitus-pilipich-and-antonia-daughter-of-joannes-pilipich))
- 29 April 1839 d. — Franciscus Pilipović aged 50 died Senj April 1839 (image 477L; [snapshot](/snapshots/#senj-death-1839-04-franciscus-pilipovich-aged-50))
- 28 January 1847 d. — Maria Pilipić infant died Senj January 1847 (image 482L; [snapshot](/snapshots/#senj-death-1847-01-maria-pilepich-aged-9-months-and-1847-02-antonia-perpich-aged-35))
- 26 March 1849 d. — Ignatz Pilipić infant died Senj March 1849 (image 531L; [snapshot](/snapshots/#senj-death-1849-03-ignatz-pilepich-aged-5-months))
- 19 November 1849 d. — Ivan Pilipić aged 60 died Senj November 1849 (image 535L; [snapshot](/snapshots/#senj-death-1849-11-ivan-pilepich-aged-60))
- 12 April 1854 d. — Margaritha Pilipić widow aged 56 died Senj April 1854 (image 561R; [snapshot](/snapshots/#senj-death-1854-04-margaritha-widow-pilepic-aged-56))
- 26 April 1854 d. — Elisabeta Pilipić aged 4 died Senj April 1854 (image 561R; [snapshot](/snapshots/#senj-death-1854-04-elisabeta-daughter-of-victor-pilepic-aged-4))

### Boras (11)

- May 1816 m. — Maria Borach Boras query bride 1816 (image 200L; [snapshot](/snapshots/#senj-marriage-1816-05-josephus-hanich-maria-borach))
- 1823 m. — Georgius Savretić groom of 1823 with Boras witnesses (image 335L; [snapshot](/snapshots/#senj-marriage-1823-georgius-savretic-lucia-lonaric-witnesses-joannes-laurentius-boras))
- 7 May 1823 m. — Josephus Boras witness at Senj marriage of 1823 (image ; [snapshot](/snapshots/#senj-marriage-1823-05-bride-from-dalmatia-witness-josephus-boras))
- 27 April 1828 m. — Joseph Boras witness at Senj marriage of 1828 (image 360L; [snapshot](/snapshots/#senj-marriage-1828-04-paulus-vukelich-catharina-miskulin-witness-joseph-boras))
- 1 October 1838 m. — Josephus Boras merchant witness at Senj marriage of 1838 (image 339R; [snapshot](/snapshots/#senj-marriage-1838-10-ambrosius-stokich-margaritha-witness-josephus-boras-merchant))
- June 1839 d. — Josephus Boras died Senj 1839 aged 50 (image 389R; [snapshot](/snapshots/#senj-death-1839-06-josephus-boros-aged-50-with-josephus-gallas))
- 1 September 1841 d. — Anna Boras widow died Senj September 1841 (image 390R; [snapshot](/snapshots/#senj-death-1841-09-anna-widow-boras-aged-51))
- 12 July 1849 d. — Johann Boras aged 73 died Senj July 1849 (image 533L; [snapshot](/snapshots/#senj-death-1849-07-johann-baraz-aged-73))
- 1 February 1851 m. — Josephus Boras groom of 1851 at Senj (image 375R; [snapshot](/snapshots/#senj-marriage-1851-02-josephus-boras-widower-maria-sucic))
- 1 February 1851 m. — Maria Sučić widow bride of Josephus Boras 1851 (image 375R; [snapshot](/snapshots/#senj-marriage-1851-02-josephus-boras-widower-maria-sucic-bride))
- 23 February 1854 d. — Franciscus Boras aged 22 died Senj February 1854 (image 560L; [snapshot](/snapshots/#senj-death-1854-02-franciscus-boras-aged-22))

### Smojver (9)

- 1 August 1831 d. — Simon Smojver aged 70 died Senj August 1831 (image 492R; [snapshot](/snapshots/#senj-death-1831-08-simon-smojver-aged-70))
- November 1838 m. — Gregorius Smojver of Jablanac groom of 1838 (image 340L; [snapshot](/snapshots/#senj-marriage-1838-11-gregorius-smojver-of-jablanac-widow-maria-miskulin))
- November 1838 m. — Maria Miškulin widow bride of Gregorius Smojver 1838 (image 340L; [snapshot](/snapshots/#senj-marriage-1838-11-gregorius-smojver-of-jablanac-widow-maria-miskulin-bride))
- 30 January 1839 m. — Josephus Schwarz corporal groom of 1839 with a Smojver bride of Karlobag (image 340R; [snapshot](/snapshots/#senj-marriage-1839-01-josephus-schwarz-maria-smojver-of-karlobag))
- 30 January 1839 m. — Maria Smojver of Karlobag bride of Josephus Schwarz 1839 (image 340R; [snapshot](/snapshots/#senj-marriage-1839-01-josephus-schwarz-maria-smojver-of-karlobag-bride))
- 20 February 1841 d. — Gregorius Smojver aged 26 died Senj February 1841 (image 498R; [snapshot](/snapshots/#senj-death-1841-02-gregorius-smojver-aged-26))
- 26 July 1854 d. — Anna Smojver aged 16 died Senj July 1854 (image 562R; [snapshot](/snapshots/#senj-death-1854-07-anna-smojver-aged-16))
- 25 October 1856 d. — Joanna Smojver aged 57 died Senj October 1856 (image 577L; [snapshot](/snapshots/#senj-death-1856-10-joanna-smojver-servant-aged-57))
- 10 November 1858 d. — Anna Smojver widow aged 90 died Senj November 1858 (image 588L; [snapshot](/snapshots/#senj-death-1858-11-anna-widow-smojver-aged-90))

### Šojat (7)

- May 1737 m. — Božo Šojat witness 1737 (image 15R; [snapshot](/snapshots/#senj-marriage-1737-05-pangracij-onufric-katarina-witness-boze-sojat))
- 10 October 1745 m. — Mihu Šojat of Senj (image 37L; [snapshot](/snapshots/#senj-marriage-1745-10-mihu-soyata-lucia-bevandich))
- 5 October 1754 m. — Anna Šojat bride 1754 (image 62R; [snapshot](/snapshots/#senj-marriage-1754-10-martin-eikovic-anna-daughter-of-mihe-sojat))
- February 1786 m. — Dube Šojat of Senj (image 130R; [snapshot](/snapshots/#senj-marriage-1786-02-dube-sojat-widow-antonia-bunich))
- 18 December 1830 d. — Antonia Šojat aged 95 died Senj December 1830 (image 492L; [snapshot](/snapshots/#senj-death-1830-12-antonia-sojat-aged-95))
- 6 December 1838 d. — Laurentius Šojat widower aged 80 died Senj December 1838 (image 497L; [snapshot](/snapshots/#senj-death-1838-12-laurentius-widower-sojat-aged-80))
- 15 June 1846 d. — Michael Šojat aged 51 died Senj June 1846 (image 503L; [snapshot](/snapshots/#senj-death-1846-06-mikael-sojat-aged-51))

### Špalj (7)

- 28 May 1747 m. — Matia Špalj lieutenant of Krmpote groom 1747 (image 42R; [snapshot](/snapshots/#senj-marriage-1747-05-matia-spalj-lieutenant-of-krmpote-barbara-simanic))
- 23 January 1814 m. — Maria Špalj bride 1814 (image 195L; [snapshot](/snapshots/#senj-marriage-1814-01-thomas-starich-maria-spalj))
- 2 July 1820 m. — Francisca Špalj bride of Malik 1820 (image ; [snapshot](/snapshots/#senj-marriage-1820-07-joannes-malik-soldier-customs-bride-francisca-spalj-bride))
- 1820 d. — Joannes Špalj Spal aged 80 died Senj 1820 (image 490R; [snapshot](/snapshots/#senj-death-1820-03-joannes-spal-aged-80))
- 27 November 1828 d. — Joannes Špalj Spal died Senj November 1828 (image 491R; [snapshot](/snapshots/#senj-death-1828-11-joannes-spal))
- 23 November 1831 d. — Hellena Špalj aged 79 died Senj November 1831 (image 492R; [snapshot](/snapshots/#senj-death-1831-11-hellena-spalj-aged-79))
- 2 August 1836 d. — Catharina Špalj widow aged 78 died Senj August 1836 (image 495R; [snapshot](/snapshots/#senj-death-1836-08-catharina-widow-spalj-aged-78))

### Župan (6)

- 9 May 1835 d. — Joanna Župan infant died Senj May 1835 (image 521L; [snapshot](/snapshots/#senj-death-1835-05-joanna-zuppan-aged-4-days))
- 21 August 1836 d. — Catharina Župan widow aged 70 died Senj August 1836 (image 521L; [snapshot](/snapshots/#senj-death-1836-08-catharina-widow-zuppan-aged-70))
- 14 May 1848 d. — Mathias Župan aged 82 died Senj May 1848 (image 519L; [snapshot](/snapshots/#senj-death-1848-05-matho-zuppan-aged-82))
- 31 May 1850 d. — Petar Župan infant died Senj May 1850 (image 540R; [snapshot](/snapshots/#senj-death-1850-05-petar-zuppan-aged-1))
- 3 August 1855 d. — Margarita Župan aged 18 died Senj August 1855 (image 569R; [snapshot](/snapshots/#senj-death-1855-08-margarita-daughter-of-antonius-zuppan-aged-18))
- 7 September 1855 d. — Vincentia Župan infant died Senj September 1855 (image 571R; [snapshot](/snapshots/#senj-death-1855-09-vincentia-daughter-of-andreas-zuppan-aged-1y2m))

### Žubrinić (5)

- 8 August 1849 d. — Mihovil Žubrinić aged 47 died Senj August 1849 (image 533R; [snapshot](/snapshots/#senj-death-1849-08-mihovil-zubranic-aged-47))
- 28 April 1850 m. — Toma Pasquan groom of 1850 at Senj with a Žubrinić bride of Baška (image 320R; [snapshot](/snapshots/#senj-marriage-1850-04-toma-pasquan-catharina-zubranic-of-baska))
- 28 April 1850 m. — Catharina Žubrinić of Baška bride of Pasquan 1850 (image 320R; [snapshot](/snapshots/#senj-marriage-1850-04-toma-pasquan-catharina-zubranic-of-baska-bride))
- 6 February 1853 m. — Georgius Zubranić witness at Senj marriage of 1853 (image ; [snapshot](/snapshots/#senj-marriage-1853-02-josephus-herro-bride-babich-witness-zubranic))
- 27 June 1855 d. — Hellena Žubrinić of Baška aged 60 died Senj June 1855 (image 567L; [snapshot](/snapshots/#senj-death-1855-06-hellena-zubranic-aged-60-of-baska))

### Lukatelli (4)

- 29 September 1844 m. — Justina Lukatelli bride of Rubelli 1844 (image 328L; [snapshot](/snapshots/#senj-marriage-1844-09-aloysius-rubelli-justina-lukatelli-bride))
- 6 January 1844 d. — Eva Lukatelli widow aged 54 died Senj January 1844 (image 452R; [snapshot](/snapshots/#senj-death-1844-01-eva-lukatelli-widow-aged-54))
- 14 May 1849 m. — Valerian Lukatella of Karlobag groom of 1849 at Senj (image 289L; [snapshot](/snapshots/#senj-marriage-1849-05-valerian-lukatella-of-karlobag-ana-dragicevic))
- 14 May 1849 m. — Ana Dragičević bride of Valerian Lukatella 1849 (image 289L; [snapshot](/snapshots/#senj-marriage-1849-05-valerian-lukatella-of-karlobag-ana-dragicevic-bride))

### Borić (4)

- January 1741 m. — Borić groom 1741 (image 26L; [snapshot](/snapshots/#senj-marriage-1741-01-boric-of-hrizina-barbara-daughter-of-loncan-of-bakar))
- 30 October 1752 m. — Jakov Borić groom 1752 (image 56R; [snapshot](/snapshots/#senj-marriage-1752-10-jakov-boric-urshula-daughter-of-matia-ugrin-of-bribir))
- 10 April 1853 m. — Ignatius Turkalj soldier groom of 1853 whose mother was a Borić (image 352R; [snapshot](/snapshots/#senj-marriage-1853-04-ignatius-turkalj-maria-maglich-mother-oreskovich))
- 19 November 1857 d. — Jacobus Borić finance watchman aged 19 died Senj November 1857 (image 582L; [snapshot](/snapshots/#senj-death-1857-11-jacobus-boric-finance-watchman-of-udbina-aged-19))

### Papić (2)

- 30 January 1746 m. — Antona Papić groom 1746 (image 38L; [snapshot](/snapshots/#senj-marriage-1746-01-antona-papic-jelena-of-grobnik))
- 11 October 1747 m. — Katarina Papić daughter of Matia (image 43R; [snapshot](/snapshots/#senj-marriage-1747-10-juretic-bakar-katarina-papic))

### Uroda (2)

- 27 December 1849 m. — Vincentius Uroda of Karlobag groom of 1849 at Senj (image 259R; [snapshot](/snapshots/#senj-marriage-1849-12-vincentius-uroda-of-karlobag-maria-gerbacz))
- 27 December 1849 m. — Maria Gerbacz bride of Vincentius Uroda 1849 (image 259R; [snapshot](/snapshots/#senj-marriage-1849-12-vincentius-uroda-of-karlobag-maria-gerbacz-bride))

### Kralj (2)

- 3 September 1836 d. — Lucia widow Kraljikas aged 106 died Senj September 1836 (image 443R; [snapshot](/snapshots/#senj-death-1836-09-lucia-widow-kraljikas-aged-106))
- November 1838 d. — Catharina widow Kralj aged 84 died Senj November 1838 (image 444L; [snapshot](/snapshots/#senj-death-1838-11-catharina-widow-kralj-aged-84))

### Pavelić (2)

- April 1793 m. — Thomas Pavelić groom 1793 (image 149R; [snapshot](/snapshots/#senj-marriage-1793-04-thomas-pavelic-magdalena))
- 21 October 1849 m. — Josip Pavetić groom 1849 (image 345R; [snapshot](/snapshots/#senj-marriage-1849-10-josip-pavetic))

### Kalanj (1)

- 23 January 1842 m. — Maria Kalanj bride of Babić 1842 (image 226L; [snapshot](/snapshots/#senj-marriage-1842-01-antonius-babich-maria-calanich-bride))

### Adamić (1)

- 19 September 1850 d. — Michael Adamić infant died Senj September 1850 (image 545R; [snapshot](/snapshots/#senj-death-1850-09-michael-son-of-volfgang-adamic-aged-1))

### Karić (1)

- 26 April 1855 d. — Maria Karić aged 22 died Senj April 1855 (image 566L; [snapshot](/snapshots/#senj-death-1855-04-maria-daughter-of-blasius-caric-aged-22))

## Findings worth saying aloud

- **Vukelić of Senj** is the best-attested family of the death register (32 deaths): a Dominus Petrus Vukelić (about 70, 1825) whose son Joannes (22) died the year before; a town physician Stephanus; a theology student (1852); and, in 1856–57, **a pensioned centurion Petrus Vukelić who lost three children in fourteen months** (Carolus 1½, Leopoldina 2, Fridericus 5). A second Petrus-less Vukelić line is the porters and watchmen of the 1850s.
- **Belobarbić** — a porter Georgius Belobarbić lost a son in December 1854, a second son in January 1856, his wife (Vincentia, 28) in February 1856 and a third son (Matthaeus, 7) in May 1857; the porters Antonius and Michael have infants in the book. The surname is spelled Belobarbich / Bellobarbick.
- **Krmpotić / Krmpote** — the Krmpote people are border-soldiers of the Ogulin regiment (Gregorius, 75, house No. 30, 1858; Margarita, a beggar of Krmpote, and Georgius Tomljanović, a Grenzer of Krmpote, both died in the Senj hospital in the cholera of September 1855; a Thomas «Vukelich?» of the company of Krmpote, 1856).
- **Babić** — five children of porters named Franciscus and Laurentius Babić died in the cholera of August 1855 (27–29 August), the largest cluster in the volume.
- **A Hellena Žubrinić, 60, «e Baška oriunda»** (native of Baška) died at Senj on 27 June 1855 — the one Žubrinić of Baška in the death register.
- **Smojver** — an Anna Smojver, a widow of 90, died on 10 November 1858 (the oldest Smojver in the volume).
- **No Papa × Pilipić marriage of 1856–57 (work-list row 4) is in the volume.** The Pilipić (Pilepich) deaths are of other households (Ivan, 60, 1849; a Margaritha, widow, from S. Georgius in the Otočac regiment, 1854; Elisabeta, daughter of Victor, 1854).

## What is still owed

The first pass, the strip pass and the second passes are done. What the reading cannot give, and what is left:

1. **Weak negatives.** The one-line death entries of 1820–30 (images 237R, 238R, 248R, 262R, 268R, 269L, 333R) are so abbreviated and so fast a hand that, even at about 1.5x, many surnames are not made out; the cramped 1753–61 hand (images 58–67) was re-read at about 2x and is legible, but the fast 1805–19 Latin cursive was read at about 1.5x, where the second line of a groom's entry can still hide a surname. For every family the registers read here, **a «not found» is a statement about what was legible, not about what the page holds.**
2. **The 39 page-scale seen rows** (Lončarić, Antić, Jurčić, Butković-by-spelling, Barac) were read at page scale and are not found persons; zoom before using any.
3. **Roll 291**, where this film continues, is not part of waypoint 9RK1-W3P and has not been opened.
4. **The marriages after 1858 and the baptisms** are in other waypoints; this volume contains none, and a death register names no parents.
5. A **Vukelić/Belobarbić/Babić household reconstruction** from these entries would need the Senj baptisms (work-list row 29) to name parents.
