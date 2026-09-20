# Three «found» people were in the tree all along

**21 September 2026.** This archive began publishing **blood** rather than a list of eight
surnames. The reason was a question about the Kosina; the first thing it actually did was
settle three standing candidates in `found.psv`.

**`found.psv` holds people read out of a register whom the family tree does not have.** That
is the rule, and it was being applied against **the published set** — which was never the
whole tree. A person could be in the GEDCOM, related by blood, and still count as «not in
the tree» because their surname was not one of the eight.

**Three of them were exactly that.**

| stood in found.psv as | is | |
|---|---|---|
| **Mare Luckinicha**, bapt. 13 April 1725 — *«CANDIDATE elder sister of ahnentafel 105»* | `mare-luckinic`, **born 13 April 1725** to Vicentius Luckinić and Maria | same day, same father |
| **Anton Joanis Uroda**, bapt. 13 June 1780 — *«brother of ahnentafel 54»* | `anton-joanis-uroda`, **born 13 June 1780** to Georgi and Maria Uroda | same day, same parents |
| **Maria Rosaria Antic**, bapt. 4 October 1847 — *«daughter of ahnentafel 24 and 25»* | `maria-rosaria-antic`, **born 4 October 1847** to Josephum Antić and Maria Jelličić | same day, same parents |

**None of this is a new discovery about any of them.** The readings were right, the
identifications were right, and the candidate rows said precisely who they were. **What
changed is that the archive can now see them**, so a candidate becomes a person and a
`found.psv` row becomes a **reading**. All three are in `readings.psv` now, and out of
`found.psv`.

## And one settle went stale, which is the part worth keeping

`foundcheck.py` flags a found person who resembles somebody published, and a **SETTLED**
list records the ones a human has decided about. Maria Rosaria Antić was settled with this
reason:

> *«ahnentafel 24 has no children published at all, so there is nothing to match her
> against; the name-and-year candidates are other families»*

**That was true when it was written and false the moment the scope changed.** He has a
published child now — **her**.

**A settle that names the STATE OF THE ARCHIVE rather than a fact about the people has a
shelf life**, and nothing was watching it. The entry is gone and the warning is in
`foundcheck.py` beside the list. The other settles are about parents and surnames — facts
about people — and they do not rot.

## What it cost to find

**Nothing.** `foundcheck` refused the build, which is what it is for. Six rows came up
unsettled, four were the day's new Kosina research resembling strangers on a given name,
and **two were these**. The third, Mare Luckinić, was caught by the same gate an hour
earlier.

**A gate that fires when the ground moves under it is worth more than one that only fires
on a typo.**
