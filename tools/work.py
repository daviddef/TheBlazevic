#!/usr/bin/env python3
"""What these people did for a living — from the registers, not from the tree.

The family tree records an occupation for 16 of 1,245 published people. The
parish registers record one for almost everybody: both the Latin and the
Croatian forms carry a *conditio* / *stalež* column, and the priest filled it in
for parents, godparents and witnesses alike.

This archive has been reading past that column. Where an occupation surfaced it
went into prose on one person's page, which means it could not be counted or
compared - and the comparison is the whole point. The Zubrinici hold salaried
Frontier posts; the Blazevici are day labourers and peasants. That is the sharpest
social fact in this family and it has never been shown as one.

Merges two sources and keeps them distinguishable:
  * the 16 occupations carried by the GEDCOM
  * sources/register/occupations.psv, read off the scans, each row citing its entry
"""
import sys, os, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom
from ancestry import fold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
SRC = os.path.join(ROOT, "sources", "register", "occupations.psv")

pub = {p["id"]: p for p in json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))}

# --- from the register sweep ---------------------------------------------
rows = []
for line in open(SRC, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = [x.strip() for x in line.split("|")]
    if len(parts) < 7:
        continue
    who, what, eng, fam, place, year, source = parts[:7]
    rows.append({"who": who, "what": what, "english": eng,
                 "family": fam if fam != "—" else None,
                 "place": place, "year": year, "source": source, "from": "register"})

# --- from the tree --------------------------------------------------------
tree_rows = []
for pid, rec in pub.items():
    for o in rec.get("occupations") or []:
        what = (o.get("what") or "").strip()
        if not what:
            continue
        tree_rows.append({"who": rec["name"], "slug": rec.get("slug"), "what": what,
                          "english": "", "family": rec.get("family"),
                          "place": (o.get("where") or "").strip(),
                          "year": "", "source": "family tree", "from": "tree"})

allrows = rows + tree_rows
by_fam = collections.Counter(r["family"] for r in allrows if r["family"])

print(f"{len(rows)} occupations read from registers, {len(tree_rows)} carried by the tree")
print(f"{len(allrows)} in total, against {len(pub)} published people\n")
for f, n in by_fam.most_common():
    print(f"  {n:>3}  {f}")

out = os.path.join(DATA, "work.json")
json.dump({"rows": allrows, "fromRegister": len(rows), "fromTree": len(tree_rows),
           "published": len(pub)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
