#!/usr/bin/env python3
"""The FindMyPast target list — everyone this archive stops following.

WHO IS IN IT. Every published person born 1840–1910 with NO DEATH RECORDED: old
enough to have sailed, young enough to be on a post-1906 manifest, and the point
at which this archive loses them. 386 people. It is not a list of emigrants; it
is a list of people the archive stops following, which is the same list until
somebody looks.

WHY IT IS A TOOL NOW. The file said of itself «it is generated from the archive
rather than typed, so it cannot drift from the tree» — and nothing generated it.
It was made once by hand on 16 September 2026 and committed, which is exactly
the drift it claimed to be immune to.

AND WHY IT GREW A COLUMN. On 17 September somebody asked whether the research
searches all the variations of a name. For surnames it did, and the list already
carried a «spellings» column proving it — ZUBRINICH 191, ZUBRINIC 119,
ZUBRINICK 10, one family. For GIVEN names it did not: the list handed the
searcher whatever the tree held, which in these parishes is the LATIN of the
baptismal entry, and ten times the Latin ACCUSATIVE, because the priest wrote
«baptizavi Gregorium». Nobody was ever indexed in the accusative. Tested:

    firstname=josip      returns records
    firstname=joseph     returns records
    firstname=josephus   0
    firstname=giuseppe   0

So the forms column is built from sources/givennames.psv by way of names.json,
and it is ORDERED BY USEFULNESS rather than alphabetically — the vernacular and
the English first, because the index being searched is an American or Australian
one, and the Latin last, because it is what the tree says and the least likely
to be written in any index outside a church.

Writes sources/findmypast/targets.psv
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(ROOT, "sources", "findmypast", "targets.psv")

BORN_FROM, BORN_TO = 1840, 1910

# The surname spellings this archive has actually met, per folded surname. These
# are not guesses: each one has been searched and returned records.
SPELLINGS = {
    "zubrinic": "Zubrinic / Zubrinich / Zubrinick / Zubrinec",
    "blazevic": "Blazevic / Blasevich / Blazevich",
    "papic": "Papic / Papich / Papa",
    "prpic": "Prpic / Prpich / Perpic / Perpich",
    "kalanj": "Kalanj / Kalan / Kalanich",
    "sestan": "Sestan / Shestan",
    "boras": "Boras / Borash",
    "vukelic": "Vukelic / Vukelich",
}

# Which language to offer first. The index on the other end is American or
# Australian, so the name the clerk there wrote comes first and the register's
# Latin comes last.
ORDER = ["croatian", "english", "german", "hungarian", "italian", "venetian", "latin"]


def fold(s):
    s = unicodedata.normalize("NFKD", str(s or "").strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.replace("æ", "ae"))


def year(s):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", str(s or ""))
    return int(m.group(1)) if m else None


def main():
    people = {}
    for f in ("people.json", "ancestors.json"):
        for p in json.load(open(os.path.join(DATA, f), encoding="utf-8")):
            people.setdefault(p["id"], p)
    names = json.load(open(os.path.join(DATA, "names.json"), encoding="utf-8"))

    # form -> the row it belongs to, so a Latin accusative in the tree finds the
    # vernacular the searcher actually needs.
    row_of, forms_of = {}, {}
    for r in names["rows"]:
        bucket = []
        for lang in ORDER:
            for f in r["langs"].get(lang, []):
                # A case ending is grammar, not a name. It is never offered as
                # something to type; it is only ever matched ON.
                if not f["case"]:
                    bucket.append(f["form"])
        seen, ordered = set(), []
        for f in bucket:
            if fold(f) not in seen:
                seen.add(fold(f))
                ordered.append(f)
        forms_of[r["canon"]] = ordered
        for lang in r["langs"]:
            for f in r["langs"][lang]:
                row_of[fold(f["form"])] = r["canon"]
        row_of[fold(r["canon"])] = r["canon"]

    rows, unknown = [], 0
    for p in people.values():
        by = year(p.get("born"))
        if not by or by < BORN_FROM or by > BORN_TO:
            continue
        if (p.get("died") or "").strip():
            continue
        given = (p.get("given") or "").strip() or "—"
        first = re.split(r"[\s(]", given)[0].strip('"')
        canon = row_of.get(fold(first))
        if canon:
            alt = [f for f in forms_of[canon] if fold(f) != fold(first)]
        else:
            alt = []
            unknown += 1
        surname = (p.get("surname") or "").strip() or "—"
        rows.append((surname, given, str(by),
                     (p.get("bornPlace") or "").split(",")[0].strip() or "—",
                     p.get("slug") or "", str(p.get("ahn") or ""),
                     SPELLINGS.get(fold(surname), "—"),
                     ", ".join(alt) if alt else "—"))
    rows.sort(key=lambda r: (fold(r[0]), r[2], fold(r[1])))

    head = f"""# FindMyPast targets — everyone this archive stops following.
#
# GENERATED by tools/fmptargets.py. Do not edit: every column comes from the
# archive's own data, so it cannot drift from the tree. The file it replaces
# claimed exactly this of itself and was made by hand.
#
# WHO IS IN IT. Every published person born {BORN_FROM}-{BORN_TO} with NO DEATH RECORDED
# — the cohort old enough to sail and young enough to be on a post-1906 manifest,
# whose story this archive loses. {len(rows)} people. It is not a list of emigrants; it
# is a list of people the archive stops following, which is the same list until
# somebody looks.
#
# HOW TO WORK IT. Surname first, not person first. One surname search read end
# to end beats forty name searches, and the trial proved why: ZUBRINICH returns
# 191 records and gives AUSTRALIA, ZUBRINIC a DIFFERENT 119 and gives LIKA.
#
# THE TWO SPELLING COLUMNS ARE NOT THE SAME KIND OF THING.
#   surname spellings   forms this archive HAS SEARCHED and got records from.
#   given forms         every form of that given name, vernacular and English
#                       FIRST because the index on the other end is American or
#                       Australian, Latin LAST because it is what the tree says
#                       and the least likely to be in any index outside a church.
#                       Built from sources/givennames.psv. Latin CASE endings are
#                       deliberately never offered: "Gregorium" is grammar, not a
#                       name anyone was called or indexed under.
#
# THE REASON THE SECOND COLUMN EXISTS. Tested on FindMyPast, 17 September 2026:
#   firstname=josip      returns records
#   firstname=joseph     returns records
#   firstname=josephus   0      <- the form the previous list handed the searcher
#   firstname=giuseppe   0
# The site's own "include name variants" box is on by default and still returns
# 0 for Josephus. It does not expand across the languages a parish was written in.
#
# {unknown} of the {len(rows)} rows have no variant group, so their given-forms cell is "—".
# That is a gap in sources/givennames.psv, not a statement that the name has no
# other forms.
#
# TWO THINGS THE TRIAL LEARNED THAT SAVE A DAY.
#   - Only the pre-1925 Ellis manifests (ELLIS2 transcripts) carry a LAST
#     RESIDENCE and the relative left behind. That residence is the whole value:
#     it is what turned the Kalanji from a Klenovica family into Brinje people.
#   - Ids ending ".../2" and ".../3" are RELATIONS NAMED ON a record, not passengers.
#
# AND ONE NEGATIVE, SO IT IS NOT RE-TESTED. FindMyPast holds NO Croatian parish
# registers, and nothing on Hedviga's emigration: no Hedviga Blazevic anywhere,
# no Defranceski in Passenger Lists Leaving UK 1890-1960. They went to South
# Africa and this service has neither end of the voyage.
#
# surname|given|born|birthplace|slug|ahn|surname spellings to try|given forms to try
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(head)
        for r in rows:
            fh.write("|".join(r) + "\n")
    withalt = sum(1 for r in rows if r[7] != "—")
    print(f"targets.psv — {len(rows)} people, {withalt} carry given-name forms to try, "
          f"{unknown} have no variant group")
    return 0


if __name__ == "__main__":
    sys.exit(main())
