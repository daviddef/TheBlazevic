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
    ("Matthaeus Kosinar", 1774,
     "b. about 1774 · witness at Franz's marriage in 1800 · d. 16 April 1819, aged 45",
     "FRANZ'S BROTHER, and for a day the archive could not say whether he was that "
     "or Franz's father. His death settles it: aged 45 in 1819 is born about 1774, "
     "and Franz was born 1775–76. He was twenty-six when he stood witness, and he "
     "could not write his own name."),
    ("Franz Kosinar", 1775,
     "b. about 1775–76 · m. 27 October 1800 · d. 22 January 1849, aged 73",
     "Martin's grandfather. A Häusler at Feichting house 10, and an Ausnehmer — "
     "retired — by the end. He died at Oberfeichting 9, in his son's house: "
     "THE HOUSE HIS GRANDSON MARTIN WAS BORN IN eight years earlier."),
    ("Maria \"Mina\" Dortschen", 1780,
     "b. about 1780 · m. 27 October 1800, aged 20 · still bearing children in 1820",
     "Martin's grandmother, and the mother of five children now known by name — "
     "three of whom died before they were a year old. Six "
     "clerks wrote her surname across thirty-three years and FOUR OF THEM WROTE "
     "«Dortschen» — 1800, 1812, 1815, 1820 — against this archive's own bracketed "
     "«Do[m]shan» of 1814 and «Tom[sh]shan» of 1833. The archive now leads with "
     "Dortschen and keeps all six."),
    ("Johann Kosina", 1802,
     "b. about 1802–03 · m. 6 January 1833 · Oberfeichting house 9",
     "Martin's uncle, and the householder of the house Martin was born in."),
    ("Lucia Labornik", 1795,
     "b. about 1795 · m. 6 January 1833, aged 38 · d. 30 November 1850, aged 55",
     "Johann's wife — Martin's aunt by marriage rather than his blood, and the "
     "woman keeping the house he was born in. She died there of the same "
     "pneumonia as her father-in-law, twenty-two months after him, and that is "
     "why Johann is beside a second wife by 1853."),
    ("Gertraud \"Gertruda\" Kosina", 1814,
     "baptised 18 March 1814, Feichting house 10",
     "MARTIN'S MOTHER — the «Gertruda» the tree knows only as a name. "
     "Twenty-seven when she bore him, and unmarried."),
]


# THE HOUSE, as against the LINE. These five are not ancestors of Hedviga and
# never will be: three are children of Franz and Maria who died small, and two
# are Kosinar of Franz's own generation and older whose parents no register
# here names. They were found on 22 September 2026 by reading the whole K
# section of the Kranj-Šmartin death index for 1812-1835 rather than the one
# page that had been asked for, and they are kept separate from CARNIOLAN
# because a descent table that mixes proven descent with probable kinship stops
# being a descent table. Each carries what the register says and no more.
HOUSEHOLD = [
    ("Maria Kosinar the elder", 1738,
     "d. 27 February 1816, aged 78, of Altersschwäche",
     "The oldest of the name the archive has reached — a generation above Franz "
     "and Matthäus. A CANDIDATE for their mother and nothing more: another "
     "village, no husband named, and this book names no parents.",
     "probably kin — not proved"),
    ("Elisabeth Kosinar", 1812,
     "baptised 18 November 1812 · died 11 April 1813, aged five months",
     "Franz and Maria's daughter. Convulsions.",
     "daughter of Franz and Maria"),
    ("Maria Kosinar", 1815,
     "baptised 8 August 1815 · died 31 March 1816, aged three quarters of a year",
     "Franz and Maria's daughter, and THE «Kozina Maria» the death index sends a "
     "reader to page 34 to find. Convulsions.",
     "daughter of Franz and Maria"),
    ("Valentin Kosina", 1820,
     "baptised 15 February 1820 · died 29 February 1820, aged one week",
     "Franz and Maria's son, fourteen days old. HIS BAPTISM IS THE PROOF OF THE "
     "HOUSE: it is the record that puts Franz at Oberfeichting 9 as a Häubler, "
     "twenty-one years before Martin was born there.",
     "son of Franz and Maria"),
    ("Margaretha Kosinar", 1781,
     "d. 14 March 1826, aged 45, a Häubler's daughter, unmarried",
     "She died in Franz's house at forty-five, of his own generation. Most likely "
     "his sister; nothing in the entry proves it.",
     "probably Franz's sister — not proved"),
]


def _found_index():
    """Citation and SLUG for every row of found.psv, keyed by name.

    The slug is read out of site/src/data/found.json rather than recomputed,
    because found.py disambiguates a repeated name with its year and a second
    implementation of that rule would drift. tools/regen.py runs found.py
    before this file; if the JSON is not there yet the name simply renders
    without a link, which is what it did before 22 September 2026.
    """
    cites, slugs = {}, {}
    path = os.path.join(ROOT, "sources", "found.psv")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 6:
                continue
            f = [x.strip() for x in line.split("|")]
            cites[f[0]] = f[6]
    jp = os.path.join(DATA, "found.json")
    if os.path.exists(jp):
        try:
            for r in json.load(open(jp, encoding="utf-8")).get("rows", []):
                if r.get("slug"):
                    slugs[r["name"]] = r["slug"]
        except Exception:
            pass
    return cites, slugs


def carniolan_above():
    """The six people above Martin, read out of registers and not in the tree."""
    rows = []
    cites, slugs = _found_index()
    for name, born, when, what in CARNIOLAN:
        rows.append({"name": name, "born": born, "when": when, "what": what,
                     "cite": cites.get(name, ""), "slug": slugs.get(name, "")})
    return rows


def carniolan_household():
    """The house around the line — kin who are not ancestors. See HOUSEHOLD."""
    rows = []
    cites, slugs = _found_index()
    for name, born, when, what, how in HOUSEHOLD:
        rows.append({"name": name, "born": born, "when": when, "what": what,
                     "how": how, "cite": cites.get(name, ""),
                     "slug": slugs.get(name, "")})
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
    house = carniolan_household()

    # THE HEADLINE NUMBERS MUST COUNT THE PEOPLE THE PAGE SHOWS. They did not,
    # for a day: the page said «Ten people, four generations» and «1841 earliest
    # birth» while six documented ancestors sat in its own first table, one of
    # them born in 1775. A generated statistic that quietly excludes half the
    # evidence is worse than no statistic, because a reader trusts a number.
    above_years = [r["born"] for r in above if r["born"]]
    house_years = [r["born"] for r in house if r["born"]]
    doc = {
        "above": above,
        "household": house,
        "note": ("The Kosina of Senj, gathered from the GEDCOM by tools/kosina.py. They are "
                 "outside this archive's eight published surnames, so they appear in no "
                 "people.json and on no family page. The living rule is applied here: anyone "
                 "who may be alive is given by GIVEN NAME ALONE and carries no date, and "
                 "neither their surname nor their dates enter this file."),
        "counts": {
            # `people` and `earliest` COUNT THE CARNIOLAN GENERATIONS TOO, because
            # the page shows them and a reader counts what they can see.
            "people": len(order) + len(above) + len(house),
            "inTree": len(order),
            "above": len(above),
            "household": len(house),
            "living": sum(1 for r in order if r["living"]),
            "lostIn1943": len(lost),
            # EARLIEST COUNTS THE HOUSE TOO. A page that shows a woman who died
            # in 1816 aged 78 and then prints «earliest birth 1774» is lying to
            # the reader about the page they are looking at.
            "earliest": min([y for y in (year(r["born"]) for r in dead) if y]
                            + above_years + house_years or [None]),
            "generations": 6,
        },
        "lostIn1943": [r["id"] for r in lost],
        "people": order,
    }
    with open(os.path.join(DATA, "kosina.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    c = doc["counts"]
    print(f"kosina.json — {c['people']} people ({c['inTree']} in the tree, {c['above']} read "
          f"from the registers, {c['household']} in the house), earliest birth {c['earliest']}, {c['living']} presumed living "
          f"and dateless, {c['lostIn1943']} dead in 1943")
    return 0


if __name__ == "__main__":
    sys.exit(main())
