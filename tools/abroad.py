#!/usr/bin/env python3
"""The raw catch from the commercial indexes — published, as it always meant to be.

WHY. Three files under sources/findmypast hold 308 rows harvested during a
two-day trial subscription in September 2026: every record returned for
ZUBRINICH (142), every record for ZUBRINIC (106), and the whole South
Australian civil-registration limb (60 — thirty-five births, eleven marriages,
fourteen deaths, three generations).

None of it was published. /america narrates what was FOUND; /port-pirie works
from gravestones. The rows themselves reached no page.

And the zubrinich file says in its own header that it is «the RAW CATCH, in the
same spirit as /register» -- which IS a page here. The intention was always to
publish it. It just never was.

WHAT A ROW IS, AND IS NOT. An index entry on a commercial site. NOT a document
read. A date here is somebody else's transcription of somebody else's register,
and the archive has spent the last week proving how badly that can go -- a
surname rendered «Piberich» that occurs nowhere else, a mother named Marie where
the page reads Antonie. These rows are leads. sources/readings.psv is evidence.
The page says so at the top and the distinction is not decorative.

THE SPELLINGS ARE THE POINT. ZUBRINICH returns 191 records and ZUBRINIC a
different 119 -- one family, two catches, and neither query finds the other.

AND THE NEGATIVES ARE PUBLISHED TOO. sources/findmypast/probes-2026-09-16.psv
records every search run against FindMyPast with its result, and most of them
are zeros. Its own header says why that is worth keeping: «a zero costs the same
as a find to obtain and nothing at all to repeat». An archive that publishes
only its hits is telling its next reader to run every one of those searches
again.

Reads  sources/findmypast/zubrinich-2026-09-13.psv   name|born|died|year|set|place
       sources/findmypast/zubrinic-2026-09-14.psv    surname|forename|born|died|year|set|place
       sources/findmypast/south-australia-bmd-2026-09-16.psv  kind|name|year|parents or spouse|district
       sources/findmypast/electoral-rolls-2026-09-16.psv      given|year|occupation|address|sub|district|state|household
       sources/findmypast/probes-2026-09-16.psv               kind|query|set|result|meaning
Writes site/src/data/abroad.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
FMP = os.path.join(ROOT, "sources", "findmypast")
KIND = {"B": "birth", "M": "marriage", "D": "death"}
DASH = {"—", "-", ""}


def clean(x):
    x = (x or "").strip()
    return "" if x in DASH else x


def rows_of(path, n):
    out = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = [clean(x) for x in line.split("|")]
        if len(f) != n:
            sys.exit(f"{path}: line {i}: expected {n} fields, got {len(f)}")
        out.append(f)
    return out


def main():
    recs = []

    for name, born, died, year, rset, place in rows_of(
            os.path.join(FMP, "zubrinich-2026-09-13.psv"), 6):
        recs.append({"surname": "Zubrinich", "name": name, "born": born, "died": died,
                     "year": year, "set": rset, "place": place, "source": "FindMyPast",
                     "harvested": "13 September 2026"})

    for surname, fore, born, died, year, rset, place in rows_of(
            os.path.join(FMP, "zubrinic-2026-09-14.psv"), 7):
        recs.append({"surname": surname or "Zubrinic", "name": fore, "born": born,
                     "died": died, "year": year, "set": rset, "place": place,
                     "source": "FindMyPast", "harvested": "14 September 2026"})

    sa = []
    for kind, name, year, rel, district in rows_of(
            os.path.join(FMP, "south-australia-bmd-2026-09-16.psv"), 5):
        sa.append({"kind": KIND.get(kind, kind), "name": name, "year": year,
                   "rel": rel, "district": district})

    rolls = []
    for given, year, occ, addr, sub, district, state, house in rows_of(
            os.path.join(FMP, "electoral-rolls-2026-09-16.psv"), 8):
        rolls.append({"given": given, "year": year, "occupation": occ, "address": addr,
                      "sub": sub, "district": district, "state": state, "household": house})

    probes = []
    for kind, query, rset, result, means in rows_of(
            os.path.join(FMP, "probes-2026-09-16.psv"), 5):
        n = int(result) if result.isdigit() else None
        probes.append({"kind": kind, "query": query, "set": rset, "result": result,
                       "n": n, "means": means, "zero": n == 0})

    # An address repeated across roll years is a household standing still, which
    # is a claim no single record makes.
    addresses = {}
    for r in rolls:
        if r["address"]:
            addresses.setdefault(r["address"], set()).add(r["year"])

    # The two spellings are the whole lesson: one family, two catches, and
    # neither query returns the other's records.
    spellings = {}
    sets, places = {}, {}
    for r in recs:
        spellings[r["surname"]] = spellings.get(r["surname"], 0) + 1
        if r["set"]:
            sets[r["set"]] = sets.get(r["set"], 0) + 1
        if r["place"]:
            places[r["place"]] = places.get(r["place"], 0) + 1

    years = [int(y) for y in (r["year"] for r in recs) if y.isdigit()]
    sayears = [int(r["year"]) for r in sa if r["year"].isdigit()]

    def top(d, n):
        return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

    recs.sort(key=lambda r: (r["year"] or "9999", r["surname"], r["name"]))
    sa.sort(key=lambda r: (r["year"] or "9999", r["name"]))
    rolls.sort(key=lambda r: (r["address"], r["year"], r["given"]))
    probes.sort(key=lambda r: (r["kind"], r["query"]))

    doc = {
        "note": ("The raw catch from the commercial indexes, harvested during a two-day "
                 "trial subscription. Index entries, not documents read. Built by "
                 "tools/abroad.py."),
        "counts": {
            "records": len(recs),
            "sa": len(sa),
            "total": len(recs) + len(sa),
            "sets": len(sets),
            "places": len(places),
            "earliest": min(years) if years else None,
            "latest": max(years) if years else None,
            "saEarliest": min(sayears) if sayears else None,
            "saLatest": max(sayears) if sayears else None,
            "rolls": len(rolls),
            "rollPeople": len({r["given"] for r in rolls}),
            "rollYears": sorted({r["year"] for r in rolls}),
            "probes": len(probes),
            "probeZeros": sum(1 for r in probes if r["zero"]),
            "sharedAddresses": sum(1 for v in addresses.values() if len(v) > 1),
        },
        "spellings": sorted(spellings.items(), key=lambda kv: -kv[1]),
        "topSets": top(sets, 14),
        "topPlaces": top(places, 16),
        "saKinds": sorted({k: sum(1 for r in sa if r["kind"] == k)
                           for k in {x["kind"] for x in sa}}.items(),
                          key=lambda kv: -kv[1]),
        "records": recs,
        "sa": sa,
        "rolls": rolls,
        "probes": probes,
    }
    with open(os.path.join(DATA, "abroad.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    c = doc["counts"]
    print(f"abroad.json — {c['total']} index rows: {c['records']} FindMyPast "
          f"({c['earliest']}–{c['latest']}) and {c['sa']} South Australian civil entries; "
          f"{c['rolls']} electoral-roll transcripts and {c['probes']} searches "
          f"({c['probeZeros']} of them zeros)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
