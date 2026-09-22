# A prompt for the other archives: does every name on your pages link?

**Copy everything below the line into any other family-research session.** It was written
after the Blažević archive found the fault on its own most prominent page and did not notice
for a day, because the page looked fine.

---

## Check one thing: a name a reader can see, with no page behind it

Your archive almost certainly publishes person pages by a **rule** — a list of surnames, or a
bloodline, or both. Every such rule has an edge, and the edge is visible to a reader as
**two names side by side, one a link and one not, for no reason they can see.**

On the Blažević archive on 22 September 2026 the Kosina page showed this, in one table:

    Pavao Kosina     1894–1943   (plain text)
    Otilija Kosina   1920–1943   (a link)

**Otilija is Pavao's daughter.** She had a page because she is the blood of the woman the
archive is built around; he had none because he married in. **The archive had read three
documents for him and one for her.**

### Do these four checks, in this order

**1. Find the dangling references.** For every published person, look at the parents,
spouses and children your data records for them. **How many of those named people have no
page?** Count them. A page that says «child of X» and cannot link X is the fault. Report the
number before you change anything — it is the size of the problem and it is usually much
bigger than it looks.

**2. Find the documented-but-unpublished.** Go through whatever file records what your
archive has actually READ — readings, citations, a research log. **Is every person named in
it published?** Watch for a trap here: if you have a gate that refuses a reading against an
unpublished person, then the answer is trivially yes and **the set of people you have
documents for but no page is invisible**, because those readings were never allowed to be
written down. In the Blažević archive Martin Kozina's own baptism had been filed under his
wife for exactly this reason.

**3. Look at the page a reader actually lands on.** Not the data — the rendered page. Take
your most-visited or most-narrative page and ask: **does the prose still describe the data?**
The Blažević Kosina page carried a callout saying *«The line stops at Martin — and the
register says why»* for a full day after two generations above Martin had been found and
published elsewhere on the same page. **Generated tables and hand-written prose drift apart,
and the prose is what a reader believes.**

**4. Check what a generated table CANNOT say.** If a table is built from the family tree, it
can only hold people the tree holds. Anything you have read out of a register and recorded
beside the tree — a `found.psv` or equivalent — **will never appear in it**, however true it
is. Either surface it next to the table or say plainly that the table is the tree.

### If you find dangling references, here is what was done and what it cost

Two doors were added to the publication rule:

* **A person the archive has opened a page for gets a page.** A hand-written list of record
  ids with the reason for each. **It has to be a list and not a query** — if your readings
  file can only name published people, deriving it from readings adds nobody.
* **The parents of every published person, to the root** — a closure, not one pass. One pass
  fixes the rows you are looking at and recreates the same fault one generation out. On a
  15,643-person tree the closure took **six rounds** and terminated.

**The cost was 1,460 published people becoming 1,903**, and a `check:living` run to make sure
none of the new ones is alive. **Measure both numbers before you decide** — single pass and
closure — and tell the account holder, because how many people an archive publishes is their
decision and not yours.

### And expect the new people to break a gate

443 new people brought three given-name forms the archive had never seen — «Mariae», «Mariæ»
and a «Maria?» where a clerk was unsure — and the name-table gate refused the build until
each was declared. **That gate doing its job is the point.** Do not silence it; add the forms,
and keep the clerk's question mark rather than resolving it for him.

### Report back with

* the number of dangling parent/spouse/child references **before**,
* the number of people documented but unpublished,
* any prose that no longer matches its own data,
* how many people the single pass and the closure would each add,
* and **what you did not change, and why**.
