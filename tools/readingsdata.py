#!/usr/bin/env python3
"""Publish what this archive has actually read, with the citation, for everyone.

WHY. sources/readings.psv is the archive's record of documents READ OUT -- one
row per person per document, each carrying the register's own words. On 20
September 2026 it held 111 rows and was published NOWHERE.

/searched lists the SITTINGS -- which books were opened, what came of them. A
person's page showed a state badge saying «read». Neither showed the citation.
So the site could tell you that a document existed for somebody and never tell
you what it said, which is the one thing an evidence-first archive is for.

The gap was invisible because coverage.py had the readings and only ever used
them to compute a state. The words went in and a colour came out.

THE DERIVED RULE TRAVELS WITH THE DATA. readingslib applies the archive's
published rule that «a baptism counts as a reading for the child AND for both
parents». A derived credit is marked as derived and carries the child it came
through, because «a register names you» and «a register is about you» are not
the same claim and this archive does not blur them -- so the page can say which
it is rather than presenting both as the same thing.

Reads  sources/readings.psv, via tools/readingslib.py
Writes site/src/data/readings.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readingslib  # noqa: E402

REPO = "https://github.com/daviddef/TheBlazevic/blob/main"
NOTE = re.compile(r"^notes/[a-z0-9][a-z0-9\-]*\.md$")
# Where a citation says it was read INDEX ONLY, the page has never been opened.
INDEX_ONLY = re.compile(r"\bINDEX ONLY\b", re.I)


def main():
    people = {}
    for f in ("people.json", "ancestors.json"):
        for p in json.load(open(os.path.join(DATA, f), encoding="utf-8")):
            people.setdefault(p["slug"], p)

    index = readingslib.by_slug(ROOT, DATA)
    by_slug, flat = {}, []
    for slug, rows in index.items():
        p = people.get(slug) or {}
        out = []
        for r in rows:
            where = r["where"]
            item = {
                "kind": r["kind"], "year": r["year"], "cite": r["cite"],
                "derived": r["derived"], "via": r["via"],
                "viaName": (people.get(r["via"]) or {}).get("name", "") if r["via"] else "",
                "where": where,
                "href": f"{REPO}/{where}" if NOTE.match(where) else "",
                "indexOnly": bool(INDEX_ONLY.search(r["cite"])),
            }
            out.append(item)
            if not r["derived"]:
                flat.append({**item, "slug": slug, "name": p.get("name", slug),
                             "ahn": p.get("ahn")})
        out.sort(key=lambda x: (x["derived"], x["year"]))
        by_slug[slug] = {
            "slug": slug, "name": p.get("name", slug), "ahn": p.get("ahn"),
            "rows": out,
            "direct": sum(1 for x in out if not x["derived"]),
            "derived": sum(1 for x in out if x["derived"]),
        }

    flat.sort(key=lambda x: (x["year"], x["name"]))
    kinds = {}
    for r in flat:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    years = [int(r["year"]) for r in flat if r["year"].isdigit()]

    doc = {
        "note": ("Every document this archive has read out, with the citation in the "
                 "register's own words. Built by tools/readingsdata.py from "
                 "sources/readings.psv."),
        "counts": {
            "rows": len(flat),
            "people": len(by_slug),
            "derived": sum(v["derived"] for v in by_slug.values()),
            "onDirectLine": sum(1 for v in by_slug.values() if v["ahn"]),
            "indexOnly": sum(1 for r in flat if r["indexOnly"]),
            "earliest": min(years) if years else None,
            "latest": max(years) if years else None,
        },
        "kinds": sorted(kinds.items(), key=lambda kv: -kv[1]),
        "rows": flat,
        "bySlug": by_slug,
    }
    with open(os.path.join(DATA, "readings.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    c = doc["counts"]
    print(f"readings.json — {c['rows']} documents read for {c['people']} people "
          f"({c['derived']} derived credits), {c['earliest']}–{c['latest']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
