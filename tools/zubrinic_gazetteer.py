#!/usr/bin/env python3
"""Every Zubrinic record in the tree, grouped by the place it names.

The point is to see the surname as a map rather than as a pedigree. Frontier
registers identify a household by village and house number, so the house number
is kept: it is the closest thing these records have to a family identifier.
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year, ev

people, families = load()


def fold(sn):
    s = sn.lower().replace("ž","z").replace("ć","c").replace("č","c").replace("š","s")
    s = s.split("(")[0].strip()
    if s.startswith("x"): s = "z" + s[1:]
    if s.endswith("ich"): s = s[:-3] + "ic"
    return s


Z = {pid: p for pid, p in people.items() if fold(p["surname"]) == "zubrinic"}

# A place string in this tree is "House N, Village, County, Country" in any order
# and any degree of completeness. Reduce it to (village, house) where possible.
HOUSE = re.compile(r"(?:^|[\s,])(?:br\.?\s*|no\.?\s*|n[o°]\s*)?(\d{1,3})(?=$|[\s,])", re.I)
NOISE = {"croatia", "hrvatska", "lika-senj county", "licko-senjska zupanija", "opcina otocac",
         "primorje-gorski kotar county", "australia", "south australia", "austria-hungary",
         "general reg. office", "", "opcina senj", "split-dalmatia"}


def norm(x):
    return (x.lower().replace("ž","z").replace("ć","c").replace("č","c")
             .replace("š","s").replace("đ","d").strip())


def place_key(pl):
    if not pl: return None, None
    parts = [x.strip() for x in pl.split(",") if x.strip()]
    house = None
    village = None
    for x in parts:
        m = HOUSE.search(x)
        if m and not village:
            house = m.group(1)
            v = HOUSE.sub("", x).strip(" ,.")
            if v: village = v
            continue
        if norm(x) in NOISE:
            continue
        if village is None:
            village = x
    if village is None:
        for x in parts:
            if norm(x) not in NOISE:
                village = x; break
    return village, house


rows = []
for pid, p in Z.items():
    b, d = born(p), died(p)
    for kind, e in (("b", b), ("d", d)):
        pl = e.get("place", "")
        if not pl: continue
        v, h = place_key(pl)
        if not v: continue
        rows.append({"pid": pid, "name": display(p), "kind": kind,
                     "year": year(e.get("date", "")), "village": v, "house": h, "raw": pl})

by_v = collections.defaultdict(list)
for r in rows:
    by_v[norm(r["village"])].append(r)

print(f"{len(Z)} Zubrinic records; {len(rows)} carrying a place; "
      f"{len(by_v)} distinct places\n")
for v, rs in sorted(by_v.items(), key=lambda kv: -len(kv[1])):
    yrs = [r["year"] for r in rs if r["year"]]
    houses = sorted({r["house"] for r in rs if r["house"]}, key=lambda x: int(x))
    span = f'{min(yrs)}–{max(yrs)}' if yrs else "no dates"
    print(f'{len(rs):>4}  {rs[0]["village"][:34]:<34} {span:<12} '
          f'{"houses " + ", ".join(houses) if houses else ""}')
