# Findings that belong to other archives, not this one

This archive publishes nine surname groups around **Hedviga Blažević**. Working
through its own material turns up faults in records that belong to the
**Defranceski**, **Falco**, **D'Arcy**, **Lerena** and **Booyzen** archives, which
share the same MyHeritage tree. They are written down here rather than fixed,
because they are not this archive's to fix — and rather than left in a commit
message, because nobody reads those.

**Nothing below has been changed in the tree.**

---

## Defranceski

### Božica Blašković has her husband's dates

`Bozica Blaskovic` is entered as **born 3 December 1911** and **died 18 May 1994**.
Her husband `Josip Petar "Pepo/Pepe" Defranceski` is entered as **born 3 December
1911** and **died 18 May 1980**.

The same day *and* the same month, in both events, for two different people. Two
people do not share a birthday and a death-day.

Her **years** are independently confirmed — the Crikvenica gravestone reads
`BOŽICA 1911–1994` — so it is the **days and months** that have been copied across
from his record. The stone gives no finer detail, so the true dates are unknown
and should be blanked rather than guessed.

*Found 13 September 2026, reading the Crikvenica grave photograph (MyHeritage
media 4503717) against the tree.*

### The Crikvenica grave is a Defranceski plot and is not on any site

MyHeritage media **4503717** and **4503459** photograph the family grave at
Crikvenica. Seven people are cut into it and six are Defranceski:

| On the stone | In the tree |
|---|---|
| ANA DE. FRANCESCHI ✻19 IX 1863 ✝28 V 1936 | Ana Kalanj — **the birth date on the stone is wrong**, see below |
| JOSIP DE. FRANCESCHI | Josephus "Josip" de Franceschi |
| RUŽA JARMACKI rođena DEFRANCESCHI ✻1903 ✝1939 | Ruža de Franceschi, m. Miro Jarmacky |
| ANT… 1890 · URSULA 1895 | Ante Defranceski b. 20 Jan 1890, Ursula Kovačina 1895–1975 |
| PEPE 1911–1980 · BOŽICA 1911–1994 | Josip Petar "Pepe" Defranceski, Božica Blašković |
| TONI 1937–1984 | Anton "Braco" Defranceski, 16 Nov 1937 – 17 Jan 1984 |

Only **Ana Kalanj** is published in the Blažević archive, so the grave is
effectively undocumented on any site. It is three generations in one photograph.

### Ana Kalanj's gravestone birth date is wrong, and the register proves it

The stone says **19 September 1863**. Her baptism — *Anno Domini 1864*, no. 2,
*Anna, legitima, Josephus Kalanj et Rosalia nata Perković ejus uxor*, at
**Klenovica N° 22** — gives **3 January 1864**, baptised 6 January. The tree
already has the correct date; the stone does not.

### Šestan is attached to the Defranceski line through a node marked "not real"

Fifty-five Šestani of **Gologorica, Istria** are published in the *Blažević*
archive. Their only route to anyone is through **Defranceschi**, and the path
crosses an entry called `Grah's for Investigation (not real)`. Remove it and all
55 are unreachable.

They are far more plausibly a **Defranceski** matter than a Blažević one, and
somebody there may know why the investigation was opened.

---

## Anyone sharing the tree

### Sorting labels are still acting as parents

Twenty-one entries like `Unknown Sorting Working Blažević`,
`Senj - Unknown To be sorted Prpic` and `Brothers [of Josephus] Žubrinić` sit in
the tree **in the father's slot**. In the Blažević archive alone, 218 published
people hang off one and 74 have no other parent at all.

Two observations worth passing on:

1. **Un-publishing them is not enough.** They were hidden from that archive's
   register months ago and went on acting as parents in every tool that asks
   whether a person has one — which made its Žubrinić fragment count wrong by 25.
2. **The specific ones are worth keeping, the vague ones are not.** Labels
   carrying a house number or a date range agree with the children's own records
   **8 times out of 8**. Labels carrying only a town agree **5 times out of 18**.

---

## Defranceski — a whole work-list row, handed over 20 September 2026

### The Šestani were never this archive's family

**Work list row 35** — *«Gologorica — twenty-four Šestani, and not one direct
ancestor»* — ran for two sittings before anyone asked why a **Šestan** row was
in a **Blažević** archive.

`tools/ancestry.py` carries eight surnames and **`sestan` is one of them**, so
55 Šestani are published here. But:

* **25 of the 55 have a DEFRANCESCHI mother** — Joanna (10 children),
  Sancta-Alexandra (9), Rosa (6).
* **No Šestan connects to Hedviga through any published person at all.** In the
  full tree the nearest is **ten steps**:

      Hedviga → married Ivan Anton Defranceski → up five Defranceschi
      generations → (unnamed) → «Grah's for Investigation (not real)»
      → «Gologorica Grah» → Josephus Grah 1864 → married Rosa Sestan 1872

* **Two of those links are sorting buckets**, and `buckets.py` already calls one
  of them not a person.

So they are reached through Hedviga's **husband's** family, and then only
through a node this archive itself says is not real. **Your queue already had
the corroboration**: Forebears gives Gračišće as *Jugovac 489, **Šestan 316**,
Pauro 234* — the second commonest surname in the village.

**The findings went to `TheDefranceski`, commit `1cbcea8`**, appended to
`notes/QUEUE.md`: Gologorica is not a catalogued parish (tested against a
nonsense control, because that catalogue pads every result with filler); **Pazin
koha:725172 reaches 1582** with films listed; the Šestan baptisms are **indexed
under PISINO and invisible under «Pazin»**; nothing yet places the 23 Gologorica
Šestani in that book, so **the film is not yet worth a sitting**; plus a death
and a married name for **Elisabetha Sestan**, and **«Gologorica Grah»** — a
village name sitting in a given-name field, on your line.

### And one question left open, because it is not ours

**Should `sestan` stay in this archive's eight-surname scope list?** Removing it
would unpublish 55 people and is a decision about what this archive is for.
**Nothing has been changed.**
