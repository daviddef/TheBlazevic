#!/usr/bin/env python3
"""Turn the parish holdings into a worklist: who to look for, in which book.

Reading a film is expensive and the expensive part is not the reading, it is
not knowing what you are looking for. This takes every published person with a
place, works out which parish register their birth or death was written in, and
says whether the year falls inside what that parish's films actually cover.

The output is a checklist per book, ordered by year, so a sitting at the viewer
is a list to tick off rather than a search.
"""
import json, os, collections

# The parish table and the place parser live in tools/parishlib.py, because
# tools/walls.py needs exactly the same answers and two copies would drift.
from parishlib import ROOT, PARISH, parish_of, covered, village_of, year_of

people, seen = [], set()
for f in ("ancestors.json", "people.json"):
    p = os.path.join(ROOT, "site", "src", "data", f)
    if not os.path.exists(p):
        continue
    for r in json.load(open(p, encoding="utf-8")):
        if r.get("slug") and r["slug"] not in seen:
            seen.add(r["slug"])
            people.append(r)

books = collections.defaultdict(list)
unplaced = collections.Counter()

for p in people:
    for field, datef, kind in (("bornPlace", "born", "births"),
                               ("diedPlace", "died", "deaths")):
        place = p.get(field)
        if not place:
            continue
        v = village_of(place)
        if not v:
            continue
        par = parish_of.get(v)
        if not par:
            unplaced[v] += 1
            continue
        y = year_of(p.get(datef))
        inside = covered(PARISH[par][kind], y)
        books[(par, kind)].append({
            "slug": p["slug"], "name": p.get("name"), "year": y,
            "village": v, "ahn": p.get("ahn"), "inside": inside,
            "date": p.get(datef) or "", "place": place})

rows = []
for (par, kind), hits in sorted(books.items()):
    inside = [h for h in hits if h["inside"]]
    rows.append({
        "parish": par, "kind": kind,
        "holds": PARISH[par][kind], "verified": PARISH[par]["verified"],
        "n": len(hits), "reachable": len(inside),
        "ahn": sorted({h["ahn"] for h in inside if h.get("ahn")}),
        "people": sorted(inside, key=lambda h: (h["year"] or 9999, h["name"] or "")),
    })
rows.sort(key=lambda r: -r["reachable"])

out = {"books": rows,
       "totalReachable": sum(r["reachable"] for r in rows),
       "unplacedVillages": unplaced.most_common(25)}
json.dump(out, open(os.path.join(ROOT, "site", "src", "data", "targets.json"), "w",
                    encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"{'reach':>5} {'of':>5}  book")
for r in rows:
    if r["reachable"]:
        a = f"  ahn {','.join(str(x) for x in r['ahn'])}" if r["ahn"] else ""
        print(f"{r['reachable']:>5} {r['n']:>5}  {r['parish']} {r['kind']} ({r['holds']}){a}")
print(f"\n{out['totalReachable']} events fall inside a film this archive can reach")
print("wrote site/src/data/targets.json")
