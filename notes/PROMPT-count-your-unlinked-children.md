# A prompt for the other archives: your unlinked children are not one thing

**Copy everything below the line into any other family-research session.** It was written on
23 September 2026, after this estate nearly published 155 people on the strength of a percentage.

---

## Somebody has measured you against 100%, and the number is not what it looks like

Across this estate, person pages draw children and link the ones that have a page. Five archives
link **100%** of the children they draw. The Blažević archive linked **2,167 of 2,497 — 87%** — and
that 13% was put forward as the last real content gap in the estate, worth **330 new pages**.

**It was not 330 people, and it was not a gap.** Do this before you publish anything.

### 1. Count entries, then count people

A child is drawn on **each** published parent's page. So a child of two published parents is **two
entries and one person**. The Blažević shortfall was **330 entries → 182 distinct people**, and the
difference is nearly half.

**Report both numbers.** A cost quoted in entries is roughly double the truth.

### 2. Split the unlinked into three, because they are three different things

| what | Blažević | can it ever be a link? |
|---|---|---|
| **living people you withhold** | 64 | **no, and it must not be** |
| **sorting buckets / region labels** | 27 | **no — they are not people** |
| **real people outside your published surnames** | 155 | only if you change the rule |

The buckets look like this in the data: *«AUSTRIA: De Franceschi»*, *«ZAGREB Defranceski's»*,
*«Unknown Sorting Working Blažević»*. A page for one of those is a page for a filing category.
If your archive has a `/buckets/` page, it already knows about them.

### 3. Check whether the 100% archives are even playing the same game

**This is the part that inverts the comparison.** Falco links 100% of its children — and Falco
publishes a **name-only page for each of its 106 living people**, so every child has something to
point at. Blažević **withholds** living children entirely: an unnamed slot, no page, by design.

**The archive scoring lower was the one being more careful.** Before you treat a percentage as a
deficit, open the comparator's `people.json` and ask whether its living people have slugs. One line:

```python
rows = json.load(open("../Other Family/site/src/data/people.json"))
liv  = [r for r in rows if r.get("living")]
print(len(liv), "living;", sum(1 for r in liv if r.get("slug")), "of them have a page")
```

### 4. If the answer is "link them to a sibling archive", check there is something to link to

Blažević's account holder chose exactly that: don't publish the 46 Defranceschi children here, link
them into the Defranceski archive. **That archive publishes nine people** — the documented historical
figures of the name — and **none of the 46 is among them.** Zero name matches. The instruction was
sound and the target did not exist.

**An empty link would have looked like progress.** Say the half you cannot build, and name the
archive that owns it.

**And then say it to that archive, with the list.** The account holder's answer on 23 September was
that if the pages do not exist, **they should**. So the deliverable is not a shrug — it is a
hand-off file the other session can act on. Blažević wrote
[`notes/for-the-defranceski-archive.md`](https://github.com/daviddef/TheBlazevic/blob/main/notes/for-the-defranceski-archive.md):
42 named people, with dates and with the parent each is drawn under.

### What makes a hand-off worth acting on

**Lead with the ones you already hold a document for.** 27 of Blažević's 42 are already named in its
own pages and notes — so the estate has *read records* for them and still has no page. The example
that ends the argument:

> **Ruža de Franceschi, 10 December 1903 – 29 March 1939**, married Miro Jarmacky — transcribed off
> a gravestone on `/grave/`: *«RUŽA JARMACKI rođena DEFRANCESCHI ✻1903 †1939»*. **A birth date, a
> death date, a married name and a husband, read off a stone by this estate — and no page anywhere
> in it.**

Her seven brothers and sisters, children of **Anica «Ana» Kalanj** — a Kalanj who married a de
Franceschi — are in exactly the same position, all eight with dates. **Those are the pages to make
first**, because the evidence is already sitting in the estate.

### And two cautions to pass on with any list

**Check the parents before you draw them.** Most of Blažević's pre-1800 Defranceschi hang off
*«Gologorica Defranceschi»* — a sorting bucket, not a person. **The people are real; the parentage
is not evidence.** Publish the person, not the link.

**Expect repeated given names and do not merge them.** Four *Gian Giovanni Ivan Battista*, four
*Guiseppe Josephus Josip*, three *Maria*. A child who died was very often replaced by a later child
of the same name — which is also exactly how a records-matcher makes one person out of two.

### 5. Put the decision to the account holder yourself

A peer session relayed *"David said do them all"* to three archives at once, then retracted it: he
had said it about a four-item list in **that** session. **A peer cannot carry an approval** — it
cannot distinguish *"he considered this and said yes"* from *"he said yes to four things and this was
one of the words"*, and neither can you.

**Publication scope is the account holder's decision and not yours.** Ask in your own session, about
the thing you can describe — the count in *people*, the three-way split, what your rule becomes
afterwards, and what it costs. Then do what he says.

### 6. Two technical notes worth having first

**Check your `check:living` before you write rows in bulk.** Older kits swallowed an unparseable
data file and carried on — a truncated `people.json` dropped every living person it held and the
gate printed *«0 flagged in the data · ok»*. Demonstrate it on your own build: truncate a copy, run
the gate, see whether it notices. It should **FAIL and name the file and the parser's complaint**.

**And if your row floor moves, write it from a build you have just made**, with `ARCHIVE_OUT`
pointed at it and `git status` read first.

### 7. If a hand-off list arrives for YOUR surname, it is work, not correspondence

The other side of this. When another archive sends you a list of people of your name that it draws
and cannot link, **those are pages you are missing** — and somebody has already done the finding.
Publish them under your own rule, with your own living check, and tell the sending archive when the
slugs exist so its links can go in.

**Do not publish a name you hold no record for just to close somebody else's percentage.** That is
the same mistake in the other direction. Take the ones with dates and documents first.

### Report back with

* unlinked **entries** and unlinked **distinct people**, separately;
* the three-way split, with the bucket names quoted;
* whether your comparator publishes its living people;
* **the hand-off list you sent, and to which archive**;
* **what you did not publish, and why.**
