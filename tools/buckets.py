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



# ---- do the labels encode anything real? ---------------------------------
#
# "1800-1830 Birth - Selce Papic (Papa)" carries a village, a date range and a
# nadimak. "Krivi Put 136 For Sorting Perpic" carries a house number. Somebody
# grouped these children for a reason, and the question is whether the reason
# survives well enough to place a person by.
#
# The answer splits sharply on how specific the label is, so the test is run
# separately for the two kinds.

PLACES = ["Klenovica", "Ledenice", "Selce", "Senj", "Krivi Put", "Otocac",
          "Otočac", "Smokvica", "Povile", "Mrzli Dol"]
RANGE = re.compile(r"(1[6-9]\d\d)\s*-\s*(1[6-9]\d\d)")
HOUSE = re.compile(r"\b(\d{2,3})\b")


def kids_of(pid):
    out = []
    for f in (P[pid].get("fams") or []):
        out += [c for c in (F.get(f, {}).get("chil") or []) if c in pub]
    return out


labels = []
for row in rows:
    name = row["name"]
    vil = [v for v in PLACES if v.lower() in name.lower()]
    rng = RANGE.search(name)
    house = HOUSE.search(re.sub(r"1[6-9]\d\d", "", name))
    if not vil and not rng:
        continue
    agree = disagree = blank = 0
    yin = yout = 0
    for c in kids_of(row["id"]):
        pl = " ".join(filter(None, [gedcom.born(P[c]).get("place", ""),
                                    gedcom.died(P[c]).get("place", "")]))
        if vil:
            if not pl.strip():
                blank += 1
            elif any(v.lower() in pl.lower() for v in vil):
                agree += 1
            else:
                disagree += 1
        if rng:
            y = gedcom.year(gedcom.born(P[c]).get("date", ""))
            if y:
                if int(rng.group(1)) <= y <= int(rng.group(2)):
                    yin += 1
                else:
                    yout += 1
    labels.append({
        "name": name, "family": row["family"],
        "village": "/".join(dict.fromkeys(vil)) or None,
        "house": house.group(1) if house else None,
        "range": [rng.group(1), rng.group(2)] if rng else None,
        "specific": bool(house or rng),
        "agree": agree, "disagree": disagree, "blank": blank,
        "yearIn": yin, "yearOut": yout,
    })

spec = [l for l in labels if l["specific"]]
vague = [l for l in labels if not l["specific"]]
def tally(rs):
    return sum(r["agree"] for r in rs), sum(r["disagree"] for r in rs), sum(r["blank"] for r in rs)
sa, sd, sb = tally(spec)
va, vd, vb = tally(vague)
print(f"\nlabel reliability, where a child's own place can test it:")
print(f"  specific (house number or date range)  {sa} agree / {sd} disagree   ({sb} placeless)")
print(f"  vague (a town and nothing else)        {va} agree / {vd} disagree   ({vb} placeless)")
print(f"  placeless children a label could place: {sb + vb}")



# ---- how much of this archive hangs on the scaffolding? -------------------
#
# The previous section asks whether a label is accurate. This one asks something
# harder: if every sorting label were deleted, how many of the people published
# here would still be connected to Hedviga at all?
#
# The graph is parent-child and spouse edges over the whole export, living people
# included, so nothing is lost to the publication filter. "Connected" means a
# path exists - not a close one, just a path.

STRICT = re.compile(
    r"\bbrothers?\b|\bsisters?\b|to be sorted|for sorting|\bsorting\b|"
    r"\bworking\b|it seems|not real|investigation|\d{4}\s*-\s*\d{4}\s*birth", re.I)


def strict_bucket(x):
    return bool(STRICT.search(gedcom.display(P[x]) or ""))


def reachable(skip_buckets):
    adj = collections.defaultdict(set)
    for fid, f in F.items():
        nodes = [x for x in (f.get("husb"), f.get("wife")) if x in P]
        ch = [c for c in (f.get("chil") or []) if c in P]
        if skip_buckets:
            nodes = [x for x in nodes if not strict_bucket(x)]
            ch = [c for c in ch if not strict_bucket(c)]
        if len(nodes) == 2:
            adj[nodes[0]].add(nodes[1])
            adj[nodes[1]].add(nodes[0])
        for c in ch:
            for par in nodes:
                adj[par].add(c)
                adj[c].add(par)
    start = next((i for i, q in P.items()
                  if gedcom.display(q).startswith('Hedviga "Seka"')), None)
    if start is None:
        return {}
    dist, queue = {start: 0}, collections.deque([start])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


with_b, without_b = reachable(False), reachable(True)
standing = []
for fam in sorted({fold(P[i].get("surname") or "") for i in pub} - {""}):
    ids = [i for i in pub if fold(P[i].get("surname") or "") == fam]
    if not ids:
        continue
    r = sum(1 for i in ids if i in without_b)
    standing.append({"family": fam, "published": len(ids), "connected": r,
                     "pct": round(100 * r / len(ids))})
standing.sort(key=lambda x: x["pct"])
tot_pub = sum(x["published"] for x in standing)
tot_con = sum(x["connected"] for x in standing)

print(f"\nreachable from Hedviga with the labels: {len(with_b)}; "
      f"without them: {len(without_b)}")
print(f"published people still connected without any sorting label: "
      f"{tot_con} of {tot_pub} ({round(100*tot_con/tot_pub)}%)\n")
for x in standing:
    print(f"  {x['family']:<10} {x['connected']:>4} of {x['published']:<4} {x['pct']:>4}%")



# ---- per person, so the fact can reach the page it belongs on -------------
#
# All of the above lived on one summary page, which meant a reader looking at
# Anna Blazevic had no way to know that her only recorded parent is the phrase
# "Unknown Sorting Working Blazevic". A finding that changes how the whole site
# should be read has to reach the pages it is about.

linkage = {}
for cid, rec in pub.items():
    par = []
    for f in (P.get(cid, {}).get("famc") or []):
        fam = F.get(f, {})
        par += [fam[r] for r in ("husb", "wife") if fam.get(r) in P]
    labelled = [gedcom.display(P[x]) for x in par if is_bucket(x)]
    real_par = [x for x in par if not is_bucket(x)]
    entry = {}
    if labelled:
        entry["label"] = labelled[0]
        entry["only"] = not real_par          # no real parent at all
    if cid not in without_b:
        entry["unlinked"] = True              # no path to Hedviga without labels
    if entry:
        linkage[cid] = entry

lout = os.path.join(DATA, "linkage.json")
json.dump(linkage, open(lout, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_lab = sum(1 for v in linkage.values() if "label" in v)
n_only = sum(1 for v in linkage.values() if v.get("only"))
n_unl = sum(1 for v in linkage.values() if v.get("unlinked"))
print(f"\nlinkage.json: {n_lab} people with a label for a parent, "
      f"{n_only} with nothing else, {n_unl} unreachable without labels")

out = os.path.join(DATA, "buckets.json")
json.dump({"buckets": rows, "orphaned": orphaned, "labels": labels,
           "standing": standing, "connected": tot_con, "publishedTotal": tot_pub,
           "specific": {"agree": sa, "disagree": sd, "blank": sb},
           "vague": {"agree": va, "disagree": vd, "blank": vb},
           "hanging": sum(r["published"] for r in rows)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
