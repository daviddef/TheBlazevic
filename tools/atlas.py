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
import atlasdata, geocode as G
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

ARK = re.compile(r"ark:/61903/([0-9]:[0-9]:[A-Z0-9\-]+)")
CC  = re.compile(r"[?&]cc=([0-9]+)")
WC  = re.compile(r"[?&]wc=([^\s\"&)<]+)")
COLL = re.compile(r'"([^"]{8,80}?),?\s*\d{4}\s*[-\u2013]\s*\d{4},?"')


def films_by_coord(people, gaz):
    """Register images cited in this archive's own notes, keyed by where they are.

    The citations are written out in full inside free-text notes — collection,
    ark, cc and wc — so they carry everything needed to open the book at the
    right page. What they do not carry is a place: that comes from the person
    the note is attached to, and the place strings differ between the notes and
    the place list ("Klenovica 22" against "Klenovica, Croatia"). Both sides are
    resolved through the gazetteer and matched on the coordinate, which is the
    one thing the two spellings agree about.
    """
    out = {}
    for p in people:
        where = p.get("bornPlace") or p.get("baptisedPlace") or p.get("diedPlace")
        hit = G.find(where, gaz) if where else None
        if not hit:
            continue
        key = (round(hit["lat"], 4), round(hit["lon"], 4))
        for note in (p.get("notes") or []):
            m = ARK.search(note)
            if not m:
                continue
            cc, wc = CC.search(note), WC.search(note)
            coll = COLL.search(note)
            out.setdefault(key, {})[m.group(1)] = {
                "t": (coll.group(1) if coll else "Parish register image"),
                "ark": m.group(1),
                "cc": cc.group(1) if cc else "",
                "wc": (wc.group(1).replace("%3A", ":").replace("%2C", ",") if wc else ""),
            }
    return out


def main():
    places = J("places.json")
    people = J("people.json")
    people = people if isinstance(people, list) else people.get("people", [])
    gaz = G.load()
    films = films_by_coord(people, gaz)
    who = {}
    for r in people:
        p = r.get("bornPlace")
        if p and r.get("name"):
            who.setdefault(p, []).append(r)
    rows = []
    for p in places:
        name = p["place"]
        ppl = who.get(name, [])
        hit = G.find(name, gaz)
        key = (round(hit["lat"], 4), round(hit["lon"], 4)) if hit else None
        f = list(films.get(key, {}).values())
        rows.append({
            "name": name.split(",")[0].strip() or name,
            "_lookup": name, "cat": cat(name), "n": p.get("n") or 0,
            "films": f[:30], "nfilms": len(f),
            "what": name,
            "people": [{"n": x["name"], "w": f"/people/{x['slug']}/" if x.get("slug") else None}
                       for x in ppl[:12]],
            "more": max(0, len(ppl) - 12) or None,
        })
    atlasdata.build(rows, OUT, countries=["Hrvatska","Croatia","Bosna","Bosnia","Srbija","Serbia","Italia","Italy","Slovenija","Slovenia","Magyarország","Hungary","Australia","Österreich","Austria"])

if __name__ == "__main__":
    sys.exit(main())
