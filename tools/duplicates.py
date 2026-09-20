#!/usr/bin/env python3
"""The same person, entered twice — across every family this archive publishes.

This started as a Zubrinic-only check and that was the mistake. Running it over
the nine published surname groups finds the same disease everywhere: Ivan Kalanj
is in the tree twice, once dated to the day and once to the year, and his brother
Marijan with him. A grave photograph at Klenovica named four people and two of
them turned out to be four records.

A duplicate is not a research problem to be solved. It is one person counted as
two, and it quietly inflates every number this archive publishes about itself.

The test is tiered, because a shared name is not a shared person. This archive
holds eighteen Ivan Blazevics, and cousins were named for the same grandfather as
a matter of course:

    same day              identical full birth date. Near-conclusive.
    fragment              same year and the same parents, where one record has
                          a day and a village and the other has neither. A
                          split, not a proof: two siblings can share a year.
    same death day        identical full DEATH date. One person dies once, and
                          unlike parents, siblings cannot share it.
    same year and place   strong, but cousins do this.
    same year only        weakest. Listed, not acted on.

  and two vetoes, because one person is born once and dies once: two firm
  death YEARS, or two full birth DAYS, and the group is two people.

Nothing is merged. The tree is reported, not edited — the same rule the rest of
this archive follows.
"""
import sys, os, re, json, collections, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom
from ancestry import fold

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

P, F = gedcom.load()
# The site publishes the UNION of people.json and ancestors.json - 52 direct
# ancestors are not in the register file - and /people counts that union. This
# check used to scan people.json alone, so its surplus figure was being
# subtracted from a larger total than it had examined. Scan what is published.
pub = {}
for _f in ("people.json", "ancestors.json"):
    for _r in json.load(open(os.path.join(DATA, _f), encoding="utf-8")):
        pub.setdefault(_r["id"], _r)

# the surname groups this archive actually publishes
GROUPS = sorted({fold(p.get("surname") or "") for p in pub.values()} - {""})


def place(p):
    for ev in (gedcom.born(p), gedcom.died(p)):
        pl = (ev.get("place") or "").split(",")[0].strip()
        if pl:
            return pl
    return None


# «11 FEB 1967» is a day. «FEB 1967» is not, and the length test could not tell
# them apart — it would have graded a shared MONTH as «same day. Near-
# conclusive.» No group published here ever rested on one, checked before the
# rule was tightened, so this changes no grading; it closes a door.
DAY = re.compile(r"^\d{1,2}\s+[A-Z]{3}\s+\d{4}$")


def full_date(p):
    """A birth date with a day in it, or nothing. A bare year, a month, or a
    hedge (ABT, BEF, AFT, EST, CAL) is not a full date."""
    d = (gedcom.born(p).get("date") or "").strip().upper()
    return d if DAY.match(d) else None


def full_death_date(p):
    """The same test, on the death. One person dies once and on one day, so two
    records carrying the SAME full death date is a confirmation of the same
    weight as two records naming the same parents — and unlike parents, siblings
    cannot share it. Danijel Kalanj, born 2 November 1829 at Klenovica, sat in
    the bare «same day» tier for two days with «26 JUN 1876» written on both of
    his records, because nothing looked at the end of a life."""
    d = (gedcom.died(p).get("date") or "").strip().upper()
    return d if DAY.match(d) else None


# Bucket on surname and birth year, then match given names WITHIN the bucket by
# token containment rather than equality. Marijan Kalanj is entered once as
# "Marijan Cigo" and once as "Marijan" - the nickname is in one record and not
# the other, so equality misses him, and his brother Ivan, and the gravestone
# that names them both. Containment catches that; it does not catch two
# unrelated Ivans, because they have the same token set, not a nested one, and
# equality already handles those.
rough = collections.defaultdict(list)
for pid in pub:
    p = P.get(pid)
    if not p:
        continue
    sur = fold(p.get("surname") or "")
    giv = fold((p.get("given") or "").strip())
    by = gedcom.year(gedcom.born(p).get("date", ""))
    if not giv or not sur or by is None:
        continue          # an undated bare name cannot be matched on safely
    rough[(sur, by)].append((pid, frozenset(giv.split())))

BUCKET = re.compile(
    r"\bbrothers?\b|\bsisters?\b|to be sorted|for sorting|\bsorting\b|"
    r"\bworking\b|it seems|not real|investigation|\bunknown\b|"
    r"\d{4}\s*-\s*\d{4}\s*birth", re.I)


def parents(pid):
    """Each parent as a SET of folded given-name tokens.

    A set, not a string, because the tree renders one man as "Michael Miho
    Michael Xubrinich" in one record and "Michaelis / Michael / Miho / Michael
    'Miko'" in another. Comparing those as strings - or worse, on their first
    token - turns Michael and Michaelis into two men. Comparing them as sets and
    asking whether they OVERLAP gets it right.
    """
    out = {"husb": set(), "wife": set()}
    for f in (P[pid].get("famc") or []):
        fam = F.get(f, {})
        for role in ("husb", "wife"):
            o = fam.get(role)
            # A sorting label in the father's slot is not a father, and letting
            # one count here rejects real duplicates: Michael Zubrinic b.1802 is
            # the son of "Jure Georgius Juraj Zubrinic" in one record and of
            # "Brothers of Casparus (It Seems)" in the other, which is not a
            # disagreement between two fathers. It is one father and one label.
            if o in P and not BUCKET.search(gedcom.display(P[o]) or ""):
                out[role] |= set((fold(P[o].get("given") or "") or "").split())
    return out


def parent_surnames(pid):
    """Each parent's SURNAME tokens — what parents() deliberately throws away.

    parents() folds a parent to their given names, which is right for the veto:
    Michael and Michaelis are one man and comparing surnames would not help. For
    the CONFIRMATION it is the wrong half of the name. Both mothers of the two
    Alexander Zubrinics of 14 March 1839 reduce to «magdalena» — one is
    Oreskovic and the other Drazenovic, and only the surname says so.
    """
    out = {"husb": set(), "wife": set()}
    for f in (P[pid].get("famc") or []):
        fam = F.get(f, {})
        for role in ("husb", "wife"):
            o = fam.get(role)
            if o in P and not BUCKET.search(gedcom.display(P[o]) or ""):
                out[role] |= set((fold(P[o].get("surname") or "") or "").split())
    return out


def same_but_spelling(a, b):
    """Two spellings of one name on otherwise identical records."""
    ba, bb = gedcom.born(P[a]), gedcom.born(P[b])
    da, db = (ba.get("date") or "").strip().upper(), (bb.get("date") or "").strip().upper()
    if not da or da != db or len(da) <= 4:
        return False                      # need a full, identical birth date
    if (ba.get("place") or "").strip() != (bb.get("place") or "").strip():
        return False
    pa, pb = parents(a), parents(b)
    for role in ("husb", "wife"):
        if not pa[role] or not pb[role] or not overlap(pa[role], pb[role]):
            return False                  # both parents must be named and agree
    ga = (fold(P[a].get("given") or "") or "").split()
    gb = (fold(P[b].get("given") or "") or "").split()
    return bool(ga and gb and ga[0][:3] == gb[0][:3])


# Which folded tokens are GIVEN names. The archive already keeps this vocabulary
# for its own Latin-to-Croatian folding, so the duplicate tool can borrow it
# rather than invent a second list that drifts from the first.
def _given_vocab():
    import json as _json
    try:
        gn = _json.load(open(os.path.join(ROOT, "site", "src", "data", "givennames.json"),
                             encoding="utf-8"))
    except Exception:
        return set()
    out = set()
    for key, variants in (gn.get("groups") or {}).items():
        out.add(fold(key))
        for v in variants:
            out.add(fold(v))
    return out


GIVEN = _given_vocab()


def parents_agree(ids):
    """True when every record names the same father and the same mother.

    parents_conflict is the veto; this is the confirmation, and the tool had only
    the veto. Two records sharing a birth DAY, a village and BOTH parents are one
    child written twice — Catharina Zubrinic of 20 November 1840 is Mate x Anna
    Mudrovcic in both copies and there is nothing left for a second Catharina to
    be. A group that passes needs no register.

    Given names are compared as parents() compares them, by overlap, because
    Michael and Michaelis are one man. But SURNAMES must not disagree, and at
    least one parent must be proved by one: «Magdalena Oreskovic» and «Magdalena
    Mande Drazenovic» both reduce to «magdalena», and they are two women. Without
    that test Alexander Zubrinic of 14 March 1839 is declared one boy when he is
    two boys born the same day to two different Michaels — the seven-Michaels
    trap in miniature.
    """
    surname_seen = False
    for role in ("husb", "wife"):
        given = [n for n in (parents(i)[role] for i in ids) if n]
        if len(given) < 2:
            return False
        for a in range(len(given)):
            for b in range(a + 1, len(given)):
                if not overlap(given[a], given[b]):
                    return False
        sur = [n for n in (parent_surnames(i)[role] for i in ids) if n]
        for a in range(len(sur)):
            for b in range(a + 1, len(sur)):
                if not overlap(sur[a], sur[b]):
                    return False
        if len(sur) >= 2:
            surname_seen = True
    return surname_seen


def parents_conflict(ids):
    """True when two records name parents that share no name at all.

    The strongest signal there is, and it cuts both ways. Josephus Zubrinic born
    16 March 1845 has Michael and Maria Markovic in both copies and is plainly
    one boy. Nicolaus Zubrinic born at Otocac in 1834 is the son of Michael in
    one record and of Lucas in the other - and he is ahnentafel 10, a direct
    ancestor. Without this test the tool would have had this archive announce
    that its own great-great-grandfather was a duplicate.

    Overlap, not equality. A missing parent proves nothing and is ignored.
    """
    for role in ("husb", "wife"):
        named = [n for n in (parents(i)[role] for i in ids) if n]
        for a in range(len(named)):
            for b in range(a + 1, len(named)):
                if not overlap(named[a], named[b]):
                    return True
    return False


# Croatian given names carry short forms that are not spelling variants but
# different words, and the registers use them interchangeably for one person.
# This archive documents that on /name; the same knowledge belongs here. The
# table is deliberately short and only holds pairs seen in these registers.
SHORT = {
    "mare": "marija", "mara": "marija", "marica": "marija", "manda": "magdalena",
    "mande": "magdalena", "kate": "katarina", "kata": "katarina",
    "ane": "ana", "anna": "ana", "antona": "anton", "antone": "anton",
    "tonka": "antonija", "joso": "josip", "jozo": "josip", "jure": "juraj",
    "miko": "mihovil", "miho": "mihovil", "mate": "matija", "ive": "ivan",
    "luce": "lucija", "luca": "lucija", "bare": "barbara",
}


def canon(tok):
    """Fold a short form to its full name, and collapse doubled letters.

    Doubled letters matter: Phillipus and Philippus are two spellings of one man
    two substitutions apart, which a single-edit test will never catch. Collapsing
    runs makes both "philipus" and settles it.
    """
    t = SHORT.get(tok, tok)
    out = []
    for ch in t:
        if not out or out[-1] != ch:
            out.append(ch)
    return "".join(out)


def near(a, b):
    """One substitution, insertion or deletion apart — Lovro / Lovre, Ane / Ana.

    Croatian given names vary in their final vowel between records without
    varying the man. Anything looser than a single edit starts merging Marija
    with Marica and Mile with Mate, so this stays at one.
    """
    if a == b:
        return True
    if min(len(a), len(b)) < 4 or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(long)):
        if long[:i] + long[i + 1:] == short:
            return True
    return False


def overlap(s1, s2):
    c1 = {canon(x) for x in s1}
    c2 = {canon(y) for y in s2}
    return any(near(x, y) for x in c1 for y in c2)


buckets = collections.defaultdict(list)
for (sur, by), members in rough.items():
    used = set()
    for i, (pid, toks) in enumerate(members):
        if pid in used:
            continue
        grp = [pid]
        for pid2, toks2 in members[i + 1:]:
            if pid2 in used:
                continue
            # Containment catches "Marijan" inside "Marijan Cigo". It does NOT
            # catch Kate against Katalyn, which are disjoint tokens and the same
            # woman - the archive held both, identical in birth date, birth
            # place, death date, death place AND parents, and this check walked
            # past them until a South Australian birth index showed only ONE
            # registration in 1886 and no Katalyn at all.
            #
            # So: where the full birth date, the birth place and BOTH parents
            # agree exactly, a shared three-letter prefix is enough. That is a
            # deliberately high bar - Marija and Marica share a prefix too, and
            # would need to share a day, a village and two parents as well.
            if toks <= toks2 or toks2 <= toks or same_but_spelling(pid, pid2):
                grp.append(pid2)
                used.add(pid2)
        used.add(pid)
        if len(grp) > 1:
            key = (sur, " ".join(sorted(toks)), by)
            buckets[key].extend(grp)

groups = []
for (sur, giv, by), ids in buckets.items():
    if len(ids) < 2:
        continue
    dates = {full_date(P[i]) for i in ids}
    places = {place(P[i]) for i in ids} - {None}
    firm = {d for d in dates if d}
    dys = {gedcom.year(gedcom.died(P[i]).get("date", "")) for i in ids} - {None}
    # Every record in the group carrying the SAME day of death, not merely the
    # same year. Empty unless all of them have one.
    _dd = [full_death_date(P[i]) for i in ids]
    ddays = set(_dd) if all(_dd) else set()

    # A necronym is not a duplicate. When a child died the next was very often
    # given the same name, so two records can share a surname, a given name, a
    # birth year and a village and still be two different children. Two firm and
    # DIFFERENT death years is the giveaway - one person dies once. Antonius
    # Kalanj of Klenovica 22, born 1868, is entered as dying in 1868 and in 1873,
    # and that is two boys, not one boy twice.
    if parents_conflict(ids):
        tier = "rejected — different parents"
    elif len(dys) > 1:
        tier = "rejected — two death years"
    elif len(firm) > 1:
        # ONE PERSON IS BORN ONCE, and this is the stronger half of the veto
        # above: not two death YEARS but two birth DAYS, both written out in
        # full, both unhedged. Magdalena Kalanj is 8 June 1829 at Klenovica in
        # one record and 19 February 1829 at Ledenice in the other — a
        # different day, a different month and a different village, and the
        # tool was carrying her as a live duplicate because it only ever
        # rejected on death years. A group reaches here only when EVERY record
        # carries a full date, so a complete copy paired with a year-only stub
        # is untouched: that is the fragment tier's business, not this one.
        tier = "rejected — two birth days"
    elif len(firm) == 1 and all(full_date(P[i]) for i in ids) and parents_agree(ids):
        tier = "same day and same parents"
    elif ddays and len(ddays) == 1:
        tier = "same day, and the same death day"
    elif parents_agree(ids) and any(full_date(P[i]) for i in ids) \
            and not all(full_date(P[i]) for i in ids):
        # ONE RECORD IS A FRAGMENT OF THE OTHER, and the parents agree.
        #
        # The confirming tier above needs a full birth date on EVERY record, and
        # the commonest shape of a split is not that: it is one complete copy —
        # day, village, house — and one stub carrying a year and two parents.
        # Danijel Kalanj is that shape, and pava Boras, and Andreas Žubrinić.
        # Four Blažević groups of Mrzli Dol 6 are that shape at once: Ivan 1853,
        # Mile 1855, Marko 1863 and Ane 1865, every record naming ANTON
        # BLAŽEVIĆ and MARIJA ŠOJAT under three spellings apiece, and every one
        # of the four scattered across the two weakest tiers where the fact that
        # the parents agree could not be seen.
        #
        # It is ranked BELOW the same-day tiers and it is not a confirmation.
        # Two siblings can share a birth year and two parents — that is what a
        # year without a day cannot rule out, and it is why this says «and one
        # is a fragment» rather than «and they are one person».
        tier = "same year, same parents, and one record is a fragment"
    elif len(firm) == 1 and all(full_date(P[i]) for i in ids):
        tier = "same day"
    elif len(places) == 1:
        tier = "same year and place"
    else:
        tier = "same year only"
    groups.append({
        "tier": tier, "surname": sur, "given": giv, "byear": by, "n": len(ids),
        "place": sorted(places)[0] if places else None,
        "date": sorted(firm)[0] if firm else None,
        "ids": ids,
        "names": [gedcom.display(P[i]) for i in ids],
        "slugs": [pub[i].get("slug") for i in ids],
        "dyears": sorted({gedcom.year(gedcom.died(P[i]).get("date", "")) for i in ids} - {None}),
    })

# ---- the pass that does not look at the name at all -----------------------
#
# Every group above is keyed on a surname and a given name, so two records can
# only meet if somebody spelled them alike. PAVA BORAS and PAULINA BORAS never
# meet: «pava» and «paulina» share two letters and no token, so containment
# fails and the three-letter-prefix rule fails with it. They are the same woman.
# Born 24 December 1895, the same parents, and BOTH MARRIED IVAN KRMPOTIĆ — one
# copy carrying the marriage and no children, the other seven children and no
# marriage, which is exactly the split Danijel Kalanj showed.
#
# So this pass starts from the family instead: children of one couple who share
# an EXACT birth date. That alone proves nothing — the tree holds 113 such pairs
# and most of them are twins, several of them labelled so. The discriminator is
# the SPOUSE: twins do not marry the same person, and a record entered twice
# does.
#
# It has to be the spouse's NAME and not their record. Both Borases married an
# «Ivan Krmpotić» and the tree holds TWO of him, one with a birth date and one
# without — because duplicating a wife duplicates her husband along with her,
# and comparing record ids would have missed exactly the case this pass was
# written for. On names it fires eight times across the whole tree.
def _spouse_names(pid):
    out = set()
    for fid in (P[pid].get("fams") or []):
        fam = F.get(fid) or {}
        for role in ("husb", "wife"):
            o = fam.get(role)
            if o and o != pid and o in P:
                out.add(fold(gedcom.display(P[o]) or ""))
    return {x for x in out if x}


# The same pass twice, because a life has two ends and only one of them was
# being looked at. Keying on the BIRTH day finds a record split down the middle
# when both halves kept the birth; it cannot find Louis Barry, who is in this
# tree twice with two different birth years — 17 February 1920 and 1907 — and
# so falls in no bucket any name-and-year key can build. What his two records
# do share is the day he died: 20 March 1983 at Cape Town, and a wife called
# Louise Sophie van Heerden in both.
#
# One veto, and it is the one that matters. Two records that BOTH carry a full
# birth date and disagree about it are two people, whatever else they share:
# Elizabeth Margaretha Catharina Botha (b. 29 January 1797) and Margaretha
# Debora Maria Botha (b. 15 May 1802) are sisters who both married a George
# Aldric and are both entered as dying on 15 March 1889. That is a coincidence
# worth recording and it is not one woman, and without this veto the pass would
# have announced her as one.
twins = []
for _fid, _fam in F.items():
    for _stamp in (full_date, full_death_date):
        byday = collections.defaultdict(list)
        for kid in (_fam.get("chil") or []):
            if kid in P and _stamp(P[kid]):
                byday[_stamp(P[kid])].append(kid)
        for _d, kids in byday.items():
            for a, b in itertools.combinations(sorted(kids), 2):
                if not (_spouse_names(a) & _spouse_names(b)):
                    continue
                ba, bb = full_date(P[a]), full_date(P[b])
                if ba and bb and ba != bb:
                    continue
                twins.append([a, b])

_seen = {frozenset(g["ids"]) for g in groups}
for ids in twins:
    if frozenset(ids) in _seen:
        continue
    _seen.add(frozenset(ids))
    places = {place(P[i]) for i in ids} - {None}
    groups.append({
        "tier": "same day, same parents, same spouse",
        "surname": fold(P[ids[0]].get("surname") or ""),
        "given": " ".join(sorted({fold(P[i].get("given") or "") for i in ids})),
        "byear": gedcom.year(gedcom.born(P[ids[0]]).get("date", "")),
        "n": len(ids),
        "place": sorted(places)[0] if places else None,
        "date": full_date(P[ids[0]]),
        "ids": ids,
        "names": [gedcom.display(P[i]) for i in ids],
        "slugs": [(pub.get(i) or {}).get("slug") for i in ids],
        "dyears": sorted({gedcom.year(gedcom.died(P[i]).get("date", "")) for i in ids} - {None}),
    })

TIER = {"same day, same parents, same spouse": 0,
        "same day and same parents": 1, "same day, and the same death day": 2,
        "same day": 3,
        "same year, same parents, and one record is a fragment": 4,
        "same year and place": 5,
        "same year only": 6,
        "rejected — two death years": 7,
        "rejected — two birth days": 8,
        "rejected — different parents": 9}
groups.sort(key=lambda g: (TIER[g["tier"]], g["surname"], g["byear"]))
live = [g for g in groups if not g["tier"].startswith("rejected")]
rejected = [g for g in groups if g["tier"].startswith("rejected")]
extra = sum(g["n"] - 1 for g in live)

print(f"{len(pub)} published people across {len(GROUPS)} surname groups")
print(f"{len(live)} duplicate groups holding {extra} surplus records; "
      f"{len(rejected)} rejected as two people sharing a name\n")
by_tier = collections.Counter(g["tier"] for g in groups)
for t in ("same day, same parents, same spouse", "same day and same parents",
          "same day, and the same death day", "same day",
          "same year, same parents, and one record is a fragment",
          "same year and place", "same year only",
          "rejected — two death years", "rejected — two birth days",
          "rejected — different parents"):
    n = by_tier.get(t, 0)
    print(f"  {t:<38} {n:3d} groups  ({sum(g['n']-1 for g in groups if g['tier']==t)} surplus)")
print()
by_sur = collections.Counter(g["surname"] for g in groups)
for s, n in by_sur.most_common():
    print(f"  {n:3d}  {s}")
print()
for g in groups:
    if g["tier"] != "same day":
        continue
    print(f"  x{g['n']}  {g['date']:<14} {g['place'] or '—':<14} "
          f"{' | '.join(n[:30] for n in g['names'])}")

out = os.path.join(DATA, "duplicates.json")
json.dump({"groups": groups, "extra": extra, "published": len(pub),
           "rejected": len(rejected), "live": len(live)},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {os.path.relpath(out, ROOT)}")
