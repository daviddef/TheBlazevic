#!/usr/bin/env python3
"""Fail the build if a page links to a person page that will not be generated.

Person slugs are derived from names, and names in this tree change spelling on
a whim, so a hand-written link rots quietly. This makes it loud.
"""
import json, re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

slugs = {p["slug"] for f in ("people.json", "ancestors.json", "line.json")
         for p in json.load(open(os.path.join(DATA, f), encoding="utf-8"))}

bad = []
for f in glob.glob(os.path.join(ROOT, "site", "src", "pages", "**", "*.astro"), recursive=True):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r'/people/([a-z0-9\-]+)', src):
        if m.group(1) not in slugs and m.group(1) != "index":
            bad.append((os.path.relpath(f, ROOT), m.group(1)))

for f, s in sorted(set(bad)):
    print(f"BROKEN  {f}  ->  /people/{s}")
print(f"{len(set(bad))} broken person link(s); {len(slugs)} person pages will be generated.")
sys.exit(1 if bad else 0)
