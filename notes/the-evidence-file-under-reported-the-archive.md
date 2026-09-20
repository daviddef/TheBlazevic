# The evidence file under-reported the archive

**20 September 2026.** This began as a request to check that everything researched had
reached the site. It found the opposite problem: **things that had reached the site had
never reached the evidence file.**

## It started with the worst possible case

This morning a note concluded that **ahnentafel 3's birth date could not be settled**
because «there is no image yet», and that «**one page**, and the archive's
second-most-important birth date is settled either way».

**The page had been read years ago and is published on this site.** `/milka` carries the
register image itself under the heading *Senj baptisms, page 122, entry 96*, with the entry
transcribed: **born 9 October 1886, baptised 17 October**. The register writes the birth
**«1886, 9/10»**. Her **1907 marriage entry** repeats it as **«9/X»** — Roman ten — thirteen
years later in a different hand.

**Two entries, two hands, both October.** The conflict was never open. The index is wrong
by one month, carried to both columns of one entry.

**The note had checked the index against the TREE and never against THIS ARCHIVE.**

## And it was not one slip

Holding `site/src/data/corrections.json` against `sources/readings.psv` turned up **thirteen
more people** whose correction quotes a register — page and entry number, occupations,
Croatian phrases read off the line — **with no reading row at all.**

**Including the document the whole archive was built around.** The marriage of
**8 December 1920**, Senj *Vjenčani* **page 366, entry 41**, re-read at full resolution
under ark `3:1:3QSQ-G99X-17M7`, with **its own page on this site** — and neither
**ahnentafel 2** nor **ahnentafel 4** had a reading of any kind.

| | |
|---|---|
| **ahn 2** Ljubomir Blažević | the 1920 marriage — **no readings at all** |
| **ahn 4** Juraj Blažević | named in it as «Juraj Blažević», annotated **«mrt.»** — dead before December 1920 — **no readings at all** |
| **ahn 5** Tereza Žubrinić | named in the same entry, annotated «mrt.»; had only a gravestone |
| Antonija, Katica, Terezija Blažević | their own Senj marriages of 1918, 1919 and 1913 |
| Tereza Papić | Senj deaths p. 162 no. 51, the entry that **names the father the tree leaves blank** |
| Ana, Franciska, Zora, Ivan Kalanj | four Novi Vinodolski baptisms found loose in the family's photo library |
| Anica Kalanj, 1864 | the entry reading «**Brinjensis parochiae ruricolae**» |

**Fourteen rows added.** `readings.psv` went from 93 rows to 108, and the dates it can hold
against the tree went from **19 to 24 — all still agreeing.**

## Why it went unseen, which is the part worth keeping

`coverage.py` grades a person `read` from **either** a reading row **or** a citation keyed
on the GEDCOM id. **The corrections carried the citation.** So every one of these people
graded correctly, the site showed their documents, and the archive's own record of what it
had read quietly did not hold them.

**Two paths to «read», and only one of them is the archive's record of its own work.** That
is the same fault that hid eight orphaned slugs earlier today — a working path masking a
broken one — and it is the third time in one day that a second, independent route to the
same conclusion has concealed a gap.

## The check

`tools/publishedcheck.py` holds every correction that quotes a register against
`readings.psv`. **It is a report and not a gate**, for one honest reason: a correction can
legitimately have no reading. **Ahnentafel 20's says «the 1845 baptism is *not* his»** — a
disproof. Recording that as a reading for him would assert the opposite of what it found.
The tool recognises disproofs and lists them separately.

It now reports **21 corrections quoting a register, 1 disproof, and nothing missing.**

## What this says about the other direction

The request that started this was «make sure everything researched is on the site». **One
thing genuinely was not**: `sources/familysearch/indexed.psv`, the table that decides how
every register row is planned, was read by no tool and shown on no page. It is now at
[`/indexed/`](https://daviddef.github.io/TheBlazevic/indexed/).

**But the traffic ran the other way too, and harder.** The site was ahead of the evidence
file, and a note written this morning reached a false conclusion because it never looked
there. **Checking that research reaches the site is half the job. The other half is
checking that the site's evidence is in the files the tools read.**
