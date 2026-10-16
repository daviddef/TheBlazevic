#!/usr/bin/env python3
"""Who is living, who is held out: the estate's rule, applied to this tree.

THE RULE (David, 16 October 2026; kit/tools/living_rule.py is the one definition):

  LIVING     born 80 years ago or less, by year, with no death or burial recorded,
             and no public source for them.
  DEAD       anyone else: a recorded death or burial (dated or not), a citation
             from a public record source, or a birth year more than 80 years ago,
             or NO birth year at all (nobody can be shown to be 80 or younger).
  HELD OUT   not published at all: a possible minor, which is somebody not recorded
             dead and with no public source who is under 18 by year, or has no
             birth year and a living parent; and anyone promised privacy by id
             (nobody here is: HELD_IDS is empty).

This module only ADAPTS the tree to that rule. It does not decide anything
itself; every verdict is living_rule.py's. It is used by the generator
(build_site_data.py) and by nothing in the gate, which computes the same verdicts
again on its own (tools/livingcheck.py) so that the two cannot share a mistake.

WHAT COUNTS AS A CITATION FROM A PUBLIC SOURCE. The tree's citations read
"title - page url". The kit's list matches on a case-insensitive substring of
that whole string, and a MyHeritage "research" page url is on it because it is
where MyHeritage's record collections live. But MyHeritage also files other
people's family trees there ("Geni World Family Tree", "WikiTree", a family's
"Web Site", a "Family Tree Index"), and the rule says a private family-tree entry
does not count. So a citation whose TITLE names a family tree, a family's site or
a DNA profile is not offered to the kit at all; FamilySearch (its own title) is,
because FamilySearch always counts. Without this, twenty people the tree can
only show through a Geni tree entry would have been treated as dead and shown with
their dates. The count of people this changes is written to
sources/living-rule.json.

No name, id or date of anybody is written by this module.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
import gedcom  # noqa: E402
import living_rule as lr  # noqa: E402

TODAY_YEAR = lr.this_year()
HELD_IDS = ()     # nobody in this archive was promised privacy by id

# A citation whose title says it is somebody's tree or website, not a record.
TREE_TITLE = re.compile(
    r"geni|wikitree|family tree index|web ?site|family site|23andme|\btree\b", re.I)


def birth_year(p):
    """Birth year, else christening or baptism year (born by then), else None."""
    for kinds in (("birth",), ("christening", "baptism")):
        for e in p["events"]:
            if e["kind"] in kinds:
                y = gedcom.year(e.get("date", ""))
                if y is not None:
                    return y
    return None


def offered(cite):
    """True if the kit may be asked about this citation."""
    title = cite.split(" — ")[0]
    if title.strip().lower().startswith("familysearch"):
        return True
    return not TREE_TITLE.search(title)


def citations(p):
    return [c for c in p.get("cites", []) if offered(c)]


def raw_public(p):
    """What the kit alone would say, for the count of people the adapter changes."""
    return lr.public_source(p.get("cites", []))


def classify(people, families, today_year=TODAY_YEAR):
    """-> dict of sets of ids:
         living   is_living() is true, whether held out or not
         held     not published at all (possible minors and promised ids)
         named    living and not held out: published as a name with town and country
         dead     everyone not living (published or not is decided elsewhere)
         public   not living ONLY because of a public-source citation
         ...and the counts of how each person came to be judged."""
    by = {pid: birth_year(p) for pid, p in people.items()}
    cit = {pid: citations(p) for pid, p in people.items()}
    dead_rec = {pid: bool(p["death_recorded"]) for pid, p in people.items()}
    living = {pid for pid, p in people.items()
              if lr.is_living(by[pid], dead_rec[pid], cit[pid], today_year)}
    held = set()
    for pid, p in people.items():
        pl = any(par in living for par in p.get("parents", []))
        if lr.is_held_out(pid, by[pid], dead_rec[pid], cit[pid], pl, HELD_IDS, today_year):
            held.add(pid)
    # how the people who would otherwise be living came to be dead (counts only)
    aged = recorded = public = nobirth = 0
    changed_by_adapter = 0
    for pid, p in people.items():
        b = by[pid]
        if dead_rec[pid]:
            if b is not None and today_year - b <= lr.LIVING_YEARS:
                recorded += 1
        elif pid not in living:
            if b is None:
                nobirth += 1
            elif today_year - b > lr.LIVING_YEARS:
                aged += 1
            elif lr.public_source(cit[pid]):
                public += 1
        if (b is not None and today_year - b <= lr.LIVING_YEARS and not dead_rec[pid]
                and raw_public(p) and not lr.public_source(cit[pid])):
            changed_by_adapter += 1
    return {
        "year": today_year, "by": by, "living": living, "held": held,
        "named": living - held, "birth_year": by,
        "counts": {"recorded_death_within_80": recorded, "public_source": public,
                   "no_birth_year": nobirth, "over_80": aged,
                   "kept_living_by_tree_titles": changed_by_adapter},
    }
