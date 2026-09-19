#!/usr/bin/env python3
"""Why each wall on the ancestor chart is a wall — one true sentence each.

The chart in the kit ends a branch with a default note: «No parents are
recorded for X in this archive. Where the line goes next is not yet known.»
Printed thirty-one times it says nothing, and worse, it says the same thing
about three different silences:

  · a person whose surname the archive does not have, so there is nothing
    to search for at all;
  · a woman entered under her husband's surname, which is the family tree's
    convention and not a record of her name;
  · a person who is properly identified and whose next document is sitting in
    a filmed register nobody has opened.

The third kind is a worklist and the first two are not, and a reader cannot
act on a page that grades them alike. This works out which each one is, names
the parish that would carry the next document, and says whether that book is
filmed, out of range, or does not exist.

TWO THINGS THIS TOOL MUST NOT DO, BOTH LEARNED THE HARD WAY.

It must not say a wall «has not been opened» without looking. It used to print
that sentence from the parish table alone, which knows what is FILMED and
nothing about what has been READ. On 15 September 2026 four walls carried it
while the register in question had been read that morning. The tool now reads
sources/readings.psv and names what this archive already holds for the person.

And it must not call a household «unplaced» when a register has placed it. The
tree is not the only evidence here. Nicolaus Gerkacs has no birthplace anywhere
in the GEDCOM, and his death entry of 1783 puts him in his son's house at
Karlobag — so «no place is recorded for this household anywhere on the line» was
false the moment that entry was read. sources/walls.psv can now supply a place
from a document, and the grading runs on it exactly as it would on the tree's.

Writes site/src/data/walls.json, keyed by ahnentafel number.
"""
import json
import os
import re
import sys

from parishlib import ROOT, PARISH, parish_of, covered, ranges, village_of, year_of

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readingslib

DATA = os.path.join(ROOT, "site", "src", "data")
OVERRIDE = os.path.join(ROOT, "sources", "walls.psv")

# A generation, for estimating when a person was born from when their child
# was. Deliberately coarse: every year derived this way is printed as "about".
GEN = 27


# The parish table is written without diacritics because it is a matching key.
# A reader should still see the parish's own name.
PNAME = {"Otocac": "Otočac", "Grizane": "Grižane", "Krmpote-Vodice": "Krmpote-Vodice"}


def pname(p):
    return PNAME.get(p, p)


def pretty(place):
    """The village as the tree actually spells it — with its diacritics, which
    the matcher strips. «Šumećica 2, Otočac, …» -> «Šumećica»."""
    for part in [x.strip() for x in str(place or "").split(",")]:
        part = re.sub(r"(?:^|\s)(?:br\.?|no\.?|n[o°]|kbr\.?|#)?\s*\d{1,3}(?=$|\s)",
                      " ", part).strip(" ,.-/")
        if part and village_of(part):
            return part
    return None


def held(spec, kindname):
    """What the parish table says about one book — and «unknown» is not «none».
    Karlobag is the archive's best-read parish and its ranges have never been
    checked; printing that as «no baptisms» would be a confident falsehood."""
    if spec == "none":
        return f"no {kindname} filmed"
    if spec == "unknown":
        return f"{kindname} not checked"
    rs = ranges(spec)
    return f"{kindname} {rs[0][0]}–{rs[-1][1]}" if rs else f"{kindname} not checked"


def main():
    anc = json.load(open(os.path.join(DATA, "ancestors.json"), encoding="utf-8"))
    fixes = json.load(open(os.path.join(DATA, "placefixes.json"), encoding="utf-8"))["rules"]
    by = {int(r["ahn"]): r for r in anc if r.get("ahn")}

    # sources/walls.psv — one correction per line, «ahn|field|value», where
    # field is place, label or note. A «place» does not assert a grade; it is
    # fed back through the normal grading so the kind is still derived.
    over = {}
    if os.path.exists(OVERRIDE):
        for line in open(OVERRIDE, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            ahn, field, value = line.split("|", 2)
            over.setdefault(int(ahn), {})[field.strip().lower()] = value.strip()

    # What this archive has actually READ for each person, so the tool can stop
    # guessing at it. sources/readings.psv is «slug|kind|year|where|citation».
    #
    # 20 September 2026: this read the first column and nothing else, so a
    # baptism counted only for the child. THIS WALL IS WHY IT MATTERS. The
    # Karlobag entry of 12 January 1779 was read on the 10th and recorded as
    # «"ex Angelo et Catharina Bacchi"» — their names are in the citation — and
    # ten days later this tool still printed, of both of them, «this wall is
    # reachable and HAS NOT BEEN OPENED» and «put at Karlobag on the strength of
    # their grandchild's death, NOT A DOCUMENT». Both false, against a document
    # in the archive's own file quoting their names.
    #
    # readingslib carries the rule /open-questions/ has published since the
    # 14th: a baptism names all three, so it is a reading for the parents too.
    read_by_slug = {k: [(x["kind"], x["year"]) for x in v]
                    for k, v in readingslib.by_slug(ROOT, DATA).items()}
    derived_of = {k: {x["via"] for x in v if x["derived"]}
                  for k, v in readingslib.by_slug(ROOT, DATA).items()}

    def real_place(row, field="bornPlace"):
        """The place string with the tree's known wrong-county strings corrected,
        so a wall is not sent to an island 400 km away."""
        p = row.get(field) or ""
        for f in fixes:
            if f["match"] and f["match"] in p:
                return f["actually"], f
        return p, None

    walls = {}
    for n in sorted(by):
        if n == 1 or 2 * n in by or 2 * n + 1 in by:
            continue
        r = by[n]
        child = by.get(n // 2)
        grandchild = by.get(n // 4)
        spouse = by.get(n + 1 if n % 2 == 0 else n - 1)
        name = r.get("name") or "—"
        given, surname = (r.get("given") or "").strip(), (r.get("surname") or "").strip()

        # Where the household was, and when this person was likely born.
        #
        # This looked at one field on two people — the person's own bornPlace,
        # then the ahnentafel child's — and called everything else «No place
        # recorded». It is not the same thing. Joanni Brozović was printed as
        # placeless while his daughter Margarita is recorded as DYING at Selce,
        # and Mara Pekass while her husband is recorded as BORN at Smiljan.
        # A death place is a place. A husband's parish is his wife's.
        #
        # So the fallback runs through the household, nearest first, and says
        # which relation supplied it. Nothing here is read off a document — it
        # is the tree's own words about the tree's own people — and a wall says
        # so rather than presenting it as a finding.
        #
        # 17 September 2026: it stopped one generation too early, and «no place
        # is recorded for this household ANYWHERE ON THE LINE» was false three
        # more times. Mateša Blažević's grandson Ilija is born at Smokvica
        # Krmpotska, Michael Sekula's granddaughter at Otočac, Angelo Bacchi's
        # granddaughter dies at Karlobag — all three written plainly in the
        # tree, all three ON THE LINE, and all three printed as nothing known.
        # The grandchild goes last because it is the weakest: a grandchild's
        # parish is where the family had got to, not necessarily where it was.
        # Only ahnentafel 84, Vitus Sekula, is placeless now, and he has no
        # descendant with a place anywhere.
        place, fix = real_place(r)
        place_from = None
        if not village_of(place):
            for label, who, field in (
                    ("their own death", r, "diedPlace"),
                    ("their child's birth", child, "bornPlace"),
                    ("their child's death", child, "diedPlace"),
                    ("their spouse's birth", spouse, "bornPlace"),
                    ("their spouse's death", spouse, "diedPlace"),
                    ("their grandchild's birth", grandchild, "bornPlace"),
                    ("their grandchild's death", grandchild, "diedPlace")):
                if not who:
                    continue
                cand, cfix = real_place(who, field)
                if village_of(cand):
                    place, fix, place_from = cand, cfix, label
                    break
        # A document may place a household the tree never placed. Recorded in
        # sources/walls.psv with the entry that says so.
        placed_by_document = False
        if not village_of(place) and over.get(n, {}).get("place"):
            place, fix = over[n]["place"], None
            placed_by_document = bool(village_of(place))
        village = village_of(place)
        parish = parish_of.get(village or "")
        byear = year_of(r.get("born"))
        cyear = year_of((child or {}).get("born"))
        est = byear or (cyear - GEN if cyear else None)
        exact = bool(byear)

        # What kind of silence this is. Order matters: a person with no surname
        # cannot be searched for whatever the parish holds.
        if not surname:
            kind, label = "nameless", "No surname"
        elif spouse and surname and surname == (spouse.get("surname") or "").strip() \
                and n % 2 == 1:
            kind, label = "borrowed", "Her husband's surname"
        elif not given:
            kind, label = "placeholder", "Only a surname"
        elif parish and PARISH[parish]["births"] == "unknown":
            kind, label = "unchecked", f"{pname(parish)} — ranges not checked"
        elif parish and not est:
            kind, label = "undated", f"{pname(parish)} — no year to test"
        elif parish and covered(PARISH[parish]["births"], est):
            kind, label = "reachable", f"{pname(parish)} — in range"
        elif parish:
            kind, label = "outside", f"{pname(parish)} — out of range"
        elif village:
            # A place IS recorded — no parish in the table claims the village.
            # «No place is recorded for this household anywhere on the line» was
            # printed over Smiljan and over Montani Stanište, both of them
            # written plainly in the tree. That is one gazetteer line from being
            # reachable and it is not the same job as having nothing at all.
            kind, label = "ungazetteered", f"{(pretty(place) or village).title()} — no parish claims it"
        else:
            kind, label = "unplaced", "No place recorded"

        # --- the note ----------------------------------------------------
        bits = []
        if kind == "nameless":
            bits.append(f"This archive has no surname for **{name}** — a given name and "
                        f"nothing else. The wall is not that her parents are unknown; "
                        f"it is that **there is nothing to search for.**")
            if spouse:
                bits.append(f"Her family name would be written on her marriage to "
                            f"**{spouse.get('name')}**, and often on the baptism of a child "
                            f"where the priest gave the mother's house.")
        elif kind == "borrowed":
            bits.append(f"**{name}** is entered under her husband's surname. That is the "
                        f"family tree's convention, not a record — nothing in this archive "
                        f"says what she was born, and the name on the chart is his.")
        elif kind == "placeholder":
            who = f"**{child.get('name')}**" if child else "this person"
            bits.append(f"The tree gives the parent of {who} as a surname with **no given "
                        f"name at all**. That is a placeholder rather than a person: it "
                        f"asserts only what the child's own surname already says.")
        else:
            bits.append(f"No parents are recorded for **{name}**"
                        + (f", born {byear}" if exact else "")
                        + (f", and this archive stops here." if not parish
                           else "."))

        # What this archive already holds for this person. A wall is about the
        # PARENTS being unknown, so a death or a marriage read here does not
        # bring the wall down — but it does mean «has not been opened» is the
        # wrong sentence, and saying which document is still shut is the right one.
        docs = read_by_slug.get(r.get("slug")) or []
        already = ", ".join(f"{k.replace('-', ' ')} {y}" for k, y in docs)

        if parish:
            P = PARISH[parish]
            about = "" if exact else "about "
            where = pretty(place) or (village or "").title()
            # For a wall whose PROBLEM is the name, the baptism is not the
            # document to look for — you cannot search for a surname you do not
            # have. The marriage is: it names her father and gives her own name.
            mar = (cyear - 2) if cyear else (est + 25 if est else None)
            books = [held(P[key], kindname) for kindname, key in
                     (("baptisms", "births"), ("marriages", "marriages"),
                      ("deaths", "deaths"))]
            bits.append(f"The household was at **{where}**, whose registers are "
                        f"**{pname(parish)}**: " + ", ".join(books) + ".")
            if P["births"] == "unknown":
                bits.append(f"**What years those films cover has never been checked**, so "
                            f"whether the next document is reachable is not known — and "
                            f"checking it is an afternoon's work, not a trip.")
            elif kind in ("nameless", "borrowed", "placeholder"):
                if not mar:
                    bits.append("No year is recorded anywhere on this branch, so there is "
                                "nothing to test the film's range against.")
                elif covered(P["marriages"], mar):
                    bits.append(f"**The marriage is the document to look for, not the "
                                f"baptism** — a surname you do not have cannot be searched "
                                f"for, and a marriage entry supplies it. A marriage of about "
                                f"{mar} falls **inside** the filmed register. "
                                + (f"This archive has already read the **{already}** for "
                                   f"her; **the marriage is the one still unopened.**"
                                   if docs else
                                   "**This one is reachable and has not been opened.**"))
                else:
                    rs = ranges(P["marriages"])
                    if rs:
                        bits.append(f"**The marriage is the document to look for, not the "
                                    f"baptism** — it is what would supply the missing name. "
                                    f"A marriage of about {mar} falls **outside** the filmed "
                                    f"register, which runs {rs[0][0]}–{rs[-1][1]}.")
                    else:
                        bits.append("**The marriage is the document to look for**, and "
                                    "**no marriage register for this parish is filmed at "
                                    "all.**")
            elif not est:
                bits.append("No year is recorded for this person or for the child below "
                            "them, so there is nothing to test the film's range against.")
            else:
                if covered(P["births"], est):
                    if docs:
                        bits.append(f"A baptism of {about}{est} falls **inside** that film. "
                                    f"This archive has already read the **{already}** for "
                                    f"this person, and none of it names **their own** parents — the "
                                    f"**baptism is the document still unopened**, and it is "
                                    f"the one that would.")
                    else:
                        bits.append(f"A baptism of {about}{est} falls **inside** that film. "
                                    f"This wall is reachable and has not been opened.")
                else:
                    rs = ranges(P["births"])
                    if rs:
                        gap = rs[0][0] - est
                        bits.append(f"A baptism of {about}{est} falls **{gap} years before** "
                                    f"the filmed register begins.")
                    else:
                        bits.append(f"**No baptismal register for this parish is filmed at "
                                    f"all**, so a baptism of {about}{est} is not reachable "
                                    f"in this collection.")
            if placed_by_document:
                bits.append(f"**The tree does not place this household at all — a document "
                            f"does.** {over[n].get('why', '')}".rstrip())
            if fix:
                bits.append(f"(The tree writes this place as *{fix['reads']}*, which is "
                            f"{fix['km']} km away and wrong.)")
        elif kind == "ungazetteered":
            where = pretty(place) or (village or "").title()
            bits.append(f"The tree does record where this household was — **{where}** — but "
                        f"**no parish in this archive's table claims that village**, so "
                        f"there is nothing to say about what is filmed for it. "
                        f"**This is not a wall in the record. It is a gap in the "
                        f"gazetteer**, and one line in `sources/parishes.psv` closes it "
                        f"once somebody establishes which parish the village belongs to.")
        elif kind not in ("nameless", "borrowed", "placeholder"):
            bits.append("No place is recorded for this household anywhere on the line, "
                        "so there is no register to open. **The wall here is a place, "
                        "not a name.**")

        # A «why» only reached the page when it arrived with a «place», because
        # it was written as the second half of "a document places them, and here
        # is the document". A wall can need a sentence without needing to move:
        # Smiljan and Montani Stanište both got one on 15 September 2026 saying
        # what had been established about the village and what had not, and both
        # were parsed and then dropped on the floor. It is appended on its own
        # now, and skipped where placed_by_document has already printed it.
        if place_from:
            bits.append(f"**The tree records no place for this person.** This household is "
                        f"put at **{pretty(place) or (village or '').title()}** on the strength "
                        f"of {place_from} — the tree's own words about the tree's own people, "
                        f"not a document.")

        why = over.get(n, {}).get("why")
        if why and not placed_by_document:
            bits.append(why)

        note = " ".join(bits)
        label = over.get(n, {}).get("label") or label
        note = over.get(n, {}).get("note") or note

        walls[str(n)] = {"ahn": n, "name": name, "slug": r.get("slug"),
                         "kind": kind, "label": label, "note": note,
                         "parish": pname(parish) if parish else None, "village": pretty(place) if village else None,
                         "year": est, "exact": exact}

    # An override for an ahnentafel number that is NOT a wall is silently
    # ignored — the loop above only visits walls, so the row is parsed, held in
    # `over`, and never read. That is the same failure as a «why» arriving
    # without a «place»: accepted, then dropped on the floor. A row written for
    # ahnentafel 213 on 17 September was inert for exactly this reason, and
    # nothing said so. Now it does.
    orphan = sorted(set(over) - {int(k) for k in walls})
    if orphan:
        print(f"WARNING  {len(orphan)} row(s) in sources/walls.psv name an ahnentafel "
              f"that is not a wall, so they do nothing: "
              + ", ".join(str(o) for o in orphan))

    counts = {}
    for w in walls.values():
        counts[w["kind"]] = counts.get(w["kind"], 0) + 1
    out = {"counts": counts, "walls": walls}
    json.dump(out, open(os.path.join(DATA, "walls.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"walls.json — {len(walls)} walls: "
          + ", ".join(f"{n} {k}" for k, n in sorted(counts.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
