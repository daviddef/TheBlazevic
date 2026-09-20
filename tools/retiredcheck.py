#!/usr/bin/env python3
"""A withdrawal at the foot of a note is not a withdrawal.

WHY. This archive corrects itself by APPENDING -- a section headed CORRECTED or
RESOLVED goes at the bottom and the original reasoning is kept whole, because the
way a thing went wrong is usually the useful part. That is a good habit and it
has one bad consequence: THE WITHDRAWN CLAIM IS STILL STATED AS FACT IN THE
PARAGRAPHS ABOVE IT.

On 20 September 2026 three notes were in that state, and the worst was about
ahnentafel 3 -- Hedviga's mother. The note said «there is no image yet» and «one
page, and the archive's second-most-important birth date is settled either way»,
and carried a correction at the foot saying the page had been read years before
and is published on this site. A reader who stopped before the last screen got
the withdrawn claim as the archive's position. Those notes are linked from the
work list, so readers do reach them.

WHAT IT CHECKS, and it is deliberately structural rather than clever. Detecting
«this sentence contradicts a later one» is not something a build should attempt.
What a build CAN insist on is that a reader meets the withdrawal FIRST:

    a note containing a CORRECTED / RESOLVED / SUPERSEDED / WITHDRAWN section
    must carry a withdrawal banner near the top that points at it.

That is cheap, always satisfiable, and it fails for exactly one reason with
exactly one fix -- which is what separates a gate from a report. The two checks
written yesterday, siblingcheck and publishedcheck, are reports precisely
because they can report things nobody can fix.

Run: python3 tools/retiredcheck.py [--quiet]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(ROOT, "notes")

# A section that withdraws something said earlier in the same note.
SECTION = re.compile(r"^#{1,3}\s*(?:\*\*)?\s*(CORRECTED|RESOLVED|SUPERSEDED|WITHDRAWN|"
                     r"PARTLY SUPERSEDED)\b", re.M)
# The banner that has to meet the reader first. A blockquote in the first
# paragraphs carrying one of those words.
BANNER = re.compile(r"^>.*\b(SUPERSEDED|WITHDRAWN|CORRECTED|RESOLVED)\b", re.M | re.I)
HEAD_LINES = 14


def main():
    quiet = "--quiet" in sys.argv
    if not os.path.isdir(NOTES):
        return 0
    checked, bad = 0, []
    for fn in sorted(os.listdir(NOTES)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(NOTES, fn), encoding="utf-8").read()
        m = SECTION.search(text)
        if not m:
            continue
        checked += 1
        head = "\n".join(text.splitlines()[:HEAD_LINES])
        if not BANNER.search(head):
            line = text[:m.start()].count("\n") + 1
            bad.append((fn, m.group(1), line))

    if bad:
        print(f"FAIL  {len(bad)} note(s) withdraw something only at the foot:")
        for fn, word, line in bad:
            print(f"      notes/{fn}")
            print(f"        «{word}» at line {line}, and nothing in the first "
                  f"{HEAD_LINES} lines says so")
        print("\n      A reader who stops before the last screen takes the withdrawn claim\n"
              "      as this archive's position. Put a blockquote banner under the title\n"
              "      saying what is withdrawn and pointing at the section that withdraws it.\n"
              "      Keep the original reasoning — the way it went wrong is the useful part.")
        return 1
    if not quiet:
        print(f"retiredcheck — {checked} note(s) withdraw an earlier claim, "
              f"and every one says so at the top")
    return 0


if __name__ == "__main__":
    sys.exit(main())
