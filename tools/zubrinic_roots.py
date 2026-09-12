#!/usr/bin/env python3
"""The 93 Zubrinic fragments, and which of them could be the same family.

232 Zubrinic records in the tree resolve into 93 people with no Zubrinic parent
- 93 separate starting points for a surname held by about 312 people on earth,
almost all of them from one district. Most of those 93 are certainly one family.
Joining them is the largest single piece of work this archive has left.

This does not join anybody. It sorts the 93 into what can be worked with and
what cannot, and then says which pairs sit close enough in place and time to be
worth a registrar's morning.

  anchored   has a year AND a place - the ones a register search can start from
  dated      has a year only
  placed     has a place only
  bare       neither, and nothing here will ever move them
"""
import sys, os, re, json, collections, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom
from build_site_data import JUNK

P, F = gedcom.load()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# One fold, shared with the rest of the archive. A private copy here is what
# produced the first run's nonsense: it did not know that "Zubrinic Xubrinich"
# is one surname, so seven siblings at Prozor 50 came out as seven separate
# root ancestors.
from ancestry import fold


HOUSE = re.compile(r"(?:^|[\s,])(?:br\.?\s*|no\.?\s*|kbr\.?\s*|#\s*)?(\d{1,3})(?=$|[\s,])", re.I)
NOISE = {"croatia", "hrvatska", "lika-senj county", "licko-senjska zupanija", "opcina otocac",
         "primorje-gorski kotar county", "australia", "south australia", "austria-hungary",
         "", "opcina senj", "split-dalmatia", "general reg. office"}
ALIAS = {"otocac croatia": "otocac", "kriviput": "krivi put",
         "smokvica, krmpote": "smokvica krmpotska", "smokvica": "smokvica krmpotska"}


def norm(x):
    return (x or "").lower().translate(str.maketrans("žćčšđ", "zccsd")).strip().strip('"')


def village(p):
    for ev in (gedcom.born(p), gedcom.died(p)):
        pl = ev.get("place", "")
        if not pl:
            continue
        for part in [x.strip() for x in pl.split(",") if x.strip()]:
            if norm(part) in NOISE:
                continue
            house = None
            m = HOUSE.search(part)
            if m:
                house = m.group(1)
                part = HOUSE.sub("", part).strip(" ,.")
            if not part:
                continue
            k = norm(part)
            return ALIAS.get(k, k), house
    return None, None


# The tree holds an A-Z INDEX of Zubrinici: eighteen nodes whose given name is
# a single letter, each hanging off a parent called "Zubrinic Zubrinix Xubrinic
# Zub", each with the people whose name starts with that letter as "children".
# Ninety-two people are attached to the surname this way. It is a filing system,
# not a family, and counting it as parentage makes the tree look joined when it
# is not.
INDEX = re.compile(r"^\s*[A-Z]\s*$")


def is_index(p):
    g = (p.get("given") or "").strip()
    return bool(INDEX.match(g)) or not g


Z = {x: p for x, p in P.items() if fold(p.get("surname")) == "zubrinic"}
index_nodes = {x for x, p in Z.items() if is_index(p)}
under_index = sum(len([c for c in (F.get(f, {}).get("chil") or []) if c in P])
                  for x in index_nodes for f in (P[x].get("fams") or []))
real = {x: p for x, p in Z.items()
        if x not in index_nodes and not JUNK.search(gedcom.display(p) or "")}

roots = []
for x, p in real.items():
    par = []
    for f in (p.get("famc") or []):
        fam = F.get(f, {})
        par += [y for y in (fam.get("husb"), fam.get("wife")) if y in P]
    if any(fold(P[y].get("surname")) == "zubrinic" and y not in index_nodes for y in par):
        continue
    roots.append(x)

rows = []
for x in roots:
    p = P[x]
    by = gedcom.year(gedcom.born(p).get("date", ""))
    dy = gedcom.year(gedcom.died(p).get("date", ""))
    v, h = village(p)
    kids = 0
    spouse = None
    for f in (p.get("fams") or []):
        fam = F.get(f, {})
        kids += len([c for c in (fam.get("chil") or []) if c in P])
        sp = fam.get("husb") if fam.get("wife") == x else fam.get("wife")
        if sp in P and not spouse:
            spouse = gedcom.display(P[sp])
    state = ("anchored" if by and v else "dated" if by else "placed" if v else "bare")
    rows.append({"id": x, "name": gedcom.display(p), "byear": by, "dyear": dy,
                 "village": v, "house": h, "children": kids, "spouse": spouse,
                 "state": state})

rows.sort(key=lambda r: (r["state"] != "anchored", -(r["children"]), r["byear"] or 9999))
st = collections.Counter(r["state"] for r in rows)
print(f"{len(Z)} Zubrinic records in the tree")
print(f"{len(index_nodes)} are alphabetical index nodes, holding {under_index} people between them")
print(f"{len(real)} real people -> {len(rows)} with no real Zubrinic parent\n")
for k in ("anchored", "dated", "placed", "bare"):
    print(f"  {st.get(k,0):>3}  {k}")

# ---- pairs worth a registrar's morning ----------------------------------
anch = [r for r in rows if r["state"] == "anchored"]
pairs = []
for a, b in itertools.combinations(anch, 2):
    if a["village"] != b["village"]:
        continue
    gap = abs(a["byear"] - b["byear"])
    if a["house"] and b["house"] and a["house"] == b["house"]:
        why, score = f"same house, {a['village']} {a['house']}", 0
    elif gap <= 12:
        why, score = "same village, born within a dozen years — siblings?", 1
    elif 18 <= gap <= 45:
        why, score = "same village, one generation apart — parent and child?", 2
    else:
        continue
    pairs.append({"a": a["name"], "ay": a["byear"], "b": b["name"], "by": b["byear"],
                  "village": a["village"], "gap": gap, "why": why, "score": score})
pairs.sort(key=lambda p: (p["score"], p["gap"]))

print(f"\n{len(anch)} anchored fragments give {len(pairs)} pairs worth checking:\n")
for p in pairs[:20]:
    print(f"  [{p['why'][:44]:<44}] {p['a'][:26]:<26} {p['ay']}  +  {p['b'][:26]:<26} {p['by']}")

by_v = collections.Counter(r["village"] for r in rows if r["village"])
print("\nfragments by village:")
for v, n in by_v.most_common(10):
    print(f"  {n:>3}  {v}")

out = os.path.join(ROOT, "site", "src", "data", "zubrinicroots.json")
json.dump({"records": len(Z), "indexNodes": len(index_nodes), "underIndex": under_index,
           "real": len(real), "fragments": rows, "pairs": pairs}, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
