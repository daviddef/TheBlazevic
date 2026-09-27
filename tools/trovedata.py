#!/usr/bin/env python3
"""The verified Trove hits, as data the page can count.

Written 28 September 2026, the day after the first Trove sweep put a
hand-typed table of ten articles on /port-pirie/. That table was already the
fault [row 68](/worklist/) had just closed — a number typed into prose that
the data should have been asked for — and it would have drifted the moment
the eleventh article was found.

THE RULE THIS FILE ENFORCES IS ABOUT WHAT COUNTS AS A HIT. Trove's search is
fuzzy: it reports 9,263 newspaper matches for «Zubrinich» and the earliest
are advertising columns containing no such name. sources/trove.psv holds ONLY
articles whose fetched OCR was read and found to contain the string, one line
each, written by hand from what was read. The big number stays in
sources/searched.json where it belongs, as context.

So the page says «N articles» by counting rows, and if a row is added or
withdrawn the sentence moves with it.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "trove.psv")
OUT = os.path.join(ROOT, "site", "src", "data", "trove.json")

FIELDS = ["date", "paper", "page", "surname", "who", "what", "id"]

rows = []
for line in open(SRC, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    f = [x.strip() for x in line.split("|")]
    if len(f) != len(FIELDS):
        raise SystemExit(
            "sources/trove.psv: %d field(s), want %d — %s"
            % (len(f), len(FIELDS), line[:70]))
    r = dict(zip(FIELDS, f))
    r["url"] = "https://nla.gov.au/nla.news-article%s" % r["id"]
    rows.append(r)

rows.sort(key=lambda r: r["date"])

# The spellings, counted rather than asserted. Xubrinich and Zubrinick are in
# here as SPELLINGS OF THE SCANNER, not of the family: one 1925 paragraph
# carries «Mrs. M. ZubrinIck» and «Mrs. Zubrlnich» three words apart.
spellings = {}
for r in rows:
    spellings[r["surname"]] = spellings.get(r["surname"], 0) + 1

states = {"SA": 0, "NSW": 0}
for r in rows:
    states["NSW" if "NSW" in r["paper"] else "SA"] += 1

out = {
    "rows": rows,
    "count": len(rows),
    "spellings": sorted(spellings.items(), key=lambda kv: -kv[1]),
    "states": states,
    "earliest": rows[0]["date"][:4] if rows else "",
    "latest": rows[-1]["date"][:4] if rows else "",
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("trove.json — %d verified article(s), %s–%s, %s"
      % (out["count"], out["earliest"], out["latest"],
         ", ".join("%s %d" % kv for kv in out["spellings"])))
