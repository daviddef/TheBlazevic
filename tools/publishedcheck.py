#!/usr/bin/env python3
"""What has this archive PUBLISHED that it never wrote into its evidence file?

WHY. On 20 September 2026 a note was written concluding that Milka Lucia Papić's
baptism -- ahnentafel 3, Hedviga's mother, after Hedviga the most important
person here -- could not be settled because «there is no image yet», and that
«one page» would decide it.

The page had been read years before and is PUBLISHED ON THIS SITE, image and
all, at /milka: «Senj baptisms, page 122, entry 96 ... born 9 October 1886,
baptised 17 October». Her 1907 marriage entry repeats the birth as «9/X» in a
different hand. Two entries, both October, both on the site.

The note checked the index against the TREE and never against THIS ARCHIVE.

It was not one slip. Holding site/src/data/corrections.json against
sources/readings.psv turned up THIRTEEN more people whose correction quotes a
register -- page and entry number, occupations, Croatian phrases off the line --
with no reading row at all. Among them the marriage of 8 December 1920, which
has its own page on this site and is the document the whole archive was built
around, and ahnentafel 2 and 4, who had no readings of any kind.

WHY IT WENT UNSEEN. coverage.py grades a person «read» from EITHER a reading row
OR a citation keyed on the GEDCOM id. The corrections carried the citation, so
the people graded correctly and the evidence file quietly did not hold what the
site was showing. Two paths to «read», and only one of them is the archive's
own record of what it has read.

WHAT IT CHECKS. Every corrections.json entry of kind corrected / confirmed /
upgraded whose text quotes a register -- a page, an entry number, a register
name -- against readings.psv.

WHY IT IS NOT A GATE. A correction can legitimately have no reading: ahnentafel
20's says «the 1845 baptism is NOT his», which is a DISPROOF. Recording that as
a reading for him would assert the opposite of what it found. A gate would have
to be argued with, so this prints and returns 0.

Run: python3 tools/publishedcheck.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readingslib  # noqa: E402

# A correction that quotes a register says a page was opened.
REG = re.compile(r"\b(register|registar|baptis|marriage|death entry|matičn|"
                 r"str\.\s*\d|page \d|entry \d|no\. ?\d|p\. ?\d)\b", re.I)
# ... unless what it found is that the entry belongs to somebody else.
DISPROOF = re.compile(r"\bis not (his|hers|theirs)\b|belongs to a different|"
                      r"\bnot his\b|\bnot hers\b", re.I)


def main():
    people = []
    for f in ("people.json", "ancestors.json"):
        people += json.load(open(os.path.join(DATA, f), encoding="utf-8"))
    by_id = {p.get("id"): p for p in people if p.get("id")}
    index = readingslib.by_slug(ROOT, DATA)
    cor = json.load(open(os.path.join(DATA, "corrections.json"), encoding="utf-8"))

    checked, missing, disproofs = 0, [], []
    for c in cor:
        if c.get("kind") not in ("corrected", "confirmed", "upgraded"):
            continue
        text = f"{c.get('why') or ''} {c.get('record') or ''} {c.get('what') or ''}"
        if not REG.search(text):
            continue
        p = by_id.get(c.get("id"))
        if not p:
            continue
        checked += 1
        if [r for r in index.get(p["slug"], []) if not r["derived"]]:
            continue
        (disproofs if DISPROOF.search(text) else missing).append((p, c))

    print(f"publishedcheck — {checked} corrections quote a register")
    if disproofs:
        print(f"\n{len(disproofs)} are disproofs, and correctly have no reading:")
        for p, c in disproofs:
            print(f"      ahn {p.get('ahn') or '-'}  {p.get('name','')[:44]} — {c.get('what')}")
    if not missing:
        print("\nok    every other one has a reading row in readings.psv")
        return 0
    print(f"\n{len(missing)} published register read(s) with NO row in readings.psv:\n")
    for p, c in missing:
        print(f"  ahnentafel {p.get('ahn') or '-'} — {p.get('name','')}")
        print(f"      {c.get('what')}: {(c.get('why') or '')[:120]}…")
        print()
    print("The site is showing evidence the evidence file does not hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
