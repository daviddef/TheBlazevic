#!/usr/bin/env python3
"""Who is living, who is held out: this archive's use of the estate's one rule.

THE RULE is the kit's, not this archive's: kit/tools/living_rule.py (David's
ruling of 16 October 2026, standard v2). Living is 80 or younger BY YEAR with no
death or burial recorded; a public source means not living; no birth year means
not living; the only people held out are an UNDATED person with a living parent.
This module only gathers what the rule needs from the tree.

WHAT "RECORDED DEAD" MEANS HERE (all of these make a person dead):
  * a death or a burial event in the tree, dated or not;
  * a death read for them in sources/documented.psv;
  * a grave photograph (a media item whose caption is a grave, stone, tomb or
    memorial) tagged with them;
  * a surveyed stone or Find a Grave row with their name, their birth year and a
    death year. The birth year is required because a wrong match here would
    publish a living person as dead, with every date the tree holds.

CITATIONS are every string a source carries for the person (gedcom.load puts them
in person["cites"]). A private tree entry does not count; FamilySearch always does.

No name, id or date of anybody held out is written anywhere by this module.
"""
import glob
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
import gedcom  # noqa: E402
import living_rule as lr  # noqa: E402

GRAVE = re.compile(r"grave|gravestone|gravesite|stone|tomb|memorial|headstone", re.I)
DEATHWORD = re.compile(r"\b(death|died|dead|deceased|buried|burial|grave|gravestone|tomb|memorial)\b", re.I)


def _fold(s):
    s = unicodedata.normalize("NFD", str(s or "").lower().replace("đ", "d"))
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def _year(s):
    m = re.search(r"\b(\d{4})\b", str(s or ""))
    return int(m.group(1)) if m else None


def recorded_in_tree(person):
    """A death or a burial event, dated or not."""
    return any(e["kind"] in ("death", "burial") for e in person["events"])


def documented_dead():
    out = set()
    path = os.path.join(ROOT, "sources", "documented.psv")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or "|" not in line:
                continue
            f = line.rstrip("\n").split("|")
            if len(f) >= 3 and DEATHWORD.search("|".join(f[2:])):
                out.add(f[0].strip())
    return out


def grave_photo_dead(people):
    out = set()
    for name in ("manifest.psv", "local.psv"):
        path = os.path.join(ROOT, "sources", "media", name)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#") or line.count("|") < 6:
                continue
            f = line.split("|")
            if not GRAVE.search(f[2]):
                continue
            for pid in f[5].split(","):
                try:
                    gid = "@I%d@" % (int(pid) - 4000000)
                except ValueError:
                    continue
                if gid in people:
                    out.add(gid)
    return out


def stone_rows():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "sources", "graves", "*.psv"))):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 4:
                continue
            f = [x.strip() for x in line.split("|")]
            rows.append((f[0], f[1], _year(f[2]), _year(f[3])))
    for path in sorted(glob.glob(os.path.join(ROOT, "sources", "findagrave", "*.psv"))):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 3:
                continue
            f = [x.strip() for x in line.split("|")]
            parts = f[0].split()
            if len(parts) >= 2:
                rows.append((parts[-1], " ".join(parts[:-1]), _year(f[1]), _year(f[2])))
    return [r for r in rows if r[2] and r[3]]


def stone_dead(people, ids):
    by = {}
    for sn, gn, b, d in stone_rows():
        by.setdefault((_fold(sn), (_fold(gn).split(" ") or [""])[0], b), d)
    out = set()
    for i in ids:
        p = people[i]
        b = gedcom.year(gedcom.born(p).get("date", ""))
        if not b:
            continue
        gn = (_fold(p["given"]).split(" ") or [""])[0]
        for s in {_fold(x) for x in re.split(r"[/ ]+", p["surname"]) if x}:
            if (s, gn, b) in by:
                out.add(i)
    return out


def extra_dead(people):
    """Dead on a record other than the tree's own death or burial event."""
    doc = documented_dead() & set(people)
    photo = grave_photo_dead(people)
    stone = stone_dead(people, [i for i, p in people.items() if not recorded_in_tree(p)])
    return doc | photo | stone, {"documented": doc, "grave photograph": photo, "stone": stone}


def birth_year(person):
    return gedcom.year(gedcom.born(person).get("date", ""))


def classify(people, families, today_year=None):
    """-> dict. living: set. held: set (undated with a living parent). Everyone
    else is not living and is handled as an ordinary person who has died."""
    ty = today_year or lr.this_year()
    extra, by = extra_dead(people)
    status = {}
    living = set()
    for i, p in people.items():
        dead = recorded_in_tree(p) or i in extra
        if lr.is_living(birth_year(p), dead, p.get("cites", ()), ty):
            living.add(i)
    held = set()
    for i, p in people.items():
        if i in living:
            continue
        dead = recorded_in_tree(p) or i in extra
        parent_living = any(par in living for par in p.get("parents", []))
        if lr.is_held_out(i, birth_year(p), dead, p.get("cites", ()), parent_living, (), ty):
            held.add(i)
    return {"living": living, "held": held, "extra_dead": extra, "extra_by": by, "today_year": ty}


def why_not_living(person, i, extra, ty):
    """For the report: why somebody the old rule called living is not living now."""
    if recorded_in_tree(person) or i in extra:
        return "recorded death or burial"
    if lr.public_source(person.get("cites", ())):
        return "public source"
    b = birth_year(person)
    if b is None:
        return "no birth year"
    if ty - b > lr.LIVING_YEARS:
        return "over 80"
    return "other"
