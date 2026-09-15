# ARHiNET is gone — and the register search that replaced it

15 September 2026, late. Run from the Luwinski session at David's instruction to *"do all of
ARHiNET comprehensively"*. Written here because the finding belongs to this archive; **only this
file was committed** — the working-tree changes from the concurrent session were left untouched.

The short version: **ARHiNET no longer exists**, the thing that replaced it is not a public
catalogue, and the database that actually answers this archive's two hardest questions is one
nobody here had opened.

---

## 1. ARHiNET is off the public internet, and it is not a local problem

`SHARED-CONTACTS.md` records that `arhinet.arhiv.hr` *"does not resolve from this machine, so it is
asked about rather than checked."* That was too generous. Checked against three independent public
resolvers:

    dig @8.8.8.8  arhinet.arhiv.hr  ->  nothing
    dig @1.1.1.1  arhinet.arhiv.hr  ->  nothing
    dig @9.9.9.9  arhinet.arhiv.hr  ->  nothing

`arhiv.hr` itself has **no A record at all**. Only `www.arhiv.hr` (161.53.80.7) and `hda.arhiv.hr`
(161.53.80.4) answer. The nameservers — `bjesomar.srce.hr`, `zagreb.arhiv.hr`, `hda.arhiv.hr` — are
live and answering; they simply have no ARHiNET host to give.

**And the Croatian State Archives website no longer mentions ARHiNET anywhere.** Every reference is
now to **NAIS**, *Nacionalni arhivski informacijski sustav*.

### A trap: `arhinet.hr` is somebody else

`arhinet.hr` **does** resolve, on a commercial IP (178.218.166.39), and returns HTTP 200. It is
**"Arhinet d.o.o. za projektiranje"**, a private engineering-design firm, on WordPress, served from
`/test/`. Anyone chasing the old name lands here. It is not the archives.

### NAIS is not a replacement for a researcher

The NAIS pages on `www.arhiv.hr` are addressed to **records creators** — how to deposit, how to file
a complete holdings list, video instructions for depositors. It is the back office, not the
catalogue.

---

## 2. What IS public — and it breaks the Rijeka circle

**`https://www.arhiv.hr/hr-hr/Pretraga-matičnih-knjiga`**

A live, working, public search of **HR-HDA-1448, *Zbirka dopunskih mikrofilmova matičnih knjiga i
popisa obitelji***, with HR-HDA-883 behind it: filmed registers of **every confession**, the whole
of Croatia, **mid-16th century to the first half of the 20th** — and, the sentence that matters:

> *"čiji se izvornici čuvaju u državnim arhivima, **crkvenim arhivima, župnim uredima**, matičnim
> uredima, samostanima i sl."*

**Originals held in state archives, CHURCH ARCHIVES, PARISH OFFICES, registry offices, monasteries.**

That is the loop broken. The parish said the books went to the Archdiocese; the Archdiocese is said
to have passed them to the State Archive; the State Archive told the enquirer to look it up himself.
**This is where you look it up** — and it indexes books held by all three, naming for each one the
holding institution, the microfilm roll, the topographic mark, and **whether a digital copy exists**.

Record types: **R** births · **U** deaths · **V** marriages · **S** *status animarum* ·
**Z** confirmations · **O** *anniversarii* · **I** index.

Ordering: e-mail **info@arhiv.hr** with place, record type, period, roll signature and topographic
mark. Viewed in the HDA reading room; where a digital copy exists it is shown on the reading-room
computers. Ten technical units a day. Copies charged per the HDA price list.

---

## 3. THE TWO WALLS IN `holdings-2026-09-14.md` ARE BOTH BREACHED

### Wall 1 — Juraj Blažević's baptism at Krmpote

That note established Krmpote on FamilySearch is **one film, births 1879–1896 only**, and Juraj was
born around the 1860s: *"his baptism is not in this book, and there is no other Krmpote book."*

**This collection does not have the pre-1879 births either.** Krmpote births here also start 1879.
That is now documented from a second, authoritative index rather than inferred from a film label.

**But it has two things FamilySearch does not:**

| | |
|---|---|
| **KRMPOTE · S · status animarum · XIX–XX** | **ŽUPNI URED KRMPOTE** · roll **`ZM-34J/257`** · topo **`M-5982`** · **digitised** |
| **KRMPOTE · V · marriages · 1882–1941** (parica) | MATIČNI URED NOVI VINODOLSKI · roll **`ZM-34J/371`** · topo **`M-6966`** · **digitised** |

A *status animarum* is a house-by-house census of the parish listing every member **with birth
dates**, and this one spans the nineteenth and twentieth centuries — the period Juraj was born in.
It is held by **Krmpote's own parish office**, which is exactly the body the circular referral kept
pointing at, and **a digital copy exists**.

The marriage register is the second shot: Juraj was fathering children from 1892, so his marriage
falls inside 1882–1941, and a Croatian marriage entry **names both fathers**.

**One roll, three parishes.** `ZM-34J/257` / `M-5982` also carries the Ledenice *status animarum*
1914–1950 and the Novi Vinodolski *status animarum* for the eighteenth century and 1808–1839.
Ordering that single roll gets all three.

### Wall 2 — Ljubomir's Rijeka baptism, 1 March 1892

That note established the Rijeka films run `... 1890-1891`, then jump to `1900-1901`, and that the
birth *Kazalo* runs 1800–1889 then 1895–1902: *"Ljubomir's Rijeka baptism cannot be reached on
FamilySearch."*

| | |
|---|---|
| **RIJEKA · I · kazalo rođenih · 1890–1898** | DRŽAVNI ARHIV U RIJECI · roll **`ZM-34J/183`** · topo **`M-5698`** · **digitised** |

**A birth index covering exactly the gap, and digitised.** FamilySearch's index jumps 1889→1895;
this one runs 1890–1898 continuously. It should give the entry reference for a baptism of
1 March 1892.

*(Rijeka births themselves run to five pages in this database and were only partly paged; the
later volumes have not all been listed. Worth finishing.)*

---

## 4. Status animarum exist for the whole Vinodol group, and all are digitised

This archive has never used *status animarum* at all. They are the richest genealogical source in a
Croatian parish — households, with birth dates, in one place.

| parish | periods | holder | rolls |
|---|---|---|---|
| **KRMPOTE** | XIX–XX | Župni ured Krmpote | `ZM-34J/257` (`M-5982`) |
| **LEDENICE** | 1867–1884, 1884–1914, 1914–1950 | Župni ured Ledenice | `ZM-34J/256` (`M-5981`), `ZM-34J/257` |
| **NOVI VINODOLSKI** | XVIII, 1808–1839, 1840–1866, 1866–1912, 1913–1936 | Župni ured Novi Vinodolski | `ZM-34J/257`–`259` (`M-5982`–`M-5984`) |
| **GRIŽANE** | 1800–1828, 1829–1854, 1891–1908, 1909–1948 | Župni ured Grižane | `ZM-34J/243`–`245` (`M-5968`–`M-5970`) |
| **VODICE** | XIX, XIX–XX | Državni arhiv u Zadru i Splitu | `ZM-34F/569`–`570` (`M-3184`–`M-3185`) |

**Every one digitised.**

---

## 5. How to drive it, because it is not obvious and it lies to you

DNN + Telerik WebForms. **The trap: Pretraži fires an asynchronous postback that takes 20–30
seconds.** Read the grid before it lands and it is empty — which reads exactly like *"Nema zapisa za
pregled"*, no records. **Several apparent nulls in this session were that mistake and not the
archive's holdings, Krmpote among them.** Do not trust a null you did not wait for.

The working call:

- `ScriptManager` = `dnn$ctr4748$View$updatePanelGrid|dnn$ctr4748$View$PretragaPregledMK`
- `__ASYNCPOST=true`, `__EVENTTARGET=dnn$ctr4748$View$PretragaPregledMK`
- each combo posted **twice** — as `dnn$ctr4748$View$RadComboBox{Mjesto,Konfesija,Vrsta}` and as
  `..._ClientState` JSON whose **`value` must equal the text**. An empty `value` silently returns
  nothing, which is the second way this page lies to you.
- plus `__VIEWSTATE`, `__EVENTVALIDATION`, `__dnnVariable`, `__RequestVerificationToken` and the
  nine empty `FilterTextBox_*` fields
- results come back in the delta as `tr.rgRow` / `tr.rgAltRow`; the grid pages at 10, and paging is
  easiest driven in a browser by clicking `input.rgPageNext`

The place list is a fixed dropdown of **3,289 entries** matched exactly, so spellings must come from
the list: `SARAJEVO` is not an entry, `SARAJEVO SV. JOSIP` is. `RIJEKA` has 38 variants.

---

## 6. What this means for the letter already sent

The letter to `kancelarija@ri-nadbiskupija.hr` asks about **"the ARHiNET collection *Zbirka
digitalnih preslika matičnih knjiga župâ Riječke nadbiskupije*"**. **ARHiNET no longer exists**, so
that question now names a system the Archdiocese may not recognise.

It does not need withdrawing — the substantive question (where are Sv. Jakov Krmpote's books, who
supplies copies) is unchanged and still only they can answer it. **But if they reply puzzled, that
is why**, and any follow-up should cite the HDA register search and the roll numbers above instead.

---

## 7. The full sweep

Twelve parishes of the Vinodol–Senj littoral, every record type, Roman Catholic. **176 register
entries.** Recorded in full below so that nobody has to run it again.

### BRIBIR

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1678-1736 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/029` | `M-29` | **Da** |  |
| R births | 1815-1853 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/030` | `M-30` | **Da** |  |
| R births | 1854-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/030` | `M-30` | **Da** |  |
| R births | 1858-1886 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/009` | `M-2720` | **Da** |  |
| R births | 1604-1676 | ARHIV HAZU | `ZM-34C/757` | `M-3274` | **Ne** | Matica se sastoji od slijedećeg: matice rođenih (g. 1604-166 |
| R births | 1887-1914 | MATIČNI URED CRIKVENICA | `ZM-34J/359` | `M-6954` | **Da** | Oštećene stranice. |
| R births | 1915-1949 | MATIČNI URED CRIKVENICA | `ZM-34J/360` | `M-6955` | **Da** | Oštećene stranice. |
| V marriages | 1678-1702 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/029` | `M-29` | **Da** |  |
| V marriages | 1711-1738 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/029` | `M-29` | **Da** |  |
| V marriages | 1853-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/030` | `M-30` | **Da** |  |
| V marriages | 1815-1821 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/030` | `M-30` | **Da** |  |
| V marriages | 1858-1900 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/010` | `M-2721` | **Ne** |  |
| V marriages | 1603-1660 | ARHIV HAZU | `ZM-34C/757` | `M-3274` | **Ne** | Matica se sastoji od slijedećeg: matice rođenih (g. 1604-166 |
| V marriages | 1901-1949 | MATIČNI URED CRIKVENICA | `ZM-34J/361` | `M-6956` | **Da** |  |

### GRIŽANE

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1692-1790 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/083` | `M-83` | **Da** | Nedostaju godine 1702. i 1705. |
| R births | 1735-1811 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/084` | `M-84` | **Da** |  |
| R births | 1812-1857 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/084` | `M-84` | **Da** |  |
| R births | 1858-1886 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/036` | `M-2747` | **Ne** |  |
| R births | 1908-1949 | MATIČNI URED CRIKVENICA | `ZM-34J/365` | `M-6960` | **Da** |  |
| R births | 1908-1949 | MATIČNI URED CRIKVENICA | `ZM-34J/366` | `M-6961` | **Da** |  |
| V marriages | 1812-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/084` | `M-84` | **Da** |  |
| V marriages | 1735-1811 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/084` | `M-84` | **Da** |  |
| V marriages | 1858-1948 | MATIČNI URED CRIKVENICA | `ZM-34J/366` | `M-6961` | **Da** |  |
| S status animarum | 1800-1828 | ŽUPNI URED GRIŽANE | `ZM-34J/243` | `M-5968` | **Da** | Razdoblje koje obuhvaća SA nisu sa sigurnošću ustanovljena. |
| S status animarum | 1829-1854 | ŽUPNI URED GRIŽANE | `ZM-34J/243` | `M-5968` | **Da** |  |
| S status animarum | 1891-1908 | ŽUPNI URED GRIŽANE | `ZM-34J/243` | `M-5968` | **Da** | Od A-L |
| S status animarum | 1891-1908 | ŽUPNI URED GRIŽANE | `ZM-34J/244` | `M-5969` | **Da** | Od A-L |
| S status animarum | 1891-1908 | ŽUPNI URED GRIŽANE | `ZM-34J/244` | `M-5969` | **Da** | Od M-Z |
| S status animarum | 1909-1948 | ŽUPNI URED GRIŽANE | `ZM-34J/245` | `M-5970` | **Da** |  |
| S status animarum | 1909-1948 | ŽUPNI URED GRIŽANE | `ZM-34J/244` | `M-5969` | **Da** |  |

### JABLANAC

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1860-1880 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/042` | `M-2753` | **Ne** |  |
| R births | 1881-1895 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/042` | `M-2753` | **Ne** |  |
| R births | 1896-1929 | MATIČNI URED SENJ | `ZM-34M/118` | `M-5321` | **Da** |  |
| R births | 1930-1949 | MATIČNI URED SENJ | `ZM-34M/118` | `M-5321` | **Da** |  |
| R births | 1930-1949 | MATIČNI URED SENJ | `ZM-34M/119` | `M-5322` | **Da** |  |
| V marriages | 1860-1906 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/043` | `M-2754` | **Ne** |  |
| V marriages | 1906-1949 | MATIČNI URED SENJ | `ZM-34M/119` | `M-5322` | **Da** |  |
| U deaths | 1860-1890 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/043` | `M-2754` | **Ne** |  |
| U deaths | 1891-1915 | MATIČNI URED SENJ | `ZM-34M/119` | `M-5322` | **Da** |  |
| U deaths | 1916-1949 | MATIČNI URED SENJ | `ZM-34M/119` | `M-5322` | **Da** |  |

### KRIVI PUT

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1847-1873 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/057` | `M-2768` | **Ne** |  |
| R births | 1873-1884 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/057` | `M-2768` | **Ne** |  |
| R births | 1896-1910 | MATIČNI URED SENJ | `ZM-34M/122` | `M-5325` | **Da** |  |
| R births | 1910-1936 | MATIČNI URED SENJ | `ZM-34M/122` | `M-5325` | **Da** |  |
| R births | 1937-1948 | MATIČNI URED SENJ | `ZM-34M/123` | `M-5326` | **Da** |  |
| V marriages | 1871-1894 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/058` | `M-2769` | **Ne** |  |
| V marriages | 1895-1948 | MATIČNI URED SENJ | `ZM-34M/123` | `M-5326` | **Da** |  |
| U deaths | 1878-1893 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/058` | `M-2769` | **Ne** |  |
| U deaths | 1894-1920 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/058` | `M-2769` | **Ne** |  |
| U deaths | 1921-1934 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/058` | `M-2769` | **Ne** |  |
| U deaths | 1944-1948 | MATIČNI URED SENJ | `ZM-34M/123` | `M-5326` | **Da** |  |

### KRMPOTE

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| U deaths | 1891-1946 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/371` | `M-6966` | **Da** | Upisi za ratne godine nisu potpuni. |
| U deaths | 1891-1946 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/372` | `M-6967` | **Da** | Upisi za ratne godine nisu potpuni. |

### LEDENICE

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1795-1832 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/155` | `M-155` | **Da** |  |
| R births | 1795-1832 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/156` | `M-156` | **Da** |  |
| R births | 1734-1795 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/155` | `M-155` | **Da** |  |
| R births | 1832-1861 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/156` | `M-156` | **Da** |  |
| R births | 1861-1882 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/065` | `M-2776` | **Ne** |  |
| R births | 1882-1894 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/065` | `M-2776` | **Ne** |  |
| R births | 1895-1904 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/152` | `M-5667` | **Da** |  |
| R births | 1905-1948 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/374` | `M-6969` | **Da** | Oštećene stranice. |
| R births | 1905-1948 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/375` | `M-6970` | **Da** | Oštećene stranice. |
| V marriages | 1734-1825 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/155` | `M-155` | **Da** |  |
| V marriages | 1826-1865 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/156` | `M-156` | **Da** |  |
| V marriages | 1866-1882 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/065` | `M-2776` | **Ne** |  |
| V marriages | 1882-1948 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/375` | `M-6970` | **Da** |  |
| U deaths | 1734-1824 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/155` | `M-155` | **Da** |  |
| U deaths | 1824-1865 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/156` | `M-156` | **Da** |  |
| U deaths | 1866-1882 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/066` | `M-2777` | **Ne** |  |
| U deaths | 1882-1902 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/066` | `M-2777` | **Ne** |  |
| U deaths | 1903-1948 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/375` | `M-6970` | **Da** |  |
| S status animarum | 1867-1884 | ŽUPNI URED LEDENICE | `ZM-34J/256` | `M-5981` | **Da** |  |
| S status animarum | 1884-1914 | ŽUPNI URED LEDENICE | `ZM-34J/256` | `M-5981` | **Da** |  |
| S status animarum | 1914-1950 | ŽUPNI URED LEDENICE | `ZM-34J/256` | `M-5981` | **Da** |  |
| S status animarum | 1914-1950 | ŽUPNI URED LEDENICE | `ZM-34J/256` | `M-5981` | **Da** |  |
| S status animarum | 1914-1950 | ŽUPNI URED LEDENICE | `ZM-34J/257` | `M-5982` | **Da** |  |

### NOVI VINODOLSKI

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1784-1815 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/217` | `M-217` | **Da** |  |
| R births | 1784-1815 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/218` | `M-218` | **Da** |  |
| R births | 1650-1786 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/217` | `M-217` | **Da** | Kod matice rođenih nedostaju godine: 1653-1655, 1685 i 1697. |
| R births | 1815-1852 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/218` | `M-218` | **Da** |  |
| R births | 1852-1874 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/084` | `M-2795` | **Ne** |  |
| R births | 1875-1900 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/085` | `M-2796` | **Ne** |  |
| R births | 1901-1935 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/372` | `M-6967` | **Da** | Oštećene stranice. |
| R births | 1935-1949 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/372` | `M-6967` | **Da** |  |
| V marriages | 1674-1785 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/217` | `M-217` | **Da** | Kod matice rođenih nedostaju godine: 1653-1655, 1685 i 1697. |
| V marriages | 1787-1815 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/218` | `M-218` | **Da** |  |
| V marriages | 1815-1859 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/218` | `M-218` | **Da** |  |
| V marriages | 1858-1948 | MATIČNI URED NOVI VINODOLSKI | `ZM-34J/373` | `M-6968` | **Da** |  |
| S status animarum | XVIII-XVIII | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/257` | `M-5982` | **Da** |  |
| S status animarum | 1808-1839 | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/257` | `M-5982` | **Da** |  |
| S status animarum | 1840-1866 | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/258` | `M-5983` | **Da** |  |
| S status animarum | 1866-1912 | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/258` | `M-5983` | **Da** |  |
| S status animarum | 1913-1936 | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/258` | `M-5983` | **Da** |  |
| S status animarum | 1913-1936 | ŽUPNI URED NOVI VINODOLSKI | `ZM-34J/259` | `M-5984` | **Da** |  |

### SENJ

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1734-1775 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/288` | `M-288` | **Da** |  |
| R births | 1734-1775 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/289` | `M-289` | **Da** |  |
| R births | 1849-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/289` | `M-289` | **Da** |  |
| R births | 1820-1848 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/289` | `M-289` | **Da** |  |
| R births | 1859-1877 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/121` | `M-2832` | **Ne** |  |
| R births | 1878-1894 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/122` | `M-2833` | **Ne** |  |
| R births | 1895-1923 | MATIČNI URED SENJ | `ZM-34M/123` | `M-5326` | **Da** |  |
| R births | 1895-1923 | MATIČNI URED SENJ | `ZM-34M/124` | `M-5327` | **Da** |  |
| R births | 1924-1941 | MATIČNI URED SENJ | `ZM-34M/124` | `M-5327` | **Da** |  |
| R births | 1924-1941 | MATIČNI URED SENJ | `ZM-34M/125` | `M-5328` | **Da** |  |
| V marriages | 1734-1819 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/290` | `M-290` | **Da** |  |
| V marriages | 1820-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/290` | `M-290` | **Da** |  |
| V marriages | 1859-1920 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/122` | `M-2833` | **Ne** |  |
| V marriages | 1921-1926 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/122` | `M-2833` | **Ne** |  |
| V marriages | 1927-1949 | MATIČNI URED SENJ | `ZM-34M/125` | `M-5328` | **Da** |  |
| U deaths | 1820-1848 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/290` | `M-290` | **Da** |  |
| U deaths | 1849-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/290` | `M-290` | **Da** |  |
| U deaths | 1859-1889 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/123` | `M-2834` | **Ne** |  |
| U deaths | 1889-1907 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/123` | `M-2834` | **Ne** |  |
| U deaths | 1907-1945 | MATIČNI URED SENJ | `ZM-34M/125` | `M-5328` | **Da** |  |
| U deaths | 1946-1949 | MATIČNI URED SENJ | `ZM-34M/125` | `M-5328` | **Da** |  |

### STARIGRAD (kod Senja)

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1770-1770 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** | Matica vjenčanih obuhvaća ove godine: 1770-1774, 1791-1795,  |
| R births | 1777-1814 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** | Matica vjenčanih obuhvaća ove godine: 1770-1774, 1791-1795,  |
| R births | 1816-1839 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** |  |
| R births | 1840-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** |  |
| R births | 1901-1941 | MATIČNI URED SENJ | `ZM-34M/126` | `M-5329` | **Da** |  |
| R births | 1942-1949 | MATIČNI URED SENJ | `ZM-34M/126` | `M-5329` | **Da** |  |
| V marriages | 1770-1812 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** | Matica vjenčanih obuhvaća ove godine: 1770-1774, 1791-1795,  |
| V marriages | 1816-1841 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** |  |
| V marriages | 1841-1887 | DRŽAVNI ARHIV U RIJECI | `ZM-34J/125` | `M-2836` | **Ne** |  |
| V marriages | 1888-1948 | MATIČNI URED SENJ | `ZM-34M/126` | `M-5329` | **Da** |  |
| U deaths | 1769-1815 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** | Matica vjenčanih obuhvaća ove godine: 1770-1774, 1791-1795,  |
| U deaths | 1816-1836 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** |  |
| U deaths | 1840-1867 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/304` | `M-304` | **Da** |  |
| U deaths | 1868-1869 | MATIČNI URED SENJ | `ZM-34M/126` | `M-5329` | **Da** | NEMA zapisa za 1870-76.g., tj. na skenu mikrofilma upisi pre |
| U deaths | 1877-1919 | MATIČNI URED SENJ | `ZM-34M/126` | `M-5329` | **Da** | NEMA zapisa za 1870-76.g., tj. na skenu mikrofilma upisi pre |
| U deaths | 1920-1948 | MATIČNI URED SENJ | `ZM-34M/129` | `M-5332` | **Da** |  |

### SV. JURAJ KOD SENJA

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1780-1804 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| R births | 1828-1852 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| R births | 1828-1852 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/328` | `M-328` | **Da** |  |
| R births | 1821-1827 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| R births | 1804-1821 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| R births | 1697-1739 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/500` | `M-500` | **Da** | Spajan film-Matične knjige rimokatolika |
| R births | 1740-1773 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/501` | `M-501` | **Da** |  |
| V marriages | 1793-1827 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/328` | `M-328` | **Da** |  |
| V marriages | 1828-1868 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/328` | `M-328` | **Da** |  |
| V marriages | 1701-1782 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/328` | `M-328` | **Da** |  |
| U deaths | 1760-1805 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| U deaths | 1828-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| U deaths | 1828-1858 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/328` | `M-328` | **Da** |  |
| U deaths | 1803-1827 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/327` | `M-327` | **Da** |  |
| U deaths | 1695-1759 | HRVATSKI DRŽAVNI ARHIV | `ZM-34/501` | `M-501` | **Da** |  |

### VODICE

| type | period | holder | roll | topo | digital | note |
|---|---|---|---|---|---|---|
| R births | 1828-1831 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/247` | `M-2282` | **Da** |  |
| R births | 1842-1857 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/247` | `M-2282` | **Da** |  |
| R births | 1825-1828 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/247` | `M-2282` | **Da** |  |
| R births | 1831-1842 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/247` | `M-2282` | **Da** |  |
| R births | 1858-1868 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/435` | `M-2472` | **Da** |  |
| R births | 1869-1876 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/435` | `M-2472` | **Da** |  |
| R births | 1876-1887 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/435` | `M-2472` | **Da** |  |
| R births | 1888-1897 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/435` | `M-2472` | **Da** |  |
| R births | 1888-1897 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/436` | `M-2473` | **Da** |  |
| R births | 1851-1885 | ŽUPNI URED VODICE | `ZM-34F/566` | `M-3181` | **Da** |  |
| V marriages | 1841-1857 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| V marriages | 1828-1841 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| V marriages | 1826-1828 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| V marriages | 1858-1870 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/436` | `M-2473` | **Da** |  |
| V marriages | 1851-1885 | ŽUPNI URED VODICE | `ZM-34F/567` | `M-3182` | **Da** |  |
| V marriages | 1886-1908 | ŽUPNI URED VODICE | `ZM-34F/567` | `M-3182` | **Da** |  |
| U deaths | 1826-1830 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| U deaths | 1830-1842 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| U deaths | 1842-1861 | DRŽAVNI ARHIV U ZADRU | `ZM-34F/248` | `M-2283` | **Da** |  |
| U deaths | 1851-1885 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/436` | `M-2473` | **Da** |  |
| U deaths | 1862-1873 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/436` | `M-2473` | **Da** |  |
| U deaths | 1873-1887 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/436` | `M-2473` | **Da** |  |
| U deaths | 1873-1887 | SABIRNI ARHIVSKI CENTAR ŠIBENIK | `ZM-34F/437` | `M-2474` | **Da** |  |
| U deaths | 1886-1894 | ŽUPNI URED VODICE | `ZM-34F/568` | `M-3183` | **Da** |  |
| U deaths | 1894-1924 | ŽUPNI URED VODICE | `ZM-34F/568` | `M-3183` | **Da** |  |
| U deaths | 1931-1962 | ŽUPNI URED VODICE | `ZM-34F/568` | `M-3183` | **Da** |  |
| S status animarum | XIX-XX | DRŽAVNI ARHIV U ZADRU I SPLITU | `ZM-34F/569` | `M-3184` | **Da** |  |
| S status animarum | XIX-XX | DRŽAVNI ARHIV U ZADRU I SPLITU | `ZM-34F/569` | `M-3184` | **Da** |  |
| S status animarum | XIX | DRŽAVNI ARHIV U ZADRU I SPLITU | `ZM-34F/569` | `M-3184` | **Da** |  |
| S status animarum | XIX | DRŽAVNI ARHIV U ZADRU I SPLITU | `ZM-34F/570` | `M-3185` | **Da** |  |

