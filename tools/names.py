#!/usr/bin/env python3
"""Every form of every given name, by language — and which ones are real.

WHY. On 17 September 2026 somebody asked whether this archive searches all the
variations of a name. For surnames it does, and the trial proved it matters:
ZUBRINICH returns 191 records, ZUBRINIC a different 119, ZUBRINICK ten more, all
one family. For GIVEN names it did not. The FindMyPast target list handed the
searcher whatever form the tree held — which in these parishes is usually the
LATIN of the baptismal entry, and ten times the Latin ACCUSATIVE, because the
priest wrote «baptizavi Gregorium». Tested against the index that day:

    firstname=josip      returns records
    firstname=joseph     returns records
    firstname=josephus   0
    firstname=giuseppe   0

And the site's own «include name variants» box is on by default and still
returns nothing for Josephus, so whatever it expands, it does not expand across
the languages a Croatian parish was written in.

The grouping existed the whole time — tools/given_names.py has folded 197 forms
into 29 groups since the first week. What was missing was the LANGUAGE, because
the question a searcher actually asks is not «what else was he called» but «what
would the clerk in THIS index have written».

THE ONE RULE THIS TOOL ENFORCES. A form is ATTESTED if it appears in a record
gathered here, and that is never a judgement — it is read out of
givennames.json, which given_names.py builds from the records themselves.
Everything else is a LOOKUP AID: the right thing to type into a Hungarian index
tomorrow, and not something this archive has seen written down. The build
refuses if the two drift apart. The sibling archive's name page claimed for
months that every form on it came «from the forms that actually appear in these
registers» when thirty-one per cent of them did not, and that is the failure
this gate exists to prevent.

Reads  sources/languages.psv        key → label, note: the archive's own languages
       site/src/data/given-names.json  the Record Atlas's given-name catalogue (a committed snapshot of
                                    https://recordatlas.org/given-names.json, fetched with the Archive
                                    Kit's tools/atlas_given_names.py). THE FORMS LIVE ONLY THERE: this
                                    archive keeps no table of its own (it was sources/givennames.psv
                                    until 4 November 2026). To add a form, add it to the Atlas with its
                                    evidence (given_name_variants.py add, then publish), then refetch.
       site/src/data/givennames.json  the fold, and what the records contain
       site/src/data/latincases.json  which people are recorded in an oblique case
Writes site/src/data/names.json
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
SNAP = os.path.join(DATA, "given-names.json")

LANGS_PSV = os.path.join(ROOT, "sources", "languages.psv")


def languages():
    """The archive's own languages, in its own order, out of its own file.

    THIS WAS A TABLE IN THIS FILE until 20 September 2026, and its blurbs named
    Senj, Zengg and the Velebit coast. Six archives are about to copy this data
    shape and not one of them is Croatian, so every one would have had to edit
    this source to say what languages its registers are in. A shared tool that
    has to be edited per archive is not shared. The order is the file's.
    """
    out = []
    for n, line in enumerate(open(LANGS_PSV, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = [x.strip() for x in line.split("|")]
        if len(f) != 3 or not f[0] or not f[1]:
            raise SystemExit(f"{LANGS_PSV}: line {n}: expected key|label|note")
        out.append({"key": f[0], "label": f[1], "note": f[2]})
    return out


LANGS = languages()
LANGNAME = {l["key"]: l["label"] for l in LANGS}

# WHY THIS FIELD IS NOT CALLED `case`. It was, and «abbreviated» is not a
# grammatical case, so the name lied about its values — the same fault as a field
# called `people` holding occurrence counts, which this file also had. What the
# column answers is WHY THIS FORM IS NOT THE NOMINATIVE.
#
# The vocabulary stays closed, but it is the Atlas's now: the catalogue spells a case on
# its own (dative, ablative, vocative) or as a pair («dative/ablative», «dative, ablative»,
# «dative or ablative»), where this archive once held only «dative or ablative» because in a
# Latin register the two are formally identical and a clerk writing «Josepho» has not told
# you which he meant. The page only prints the label, so nothing here depends on the split.
# A value is accepted when every part of it is a real case name or «abbreviated»; anything
# else still stops the build and prints this list.
NOT_NOMINATIVE = {"accusative", "genitive", "dative", "ablative", "vocative", "nominative", "abbreviated"}


def case_ok(v):
    parts = [p.strip() for p in re.split(r"\s*(?:,|/|\bor\b)\s*", v) if p.strip()]
    return bool(parts) and all(p in NOT_NOMINATIVE for p in parts)


CASES = NOT_NOMINATIVE  # the old name, until the shared component stops reading it


def fold(s):
    """The comparison key: no diacritics, no case. A Hungarian aid is written
    «Mihály» because that is what a searcher must type, and matched as mihaly."""
    s = unicodedata.normalize("NFKD", str(s or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def main():
    given = json.load(open(os.path.join(DATA, "givennames.json"), encoding="utf-8"))
    latin = json.load(open(os.path.join(DATA, "latincases.json"), encoding="utf-8"))
    people = []
    for f in ("people.json", "ancestors.json"):
        people += json.load(open(os.path.join(DATA, f), encoding="utf-8"))

    # WHO ACTUALLY BORE THE NAME, counted, rather than a sex asserted in a table.
    # given_names.py declares «matija» male. Four of the people written «Matia»
    # in this archive are women — one of them ahnentafel 13, Matia Pilipić, whose
    # marriage is work list row 4 — because Matija is unisex in Croatian and the
    # table has one column for it. A page that printed «a man's name» over her
    # would be asserting something the records deny.
    bysex = {}
    for p in people:
        first = re.split(r"[\s(]", (p.get("given") or "").strip())[0].strip('"')
        if first:
            bysex.setdefault(fold(first), {"m": 0, "f": 0})
            k = (p.get("sex") or "").lower()[:1]
            if k in ("m", "f"):
                bysex[fold(first)][k] += 1

    # What the RECORDS hold: form -> how many times, per canonical name.
    attested = {}
    for canon, counts in given["observed"].items():
        for form, n in counts.items():
            attested.setdefault(canon, {})
            # A reading the clerk's hand left doubtful, «Ivan?», is a reading of the
            # base form: the Atlas catalogues the form, not our doubt about the ink.
            k = fold(form).rstrip("? ")
            attested[canon][k] = attested[canon].get(k, 0) + n

    # THE FORMS COME FROM THE ATLAS. One Atlas row is one name across languages; our
    # own canons (given_names.py's groups, which the records are filed under) are mapped
    # onto the Atlas row that lists them. Where the Atlas has put two of our canons in one
    # row (Ivan and Joan are Giovanni there) they become one row here, as the Atlas says.
    atlas = json.load(open(SNAP, encoding="utf-8"))
    arows = atlas["rows"]
    where = {}                                    # folded form -> Atlas row indexes
    for i, ar in enumerate(arows):
        for lang, fl in ar["langs"].items():
            for f in fl:
                where.setdefault(fold(f["form"]), set()).add(i)
    # The archive's own languages (sources/languages.psv) come first, in its order and its
    # words. A language only the Atlas catalogues (Slovene, Portuguese, ... it seeds forms in
    # fifty) is named by the Atlas's own list in the snapshot and follows them; one the Atlas
    # lists in neither place is still a failure below.
    for l in atlas.get("languages", []):
        if l["key"] not in LANGNAME:
            LANGS.append({"key": l["key"], "label": l["label"], "note": l.get("note", "")})
            LANGNAME[l["key"]] = l["label"]
    fails = []
    for i, ar in enumerate(arows):
        for lang in ar["langs"]:
            if lang not in LANGNAME:
                fails.append(f"{SNAP}: «{ar['canon']}» has a form filed under «{lang}», "
                             f"which neither sources/languages.psv nor the snapshot's language list names")

    # THE GATE THAT MATTERS, and it runs in the direction that can hurt. A form this
    # archive HAS met and the Atlas does not list is a form the page will not offer.
    # The fix is never a local table: add the form to the Atlas with its evidence
    # (given_name_variants.py add ..., then publish, then refetch the snapshot).
    # A reading marked doubtful with a trailing «?» is the base form, not a new one.
    for canon, forms in attested.items():
        for f in forms:
            if f.rstrip("? ") not in where:
                fails.append(f"records contain «{f}» for {canon} and the Atlas catalogue "
                             f"does not list it — the page would not offer it")
    if fails:
        print(f"FAIL  {len(fails)} problem(s) between the records and the Atlas given-name catalogue:")
        for f in sorted(set(fails))[:24]:
            print("        " + f)
        return 1

    known = set(given["groups"]) | set(given["observed"])
    canons_of = {}                                # Atlas row index -> our canons that map to it
    for c in sorted(known):
        for i in where.get(fold(c), ()):
            canons_of.setdefault(i, []).append(c)
    # WHERE AN OBSERVED FORM IS COUNTED. The Atlas files Helena, Luca and Martha as names
    # of their own, where this archive's grouping (given_names.py) had put them under
    # Elizabeta, Lucija and Margarita. A form goes to the Atlas row reachable from the
    # canon the records filed it under; if no such row lists it, to the row(s) that do,
    # and that row then appears on the page under the Atlas's own id.
    ours_of, extra = {}, set()
    for c, forms in attested.items():
        for f, n in forms.items():
            cand = where.get(f, set())
            prim = [i for i in cand if c in canons_of.get(i, [])]
            for i in (prim or sorted(cand)):
                ours_of.setdefault(i, {})
                ours_of[i][f] = ours_of[i].get(f, 0) + n
                if i not in canons_of:
                    extra.add(i)
    for i in extra:
        canons_of[i] = [arows[i]["id"]]
    # a name's first-listed canon is the one the records use most
    rows = []
    for i, cs in canons_of.items():
        ar = arows[i]
        cs.sort(key=lambda c: (-sum(attested.get(c, {}).values()), c))
        for lang, fl in ar["langs"].items():
            for f in fl:
                rows.append({"canon": cs[0], "canons": cs, "ai": i, "form": f["form"], "lang": lang,
                             "note": f.get("note", ""), "case": f.get("notNominative", "") or f.get("case", ""),
                             "status": f.get("status", ""), "seenAll": f.get("seenAll", f.get("seen", 0))})
    for r in rows:
        if r["case"] and not case_ok(r["case"]):
            fails.append(f"{SNAP}: «{r['form']}» declares an unknown notNominative value "
                         f"«{r['case']}» — the vocabulary is {' · '.join(sorted(NOT_NOMINATIVE))}, alone or paired")
    if fails:
        print(f"FAIL  {len(fails)} problem(s) in the Atlas given-name snapshot:")
        for f in sorted(set(fails))[:24]:
            print("        " + f)
        return 1

    # Which people are recorded in an oblique case, so the page can name them
    # rather than merely asserting that Latin declines.
    oblique = {}
    for l in latin:
        oblique.setdefault(fold(l["nominative"]), []).append(
            {"name": l["name"], "slug": l.get("slug"), "recorded": l["recorded"],
             "case": l["case"], "ahn": l.get("ahn")})

    out, n_att, n_aid = [], 0, 0
    for ai in sorted(canons_of, key=lambda i: canons_of[i][0]):
        canon = canons_of[ai][0]
        cs = canons_of[ai]
        mine = [r for r in rows if r["ai"] == ai]
        ours = ours_of.get(ai, {})                 # what THESE records hold of THIS row's forms
        by_lang = {}
        for r in mine:
            hit = ours.get(fold(r["form"]), 0)
            n_att, n_aid = (n_att + 1, n_aid) if hit else (n_att, n_aid + 1)
            by_lang.setdefault(r["lang"], []).append({
                "form": r["form"], "note": r["note"], "seen": hit,
                # BOTH KEYS, for as long as the rename is in flight. The shared
                # component is being changed to read notNominative and fall back
                # to case; emitting one of them would break whichever side
                # deployed first. `case` comes out when the component has landed
                # in the pinned kit — and this comment is how anybody knows that.
                "notNominative": r["case"],
                "case": r["case"],
                # the catalogue's own claim for the form, and the count of every
                # archive; `seen` above stays THIS archive's, so the page says only
                # what these records hold
                "status": r["status"], "seenAll": r["seenAll"],
            })
        for v in by_lang.values():
            v.sort(key=lambda x: (not x["seen"], bool(x["case"]), fold(x["form"])))
        top = sorted(ours.items(), key=lambda kv: -kv[1])
        # ONE PERSON, ONCE. Summing over the rows counts a bearer again for
        # every language the form is filed under, and eighteen forms are filed
        # under two or three: «Maria» is Latin, Italian and Hungarian, so the
        # one person written Maria and recorded M was three men here, and the
        # page said so out loud. Fold first, then count.
        # A form the Atlas marks case-by-case (Joan, Luca, Luce: the same letters are
        # sometimes this name and sometimes another's) says nothing about who bore THIS
        # name, so it is left out of the tally; it stays listed, with its status.
        forms = {fold(r["form"]) for r in mine if r["status"] != "case-by-case"}
        men = sum(bysex.get(f, {}).get("m", 0) for f in forms)
        women = sum(bysex.get(f, {}).get("f", 0) for f in forms)
        asserted = next((given.get("sex", {}).get(c) for c in cs if given.get("sex", {}).get(c)), "")
        out.append({
            "canon": canon,
            # The matching key is lower case; a name is a name and gets its
            # capital back before anybody reads it. The shared component asks
            # for `label` and every archive was writing the same adapter.
            "label": canon[:1].upper() + canon[1:],
            "sex": asserted,
            # THE ASSERTED SEX AND THE COUNTED BEARERS DISAGREE NINE TIMES HERE.
            # given_names.py declares «matija» male and four of the people
            # written Matia are women, because Matija is unisex and the table
            # has one column for it. The disagreement is data, so it is carried
            # rather than resolved.
            "sexDisputed": bool((asserted == "m" and women) or (asserted == "f" and men)),
            "men": men,
            "women": women,
            "forms": len(mine),
            "attested": sum(1 for r in mine if ours.get(fold(r["form"]), 0)),
            # PEOPLE MEANS PEOPLE. It used to be the sum of the occurrence
            # counts, which disagreed with men+women in 21 of 39 rows, and the
            # shared component renders it as a count of bearers. `tokens` is the
            # occurrences, which is a different and also useful number.
            "people": men + women,
            "tokens": sum(ours.values()),
            "commonest": top[0][0] if top else "",
            "langs": by_lang,
            "slips": arows[ai].get("slips", []),
            "notSame": arows[ai].get("notSame", []),
            "oblique": [p for f, ps in oblique.items()
                        if any(fold(r["form"]) == f for r in mine) for p in ps],
        })

    doc = {
        "note": ("Every form of every given name this archive holds, filed by the language "
                 "that wrote it. Built by tools/names.py from the Record Atlas given-name catalogue and the "
                 "records themselves; nothing here is marked attested by hand."),
        "languages": LANGS,
        "totalForms": n_att + n_aid,
        "attested": n_att,
        "aids": n_aid,
        "rows": out,
    }
    with open(os.path.join(DATA, "names.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"names.json — {len(out)} names, {n_att + n_aid} forms: "
          f"{n_att} attested in the records, {n_aid} lookup aids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
