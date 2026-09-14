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

# Four worlds, not one list. The same family tree reaches into a Habsburg
# garrison town, a stretch of the Military Frontier, a set of hill villages and
# a port with a tobacco monopoly, and the trades in each are not comparable.
# Keyed on the place string the register itself gives.
STRATA = [
    ("Karlobag — the port town",
     ("karlobag",),
     "A chartered town on the Adriatic. Merchants, master mariners, "
     "and a parish register full of Dominus honorifics, a Pro-Colonel, "
     "a Captain and a Baron von Holstein."),
    ("The Military Frontier — Otočac and its villages",
     ("otocac", "otočac", "prozor", "sumecica", "šumećica", "dubrava"),
     "Not civilians. Every adult male is enrolled, and the register records "
     "the rank or the office rather than a trade: Confiniarius, keeper of the "
     "watch, forest warden, keeper of the prison."),
    ("The hill villages — Krmpote, Smokvica, Krivi Put",
     ("smokvica", "krmpote", "krivi put", "sv. jakov", "klenovica", "povile",
      "novi vinodolski", "ledenice"),
     "Seljaci and težaci, almost without exception. Where a register gives "
     "anything else it is usually the household, not the man."),
    ("Senj — the town and the tobacco factory",
     ("senj",),
     "A working port with a state tobacco monopoly. The register grades the "
     "factory workforce from radnica to nadglednica, and the town trades run "
     "from bremenar to gostioničar."),
]


def stratum_of(place):
    p = (place or "").lower()
    for name, keys, _ in STRATA:
        if any(k in p for k in keys):
            return name
    return None


strata = []
for name, _keys, blurb in STRATA:
    hits = [r for r in allrows if stratum_of(r.get("place")) == name]
    if not hits:
        continue
    strata.append({
        "name": name, "blurb": blurb, "n": len(hits),
        "rows": sorted(hits, key=lambda r: (str(r.get("year") or ""), r["who"])),
    })
placed = sum(s["n"] for s in strata)

print(f"{len(rows)} occupations read from registers, {len(tree_rows)} carried by the tree")
print(f"{len(allrows)} in total, against {len(pub)} published people\n")
for f, n in by_fam.most_common():
    print(f"  {n:>3}  {f}")
print()
for st in strata:
    print(f"  {st['n']:>3}  {st['name']}")
print(f"  {len(allrows) - placed:>3}  (no place given)")

out = os.path.join(DATA, "work.json")
json.dump({"rows": allrows, "fromRegister": len(rows), "fromTree": len(tree_rows),
           "published": len(pub), "strata": strata, "placed": placed,
           "unplaced": len(allrows) - placed},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
