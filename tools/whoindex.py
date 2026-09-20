#!/usr/bin/env python3
"""Names that can safely be turned into links in running prose.

The Defranceschi archive links every known person's name wherever it appears.
That cannot be copied here unchanged: this archive holds 18 men called Ivan
Blazevic and 12 women called Marija Kalanj, and linking one of eighteen would
be the merge-on-a-name error the rest of the site exists to document.

So only names held by EXACTLY ONE published person are indexed. Everything
repeated is left as plain text, and /people carries the disambiguation.

Emitted as [display name, slug, how many other spellings fold to it].

TWO THINGS THIS FILE LEARNED ON 21 SEPTEMBER 2026, both found by a reader
noticing that a page full of names carried no links.

  * THE SURNAME IS SLASH-JOINED AS OFTEN AS THE GIVEN NAME, and only the given
    name was being split. So «Tereza Žubrinić» -- the form every page of this
    archive actually writes -- was absent, while two forms nobody writes were
    present.
  * THE INDEX IS BUILT FROM THE TREE'S SPELLING AND THE PROSE USES THE
    ARCHIVE'S. The tree holds ahnentafel 4 as «Blazevic» and every page writes
    «Blažević». The matcher was case-insensitive and not accent-insensitive, so
    z and ž were two letters and the commonest name in the archive never linked.
    That half is fixed in public/wholink.js, which now folds accents on BOTH
    sides -- the same rule namefold.py applies to the register search, where
    folding an accent «needs nobody's permission».
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
        # THE SURNAME IS SLASH-JOINED TOO, and splitting only the given name is
        # why «Tereza Žubrinić» was not in this index while «Tereza Žubrinić /
        # Zubrinic» and «Tereza Žubrinić Zubrinic» both were. The tree carries
        # her surname as «Žubrinić / Zubrinic»; every page of this archive
        # writes her as Tereza Žubrinić, and the one form the prose actually
        # uses was the one form the linker could not see.
        surnames = [x.strip().strip('"') for x in re.split(r"\s*/\s*", surname)]
        surnames = [x for x in surnames if len(x) > 2] or [surname]
        givens = [x.strip().strip('"') for x in re.split(r"\s*/\s*", given)]
        # AN INLINE QUOTED NICKNAME IS NOT PART OF THE NAME ANYBODY WRITES.
        # The tree gives ahnentafel 2 as «Ljubomir "Ljubo"», so every form this
        # file emitted carried the quotes and «Ljubomir Blažević» -- which is
        # what the pages say -- was not among them. Offer both: the name with
        # the nickname taken out, and the nickname on its own.
        for g in list(givens):
            inline = re.findall(r'"([^"]{3,})"', g)
            bare = re.sub(r'\s*"[^"]*"\s*', " ", g).strip()
            if bare and bare != g:
                givens.append(bare)
            givens.extend(inline)
        nick = (p.get("nick") or "").strip().strip('"')
        if len(nick) > 2:
            givens.append(nick)
        for sn in surnames:
            for g in givens:
                if len(g) > 2:
                    out.add(f"{g} {sn}")
    # a bare given name is never enough to identify anybody
    return {o for o in out if len(o) >= 7 and " " in o}


# sorted(), not the raw set: variants() returns a set, and set iteration order
# for strings changes with every Python process. That leaked into the order of
# `claims` and so into the order of equal-length rows below, which made this
# file differ on every run and defeated regen.py --check.
claims = collections.defaultdict(set)
for p in people:
    for v in sorted(variants(p)):
        claims[v.lower()].add(p["slug"])

display = {}
for p in people:
    for v in sorted(variants(p)):
        display.setdefault(v.lower(), v)

rows = []
for key, slugs in claims.items():
    if len(slugs) != 1:
        continue                      # ambiguous: leave it as plain text
    rows.append([display[key], next(iter(slugs)), len(claims[key])])

# longest first, so the regex prefers them; name breaks ties so the file is
# byte-identical between runs
rows.sort(key=lambda r: (-len(r[0]), r[0]))
out = os.path.join(ROOT, "site", "public", "whoindex.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)

amb = sum(1 for s in claims.values() if len(s) > 1)
print(f"{len(rows)} unambiguous name forms indexed for auto-linking")
print(f"{amb} forms left as plain text because more than one person answers to them")
print(f"  covering {len({s for v in claims.values() if len(v) > 1 for s in v})} people")
print(f"wrote {os.path.relpath(out, ROOT)}")
