#!/usr/bin/env python3
"""Which parish register a village's events were written in, and what it holds.

Split out of tools/targets.py when tools/walls.py needed the same answer: a
wall on the ancestor chart is only interesting once you can say whether the
book that would get past it is filmed, out of range, or does not exist. Two
copies of this table would have drifted, and the drift would have been
invisible — both tools would still have printed confident numbers.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(x):
    return (str(x or "").lower().replace("ž", "z").replace("ć", "c").replace("č", "c")
            .replace("š", "s").replace("đ", "d").strip())


# village -> (parish, holdings)
parish_of, PARISH = {}, {}
for line in open(os.path.join(ROOT, "sources", "parishes.psv"), encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, villages, b, m, d, ver = line.split("|")
    PARISH[name] = {"births": b, "marriages": m, "deaths": d, "verified": ver,
                    "villages": [v.strip() for v in villages.split(",")]}
    for v in PARISH[name]["villages"]:
        parish_of[norm(v)] = name


def ranges(spec):
    """'1650-1900' or '1734-1858,1859-1920' -> [(1650,1900), ...]; 'none' -> []"""
    if spec in ("none", "unknown"):
        return []
    out = []
    for part in spec.split(","):
        m = re.match(r"(\d{4})-(\d{4})", part.strip())
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    return out


def covered(spec, year):
    if not year:
        return None
    rs = ranges(spec)
    if not rs:
        return False
    return any(a <= year <= b for a, b in rs)


NOISE = {"croatia", "hrvatska", "lika-senj county", "opcina otocac", "opcina senj",
         "primorje-gorski kotar county", "austria-hungary", "split-dalmatia",
         "licko-senjska zupanija", "lika-senj", "general reg. office"}
# "Klenovica 22", "#6 Mrzli Dol", "Prozor 50" — the house number rides along with
# the village in this tree, and a parser that only recognises a bare number as a
# house leaves 134 events unplaced.
HOUSE_ONLY = re.compile(r"^\s*(?:br\.?|no\.?|n[o°]|kbr\.?|#)?\s*\d{1,3}\s*$", re.I)
HOUSE_IN = re.compile(r"(?:^|\s)(?:br\.?|no\.?|n[o°]|kbr\.?|#)?\s*\d{1,3}(?=$|\s)", re.I)

ALIAS = {"smokvica": "smokvica krmpotska", "smokvica, krmpote": "smokvica krmpotska",
         "otocac croatia": "otocac", "kriviput": "krivi put",
         "sv. jakov krmpote": "sv. jakov"}


def village_of(place):
    for part in [p.strip() for p in str(place or "").split(",")]:
        if HOUSE_ONLY.match(part):
            continue
        # strip an embedded house number, then re-test
        part = HOUSE_IN.sub(" ", part).strip(" ,.-/")
        n = norm(part)
        if not n or n in NOISE:
            continue
        n = n.split("/")[0].strip()        # "smokvica krmpotska / krmpote"
        return ALIAS.get(n, n)
    return None


def year_of(datestr):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", str(datestr or ""))
    return int(m.group(1)) if m else None
