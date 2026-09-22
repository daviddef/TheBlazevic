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

### Report back with

* unlinked **entries** and unlinked **distinct people**, separately;
* the three-way split, with the bucket names quoted;
* whether your comparator publishes its living people;
* **what you did not publish, and why.**
