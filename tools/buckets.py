#!/usr/bin/env python3
"""Sorting buckets that are still acting as parents.

This archive already found and un-published four of these: "1800-1830 Birth -
Selce Papic (Papa)" and three like it, removed because publishing research
scaffolding as an ancestor "would be a lie".

They were removed from the list of PEOPLE. They were not removed from the list
of PARENTS. A bucket that is hidden from the register still sits in the tree as
the father of published people, and every tool that asks "does this person have a
parent?" gets the answer yes.

That matters most on /zubrinic-roots, where a loose end is defined as a Zubrinic
with no real Zubrinic parent. The fragment count there treats "Brothers [of
Josephus] Zubrinic" as a real Zubrinic parent, so anyone hanging off a bucket was
counted as joined. They are not joined. They are loose ends with a label where
the father should be.
"""
import sys, os, re, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom
from ancestry import fold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
P, F = gedcom.load()
pub = {p["id"]: p for p in json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))}

# What a bucket looks like. Deliberately narrow: these are phrases no priest ever
# wrote, and no person was ever called.
BUCKET = re.compile(
    r"\bbrothers?\b|\bsisters?\b|\bto be sorted\b|\bfor sorting\b|\bsorting\b|"
    r"\bworking\b|\bit seems\b|\bunknown\b|\d{4}\s*-\s*\d{4}\s*birth", re.I)


def is_bucket(pid):
    return bool(BUCKET.search(gedcom.display(P[pid]) or ""))


rows, orphaned = [], []
for pid in P:
    if not is_bucket(pid):
        continue
    kids = []
    for f in (P[pid].get("fams") or []):
        kids += [c for c in (F.get(f, {}).get("chil") or []) if c in P]
    if not kids:
        continue
    pk = [c for c in kids if c in pub]
    if not pk:
        continue
    rows.append({"name": gedcom.display(P[pid]), "id": pid,
                 "children": len(kids), "published": len(pk),
                 "family": fold(P[pid].get("surname") or "") or "—"})

# published people whose every named parent is a bucket
for cid, rec in pub.items():
    par = []
    for f in (P.get(cid, {}).get("famc") or []):
        fam = F.get(f, {})
        par += [fam[r] for r in ("husb", "wife") if fam.get(r) in P]
    if par and all(is_bucket(x) for x in par):
        orphaned.append({"id": cid, "name": rec["name"], "slug": rec.get("slug"),
                         "family": fold(P[cid].get("surname") or ""),
                         "parent": gedcom.display(P[par[0]])})

rows.sort(key=lambda r: -r["published"])
by_fam = collections.Counter(o["family"] for o in orphaned)

print(f"{len(rows)} sorting buckets are still acting as a parent")
print(f"{sum(r['published'] for r in rows)} published people hang off one")
print(f"{len(orphaned)} of them have NO other parent at all\n")
for r in rows[:16]:
    print(f"  {r['published']:>3} published / {r['children']:>3} total   {r['name'][:52]}")
print("\norphaned-by-bucket, by family:")
for f, n in by_fam.most_common():
    print(f"  {n:>3}  {f}")

out = os.path.join(DATA, "buckets.json")
json.dump({"buckets": rows, "orphaned": orphaned,
           "hanging": sum(r["published"] for r in rows)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
