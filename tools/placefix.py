#!/usr/bin/env python3
"""Find every published person carrying a place string that names the wrong place.

The gazetteer folds these already, so the village counts have been right for a
while. What was never fixed is the person page, which prints the raw string —
so a reader meeting Juraj Blažević is told he was born in Dubrovnik-Neretva
county, 400 km from the village the register names.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "places-wrong.psv")

rules = []
for line in open(SRC, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split("|")
    if len(parts) != 5:
        sys.exit(f"places-wrong.psv: expected 5 fields, got {len(parts)}: {line[:60]}")
    m, reads, actually, km, why = parts
    rules.append({"match": m, "reads": reads, "actually": actually,
                  "km": int(km), "why": why})

people = []
for f in ("people.json", "ancestors.json"):
    p = os.path.join(ROOT, "site", "src", "data", f)
    if os.path.exists(p):
        people += json.load(open(p, encoding="utf-8"))

hits, by_slug = [], {}
seen = set()
for p in people:
    slug = p.get("slug")
    if not slug or slug in seen:
        continue
    seen.add(slug)
    for field, label in (("bornPlace", "born"), ("diedPlace", "died")):
        raw = p.get(field) or ""
        if not raw:
            continue
        for r in rules:
            if r["match"].lower() in raw.lower():
                row = {"slug": slug, "name": p.get("name"), "field": label,
                       "raw": raw, **r}
                hits.append(row)
                by_slug.setdefault(slug, []).append(row)

out = {"rules": rules, "hits": hits, "bySlug": by_slug,
       "people": len(by_slug)}
dest = os.path.join(ROOT, "site", "src", "data", "placefixes.json")
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for r in rules:
    n = sum(1 for h in hits if h["match"] == r["match"])
    print(f"  {n:>3}  {r['match']:<26} -> {r['actually'].split(',')[0]}")
print(f"\n{len(hits)} place strings on {len(by_slug)} people")
print("wrote site/src/data/placefixes.json")
