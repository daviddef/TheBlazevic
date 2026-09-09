#!/usr/bin/env python3
"""Every record of the four surnames, grouped by the place it names.

The point is to see a surname as a map rather than as a pedigree. Frontier
registers identify a household by village and house number, so the house number
is kept: it is the closest thing these records have to a family identifier.

Was Zubrinic-only. Running the same reduction over Blazevic, Papic and Prpic is
what makes the villages comparable - and comparison is the whole value, because
a surname that sits in one village and a surname that sits in six are different
kinds of family.
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


# Prpic and Perpic are one family, as everywhere else in this archive.
ALIAS = {"perpic": "prpic"}
SURNAMES = ("blazevic", "zubrinic", "papic", "prpic")

def key(sn):
    f = fold(sn)
    return ALIAS.get(f, f)

# A place string in this tree is "House N, Village, County, Country" in any order
# and any degree of completeness. Reduce it to (village, house) where possible.
HOUSE = re.compile(r"(?:^|[\s,])(?:br\.?\s*|no\.?\s*|n[o°]\s*|#\s*|kbr\.?\s*)?(\d{1,3})(?=$|[\s,])", re.I)
NOISE = {"croatia", "hrvatska", "lika-senj county", "licko-senjska zupanija", "opcina otocac",
         "primorje-gorski kotar county", "australia", "south australia", "austria-hungary",
         "general reg. office", "", "opcina senj", "split-dalmatia"}


# The tree writes one village several ways. These are the same place, and
# leaving them apart makes a village look half as populated as it is.
VILLAGE_ALIAS = {
    "otocac croatia": "otocac",
    "kriviput": "krivi put",
    "krivi put, senj": "krivi put",
    "smokvica krmpotska / krmpote": "smokvica krmpotska",
    "smokvica, krmpote": "smokvica krmpotska",
    "smokvica": "smokvica krmpotska",
    "sv. jakov krmpote": "sv. jakov",
}
PRETTY = {
    "otocac": "Otočac", "krivi put": "Krivi Put",
    "smokvica krmpotska": "Smokvica Krmpotska", "sv. jakov": "Sv. Jakov",
}


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


def gather(surname):
    Z = {pid: p for pid, p in people.items() if key(p["surname"]) == surname}
    rows = []
    for pid, p in Z.items():
        for kind, e in (("b", born(p)), ("d", died(p))):
            pl = e.get("place", "")
            if not pl:
                continue
            v, h = place_key(pl)
            if not v:
                continue
            rows.append({"pid": pid, "name": display(p), "kind": kind,
                         "year": year(e.get("date", "")), "village": v,
                         "house": h, "raw": pl})
    return Z, rows


out = {}
for sn in SURNAMES:
    Z, rows = gather(sn)
    by_v = collections.defaultdict(list)
    for r in rows:
        k = norm(r["village"]).strip('"').strip()
        by_v[VILLAGE_ALIAS.get(k, k)].append(r)

    places = []
    for v, rs in by_v.items():
        yrs = [r["year"] for r in rs if r["year"]]
        houses = sorted({r["house"] for r in rs if r["house"]}, key=lambda x: int(x))
        places.append({
            "village": PRETTY.get(v, rs[0]["village"].strip('"').strip()),
            "n": len(rs),
            "from": min(yrs) if yrs else None, "to": max(yrs) if yrs else None,
            "houses": houses,
        })
    places.sort(key=lambda x: -x["n"])
    out[sn] = {"records": len(Z), "placed": len(rows), "places": places}

    print(f"\n=== {sn}: {len(Z)} records, {len(rows)} carrying a place, "
          f"{len(by_v)} distinct places")
    for pl in places[:8]:
        span = f'{pl["from"]}-{pl["to"]}' if pl["from"] else "no dates"
        print(f'  {pl["n"]:>4}  {pl["village"][:32]:<32} {span:<12} '
              f'{"houses " + ", ".join(pl["houses"]) if pl["houses"] else ""}')

import json
dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "site", "src", "data", "gazetteer.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f"\nwrote {dest}")
