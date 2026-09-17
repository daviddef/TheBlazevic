#!/usr/bin/env python3
"""People read out of a register who are not in the family tree.

Every other source in this archive keys on a slug from the GEDCOM, so a person
could only be recorded if MyHeritage already knew about them. On 15 September
2026 ahnentafel 54's baptism named his father and mother and there was nowhere
to put them. This reads sources/found.psv and emits the data the site needs,
keeping the archive's own evidence beside the tree rather than inside it.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for line in open(os.path.join(ROOT, "sources", "found.psv"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    f = line.split("|")
    if len(f) != 7:
        sys.exit("found.psv: expected 7 fields, got %d: %s" % (len(f), line[:70]))
    name, ahn, relation, event, date, place, citation = [x.strip() for x in f]
    if not name or not relation or not citation:
        sys.exit("found.psv: name, relation and citation are all required: %s" % line[:70])
    if ahn and not ahn.isdigit():
        sys.exit("found.psv: ahn must be a number or empty: %s" % line[:70])
    rows.append({"name": name, "ahn": int(ahn) if ahn else None,
                 "relation": relation, "event": event, "date": date,
                 "place": place, "citation": citation})

byplace = {}
for r in rows:
    byplace.setdefault(r["place"], []).append(r["name"])

out = {
    "note": ("People read out of a register who are not in the family tree. "
             "Deliberately not given slugs and not merged into it: the tree is a "
             "MyHeritage export and this archive does not edit it."),
    "count": len(rows),
    "onDirectLine": sum(1 for r in rows if r["ahn"]),
    "places": {k: len(v) for k, v in sorted(byplace.items())},
    "rows": rows,
}
dest = os.path.join(ROOT, "site", "src", "data", "found.json")
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("found.json — %d people the tree does not have, %d of them on the direct line"
      % (len(rows), out["onDirectLine"]))
