#!/usr/bin/env python3
"""Count the household by-names read out of the registers.

Question 5 asked whether "Papa" was a surname or a by-name. The answer turned
out not to be about this family at all: the parish wrote both names as a matter
of course. This counts what has actually been read, so the claim rests on a
number rather than on an impression.
"""
import json, os, collections, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for line in open(os.path.join(ROOT, "sources", "bynames.psv"), encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    f = line.split("|")
    if len(f) != 8:
        sys.exit(f"bynames.psv: expected 8 fields, got {len(f)}: {line[:60]}")
    surname, conn, byname, written, place, year, und, src = f
    rows.append({"surname": surname, "conn": conn, "byname": byname,
                 "written": written, "place": place, "year": int(year),
                 "underlined": und, "source": src})

rows.sort(key=lambda r: (r["year"], r["surname"]))
pairs = sorted({(r["surname"], r["byname"]) for r in rows})
out = {
    "rows": rows,
    "pairs": [{"surname": a, "byname": b} for a, b in pairs],
    "nPairs": len(pairs),
    "nSurnames": len({r["surname"] for r in rows}),
    "nUnderlined": sum(1 for r in rows if r["underlined"] == "u"),
    "years": [min(r["year"] for r in rows), max(r["year"] for r in rows)],
    "places": sorted({r["place"] for r in rows}),
    "byYear": sorted(collections.Counter(r["year"] for r in rows).items()),
}
json.dump(out, open(os.path.join(ROOT, "site", "src", "data", "bynames.json"),
                    "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(rows)} phrases · {out['nPairs']} distinct pairs · "
      f"{out['nSurnames']} surnames · {out['nUnderlined']} underlined · "
      f"{out['years'][0]}–{out['years'][1]}")
print("wrote site/src/data/bynames.json")
