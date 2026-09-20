# Row 35, closed with one catalogue search — and the book it found is the
# oldest this archive has ever reached

*20 September 2026. The row said «one catalogue search decides whether it is
reachable or whether it joins the unreachable list honestly». It was one
search, and the answer is neither of those.*

---

## Gologorica is not in the catalogue

`parishes.psv` has carried **Gologorica** since the beginning with *unknown* in
all three range columns and the note *«Istria — likely a different collection
entirely»*. `targets.json` puts **23 Šestani** behind it. It is the only parish
in the table never resolved at all.

**It is not a catalogued parish.** Searched under four forms — *Gologorica*,
*Gollogorizza*, *Gologorizza*, and the modern municipality *Cerovlje* — and
every one returns nothing.

**And that zero was tested, not assumed.** This catalogue API returns matches
first and then **pads the result with a constant filler list** — a Staffordshire
map, a Wagler family history, a Hungarian Presbyterian church in Hamilton. A
careless reader sees thirty rows and calls it a hit.

    q.keywords=Karlobag            koha:655222 «Matična knjiga, 1691-1861», then filler
    q.keywords=Gologorica          filler only
    q.keywords=zzzzqqqnotaplace    filler only — BYTE-IDENTICAL to Gologorica

**Gologorica's result is the same as a nonsense string's.** That is what makes
it a zero rather than a guess, and it is the same discipline the FindMyPast work
needed when four surnames were briefly recorded as returning nothing.

## Pazin is, and it reaches 1582

Gologorica sits in the **Pazin** district, about ten kilometres from the town.
The town's registers are catalogued, and they are extraordinary:

**`koha:725172` — «Matična knjiga, 1582-1882»**, filmed by the Genealogical
Society of Utah in 1997 from the **Hrvatski državni arhiv u Zagrebu**:

| | |
|---|---|
| **Births** | 1582, 1614–1624, 1645, 1643–1685, 1685–1847, 1847–1882 |
| **Marriages** | 1597–1635, 1656–1852, 1812–1847 |
| **Deaths** | 1655–1691, 1692–1847 |

and **`koha:725059`** adds births 1656–1722 and 1744–1822.

**Births from 1582.** The earliest register this archive has had access to
until today is **Novi Vinodolski, 1650** — and row 32 calls that *«the earliest
register in the estate»*. **Pazin is sixty-eight years older.**

## And the catalogue note is the sovereignty problem in one sentence

> *Metrical books (births, marriages, deaths) for **Mitterburg, Küstenland,
> Austria**; later **Pisino, Istria, Italy**; now **Pazin, Croatia**. Text in
> Italian and Latin.*

**One parish, three countries, three names** — and the catalogue files it under
all three: *Austria, Küstenland, Mitterburg*; *Italy, Pola, Pisino*; *Croatia,
Pazin*. This archive met the same thing four days ago from the other end, when
one man gave **«Zara, Austria»** on a 1919 filing and **«Italy»** on a 1924 one
because Rapallo happened in between.

**A searcher who knows only the Croatian name finds one third of this parish.**

## What is NOT established

**That the Šestani of Gologorica were written into the Pazin book.** A village
ten kilometres from a district town may have had its own chapel, or belonged to
a nearer parish that is itself uncatalogued. **The row moves from «never
resolved» to «the village is not a parish, and here is the district's book» —
which is a different and much better position, and not an answer.**
