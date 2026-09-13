# Three Senj marriage entries, read at full resolution

13 September 2026. All three of the 960-pixel documents named in open question 5c
were found on FamilySearch and read from the deep-zoom tiles at level 13 — roughly
**six times** the width of the copies held in the family tree, and about **nine
times** on the crops that mattered.

Film: *Croatia, Church Books, 1516–1994 → Roman Catholic → Senj (Senj) →
Marriages (Vjenčani) 1859–1920*, **376 images**, DGS 005497949.

## Navigation — corrected

The earlier note that "image 374 is page 350" was wrong. The mapping actually runs
about **page = image − 5**, and it was established from three fixed points:

    image 196  =  page 192
    image 280  =  page 275
    image 299  =  page 294
    image 371  =  page 366   (last register opening; image 372 is END OF ITEM)

The image number is not in the URL. The `?i=N` parameter is ignored on a fresh
load. What *does* work: every filmstrip thumbnail carries `alt="Image N"` and a
deep-zoom ARK in its `src`, so a number→ARK map can be scraped straight out of the
DOM and the tiles fetched directly, with no viewer navigation at all. See
`tools/familysearch.md`.

ARKs for the three entries:

    image 196  3:1:3QSQ-G99X-17PK   page 192, the 1885 marriage
    image 299  3:1:3QS7-L99X-175J   page 294, the 1907 marriage
    image 371  3:1:3QSQ-G99X-17M7   page 366, the 1920 marriage

---

## 1 · Senj marriages, page 192, entry 5 — 3 May 1885

*Josip Papić × Antonija Prpić.* Hedviga's great-grandparents.

    Nr.      5
    Date     1885, dne 3. svibnja
    Groom    Josip Papić, bremenar            porter / load-carrier
             origo Senj · rim. kat. · 27 · neoženjen
    Bride    Antonia Prpić
             origo KRIVI PUT · domicilium Senj · rim. kat. · 26 · neudana
    Groom's parents   Juraj PAPA, težak, i Matia rodjena Filipić
    Bride's parents   Ivan Perpić, seljak, i Luca rodjena Pèrpić, rimokatolici
    Witnesses         Franjo Prpić i Tomo Prpić, seljaci, rimo-katolici
    Priest            Mirko Babić, kapelan
    Remarks           Napovjedani  (banns published)

**Two open questions answered by this row.**

**Question 5 — the word is *Papa*.** The archive assumed the missing `-ić` was an
artefact of the 960-pixel scan. It is not. At ~9× the surname is written **Papa**,
ending in a clean round *a*, with no abbreviation stroke and with room to spare in
the column. The priest wrote the by-name, not the surname.

**Question 5c — Lucia has a surname.** The bride's mother, ahnentafel 15, carried
a blank surname field in the tree and is one of the seven women on the direct line
with no name. The register writes her **Luca rodjena Pèr‑pić** — hyphenated across
two lines, with the Illyrian grave accent standing for the syllabic *r*. She is a
**Prpić who married a Prpić** at Krivi Put.

Note also **Krivi Put** as the bride's *origo*: Antonija was an incomer to Senj,
which is the same pattern the 1885 baptisms showed.

---

## 2 · Senj marriages, page 294, entry 30 — 4 November 1907

*Zvonimir Vukelić × Milka Papić.* Milka's first marriage.

    Nr.      30
    Date     1907, studenoga 4
    Groom    Zvonimir M. Vukelić, gostioničarski pomoćnik   innkeeper's assistant
             domicilium Senj · R.K. · b. 1883, 13/1 · neoženjen
    Bride    Milka Papić, radnica u tvornici duhana         tobacco-factory worker
             domicilium Senj · R.K. · b. 1886, 9/10 · neudana
    Groom's parents   Vukelić pl. Petar, gostioničar, i †Vjekoslava Putnik(?), R.k.
    Bride's parents   Joso Papić, gostioničar, i Tonka rodj. Prpić
    Witnesses         Koloman pl. Vukelić, meštar u tvornici duhana, R.k.
                      Franjo Olivieri, trgovac
    Priest            kapelan (signature not resolved)

This register gives **birth dates, not ages** — which is why it is worth more than
the tree's estimate. Milka's **9/10 1886** here is repeated exactly as **9/X 1886**
in her 1920 entry: two independent registers, thirteen years apart, agreeing.

**Josip Papić's trade has moved.** *Bremenar* in 1885, *težak* in 1891, and
**gostioničar** — innkeeper — by 1907. Three documents, one man, a rising line.

**"Tonka rodj. Prpić"** — the same Antonija of the 1885 entry, under her pet name.

**Koloman pl. Vukelić, *meštar u tvornici duhana*.** A Vukelić holding *master*
grade in the tobacco factory, and *pl.* — plemeniti, noble — on both Vukelić men
named in the row.

---

## 3 · Senj marriages, page 366, entry 41 — 8 December 1920

*Ljubomir Blažević × Milka Vukelić.* Hedviga's parents. Already known to the
archive from the tree's own copy; this adds the page and entry number, the
witnesses and the marginal note.

    Nr.      41
    Date     1920, prosinca 8
    Groom    Ljubomir Blažević, mornar                      sailor
             origo RIJEKA · domicilium Senj · r.k.
             b. 1892, 1/III · neoženjen
    Bride    Milka Vukelić, radnica u tvornici duhana
             origo Senj · r.k. · b. 1886, 9/X · UDOVA (widow)
    Groom's parents   †Juraj Blažević i Tereza r. Žubrinić, mrt.
    Bride's parents   Josip Papić i Antonija r. Prpić, r.k.
    Witnesses         Franjo Bora— , brijač                 barber
                      Vinko Tijan, …činovnik u tvornici duhana
    Priest            Ivan Vidas, parohijalni administrator
    Remarks           dispensation of the ordinariate no. 3371, dated 4.XII.,
                      banns read three times, married in the stolna crkva

**A correction to my own reading.** At page scale I read the groom's birth as
**1/VIII**. At 2.7× it is **1/III** — three strokes under a single overline, no
*V*. The existing `/marriage-1920` page was right and I was wrong; the date is
**1 March 1892**.

**The witness's surname is not read.** It begins *Bora‑* and runs into the column
rule; the tail is illegible at every crop tried. **Boras** is one of this archive's
own surnames, which is exactly why it is left unread here rather than guessed.

**Tereza r. Žubrinić** is legible with the caron on the Ž — the Blažević–Žubrinić
junction, in a contemporary hand, at full size.
