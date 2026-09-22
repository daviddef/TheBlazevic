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

# ---------------------------------------------------------------------------
# A SLUG, SO THE NAME CAN BE A LINK.
#
# The header of found.psv says these people are «deliberately NOT given slugs
# and NOT merged into the tree», and that still holds where it matters: this
# slug is the ARCHIVE'S, it names a page under /found/, and nothing about it
# enters people.json or pretends the MyHeritage export knows these people.
# What changes is only that a reader can click a name instead of reading it
# as plain text beside the linked names around it.
#
# TWO SPELLINGS ARE NOT ONE MAN. «Stephanus Zubrinic», baptised at Otocac in
# 1856, son of ahnentafel 10 and 11; and «Stephanus Žubrinić», baptised at
# Šumećica in 1858, son of Michael Žubrinić and Maria Marković. Folded for a
# URL they are the same string, and this archive does not merge records on a
# name. Where a base slug repeats, the year of the reading separates them,
# and if that is not enough the build stops rather than guess.
# ---------------------------------------------------------------------------
import re, unicodedata

def slugify(s):
    s = unicodedata.normalize("NFD", s).replace("\u0111", "d").replace("\u0110", "D")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

def year_of(d):
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", d or "")
    return m.group(1) if m else ""

base = {}
for r in rows:
    base.setdefault(slugify(r["name"]), []).append(r)
for b, group in base.items():
    for r in group:
        r["slug"] = b if len(group) == 1 else (b + "-" + year_of(r["date"]) if year_of(r["date"]) else b)

seen = {}
for r in rows:
    if r["slug"] in seen:
        sys.exit("found.psv: two rows want the slug %r — %r and %r. Separate them by hand; "
                 "this archive does not merge records on a name."
                 % (r["slug"], seen[r["slug"]]["name"], r["name"]))
    seen[r["slug"]] = r

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
print("found.json — %d people the tree does not have, %d of them on the direct line, "
      "%d with a page of their own" % (len(rows), out["onDirectLine"], len(rows)))
