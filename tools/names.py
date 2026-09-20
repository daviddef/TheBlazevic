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
       sources/givennames.psv       canon|form|lang|note|case, written by hand
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
PSV = os.path.join(ROOT, "sources", "givennames.psv")

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

CASES = {"accusative", "genitive", "dative or ablative", "abbreviated"}


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
            attested[canon][fold(form)] = attested[canon].get(fold(form), 0) + n

    rows, seen, fails = [], set(), []
    for line in open(PSV, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        canon, form, lang = parts[0], parts[1], parts[2]
        # The table is written in lower case because it is a matching key. A
        # name is a name and gets its capital back before anybody reads it.
        if form[:1].islower():
            form = form[:1].upper() + form[1:]
        note = parts[3] if len(parts) > 3 else ""
        # THE FIFTH COLUMN, and the fallback that lets sister archives keep
        # four. `case` used to be derived from `note` -- if the note read
        # «genitive» it became the case -- so a form could carry a case OR a
        # remark and never both. It is its own column now. A four-column row
        # still behaves exactly as it did.
        case = parts[4] if len(parts) > 4 else ""
        if not case and note in CASES:
            case = note
        if case and case not in CASES:
            fails.append(f"{PSV}: «{form}» declares an unknown case «{case}» — "
                         f"the vocabulary is {' · '.join(sorted(CASES))}")
        rows.append({"canon": canon, "form": form, "lang": lang,
                     "note": note, "case": case})
        seen.add((canon, fold(form)))

    known = set(given["groups"]) | set(given["observed"])
    for r in rows:
        if r["canon"] not in known:
            fails.append(f"{PSV}: «{r['canon']}» is not a name group given_names.py builds")
        if r["lang"] not in LANGNAME:
            fails.append(f"{PSV}: «{r['form']}» is filed under an unknown language «{r['lang']}»")

    # THE GATE THAT MATTERS, and it runs in the direction that can hurt. A form
    # this archive HAS met and this file does not list is a form the page will
    # not offer — which is the whole defect being fixed, reappearing quietly.
    for canon, forms in attested.items():
        for f in forms:
            if (canon, f) not in seen:
                fails.append(f"{PSV}: the records contain «{f}» for {canon} and this file "
                             f"does not list it — the page would not offer it")
    if fails:
        print(f"FAIL  {len(fails)} problem(s) in the given-name table:")
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
    for canon in sorted(set(r["canon"] for r in rows)):
        mine = [r for r in rows if r["canon"] == canon]
        by_lang = {}
        for r in mine:
            hit = attested.get(canon, {}).get(fold(r["form"]), 0)
            n_att, n_aid = (n_att + 1, n_aid) if hit else (n_att, n_aid + 1)
            by_lang.setdefault(r["lang"], []).append({
                "form": r["form"], "note": r["note"], "seen": hit,
                "case": r["case"],
            })
        for v in by_lang.values():
            v.sort(key=lambda x: (not x["seen"], bool(x["case"]), fold(x["form"])))
        top = sorted(attested.get(canon, {}).items(), key=lambda kv: -kv[1])
        # ONE PERSON, ONCE. Summing over the rows counts a bearer again for
        # every language the form is filed under, and eighteen forms are filed
        # under two or three: «Maria» is Latin, Italian and Hungarian, so the
        # one person written Maria and recorded M was three men here, and the
        # page said so out loud. Fold first, then count.
        forms = {fold(r["form"]) for r in mine}
        men = sum(bysex.get(f, {}).get("m", 0) for f in forms)
        women = sum(bysex.get(f, {}).get("f", 0) for f in forms)
        asserted = given.get("sex", {}).get(canon, "")
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
            "attested": sum(1 for r in mine
                            if attested.get(canon, {}).get(fold(r["form"]), 0)),
            # PEOPLE MEANS PEOPLE. It used to be the sum of the occurrence
            # counts, which disagreed with men+women in 21 of 39 rows, and the
            # shared component renders it as a count of bearers. `tokens` is the
            # occurrences, which is a different and also useful number.
            "people": men + women,
            "tokens": sum(attested.get(canon, {}).values()),
            "commonest": top[0][0] if top else "",
            "langs": by_lang,
            "oblique": [p for f, ps in oblique.items()
                        if any(fold(r["form"]) == f for r in mine) for p in ps],
        })

    doc = {
        "note": ("Every form of every given name this archive holds, filed by the language "
                 "that wrote it. Built by tools/names.py from sources/givennames.psv and the "
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
