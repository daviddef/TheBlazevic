# The Blažević Archive

An evidence-first family archive for the **Blažević** family of **Senj** and **Smokvica
Krmpotska** — and of Otočac, Krivi Put, Selce, Karlobag, Port Pirie and Johannesburg.

> It begins with one woman: **Hedviga "Seka" Blažević**, born at Senj on 3 August 1926, married to
> Ivan Anton Defranceski, and dead at Johannesburg on 30 October 2001. Everything here works
> outward from her.

## What is here

- **Nine generations and 70 named ancestors**, the earliest born about **1717**, in four parishes
  along a hundred kilometres of the Croatian Littoral.
- **The Bunjevac origin, stated as the inference it is.** Smokvica Krmpotska and Krivi Put were not
  old Croatian villages — they were *founded*, settled between about **1605 and 1647** by
  **Bunjevci Krmpoćani** who fled the Ottoman advance from Krmpote near Zemunik and were planted in
  the Senj mountain by the Habsburg Military Frontier. Two of Hedviga's four grandparental lines
  come out of those settlements. No record in the tree says the word "Bunjevac"; the villages say it.
- **A railway that went somewhere else.** In **1873** the Karlovac–Rijeka line bypassed Senj and the
  port died. Every occupation in this family sits downstream of that: *nadničar* — day labourer;
  *trhonoša* and *bremenar* — load-carrier and porter; *mornar* — sailor; and then the town's
  **tobacco factory**, where Hedviga's mother supervised the floor and her aunt worked it.
- **One name in three alphabets.** **Žubrinić** in modern Croatian, **Xubrinich** in the
  Venetian-Italian convention where *X* wrote the sound *Ž*, **Zubrinich** in the German-Latin
  administrative hand — and **Zubrinich** again, permanently, at **Port Pirie in South Australia**,
  where Ivan Žubrinić landed about 1884. The homeland form (312 bearers) and the diaspora form
  (69 bearers) do not share a single country between them.
- **A brother with two deaths and no grave.** **Oto Blažević** (1923–1945) died at twenty-two. The
  family record carries two irreconcilable accounts, attributed to two named relatives — a
  snakebite, and the war in Slavonia. Both are reproduced; neither is resolved.
- **A Sephardic Jew from Rhodes.** Hedviga's second husband, **Santou (Shemtov) Isaac Codron**
  (1913–1997), was born on an island whose Jewish community was deported to Auschwitz in July 1944
  with about 150 survivors of 1,615. This archive does **not** claim he survived it — it sets out
  the documented Rhodes-to-Rhodesia migration that is the likelier explanation, and marks the
  question open.
- **Ten open questions**, each with what would actually close it.

## Method

| | |
|---|---|
| **Documented** | A named source with a reference, and where possible the scan. |
| **Inferred** | A reasoned conclusion from documented facts, with the reasoning written out so it can be overturned. |
| **Superseded** | Asserted in the family record, and now displaced by a document that says otherwise. |
| **Disputed** | Asserted in the family record but unsupported, or contradicted, by what can be seen. |
| **Family lore** | Told, remembered, not corroborated. Kept because it is precious; labelled because pretending otherwise is how family myths become family history. |

**Living people are omitted from the build entirely** — not hidden, not gated, not present in the
output. The rule is applied once, in `classify_living()` in `tools/gedcom.py`, at the boundary
between the research data and the published site.

Because thousands of people in a tree this size carry no dates at all, judging each by their own
record alone marks every one of them living — safe, but useless. So the build computes an **upper
bound on each person's birth year** from their own events, their children's births, their marriages
and their parents' bounds, and publishes somebody only when *even the latest year they could have
been born* is more than a century ago. Every step is a real bound, never a guess, and a recorded
birth is never overridden by inference. On the current export that judges **2,034 of 15,643** people
living. A living spouse, parent or child is not named on anybody else's page either. A removal
request is honoured within days, without argument and without requiring a reason.

Two further things the build does, and admits to:

- **It folds spellings.** Žubrinić / Zubrinic / Zubrinich / Xubrinich / Xubrinić are counted as one
  name, and so are Prpić and Perpić. Without that the family fragments into small families that
  appear unrelated. The folding lives in one function, `fold()` in `tools/ancestry.py`.
- **It drops the working scaffolding.** The tree carries sorting stubs — *"Senj – Unknown To be
  Sorted Papić"*, *"Brothers [of Stephanus] Žubrinić"*, *"NN Blažević"*. These are research notes,
  not people, and publishing them as ancestors would be a lie.

The raw GEDCOM is **not committed** — it contains every living person in full. `sources/*.ged` is
gitignored; regenerate it with a fresh MyHeritage export and re-run the tools.

**An online family tree is a witness, not a source.** The spine here is a MyHeritage tree of 15,643
people, and most "sources" attached within it are *other trees*. Where a citation reaches a parish
register image, the page says so.

**Media is reachable even though it does not export.** A person's media in a MyHeritage tree is at
`photo-world/<site>?tree_id=4&individual_id=N`, where **N = 4000000 + n** for GEDCOM record `@In@`.
`tools/build_media.py` turns the resulting manifest into the site's gallery.

## Running it

```bash
cd site
npm install
npm run dev      # http://localhost:4324/TheBlazevic
npm run build    # static output in site/dist
```

Deploys to GitHub Pages on every push to `main`.

## Layout

```
sources/                 myheritage-tree4-2026-09-09.ged (15,643 people, 4,777 families) — gitignored
data/                    ancestors.tsv, blazevic-spine.tsv, surname-*.tsv
notes/                   dossier-ancestors.txt — every event, note and citation on the direct line
photos/hedviga/          the six items on Hedviga's profile, with the certificate transcribed
photos/line/             70 full-resolution originals (108 MB) — gitignored
sources/media/           manifest.psv — media id, caption, size, tagged people, source url
site/public/photos/      1,600 px derivatives, committed
tools/                   gedcom.py, ancestry.py, dossier.py, household.py,
                         build_site_data.py, build_media.py, check_links.py
site/src/data/           line, ancestors, people, families, places
site/src/pages/          the archive itself
```

`tools/check_links.py` fails if any page links to a person page that will not be generated —
person slugs come from names, and names in this tree change spelling on a whim.

## Sources

Croatian Roman Catholic parish registers via FamilySearch, *"Croatia, Church Books, 1516–1994"*,
from the Hrvatski državni arhiv, Zagreb — Senj, Krivi Put, Otočac, Karlobag · MyHeritage ·
Geni · Forebears surname distribution · Croatian scholarship on the Bunjevci Krmpoćani settlement ·
SA History Hub on Croatians in South Australia · *Tierra prometida: Jews from Rhodes in the Belgian
Congo and Southern Rhodesia, 1910s–1960s* · Rhodes Jewish Museum · Yad Vashem.

**Seventy media items have been swept out of the MyHeritage library** across the direct line —
34 of them register scans, certificates and gravestones, many at 4,500 px. None were in the GEDCOM;
media does not export. They changed the archive's own conclusions:

- **The 1920 Senj marriage register** (page 366, entry 41, 8 December 1920) names the groom's
  parents as **Juraj Blažević and Tereza *r.* Žubrinić** — closing the generation-three join this
  archive was built around and had labelled *Disputed*. It also records Milka marrying as
  **Milka Vukelić, *udova* — a widow**, which nothing in the tree had recorded, and gives her
  occupation as ***radnica u tvornici duhana***, a worker in the tobacco factory she would later
  supervise.
- **The Blažević grave at Senj** carries **OTO BLAŽEVIĆ ✳1923 †1945** and, on a later plaque,
  **LEO** and **KATA** — corroborating Nives Blažević's account of Oto's death in exact detail,
  including two burials added sixty years afterwards.
- **A sworn translation of the Yugoslav birth extract for Ivan Defranceski** (Senj Hospital,
  17 December 1951; reg. 152/1954) confirms Hedviga's own birth from a state record, gives her
  husband's nationality as **Italian**, and was certified for the **Supreme Court of South
  Africa** — emigration paperwork as well as a birth record.
- **Three Arolsen Archives cards** place Hedviga's husband, aged **sixteen**, in Germany:
  *Hilfsarbeiter* — unskilled labourer — at **Licht und Kraft, Reutlingen** from
  **21 October 1941**, lodging at Brunnenstraße 7, Pfullingen, with a second Reutlingen employer
  from January 1942. Identity is firm: all three give the birth as 25 June 1925 at Crikvenica,
  matching the civil extract. **Whether he was forced or free is not established** — the three
  printed lines on the 1950 questionnaires that would say so (*restlos entlohnt*,
  *dienstverpflichtet*, *freier Arbeiter*) were all left blank, and the collection's title,
  "card file of persecutees", names a zone-wide registration file rather than a finding about
  anyone in it.

**Still resting on the tree:** no death certificate for Hedviga (Johannesburg 2001) or Ivan
(Senj 1995), and no record of Milka's first marriage. And the gravestone dates Ljubomir's birth to
**1891** where the register says **1 March 1892**; the archive follows the register and says so.
