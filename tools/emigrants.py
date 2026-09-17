#!/usr/bin/env python3
"""Who left Senj and Otočac, from the US naturalisation petitions.

The passenger manifests give a RESIDENCE and a relative. A petition for
naturalization gives an exact BIRTH DATE, an exact BIRTH PLACE, the spouse's
birth date and every child's — and in that collection alone the birth place is
INDEXED, so it can be searched. That is the only way this archive has found to
search by where somebody came from rather than by what they were called.

The point of this tool is the last column. Every row carries a birth date to the
day, and this archive knows which years of which parish are on film. So it can
say, per person, whether the baptism that would confirm them is READABLE — and
the answer is not encouraging at Otočac, where the births stop in 1858 and every
one of these people was born after 1888.

Reads  sources/findmypast/senj-otocac-naturalisations.psv
Writes site/src/data/emigrants.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parishlib import ROOT, PARISH, ranges

SRC = os.path.join(ROOT, "sources", "findmypast", "senj-otocac-naturalisations.psv")
DATA = os.path.join(ROOT, "site", "src", "data")

# The town as this archive spells it -> the parish key in parishes.psv.
PARISH_OF = {"Senj": "Senj", "Otočac": "Otocac", "Brinje": "Brinje"}


def year(s):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", s or "")
    return int(m.group(1)) if m else None


def main():
    rows = []
    for line in open(SRC, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = [x.strip() for x in line.split("|")]
        if len(f) < 6:
            continue
        town, name, born, place, family, filed = f[:6]
        by = year(born)
        parish = PARISH_OF.get(town)
        spec = (PARISH.get(parish) or {}).get("births", "unknown")
        rs = ranges(spec) if spec not in ("none", "unknown") else []
        # Readable means: the baptism year falls inside a filmed range. Not
        # «probably there» — inside a range this archive has checked.
        readable = bool(by and any(a <= by <= b for a, b in rs))
        rows.append({
            "town": town, "name": name, "born": born, "byear": by,
            "place": place, "family": family, "filed": filed,
            "parish": parish, "births": spec, "readable": readable,
        })
    rows.sort(key=lambda r: (r["town"], r["byear"] or 0))

    towns = {}
    for r in rows:
        t = towns.setdefault(r["town"], {"town": r["town"], "n": 0, "readable": 0,
                                         "births": r["births"]})
        t["n"] += 1
        t["readable"] += 1 if r["readable"] else 0

    # Where they went. The destination is the first useful word of «filed».
    where = {}
    for r in rows:
        city = r["filed"].split(",")[0].strip()
        city = re.sub(r"\s+\d{4}.*$", "", city).strip()
        where[city] = where.get(city, 0) + 1

    out = {
        "what": ("Everyone born at Senj, Otočac or Brinje in the United States "
                 "naturalization petitions. Found by searching the BIRTHPLACE, "
                 "which is indexed in that collection and in no other here; "
                 "every row confirmed by opening the transcript."),
        "n": len(rows),
        "readable": sum(1 for r in rows if r["readable"]),
        "towns": sorted(towns.values(), key=lambda t: -t["n"]),
        "where": sorted(where.items(), key=lambda kv: (-kv[1], kv[0])),
        "rows": rows,
    }
    json.dump(out, open(os.path.join(DATA, "emigrants.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"emigrants.json — {len(rows)} people, {out['readable']} inside a filmed register")
    for t in out["towns"]:
        print(f"  {t['n']:>3}  {t['town']:<10} births filmed {t['births']:<22} "
              f"{t['readable']} readable")


if __name__ == "__main__":
    main()
