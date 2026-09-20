#!/usr/bin/env python3
"""Whose household was swept while they themselves were left out of it?

WHY. Twice on 20 September 2026 a household was worked out of the record index,
the siblings were written into sources/found.psv with their arks, and THE
ANCESTOR THE SWEEP WAS RUN FOR got no row at all.

    ahnentafel 21   both parents credited from her own baptism; she was not
    ahnentafel  7   three siblings into found.psv from one query; she was not

Neither is a typo. It is what a household sweep does to attention: the new
people are the interesting ones, and the person already in the tree -- who is
the reason the query was written -- reads as «done» because their name is
familiar. Ahnentafel 7 sat with a gravestone and four derived credits while the
entry giving her birth to the day, «Antonia Perpić, born 12 May 1859, Krivi
Put», had been passed over in the same result set that produced her brothers.

WHAT IT CHECKS. Every row of found.psv that positions somebody as a BROTHER,
SISTER or SIBLING of an ahnentafel number is a claim that the household has been
looked at. If that ancestor has no baptism row of their own in readings.psv,
the sweep stopped short.

WHY IT IS NOT A GATE, and this is the honest part. It reports five, and three of
them CANNOT be fixed:

    ahn 105  Catta Luckinić   her 1727 baptism is not in the index under any
                              name -- probed surname-free, 20 Sept
    ahn 110  Michael Gerkacs  about 1762; ten spellings and a surname-free
                              query return nothing at Karlobag
    ahn 213  Antonia Pekass   born in a gap the index does not hold

A gate that fails the build on a fact about somebody else's transcription would
have to be silenced, and a silenced gate teaches people to silence gates. So
this prints and returns 0. It is a worklist, not a contract.

Run: python3 tools/siblingcheck.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readingslib  # noqa: E402

REL = re.compile(r"(?:brother|sister|sibling)[^0-9]{0,30}ahnentafel\s+(\d+)", re.I)


def main():
    people = []
    for f in ("people.json", "ancestors.json"):
        people += json.load(open(os.path.join(DATA, f), encoding="utf-8"))
    by_ahn = {p["ahn"]: p for p in people if p.get("ahn")}
    index = readingslib.by_slug(ROOT, DATA)

    path = os.path.join(ROOT, "sources", "found.psv")
    claims = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or line.count("|") < 6:
            continue
        f = [x.strip() for x in line.split("|")]
        for a in REL.findall(f[2]):
            claims.setdefault(int(a), []).append((f[0], f[4]))

    short = []
    for ahn in sorted(claims):
        p = by_ahn.get(ahn)
        if not p:
            continue
        # A HAND-WRITTEN baptism row. A derived credit is the parent being named
        # on a child's entry, which is not the same as their own baptism.
        own = [r for r in index.get(p["slug"], [])
               if r["kind"] == "baptism" and not r["derived"]]
        if not own:
            short.append((ahn, p, claims[ahn]))

    print(f"siblingcheck — {len(claims)} ancestors have a sibling recorded in found.psv")
    if not short:
        print("ok    every one of them has their own baptism row too")
        return 0
    print(f"\n{len(short)} whose household was swept without them:\n")
    for ahn, p, sibs in short:
        print(f"  ahnentafel {ahn} — {p.get('name','')}")
        print(f"      born {p.get('born') or '?'}  {p.get('bornPlace') or ''}")
        for who, when in sibs[:3]:
            print(f"      sibling on file: {who} ({when})")
        print()
    print("Not a failure. Some of these are unreachable — see the docstring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
