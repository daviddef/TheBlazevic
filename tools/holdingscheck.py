#!/usr/bin/env python3
"""Does holdings.psv still say what the catalogue says?

holdings.psv is the readable summary — one line per film, contents in plain
words. filmnotes.psv is the catalogue's own text, verbatim, with the physical
ROLL NUMBER and the ITEM RANGE. The summary is the one people read and the one
that goes stale; the verbatim copy is the one that can be re-fetched and
checked by hash.

This keeps them in step. It tests three things and nothing else:

  every film in the catalogue is in the summary
  every film in the summary is in the catalogue
  the years each one claims are the years the catalogue claims

The third is the one that matters. Brinje sat in holdings.psv for a week as
«film notes not pulled» with no DGS number at all, and nothing noticed, because
nothing compared the file with its source.

Run: python3 tools/holdingscheck.py [--quiet]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FS = os.path.join(ROOT, "sources", "familysearch")


def rows(name, n):
    out = []
    for line in open(os.path.join(FS, name), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("|")
        if len(f) >= n:
            out.append(f)
    return out


def years(s):
    """Every four-digit year in a contents string, as a set.

    Deliberately blunt. The summary writes «Rodjeni 1734-1795, 1795-1820» where
    the catalogue writes «Rođeni 1734-1795 -- Rođeni 1795-1820»; the words differ
    and the years do not. Years are what a researcher acts on.
    """
    return {int(y) for y in re.findall(r"\b(1[5-9]\d\d|20\d\d)\b", s)}


def main():
    quiet = "--quiet" in sys.argv
    held = {r[2]: r for r in rows("holdings.psv", 4) if r[2]}
    cat = {r[2]: r for r in rows("filmnotes.psv", 6)}

    fails = []
    missing = sorted(set(cat) - set(held))
    extra = sorted(set(held) - set(cat))
    for d in missing:
        fails.append(f"in the catalogue, not in holdings.psv: {cat[d][0]} DGS {d} — {cat[d][5]}")
    for d in extra:
        fails.append(f"in holdings.psv, not in the catalogue: {held[d][0]} DGS {d} — {held[d][3]}")

    drift = []
    for d in sorted(set(held) & set(cat)):
        h, c = years(held[d][3]), years(cat[d][5])
        # The summary may say less than the catalogue — it collapses items — but
        # it must never claim a year the catalogue does not have.
        invented = h - c
        if invented:
            drift.append((cat[d][0], d, sorted(invented), held[d][3], cat[d][5]))
    for p, d, ys, hs, cs in drift:
        fails.append(f"holdings.psv claims years the catalogue does not: {p} DGS {d} "
                     f"{ys}\n        summary:   {hs}\n        catalogue: {cs}")

    if not quiet:
        parishes = {r[0] for r in cat.values()}
        # The number that matters. A film whose items start at 1 can be walked
        # from its DGS number. A film that starts at item 4 cannot: the viewer
        # opens the ROLL, and items 1 to 3 are whatever else was photographed
        # that day — for Karlobag's baptisms, the parish of Kaptol.
        late = [r for r in cat.values()
                if int((re.findall(r"\d+", r[4]) or ["1"])[0]) > 1]
        print(f"holdings — {len(cat)} films across {len(parishes)} parishes; "
              f"{len(held)} summarised")
        print(f"          {len(late)} of them do not begin at item 1 of their roll "
              f"— reach those by waypoint, never by film number")
    if fails:
        print(f"\nFAIL  {len(fails)} disagreement(s) between holdings.psv and the catalogue:")
        for f in fails:
            print("      " + f)
        return 1
    if not quiet:
        print("ok    every film is in both files and no year is invented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
