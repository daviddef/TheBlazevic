# What is in here, and why it is not on the site

**There is no `/notes/` route, and that is deliberate.** The site carries the
**argument**; these files carry the **working**. A reader meets one only when a
page cites it — `tools/notelinks.py` turns a bare `notes/` + filename in a page into a
link to the file on GitHub.

That design has one failure mode, and on **28 September 2026** this archive was
in it. The account holder asked *«is everything in our site?»* and the answer
was no: **76 notes on disk and 17 reachable from nowhere**, including a
**4,769-word** guide to the Croatian state archive's register search and a
**2,559-word** account of the reading that produced a whole Kozina household.
Nine of the ten substantive ones were cited the same day; the tenth became a
row in `sources/readings.psv`.

**`tools/notescheck.py` now runs in the build** and fails when a note is
reachable from nowhere. So there are three kinds of file in here, and each has
to declare itself rather than be assumed.

## 1. Notes cited from a page — the normal kind

A reading, a source, a method, a negative worth keeping. It belongs to a page,
and that page names it. Most of the 69 are these.

**Where the citation goes depends on what the note is:**

| the note is about | cite it from |
|---|---|
| a document read **for a person** | `sources/readings.psv` — one row, and `/readings/` links it |
| a **source searched**, whatever it gave | `sources/searched.json` — the row for that search |
| a **finding or a method** belonging to one story | the prose of the page that tells it |

## 2. Prompts — `PROMPT-*.md`

Briefs written to be pasted into another archive's session. **Addressed to a
machine and a maintainer, not to a reader**, and excused by name in the gate.

## 3. Hand-offs and superseded working — declared in the gate

Listed in `NOT_FOR_READERS` in `tools/notescheck.py`, each with its reason on
the line. Two of them exist precisely so their contents are **not** published
here: `for-the-defranceski-archive.md` and `the-kozina-of-zgornje-bitnje.md`
are addressed to other archives in this estate, and citing them from a page
would publish the lists they exist to keep off this site. The rest are
generated dumps that the data files superseded.

---

**If you are adding a note:** decide which of the three it is before you write
it, and if it is the first kind, cite it the same hour. A working paper nobody
can reach is a working paper nobody has.
