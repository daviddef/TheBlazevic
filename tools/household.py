#!/usr/bin/env python3
"""Print a person's household: parents, siblings, spouses and children."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, ev

people, families = load()

def line(p):
    b, d = born(p), died(p)
    occ = (ev(p, "occupation") or {})
    o = occ.get("detail") or occ.get("place") or ""
    return (f'{display(p)[:44]:<44} {(b.get("date","") or "?")[-4:]:>4}-{(d.get("date","") or "?")[-4:]:<4} '
            f'{b.get("place","")[:30]:<30} {o[:34]}')

for pid in sys.argv[1:]:
    pid = pid if pid.startswith("@") else f"@{pid}@"
    p = people[pid]
    print("="*120); print("SELF    ", line(p))
    for fid in p["famc"]:
        f = families[fid]
        for r, k in (("FATHER  ","husb"),("MOTHER  ","wife")):
            if f[k]: print(r, line(people[f[k]]))
        for c in f["chil"]:
            if c != pid: print("SIBLING ", line(people[c]))
    for fid in p["fams"]:
        f = families[fid]
        sp = f["wife"] if f["husb"]==pid else f["husb"]
        m = next((e for e in f["events"] if e["kind"]=="marriage"), {})
        if sp: print("SPOUSE  ", line(people[sp]), f'   m.{m.get("date","")} {m.get("place","")}')
        for c in f["chil"]: print("CHILD   ", line(people[c]))
