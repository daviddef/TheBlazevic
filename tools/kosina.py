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

AND SINCE 21 SEPTEMBER 2026, NOT THE SURNAME EITHER. A living person is given
here by GIVEN NAME ALONE, everywhere a name is emitted -- their own row and every
mention of them as somebody's child, parent, sibling or spouse. The reason is
that a surname plus a first name plus a country is an identification, and this
page carries the country. `named-bare` was always meant to mean "enough that the
family recognises them, not enough that a stranger can find them", and a full
name on a public genealogy page is the wrong side of that line. The surname does
not reach the JSON at all, so no template can leak it back.

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



# The Carniolan generations, in descent order, from sources/found.psv. Named
# explicitly rather than pattern-matched: this is a claim about five people and
# it should be legible as one, not inferred from a string that might drift.
CARNIOLAN = [
    ("Matthaeus Kosinar",
     "witness at Franz's marriage in 1800, signing with a cross",
     "Father or brother of Franz — and nothing says which. The oldest of the name reached."),
    ("Franz Kosinar",
     "b. about 1776 · m. 27 October 1800 · Feichting house 10",
     "Martin's grandfather. A Häusler. Named at his daughter's baptism in 1814 "
     "and his son's marriage in 1833."),
    ("Maria \"Mina\" Domshan",
     "b. about 1780 · m. 27 October 1800, aged 20",
     "Martin's grandmother. Written «Dortshen» in 1800, «Do[m]shan» in 1814 and "
     "«Tom[sh]shan» in 1833 — three clerks, and not smoothed into one."),
    ("Johann Kosina",
     "b. about 1802–03 · m. 6 January 1833 · Oberfeichting house 9",
     "Martin's uncle, and the householder of the house Martin was born in."),
    ("Gertraud \"Gertruda\" Kosina",
     "baptised 18 March 1814, Feichting house 10",
     "MARTIN'S MOTHER — the «Gertruda» the tree knows only as a name. "
     "Twenty-seven when she bore him, and unmarried."),
]


def carniolan_above():
    """The five people above Martin, read out of registers and not in the tree."""
    rows = []
    path = os.path.join(ROOT, "sources", "found.psv")
    cites = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 6:
                continue
            f = [x.strip() for x in line.split("|")]
            cites[f[0]] = f[6]
    for name, when, what in CARNIOLAN:
        rows.append({"name": name, "when": when, "what": what,
                     "cite": cites.get(name, "")})
    return rows


def main():
    P, F = gedcom.load()
    living = gedcom.classify_living(P, F)

    def is_living(pid):
        v = living.get(pid)
        return bool(v) if not isinstance(v, dict) else bool(v.get("living"))

    def name_of(pid):
        """Given name only when they may be alive -- see the docstring."""
        full = gedcom.display(P[pid]) or ""
        if not is_living(pid):
            return full
        sur = (P[pid].get("surname") or "").strip()
        if not sur:
            return full
        out = " ".join(w for w in full.split() if w.strip('"\u201c\u201d') != sur)
        return out or full

    def person(pid):
        b, d = gedcom.born(P[pid]), gedcom.died(P[pid])
        alive = is_living(pid)
        return {
            "id": pid,
            "name": name_of(pid),
            # The surname of a living person never enters this file.
            "surname": "" if alive else (P[pid].get("surname") or "").strip(),
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
                    rec["parents"].append({"id": o, "name": name_of(o)})
            for c in (fam.get("chil") or []):
                if c != pid and c in P:
                    rec["siblings"].append({"id": c, "name": name_of(c)})
        for f in (P[pid].get("fams") or []):
            fam = F.get(f) or {}
            o = fam.get("wife") if fam.get("husb") == pid else fam.get("husb")
            if o in P:
                m = fam.get("marr") or {}
                rec["spouses"].append({"id": o, "name": name_of(o),
                                       "married": m.get("date") or "",
                                       "place": m.get("place") or ""})
            for c in (fam.get("chil") or []):
                if c in P:
                    rec["children"].append({"id": c, "name": name_of(c)})

    def year(s):
        import re
        m = re.search(r"(1[6-9]\d\d|20\d\d)", s or "")
        return int(m.group(1)) if m else None

    order = sorted(people.values(), key=lambda r: (year(r["born"]) or 9999, r["name"]))
    dead = [r for r in order if not r["living"]]
    lost = [r for r in dead if year(r["died"]) == 1943]

    # THE GENERATIONS THE TREE DOES NOT HAVE. Everything above Martin was read
    # out of the Carniolan registers on 21-22 September 2026 and is in no tree
    # anywhere, so it lives in sources/found.psv beside the tree rather than in
    # it — this archive does not edit the GEDCOM. But a reader should not have
    # to know which FILE a person is kept in: the descent table showed Martin
    # with «child of Gertruda» and nothing above him while four documented
    # ancestors sat in a second table further down the page. They are emitted
    # here so the one table can show the whole line, each marked for what it is.
    above = carniolan_above()

    doc = {
        "above": above,
        "note": ("The Kosina of Senj, gathered from the GEDCOM by tools/kosina.py. They are "
                 "outside this archive's eight published surnames, so they appear in no "
                 "people.json and on no family page. The living rule is applied here: anyone "
                 "who may be alive is given by GIVEN NAME ALONE and carries no date, and "
                 "neither their surname nor their dates enter this file."),
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
