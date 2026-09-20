# Blasevic is the same family. Subrinic is a sentence.

**20 September 2026.** `namefold.py` clusters surname spellings so that typing one reaches
the others. It folds **accent differences** on its own authority — *Blazevic* for
*Blažević* is one word two keyboards wrote differently — and it **refuses to fold a letter
change** without a human saying so, because *Sanzone* for *Sansone* is a claim about a
family and not a claim about a keyboard.

It had two waiting. **They are not the same kind of thing, and only one of them is about a
family at all.**

## Blasevic → Blažević: accepted, on the tree's own evidence

**52 tokens.** The archive's own GEDCOM settles it. There is a sibling set of **twenty-seven**
children at Mrzli Dol in which **twenty-five are written Blažević** and two — **Ana** and
**Maria** — are written **Blasevic**:

    … Ana Blažević · Ana BLASEVIC · Maria BLASEVIC · Marija Blažević · Stanka Blažević …

**Same parents, same household, one list.** Whoever entered the tree wrote two of the
children with an *s*. That is not two families; it is one family and two keystrokes, and
the folding rule exists for exactly this.

It is corroborated from outside as well: the FindMyPast target list has carried
*«Blazevic / Blasevich / Blazevich»* as one family's forms since the trial, and the
emigration catch holds **100 tokens of Blasevich**.

## Subrinic → Žubrinić: accepted, and it is not what it looks like

**2 tokens — and neither is anybody's name.** Both sit inside a sentence this archive wrote
about a search that **failed**:

> «Zubrinich **191**, Zubrinic **119**, Zubrinick **10**, Zubrinec **1**;
> **Subrinic**, Xubrinich and Zubrinicz **are zero**.»

One copy in `worklist.json`, one in `searched.json`. **There is no Subrinic in any record
this archive holds.** The form exists here only as a guess that was tested and came back
empty — written down precisely so nobody guesses it again.

**It is folded anyway, and the reason is worth stating.** The tool's own rule is that
*«folding is allowed to miss; it is not allowed to join»*. Folding *Subrinic* **joins
nothing**, because there is no Subrinic family to join to a Žubrinić one. All it does is
make a reader who types the spelling this archive already knows people guess reach the rows
they were looking for. **That is the fold working as intended on a word that arrived by
accident.**

## And the accident is worth reporting to the kit

`corpus()` scans **every `*.json` in the data directory** for capitalised words — which in
this estate includes `worklist.json` and `searched.json`, the archive's **narrative**. So
the folder is reading prose, and a surname that appears only in a sentence **about** a
surname enters the corpus as though it were a record.

**Here that is harmless.** Elsewhere it need not be. An archive whose work list discusses a
neighbouring family by name — «the other Roos family, who are not ours» — would offer that
name to the folder with the same confidence as a register row, and the tool's one
catastrophic failure mode is a fold that joins two families. **The counts are what save it:
2 tokens against 1,059 announces itself as not-a-family to anyone reading the output, which
is why the tool prints every cluster and waits.**

**A suggestion rather than a patch**, since the kit is shared: `corpus()` could take the
list of files to read, or skip a declared set of narrative files, so that a fold is proposed
only from records. `perpič → perpic` was in the same run and is an ordinary accent fold,
accepted without question.

---

## The kit fixed it, and Subrinic will drop out on its own

**Same day.** The suggestion above was taken: `corpus()` now skips sixteen narrative
filenames, in archive-kit `66328a11`. On this archive that removes **Subrinic from the
clusters entirely** — which is the right answer, because it was never anybody's name, only
two tokens inside a sentence about a search that failed. On Booyzen it changes nothing:
thirteen clusters and seventy forms before and after.

**Nothing to undo here.** The fold is harmless and stays until the pinned kit reaches that
commit; `site/package.json` is managed by the fleet rollout and is not this session's file
to bump. **When the pin lands, re-run `namefold.py --root site --all` and expect one
proposal — Blasevic — where there were two.** The Blasevic decision is unaffected: it rests
on twenty-five siblings against two in the GEDCOM, not on the corpus scan.

**And the reasoning for keeping Subrinic was confirmed rather than overturned**: folding is
allowed to miss and not allowed to join, and there was no Subrinic family for it to join
anything to. The fix removes the *accident*, not the judgement.

---

## Done, and it came out as written

**21 September 2026.** The fleet rollout landed the fixed kit (pin
`2665be5e`). `namefold.py --root site --all` re-run against it:

**One `?` proposal where there were two.** *Blasevic* still waiting on a human;
**Subrinic gone from the clusters entirely**, and one line out of `namefold.json`.
Nothing else in the map moved.

**The prediction in the section above was the point of writing it.** A note that
says what will happen when somebody else's change lands is checkable when it does,
and this one was.
