#!/usr/bin/env python3
"""Count the infant deaths the birth register implies but the tree does not record.

Catholic families of this period reused a given name when the child who had
carried it died. So a sibling set containing two Franciscas is, on its own, a
record of a death — even where no death entry has ever been read. This counts
those pairs for one surname and reports them as an *inference*, which is what
they are.
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year

people, families = load()
SURNAME = sys.argv[1] if len(sys.argv) > 1 else "zubrinic"


def fold(sn):
    s = sn.lower().replace("ž","z").replace("ć","c").replace("č","c").replace("š","s")
    s = s.split("(")[0].strip()
    if s.startswith("x"): s = "z" + s[1:]
    if s.endswith("ich"): s = s[:-3] + "ic"
    return s


def first(given):
    """The baptismal first name, ignoring the tree's piled-up variants."""
    g = re.split(r"[\s/]", (given or "").strip())
    return (g[0] if g else "").lower().replace("ž","z").replace("ć","c").replace("č","c")


# Latin/Croatian forms of one name are one name for this purpose.
SAME = {"joannes":"ivan","ivan":"ivan","ivo":"ivan","ive":"ivan","juan":"ivan","john":"ivan",
        "nicolaus":"nikola","nikola":"nikola","miko":"nikola","nicolai":"nikola",
        "mathias":"matija","matthaus":"matija","mate":"matija","mathia":"matija","matija":"matija",
        "georgius":"juraj","juraj":"juraj","jure":"juraj",
        "michael":"mihovil","mihovil":"mihovil","miho":"mihovil","michaël":"mihovil",
        "franciscus":"franjo","franjo":"franjo","francisca":"franciska","franciska":"franciska",
        "maria":"marija","marija":"marija","mary":"marija",
        "catharina":"katarina","kata":"katarina","katarina":"katarina","catarina":"katarina",
        "elias":"ilija","ilija":"ilija","josephus":"josip","josip":"josip","joseph":"josip"}
def key(g): 
    f = first(g)
    return SAME.get(f, f)

# The tree contains alphabetical sorting buckets - parents named "J Zubrinic
# Xubrinich Zubrinic" with a dozen undated children. Those are scaffolding, not
# families, and they must be excluded or they dominate the count.
BUCKET = re.compile(r"^[A-Z]\s|sorting|working|brothers|sisters|unnamed|^nn\b|\[", re.I)


def is_bucket(f):
    for x in (f["husb"], f["wife"]):
        if x in people and BUCKET.search(display(people[x])):
            return True
    return False


reuse, dup, impossible, undated, fams = [], [], [], 0, 0
for fid, f in families.items():
    kids = [c for c in f["chil"] if c in people]
    if not kids or not any(fold(people[c]["surname"]) == SURNAME for c in kids):
        continue
    if is_bucket(f):
        undated += 1
        continue
    fams += 1
    seen = collections.defaultdict(list)
    for c in kids:
        k = key(people[c]["given"])
        if k and not BUCKET.search(display(people[c])):
            seen[k].append(c)
    for k, cs in seen.items():
        if len(cs) < 2:
            continue
        yrs = [year(born(people[c]).get("date", "")) for c in cs]
        if any(y is None for y in yrs):
            continue                      # undated: nothing can be concluded
        cs = [c for _, c in sorted(zip(yrs, cs))]
        yrs = sorted(yrs)
        gap = yrs[-1] - yrs[0]
        rec = [c for c in cs if died(people[c]).get("date")]
        row = (fid, k, cs, yrs, gap, rec)
        if gap > 25:
            impossible.append(row)        # too wide for one mother: a bad attachment
        elif gap == 0:
            dup.append(row)               # same year twice: a duplicated record
        elif gap >= 2 and len(rec) != len(cs):
            reuse.append(row)             # the classic pattern
        else:
            dup.append(row)


def par(fid):
    f = families[fid]
    return " & ".join(display(people[x])[:26] for x in (f["husb"], f["wife"]) if x in people)


print(f"{fams} real families containing a {SURNAME.title()} child "
      f"({undated} sorting buckets excluded)\n")
print(f"--- {len(reuse)} name reused after a gap: an infant death the tree does not record ---")
for fid, k, cs, yrs, gap, rec in sorted(reuse, key=lambda r: r[3][0]):
    print(f'  {par(fid):<54} {k:<10} {yrs[0]} then {yrs[-1]}  (+{gap}y)')
print(f"\n--- {len(dup)} same name, same or adjacent year: probably one child recorded twice ---")
for fid, k, cs, yrs, gap, rec in sorted(dup, key=lambda r: r[3][0]):
    note = "both carry a death date" if len(rec) == len(cs) else ""
    print(f'  {par(fid):<54} {k:<10} {yrs[0]}/{yrs[-1]}  {note}')
print(f"\n--- {len(impossible)} same name more than 25 years apart: not reuse, a bad attachment ---")
for fid, k, cs, yrs, gap, rec in impossible:
    print(f'  {par(fid):<54} {k:<10} {yrs[0]} and {yrs[-1]}  ({gap} years apart)')
print(f"\n{len(reuse)} infant deaths implied by the birth register alone.")
