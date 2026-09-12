#!/usr/bin/env python3
"""The families who married into this one.

This archive follows four surnames and gives each a page. But Hedviga's descent
runs through more than twenty, and the other twenty have had nowhere to live:
Uroda, Sekula, Jellicic, Bacchi, Gerkacs, Pekass, Orescovic, Tomljanovic and the
rest carry 43 direct ancestors between them and not one page.

If one of these is your family, that is the page this builds.
"""
import json, os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ancestry import fold, SURNAMES, FAMILY_OF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
L = lambda f: json.load(open(os.path.join(DATA, f), encoding="utf-8"))

anc = L("ancestors.json")
people = list({p["id"]: p for p in L("people.json") + anc}.values())
HAS_PAGE = {"blazevic", "zubrinic", "papic", "prpic"}

groups = collections.defaultdict(lambda: {"names": collections.Counter(), "anc": [],
                                          "people": [], "places": collections.Counter()})
for p in people:
    sn = (p.get("surname") or "").strip()
    if not sn:
        continue
    k = fold(sn)
    k = FAMILY_OF.get(k, k)          # "Perpic" belongs to the Prpic page
    if k in HAS_PAGE:
        continue
    g = groups[k]
    g["names"][sn] += 1
    g["people"].append(p)
    pl = (p.get("bornPlace") or p.get("diedPlace") or "").split(",")[0].strip().strip('"')
    if pl:
        g["places"][pl] += 1

ahn = {}
for a in anc:
    n = a.get("ahnentafel") or a.get("ahn")
    if n:
        ahn[a["id"]] = n

rows = []
for k, g in groups.items():
    ancs = sorted(((ahn[p["id"]], p) for p in g["people"] if p["id"] in ahn),
                  key=lambda t: t[0])
    if not ancs:
        continue                                   # only families on the direct line
    yrs = sorted(p["byear"] for p in g["people"] if p.get("byear"))
    rows.append({
        "key": k,
        "label": g["names"].most_common(1)[0][0],
        "spellings": [n for n, _ in g["names"].most_common()],
        "published": len(g["people"]),
        "ancestors": [{"ahn": a, "name": p["name"], "slug": p["slug"],
                       "born": p.get("born") or "", "place": (p.get("bornPlace") or "").split(",")[0]}
                      for a, p in ancs],
        "from": yrs[0] if yrs else None, "to": yrs[-1] if yrs else None,
        "places": [{"place": v, "n": c} for v, c in g["places"].most_common(3)],
    })

rows.sort(key=lambda r: (-len(r["ancestors"]), r["ancestors"][0]["ahn"]))
out = os.path.join(DATA, "marriedin.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"{len(rows)} families married into this one, carrying "
      f"{sum(len(r['ancestors']) for r in rows)} direct ancestors\n")
for r in rows:
    pl = r["places"][0]["place"] if r["places"] else "—"
    print(f"  {len(r['ancestors'])} anc · {r['published']:>3} published · "
          f"{r['label'][:22]:<22} {str(r['from'] or '?'):>5}–{str(r['to'] or '?'):<5} {pl}")
print(f"\nwrote {os.path.relpath(out, ROOT)}")
