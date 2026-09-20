#!/usr/bin/env python3
"""Does every date this archive says it READ agree with the date it PUBLISHES?

WHY. sources/readings.psv is the archive's record of what has been read off a
page, and each row carries the citation in the register's own words — often with
the date in it. site/src/data/*.json carries what the tree says. Nothing ever
held the two against each other.

On 20 September 2026 an audit did, by hand, to test an unrelated theory about
Roman numerals. Seventeen dates agreed exactly and one did not:

    ivan-blazevic   tree 25 JULY 1882    citation «bapt. 26 Aug 1882»

The tree was right. notes/reading-2026-09-09.md records the entry as
«1882, 25 / 26 SRPNJA» — and **srpanj is July**. Whoever wrote the readings.psv
row rendered the Croatian month as August. A citation is what a later reader
trusts instead of re-opening the film, so a wrong month in one is worse than a
wrong month in the tree: the tree can be checked against the citation, and the
citation is what you check against.

WHAT IT WILL NOT DO. It refuses to guess. A comparison is only made when

  * the row is a baptism or a death — the two kinds whose date is the person's
    own. A «baptism-of-child» row carries the CHILD's date, not this person's,
    and comparing them is how the by-hand audit produced three false alarms;
  * the citation yields a full day, month and year;
  * that year equals the row's own year column AND the tree's year, so a
    citation that happens to mention some other date in passing is skipped;
  * the row is not marked INDEX ONLY. Those are transcriptions this archive has
    deliberately recorded WITHOUT opening the page, and a disagreement is the
    point of them rather than a fault.

Croatian and Latin month names are understood, because that is what the
registers are written in and that is where the one error came from.

Run: python3 tools/datecheck.py [--quiet]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

EN = {m: i + 1 for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split())}

# The registers are kept in Latin, then Croatian. Both are here because the one
# error this check exists for was a Croatian month read as an English one.
OTHER = {
    "januar": 1, "ianuar": 1, "siječ": 1, "sijec": 1, "prosin": 12,
    "februar": 2, "veljač": 2, "veljac": 2,
    "martii": 3, "marti": 3, "ožuj": 3, "ozuj": 3,
    "aprilis": 4, "travn": 4,
    "maji": 5, "maij": 5, "svibn": 5,
    "junii": 6, "junij": 6, "lipnj": 6,
    "julii": 7, "julij": 7, "srpnj": 7, "srpanj": 7,
    "augusti": 8, "kolovoz": 8, "kolovoza": 8,
    "septembris": 9, "rujn": 9,
    "octobris": 10, "listopad": 10,
    "novembris": 11, "studen": 11,
    "decembris": 12,
}

DAY_RE = re.compile(
    r"\b(\d{1,2})\s*\.?\s*([A-Za-zŠšČčĆćŽžĐđ]{3,12})\.?\s*,?\s*(1[5-9]\d\d|20\d\d)\b")
TREE_RE = re.compile(r"^(?:ABT\s+|CAL\s+|EST\s+)?(\d{1,2})\s+([A-Z]{3})\s+(\d{4})$")


def month(word):
    w = word.lower()
    if w[:3] in EN:
        return EN[w[:3]]
    for k, v in OTHER.items():
        if w.startswith(k[:5]):
            return v
    return None


def cite_date(text):
    """Every full day-month-year in a citation, as (d, m, y)."""
    out = []
    for d, w, y in DAY_RE.findall(text):
        m = month(w)
        if m:
            out.append((int(d), m, int(y)))
    return out


def tree_date(value):
    m = TREE_RE.match(str(value or "").strip().upper())
    if not m:
        return None
    mo = EN.get(m.group(2).lower())
    return (int(m.group(1)), mo, int(m.group(3))) if mo else None


def main():
    quiet = "--quiet" in sys.argv
    people = {}
    for f in ("people.json", "ancestors.json"):
        for p in json.load(open(os.path.join(DATA, f), encoding="utf-8")):
            people.setdefault(p["slug"], p)

    path = os.path.join(ROOT, "sources", "readings.psv")
    compared, bad = 0, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#") or line.count("|") < 4:
            continue
        slug, kind, year, _where, cite = [x.strip() for x in line.split("|")[:5]]
        if kind not in ("baptism", "death"):
            continue
        if "INDEX ONLY" in cite:
            continue
        p = people.get(slug)
        if not p:
            continue
        td = tree_date(p.get("born") if kind == "baptism" else p.get("died"))
        if not td:
            continue
        try:
            rowyear = int(year)
        except ValueError:
            continue
        # Only a date that is about THIS row: same year on the row, the tree and
        # the citation. Anything else is some other date mentioned in passing.
        cands = [c for c in cite_date(cite) if c[2] == rowyear == td[2]]
        if not cands:
            continue
        compared += 1
        if not any(c == td for c in cands):
            bad.append((slug, kind, td, cands))

    if not quiet:
        print(f"datecheck — {compared} readings carry a full date that can be held "
              f"against the tree")
    if bad:
        print(f"\nFAIL  {len(bad)} citation(s) disagree with the published date:")
        for slug, kind, td, cands in bad:
            got = " / ".join(f"{d}.{m}.{y}" for d, m, y in cands)
            print(f"      {slug}  ({kind})")
            print(f"        the tree says   {td[0]}.{td[1]}.{td[2]}")
            print(f"        the citation says  {got}")
        print("\n      One of the two is wrong. Check the citation against the note it "
              "cites\n      before changing either — the one error this check was written "
              "for was\n      a Croatian month, «srpnja», written into the citation as August.")
        return 1
    if not quiet:
        print("ok    every dated reading agrees with the date this archive publishes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
