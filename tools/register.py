#!/usr/bin/env python3
"""The raw catch: every named individual this archive has found, kin or not.

The Falco archive keeps one of these and this one did not, which meant the
people met while reading — godparents, witnesses, priests, the other brides on
the page — lived only as prose in notes/. A baptism names a priest and two
godparents; a marriage names four parents, two witnesses and an officiant.
Almost none of them are in the family tree, and all of them are evidence.

Two kinds go in:

    tree    a person carried by the MyHeritage tree and published here
    swept   a person met while reading a register act by act

Held apart deliberately. A tree entry is what the family believes; a swept
entry is what a named page says. They are not the same weight, and the page
says so.
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sources", "register"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swept import ALL as SWEPT
from ancestry import fold

DATA = os.path.join(ROOT, "site", "src", "data")
ALIAS = {"perpic": "prpic"}


def key(s):
    f = fold(s or "")
    return ALIAS.get(f, f)


rows = []

# ---- the tree ------------------------------------------------------------
pub = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8")) + \
      json.load(open(os.path.join(DATA, "ancestors.json"), encoding="utf-8"))
anc = {a["id"]: (a.get("ahnentafel") or a.get("ahn"))
       for a in json.load(open(os.path.join(DATA, "ancestors.json"), encoding="utf-8"))}
seen = set()
for p in pub:
    if p["id"] in seen:
        continue
    seen.add(p["id"])
    bits = []
    if p.get("born"):
        bits.append("b. " + p["born"] + (f", {p['bornPlace'].split(',')[0]}" if p.get("bornPlace") else ""))
    if p.get("died"):
        bits.append("d. " + p["died"] + (f", {p['diedPlace'].split(',')[0]}" if p.get("diedPlace") else ""))
    for o in (p.get("occupations") or [])[:1]:
        if o.get("what"):
            bits.append(o["what"][:60])
    a = anc.get(p["id"])
    if a:
        bits.append(f"ahnentafel {a} — a direct ancestor of Hedviga")
    rows.append({
        "name": p.get("name") or "(unnamed)",
        "surname": (p.get("surname") or "—").strip() or "—",
        "detail": " · ".join(bits) or "no dates recorded",
        "source": "MyHeritage family tree",
        "link": "", "kind": "tree", "slug": p["slug"],
        "sort": str(p.get("byear") or ""),
    })

# ---- the registers -------------------------------------------------------
slug_by_name = {}
for p in pub:
    slug_by_name.setdefault((p.get("name") or "").lower(), p["slug"])

for name, surname, detail, source in SWEPT:
    rows.append({
        "name": name, "surname": surname or "—", "detail": detail,
        "source": source, "link": "", "kind": "swept",
        "slug": slug_by_name.get(name.lower()),
        "sort": "",
    })

# group key so Perpic and Prpic, Zubrinic and Xubrinich sit together
for r in rows:
    r["group"] = key(r["surname"]) or "—"

rows.sort(key=lambda r: (r["group"], r["kind"] != "tree", r["name"]))
out = os.path.join(DATA, "register.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

kinds = collections.Counter(r["kind"] for r in rows)
groups = collections.Counter(r["group"] for r in rows)
print(f"{len(rows)} register entries -> {os.path.relpath(out, ROOT)}")
for k, n in kinds.most_common():
    print(f"  {n:>5}  {k}")
print(f"  {len(groups):>5}  distinct surnames")
print(f"  {sum(1 for r in rows if r['slug']):>5}  linked to a person page")
print("\nlargest groups:")
for g, n in groups.most_common(8):
    print(f"  {n:>5}  {g}")
