#!/usr/bin/env python3
"""Turn the parish holdings into a worklist: who to look for, in which book.

Reading a film is expensive and the expensive part is not the reading, it is
not knowing what you are looking for. This takes every published person with a
place, works out which parish register their birth or death was written in, and
says whether the year falls inside what that parish's films actually cover.

The output is a checklist per book, ordered by year, so a sitting at the viewer
is a list to tick off rather than a search.
"""
import json, os, re, collections

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
