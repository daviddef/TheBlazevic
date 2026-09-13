#!/usr/bin/env python3
"""The same person, entered twice — across every family this archive publishes.

This started as a Zubrinic-only check and that was the mistake. Running it over
the nine published surname groups finds the same disease everywhere: Ivan Kalanj
is in the tree twice, once dated to the day and once to the year, and his brother
Marijan with him. A grave photograph at Klenovica named four people and two of
them turned out to be four records.

A duplicate is not a research problem to be solved. It is one person counted as
two, and it quietly inflates every number this archive publishes about itself.

The test is tiered, because a shared name is not a shared person. This archive
holds eighteen Ivan Blazevics, and cousins were named for the same grandfather as
a matter of course:

    same day              identical full birth date. Near-conclusive.
    same year and place   strong, but cousins do this.
    same year only        weakest. Listed, not acted on.

Nothing is merged. The tree is reported, not edited — the same rule the rest of
this archive follows.
"""
import sys, os, re, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom
from ancestry import fold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

P, F = gedcom.load()
pub = {p["id"]: p for p in json.load(
    open(os.path.join(DATA, "people.json"), encoding="utf-8"))}

# the surname groups this archive actually publishes
GROUPS = sorted({fold(p.get("surname") or "") for p in pub.values()} - {""})


def place(p):
    for ev in (gedcom.born(p), gedcom.died(p)):
        pl = (ev.get("place") or "").split(",")[0].strip()
        if pl:
            return pl
    return None


def full_date(p):
    d = (gedcom.born(p).get("date") or "").strip().upper()
    # a bare year, or a hedge, is not a full date
    return d if len(d) > 4 and not d.startswith(("ABT", "BEF", "AFT", "EST", "CAL")) else None


# Bucket on surname and birth year, then match given names WITHIN the bucket by
# token containment rather than equality. Marijan Kalanj is entered once as
# "Marijan Cigo" and once as "Marijan" - the nickname is in one record and not
# the other, so equality misses him, and his brother Ivan, and the gravestone
# that names them both. Containment catches that; it does not catch two
# unrelated Ivans, because they have the same token set, not a nested one, and
# equality already handles those.
rough = collections.defaultdict(list)
for pid in pub:
    p = P.get(pid)
    if not p:
        continue
    sur = fold(p.get("surname") or "")
    giv = fold((p.get("given") or "").strip())
    by = gedcom.year(gedcom.born(p).get("date", ""))
    if not giv or not sur or by is None:
        continue          # an undated bare name cannot be matched on safely
    rough[(sur, by)].append((pid, frozenset(giv.split())))

BUCKET = re.compile(
    r"\bbrothers?\b|\bsisters?\b|to be sorted|for sorting|\bsorting\b|"
    r"\bworking\b|it seems|not real|investigation|\bunknown\b|"
    r"\d{4}\s*-\s*\d{4}\s*birth", re.I)


def parents(pid):
    """Each parent as a SET of folded given-name tokens.

    A set, not a string, because the tree renders one man as "Michael Miho
    Michael Xubrinich" in one record and "Michaelis / Michael / Miho / Michael
    'Miko'" in another. Comparing those as strings - or worse, on their first
    token - turns Michael and Michaelis into two men. Comparing them as sets and
    asking whether they OVERLAP gets it right.
    """
    out = {"husb": set(), "wife": set()}
    for f in (P[pid].get("famc") or []):
        fam = F.get(f, {})
        for role in ("husb", "wife"):
            o = fam.get(role)
            # A sorting label in the father's slot is not a father, and letting
            # one count here rejects real duplicates: Michael Zubrinic b.1802 is
            # the son of "Jure Georgius Juraj Zubrinic" in one record and of
            # "Brothers of Casparus (It Seems)" in the other, which is not a
            # disagreement between two fathers. It is one father and one label.
            if o in P and not BUCKET.search(gedcom.display(P[o]) or ""):
                out[role] |= set((fold(P[o].get("given") or "") or "").split())
    return out


def parents_conflict(ids):
    """True when two records name parents that share no name at all.

    The strongest signal there is, and it cuts both ways. Josephus Zubrinic born
    16 March 1845 has Michael and Maria Markovic in both copies and is plainly
    one boy. Nicolaus Zubrinic born at Otocac in 1834 is the son of Michael in
    one record and of Lucas in the other - and he is ahnentafel 10, a direct
    ancestor. Without this test the tool would have had this archive announce
    that its own great-great-grandfather was a duplicate.

    Overlap, not equality. A missing parent proves nothing and is ignored.
    """
    for role in ("husb", "wife"):
        named = [n for n in (parents(i)[role] for i in ids) if n]
        for a in range(len(named)):
            for b in range(a + 1, len(named)):
                if not overlap(named[a], named[b]):
                    return True
    return False


def near(a, b):
    """One substitution, insertion or deletion apart — Lovro / Lovre, Ane / Ana.

    Croatian given names vary in their final vowel between records without
    varying the man. Anything looser than a single edit starts merging Marija
    with Marica and Mile with Mate, so this stays at one.
    """
    if a == b:
        return True
    if min(len(a), len(b)) < 4 or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(long)):
        if long[:i] + long[i + 1:] == short:
            return True
    return False


def overlap(s1, s2):
    return any(near(x, y) for x in s1 for y in s2)


buckets = collections.defaultdict(list)
for (sur, by), members in rough.items():
    used = set()
    for i, (pid, toks) in enumerate(members):
        if pid in used:
            continue
        grp = [pid]
        for pid2, toks2 in members[i + 1:]:
            if pid2 in used:
                continue
            if toks <= toks2 or toks2 <= toks:
                grp.append(pid2)
                used.add(pid2)
        used.add(pid)
        if len(grp) > 1:
            key = (sur, " ".join(sorted(toks)), by)
            buckets[key].extend(grp)

groups = []
for (sur, giv, by), ids in buckets.items():
    if len(ids) < 2:
        continue
    dates = {full_date(P[i]) for i in ids}
    places = {place(P[i]) for i in ids} - {None}
    firm = {d for d in dates if d}
    dys = {gedcom.year(gedcom.died(P[i]).get("date", "")) for i in ids} - {None}

    # A necronym is not a duplicate. When a child died the next was very often
    # given the same name, so two records can share a surname, a given name, a
    # birth year and a village and still be two different children. Two firm and
    # DIFFERENT death years is the giveaway - one person dies once. Antonius
    # Kalanj of Klenovica 22, born 1868, is entered as dying in 1868 and in 1873,
    # and that is two boys, not one boy twice.
    if parents_conflict(ids):
        tier = "rejected — different parents"
    elif len(dys) > 1:
        tier = "rejected — two death years"
    elif len(firm) == 1 and all(full_date(P[i]) for i in ids):
        tier = "same day"
    elif len(places) == 1:
        tier = "same year and place"
    else:
        tier = "same year only"
    groups.append({
        "tier": tier, "surname": sur, "given": giv, "byear": by, "n": len(ids),
        "place": sorted(places)[0] if places else None,
        "date": sorted(firm)[0] if firm else None,
        "ids": ids,
        "names": [gedcom.display(P[i]) for i in ids],
        "slugs": [pub[i].get("slug") for i in ids],
        "dyears": sorted({gedcom.year(gedcom.died(P[i]).get("date", "")) for i in ids} - {None}),
    })

TIER = {"same day": 0, "same year and place": 1, "same year only": 2,
        "rejected — two death years": 3,
        "rejected — different parents": 4}
groups.sort(key=lambda g: (TIER[g["tier"]], g["surname"], g["byear"]))
live = [g for g in groups if not g["tier"].startswith("rejected")]
rejected = [g for g in groups if g["tier"].startswith("rejected")]
extra = sum(g["n"] - 1 for g in live)

print(f"{len(pub)} published people across {len(GROUPS)} surname groups")
print(f"{len(live)} duplicate groups holding {extra} surplus records; "
      f"{len(rejected)} rejected as two people sharing a name\n")
by_tier = collections.Counter(g["tier"] for g in groups)
for t in ("same day", "same year and place", "same year only",
          "rejected — two death years", "rejected — different parents"):
    n = by_tier.get(t, 0)
    print(f"  {t:<20} {n:3d} groups  ({sum(g['n']-1 for g in groups if g['tier']==t)} surplus)")
print()
by_sur = collections.Counter(g["surname"] for g in groups)
for s, n in by_sur.most_common():
    print(f"  {n:3d}  {s}")
print()
for g in groups:
    if g["tier"] != "same day":
        continue
    print(f"  x{g['n']}  {g['date']:<14} {g['place'] or '—':<14} "
          f"{' | '.join(n[:30] for n in g['names'])}")

out = os.path.join(DATA, "duplicates.json")
json.dump({"groups": groups, "extra": extra, "published": len(pub),
           "rejected": len(rejected), "live": len(live)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
