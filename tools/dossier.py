#!/usr/bin/env python3
"""Dump everything the GEDCOM holds on a set of people: every event with its
date, place, cause, age and note, plus biographies, sources and media counts.

The ancestry sweep answers "who"; this answers "what does the record actually
say". Run it on the direct line before writing a word of narrative.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, ev

people, families = load()

def dump(pid):
    p = people.get(pid)
    if not p:
        print(f"!! {pid} not found"); return
    print("=" * 78)
    print(f'{display(p)}   [{p["id"]} / {p["mh"]}]  {p["sex"]}')
    for e in p["events"]:
        bits = [e.get("date",""), e.get("place","")]
        line = "  ".join(x for x in bits if x)
        print(f'  - {e["kind"]:<14} {line}')
        for k in ("cause","age","detail","note","agency"):
            if e.get(k):
                print(f'      {k}: {e[k]}')
    for n in p["notes"]:
        if n and n.strip():
            print(f'  NOTE: {n.strip()[:1500]}')
    if p["sources"]:
        print(f'  SOURCES ({len(p["sources"])}): ' + " | ".join(s[:110] for s in p["sources"][:6]))

for pid in sys.argv[1:]:
    dump(pid if pid.startswith("@") else f"@{pid}@")
