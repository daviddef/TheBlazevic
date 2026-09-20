#!/usr/bin/env python3
"""Which parish books are INDEXED — the table, published.

WHY THIS TOOL EXISTS. `sources/familysearch/indexed.psv` decides how every
register row on the work list is planned: an indexed book is a search box and an
unindexed one is a sitting in front of a film. It is the most consequential
measurement in the archive.

It was also, until 20 September 2026, read by NOTHING. No tool loaded it, no
page showed it, and the only way to learn what it says was to open the file. Its
findings reached the site as prose inside work-list rows, which is where a
conclusion goes to be forgotten. This tool puts the measurement itself on the
site, with the corrections attached, because the corrections are the point: the
table has been wrong twice and both times in a way that would have cost a
sitting.

THREE SHAPES OF ROW, and the third is the one that catches people out.

    collection named, event named    the book is indexed
    collection «—»,   event «none»   nothing indexed for this parish
    collection named, event «—»      A COLLECTION THAT IS NOT A REGISTER

The third is «Croatia, Lika-Senj, Deaths, from 1500 to 2024», which is the FIND
A GRAVE index — gravestones this archive already holds in graves.json — sitting
in the results looking exactly like a parish death register. The file warns
«Do not count it», and this tool carries the warning through to the page rather
than letting a reader total the collections and get the wrong number.

A row naming NEITHER — «Brinje|—|none|…» — is the zero shape, and it is one of
the most useful rows in the file: it is the difference between «not searched»
and «searched and empty». It is data, not a fault.

WHAT IT REFUSES. A row with no parish, and any row that is not five fields.

Reads  sources/familysearch/indexed.psv
Writes site/src/data/indexed.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
PSV = os.path.join(ROOT, "sources", "familysearch", "indexed.psv")

# A parish with no indexed collection at all. The dash is how the file writes it.
NONE = {"—", "-", "", "none"}


def main():
    rows, fails = [], []
    for n, line in enumerate(open(PSV, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = [x.strip() for x in line.split("|")]
        if len(f) != 5:
            fails.append(f"line {n}: expected 5 fields, got {len(f)}")
            continue
        parish, collection, event, windows, note = f
        if not parish:
            fails.append(f"line {n}: every row needs a parish")
            continue
        has_coll = collection.lower() not in NONE
        has_event = event.lower() not in NONE
        # Neither named is the ZERO shape — «Brinje|—|none|…» — and it is one of
        # the most useful rows in the file. It is data, not a fault.
        # A named collection with no event is the Find a Grave shape: real, and
        # deliberately NOT counted as an indexed register.
        not_a_register = has_coll and not has_event
        indexed = has_coll and has_event
        rows.append({
            "parish": parish, "collection": collection if (indexed or not_a_register) else "",
            "event": event, "windows": windows, "note": note,
            "indexed": indexed,
            "notARegister": not_a_register or "FIND A GRAVE" in note.upper(),
        })

    if fails:
        print(f"FAIL  {len(fails)} problem(s) in indexed.psv:")
        for f in fails:
            print("        " + f)
        return 1

    parishes = {}
    for r in rows:
        p = parishes.setdefault(r["parish"], {
            "parish": r["parish"], "rows": [], "indexed": False,
            "events": [], "collections": 0})
        p["rows"].append(r)
        if r["indexed"] and not r["notARegister"]:
            p["indexed"] = True
            p["collections"] += 1
            if r["event"] not in p["events"]:
                p["events"].append(r["event"])

    # Indexed parishes first, then the zeros, each alphabetical: the page reads
    # as «here is what you can search, and here is what you cannot».
    order = sorted(parishes.values(), key=lambda p: (not p["indexed"], p["parish"]))

    doc = {
        "note": ("Which parish books are indexed as searchable text, measured parish by "
                 "parish through the FamilySearch persona search. Built by "
                 "tools/indexcoverage.py from sources/familysearch/indexed.psv."),
        "measured": "20 September 2026",
        "parishes": order,
        "rows": rows,
        "counts": {
            "parishes": len(order),
            "indexed": sum(1 for p in order if p["indexed"]),
            "zero": sum(1 for p in order if not p["indexed"]),
            "collections": sum(p["collections"] for p in order),
        },
    }
    with open(os.path.join(DATA, "indexed.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    c = doc["counts"]
    print(f"indexed.json — {c['parishes']} parishes: {c['indexed']} indexed across "
          f"{c['collections']} collections, {c['zero']} with nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
