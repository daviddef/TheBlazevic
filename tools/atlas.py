#!/usr/bin/env python3
"""Blažević's places, for the map.

The place list carries only a name and a count. The names of the people come
from people.json, which records a birthplace for 611 of its 1,245 — and every
one of those carries a slug, so each name on the map links to its own page.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "site", "node_modules",
                                "@daviddef", "archive-kit", "kit", "tools"))
import atlasdata
D = os.path.join(HERE, "..", "site", "src", "data")
J = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))
OUT = os.path.join(HERE, "..", "site", "public", "atlas-data.json")

def cat(p):
    s = p.lower()
    if re.search(r"senj|krivi put|klenovica|sveti juraj", s):   return "senj"
    if re.search(r"otocac|otočac|lika|gospić|brinje", s): return "lika"
    if re.search(r"rijeka|crikvenica|kvarner|novi vinodol", s): return "kvarner"
    if re.search(r"croatia|hrvatska|zagreb|split|dalmat", s):   return "hr"
    return "other"

def main():
    places = J("places.json")
    people = J("people.json")
    people = people if isinstance(people, list) else people.get("people", [])
    who = {}
    for r in people:
        p = r.get("bornPlace")
        if p and r.get("name"):
            who.setdefault(p, []).append(r)
    rows = []
    for p in places:
        name = p["place"]
        ppl = who.get(name, [])
        rows.append({
            "name": name.split(",")[0].strip() or name,
            "_lookup": name, "cat": cat(name), "n": p.get("n") or 0,
            "what": name,
            "people": [{"n": x["name"], "w": f"/people/{x['slug']}/" if x.get("slug") else None}
                       for x in ppl[:12]],
            "more": max(0, len(ppl) - 12) or None,
        })
    atlasdata.build(rows, OUT, countries=["Hrvatska","Croatia","Bosna","Bosnia","Srbija","Serbia","Italia","Italy","Slovenija","Slovenia","Magyarország","Hungary","Australia","Österreich","Austria"])

if __name__ == "__main__":
    sys.exit(main())
