#!/usr/bin/env python3
"""The Kosina family, gathered out of the GEDCOM for a page of their own.

WHY THEY HAVE NO PAGE. This archive publishes eight surnames and Kosina is not
one of them, so all ten of them are invisible: `people.json` holds none, the
family pages are generated from the surname scope, and everything known about
them is scattered across /senj-1943/, the Boras pages and a gravestone reading.

WHY THEY DESERVE ONE. They reach this family twice over. Pavao Kosina married
ANKA BLAŽEVIĆ, daughter of ahnentafel 4 and 5 -- Hedviga's own aunt, her
father's sister. And Pavao's mother was ANGELIKA BORAS, through whom the Boras
reach this archive at all. Two of the eight surnames meet in this household.

And then the town was bombed. On 7-8 October 1943 German aircraft destroyed
about half of Senj. PAVAO KOSINA WAS KILLED ON THE SECOND DAY, and his stone
says so in the word used for a violent death: *pog.*, poginuo. Of a household of
seven, three were dead within thirteen months.

THE LIVING RULE IS APPLIED HERE AND NOT BY HAND. Two of the ten have no death
and may be alive. Under this estate's `named-bare` policy a living person may be
NAMED and no date of theirs may be published, so this tool runs the same
classifier the build checks against and strips the dates itself. A page written
by hand would have published a birth year for a woman born in 1964.

Reads  the GEDCOM, via tools/gedcom.py
Writes site/src/data/kosina.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom  # noqa: E402

SURNAME = "kosina"


def main():
    P, F = gedcom.load()
    living = gedcom.classify_living(P, F)

    def is_living(pid):
        v = living.get(pid)
        return bool(v) if not isinstance(v, dict) else bool(v.get("living"))

    def person(pid):
        b, d = gedcom.born(P[pid]), gedcom.died(P[pid])
        alive = is_living(pid)
        return {
            "id": pid,
            "name": gedcom.display(P[pid]) or "",
            "surname": (P[pid].get("surname") or "").strip(),
            # NAMED AND NOTHING MORE when they may be alive. The dates are not
            # merely hidden from the page; they never enter the data file.
            "born": "" if alive else (b.get("date") or ""),
            "bornPlace": "" if alive else (b.get("place") or ""),
            "died": "" if alive else (d.get("date") or ""),
            "diedPlace": "" if alive else (d.get("place") or ""),
            "living": alive,
        }

    kos = [pid for pid in P if (P[pid].get("surname") or "").lower().find(SURNAME) >= 0]
    people = {pid: person(pid) for pid in kos}

    # The households, so the page can draw descent rather than list names.
    for pid in kos:
        rec = people[pid]
        rec["parents"], rec["spouses"], rec["children"], rec["siblings"] = [], [], [], []
        for f in (P[pid].get("famc") or []):
            fam = F.get(f) or {}
            for role in ("husb", "wife"):
                o = fam.get(role)
                if o in P:
                    rec["parents"].append({"id": o, "name": gedcom.display(P[o]) or ""})
            for c in (fam.get("chil") or []):
                if c != pid and c in P:
                    rec["siblings"].append({"id": c, "name": gedcom.display(P[c]) or ""})
        for f in (P[pid].get("fams") or []):
            fam = F.get(f) or {}
            o = fam.get("wife") if fam.get("husb") == pid else fam.get("husb")
            if o in P:
                m = fam.get("marr") or {}
                rec["spouses"].append({"id": o, "name": gedcom.display(P[o]) or "",
                                       "married": m.get("date") or "",
                                       "place": m.get("place") or ""})
            for c in (fam.get("chil") or []):
                if c in P:
                    rec["children"].append({"id": c, "name": gedcom.display(P[c]) or ""})

    def year(s):
        import re
        m = re.search(r"(1[6-9]\d\d|20\d\d)", s or "")
        return int(m.group(1)) if m else None

    order = sorted(people.values(), key=lambda r: (year(r["born"]) or 9999, r["name"]))
    dead = [r for r in order if not r["living"]]
    lost = [r for r in dead if year(r["died"]) == 1943]

    doc = {
        "note": ("The Kosina of Senj, gathered from the GEDCOM by tools/kosina.py. They are "
                 "outside this archive's eight published surnames, so they appear in no "
                 "people.json and on no family page. The living rule is applied here: anyone "
                 "who may be alive is named and carries no date."),
        "counts": {
            "people": len(order),
            "living": sum(1 for r in order if r["living"]),
            "lostIn1943": len(lost),
            "earliest": min([y for y in (year(r["born"]) for r in dead) if y] or [None]),
        },
        "lostIn1943": [r["id"] for r in lost],
        "people": order,
    }
    with open(os.path.join(DATA, "kosina.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    c = doc["counts"]
    print(f"kosina.json — {c['people']} people, {c['living']} presumed living and dateless, "
          f"{c['lostIn1943']} dead in 1943")
    return 0


if __name__ == "__main__":
    sys.exit(main())
