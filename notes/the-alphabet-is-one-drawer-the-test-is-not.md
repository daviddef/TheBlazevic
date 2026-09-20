# The alphabet is one drawer. The test for it is not.

**21 September 2026.** [Row 15](/worklist/) asked whether the fifteen Žubrinić «alphabet
nodes» — *«M Žubrinić Xubrinich Zubrinic»*, a card drawer typed in as a family — are only a
Žubrinić problem, since all seven archives share one GEDCOM and nothing had checked.

**Run against all 15,643 records, the answer is two answers, and they point opposite ways.**

## The problem is unique to Žubrinić

A **sibling set of three or more in which *every* member is alphabet-shaped and dateless**
fires **once in the entire estate**: family `@F501632@`, the fifteen Žubrinić, with
**eighty-two real people published as their children.**

Nothing else comes close. Every other sibling set containing an alphabet-shaped member has
**one or two of them among real siblings**:

| family | members | alphabet-shaped |
|---|---|---|
| Corbett `@F308@` | 11 | 2 |
| De Franceschi `@F501937@` | 14 | 1 |
| Jelcic `@F501477@` | 11 | 1 |
| Defranceschi `@F501934@` | 10 | 1 |
| Willemse `@F471@` | 6 | 1 |
| Leonesio `@F501936@` | 5 | 2 |
| D'Arcy `@F945@` | 3 | 1 |

## But the TEST is not unique to Žubrinić, and that is the warning

The per-node test — **one leading capital, then a surname, and no dates** — matches
**thirty-one records**, and only fifteen of them are the drawer. **The other sixteen are in
the sister archives, and at least ten of them are real people:**

    W Florance Barry     H E Corbett      J C Corbett     J M Willemse
    G Norman D'Arcy      H W Pretorius    N L S Klaassen
    E Riedo Defranceschi          J B D Defranceschi      M K Defranceschi

**These are people recorded by their initials**, which is an ordinary English and Afrikaans
convention and not a filing artifact. *H E Corbett* is a man his own family knew by his
initials. **Shipping the per-node test to the kit would suppress him.**

The remaining six are lone letters with **no children at all** — *A Defranceschi*,
*N Defranceschi*, *A De Franceschi*, *J Griffin*, *P van Tonder*, *N Jelcic*. They parent
nobody and misfile nothing. Stubs, not drawers.

## So the rule is about a SET, not a node

**What makes the Žubrinić fifteen a card drawer is not that each is a letter.** It is that
**they are entered as one another's siblings** — the tree asserts fifteen brothers and
sisters called A through W — **and that eighty-two real people hang off them as children.**
A single initial tells you nothing. **A family all of whose children are single initials is
a filing cabinet.**

    an alphabet DRAWER = a sibling set, 3 or more, every member a lone leading
                         capital with no birth, baptism, death or burial

That fires once here and would fire zero times in six other archives, where the naive test
fires sixteen times.

## What this archive is doing about it

**Nothing, deliberately.** `tools/buckets.py` already refuses the fifteen and the site's junk
filter already refuses them, so no Žubrinić drawer reaches a page. The sixteen others are
outside this archive's surname scope and are not published here either way.

**The finding belongs in the kit, which is what row 15 said**, and it has been sent to the
session that keeps it — with the measurement, and with the warning that the four-line
version of this test has ten real people in its blast radius.
