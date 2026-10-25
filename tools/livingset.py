#!/usr/bin/env python3
"""Who is living, who is held out: this archive's use of the estate's one rule.

THE RULE is the kit's, not this archive's: kit/tools/living_rule.py (David's
ruling of 16 October 2026, standard v2, tightened 25 October 2026 and carried by
kit 341af33). Living is 80 or younger BY YEAR with no death RECORD; no birth year
means not living; the only people held out are an UNDATED person with a living
parent. This module gathers what the rule needs from the tree and passes it on:

  * A DEATH RECORD (`recorded_dead`) is a dated death or burial, a death with a
    place, a cause or a note, or a death read elsewhere in the archive (below).
    A BARE FLAG (a DEAT event that is only `Y`: no date, no place, no burial) is
    `undated_dead`: for somebody born inside the window it is the tree's belief,
    not evidence, and they stay LIVING; for somebody with no birth year it means
    dead. (Kit 341af33. Before it this module treated every death event as a
    record and kept a list of holds; the list remains for the one person a death
    with a place and no date left in doubt.)
  * A PUBLIC-SOURCE CITATION NEVER RELEASES A DATED PERSON: the kit now does it
    (it did not until 25 October 2026, when the same hole put a living man's year
    on the Mazza archive). `cites_for_living` below passes none for somebody with
    a birth year as it did before; it is redundant with the kit and is kept
    working beside it, to be deleted once the kit gate has run clean for a release.
  * `data/living-hold.tsv` still names somebody the tree records dead with a place
    and no date, and nothing else, whom David has not confirmed. They are treated
    as living (masked) until he does. The gate refuses a hold on anybody with a
    dated death.

THE CUTOFF. `cutoff_year()` is the one place the window's edge is computed:
this year minus the kit's LIVING_YEARS. The generators and every gate import it.

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


def death_evidence(person):
    """'record', 'flag' or None, from the person's own death and burial events, through the kit's `death_kind`
    (the classifier both of the kit's languages answer to). A burial, a date, a place, a cause or a note on a
    death is a record; a death that is only `Y` is a flag."""
    kinds = []
    for e in person["events"]:
        if e["kind"] == "burial":
            kinds.append("record")
        elif e["kind"] == "death":
            extra = any(e.get(k) for k in ("cause", "note", "agency", "type"))
            kinds.append(lr.death_kind(died=e.get("date", ""), death_place=e.get("place", ""),
                                       dead_flag=True,
                                       death_recorded=extra))
    if "record" in kinds:
        return "record"
    return "flag" if "flag" in kinds else None


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


def cutoff_year(today_year=None):
    """THE cutoff, derived and never written down as a number: a birth year at or
    after this is within the window, so the person is living unless a death is
    recorded. 2026 - 80 = 1946. Used by the generators and by every gate."""
    return lr.cutoff_year(today_year)


def cites_for_living(person):
    """The citations the LIVING test may see for a person: none for somebody with
    a birth year (see the module docstring); all of them for somebody without."""
    return [] if birth_year(person) is not None else person.get("cites", ())


HOLD = os.path.join(ROOT, "data", "living-hold.tsv")


def hold_ids():
    """{id: reason} from data/living-hold.tsv: people the tree flags dead with no
    date and nothing else, held as living until David confirms the death."""
    out = {}
    if os.path.exists(HOLD):
        for line in open(HOLD, encoding="utf-8"):
            if line.startswith("#") or "|" not in line:
                continue
            f = [x.strip() for x in line.rstrip("\n").split("|")]
            if re.fullmatch(r"@I\d+@", f[0]):
                out[f[0]] = f[1] if len(f) > 1 else ""
    return out


def dated_death(person):
    """A death or burial event that carries a date (a year is enough)."""
    return any(e["kind"] in ("death", "burial") and gedcom.year(e.get("date", ""))
               for e in person["events"])


def classify(people, families, today_year=None):
    """-> dict. living: set. held: set (undated with a living parent). Everyone
    else is not living and is handled as an ordinary person who has died."""
    ty = today_year or lr.this_year()
    extra, by = extra_dead(people)
    status = {}
    holds = {i: why for i, why in hold_ids().items() if i in people}
    for i in holds:
        if dated_death(people[i]) or i in extra:
            raise SystemExit(f"data/living-hold.tsv holds {i}, who has a dated death or other evidence of one: "
                             "take the row out (a hold is only for an undated flag)")
        b = birth_year(people[i])
        if b is None or b < lr.cutoff_year(ty):
            raise SystemExit(f"data/living-hold.tsv holds {i}, who is not within the window: take the row out")
    living = set()
    flag_only = set()
    for i, p in people.items():
        kind = death_evidence(p)
        record = (kind == "record" and i not in holds) or i in extra
        flag = kind == "flag" and not record and i not in holds
        if flag:
            flag_only.add(i)
        if lr.is_living(birth_year(p), record, cites_for_living(p), ty, undated_dead=flag):
            living.add(i)
    held = set()
    for i, p in people.items():
        if i in living:
            continue
        kind = death_evidence(p)
        record = kind == "record" or i in extra
        flag = kind == "flag" and not record
        parent_living = any(par in living for par in p.get("parents", []))
        if lr.is_held_out(i, birth_year(p), record, p.get("cites", ()), parent_living, (), ty, undated_dead=flag):
            held.add(i)
    return {"living": living, "held": held, "flag_only": flag_only, "extra_dead": extra, "extra_by": by, "today_year": ty,
            "holds": holds}


def why_not_living(person, i, extra, ty):
    """For the report: why somebody the old rule called living is not living now."""
    if death_evidence(person) == "record" or i in extra:
        return "recorded death or burial"
    b = birth_year(person)
    if lr.public_source(cites_for_living(person)):
        return "public source (undated person)"
    if b is None:
        return "no birth year"
    if b < lr.cutoff_year(ty):
        return "over 80"
    return "other"
