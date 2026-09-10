#!/usr/bin/env python3
"""Names that can safely be turned into links in running prose.

The Defranceschi archive links every known person's name wherever it appears.
That cannot be copied here unchanged: this archive holds 18 men called Ivan
Blazevic and 12 women called Marija Kalanj, and linking one of eighteen would
be the merge-on-a-name error the rest of the site exists to document.

So only names held by EXACTLY ONE published person are indexed. Everything
repeated is left as plain text, and /people carries the disambiguation.

Emitted as [display name, slug, how many other spellings fold to it].
"""
import json, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

people = list({p["id"]: p for p in
               json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8")) +
               json.load(open(os.path.join(DATA, "ancestors.json"), encoding="utf-8"))}.values())


def clean(n):
    """Drop the tree's bracketed alternatives and slash-joined variants, so
    'Joannes / Juan / Ivan Zubrinic' offers 'Joannes Zubrinic' to match on."""
    n = re.sub(r"\s*\(.*?\)\s*", " ", n or "")
    n = re.sub(r"\s+", " ", n).strip()
    return n


def variants(p):
    """Every form of the name worth matching in prose."""
    out = set()
    full = clean(p.get("name"))
    if full:
        out.add(full)
    given, surname = clean(p.get("given")), clean(p.get("surname"))
    if given and surname:
        # each given-name alternative paired with the surname
        for g in re.split(r"\s*/\s*", given):
            g = g.strip().strip('"')
            if len(g) > 2:
                out.add(f"{g} {surname}")
        nick = (p.get("nick") or "").strip().strip('"')
        if len(nick) > 2:
            out.add(f"{nick} {surname}")
    # a bare given name is never enough to identify anybody
    return {o for o in out if len(o) >= 7 and " " in o}


claims = collections.defaultdict(set)
for p in people:
    for v in variants(p):
        claims[v.lower()].add(p["slug"])

display = {}
for p in people:
    for v in variants(p):
        display.setdefault(v.lower(), v)

rows = []
for key, slugs in claims.items():
    if len(slugs) != 1:
        continue                      # ambiguous: leave it as plain text
    rows.append([display[key], next(iter(slugs)), len(claims[key])])

rows.sort(key=lambda r: -len(r[0]))   # longest first, so the regex prefers them
out = os.path.join(ROOT, "site", "public", "whoindex.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)

amb = sum(1 for s in claims.values() if len(s) > 1)
print(f"{len(rows)} unambiguous name forms indexed for auto-linking")
print(f"{amb} forms left as plain text because more than one person answers to them")
print(f"  covering {len({s for v in claims.values() if len(v) > 1 for s in v})} people")
print(f"wrote {os.path.relpath(out, ROOT)}")
