#!/usr/bin/env python3
"""A working paper nobody can reach is a working paper nobody has.

Asked on 28 September 2026: «is everything in our site? e.g.
notes/the-kozina-of-zgornje-bitnje.md — is there a reason we're creating more
docs or should it be in our site?» The answer was no, not everything, and the
question was right.

HOW NOTES WORK HERE, WHICH IS NOT OBVIOUS. There is no /notes/ route. A note is
a working paper in the repository, and the only way a reader meets one is when
a page cites it: tools/notelinks.py rewrites a bare `notes/x.md` in a page into
a link to the file on GitHub. That is a deliberate design — the site carries
the argument, the notes carry the working — but it has one failure mode, and on
28 September 2026 the estate was in it. SEVENTY-SIX NOTES ON DISK AND SEVENTEEN
CITED FROM NOWHERE, including a 4,769-word guide to the Croatian state
archive's register search and a 2,559-word account of the reading that found a
whole Kosina household.

So this gate asks one question of every file in notes/: does any page or data
file mention it? Three kinds are allowed not to be cited, and each has to say
so out loud rather than be assumed:

  PROMPT-*        a brief written to be pasted into another archive's session.
                  Not for readers of this site and never was.
  notes/README.md the file explaining the three kinds.
  a note listed in NOT_FOR_READERS below, with a reason in the line.

Everything else must be reachable. Add the citation to the page the note
belongs to, or put the note in the list and say why.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(ROOT, "notes")

# Notes that are deliberately unreachable from the site, and why. A line here
# is a decision, not a parking space.
NOT_FOR_READERS = {
    "dossier-ancestors.txt":
        "a generated dump of the direct line, superseded by site/src/data/"
        "ancestors.json which every page reads. Kept because it is what the "
        "first week's reading was done against.",
    "zubrinic-name-reuse.txt":
        "working output behind tools/name_reuse.py, whose result is published "
        "at /impossible/. The file is the scratch, the page is the finding.",
    "zubrinic-places.txt":
        "working output behind the Žubrinić place counts, published at "
        "/frontier/ and /zubrinic-roots/.",
    "for-the-defranceski-archive.md":
        "a hand-off to another archive in this estate, written at the account "
        "holder's instruction that those 42 people should NOT be published "
        "here. Citing it from a page would publish the list it exists to keep "
        "off this site.",
    "the-kozina-of-zgornje-bitnje.md":
        "the same, for the Kozina household — addressed to the other seven "
        "archives rather than to a reader. Its findings are all on /kosina/; "
        "the note is the hand-off, not the evidence.",
}


def cited_names():
    seen = set()
    pats = (glob.glob(os.path.join(ROOT, "site", "src", "pages", "**", "*.astro"),
                      recursive=True)
            + glob.glob(os.path.join(ROOT, "site", "src", "data", "*.json"))
            + glob.glob(os.path.join(ROOT, "site", "src", "lib", "*.js")))
    for f in pats:
        body = open(f, encoding="utf-8", errors="replace").read()
        for m in re.findall(r"notes/([A-Za-z0-9._-]+\.(?:md|txt))", body):
            seen.add(m)
    return seen


def main():
    if not os.path.isdir(NOTES):
        print("  ok    notes      no notes/ directory")
        return
    cited = cited_names()
    on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(NOTES, "*"))
                     if os.path.isfile(p))
    orphans, excused = [], 0
    for name in on_disk:
        if name in cited:
            continue
        if name.startswith("PROMPT-") or name == "README.md":
            excused += 1
            continue
        if name in NOT_FOR_READERS:
            excused += 1
            continue
        words = len(open(os.path.join(NOTES, name), encoding="utf-8",
                         errors="replace").read().split())
        orphans.append((words, name))

    if orphans:
        orphans.sort(reverse=True)
        print("\n  FAIL  notes      %d note(s) reachable from nowhere on the site"
              % len(orphans))
        for words, name in orphans:
            print("          %-54s %5d words" % (name, words))
        print("        Cite it from the page it belongs to, or add it to "
              "NOT_FOR_READERS in tools/notescheck.py with the reason.")
        sys.exit(1)
    print("  ok    notes      %d note(s), %d cited from a page, %d deliberately not"
          % (len(on_disk), len(on_disk) - excused, excused))


if __name__ == "__main__":
    main()
