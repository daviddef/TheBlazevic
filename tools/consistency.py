#!/usr/bin/env python3
"""Check the tree against itself.

Tereza Pećanić was published as having died in 1850, married in 1858 and borne
children until 1884. No register was needed to catch that — only reading her own
record beside itself. Everything here is that kind of check: no external source,
just dates that cannot all be true at once.

Ordered by how badly the archive would be embarrassed to publish it.
"""
import json, re, sys, os, collections, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year
from build_site_data import JUNK          # the same sorting-bucket filter

MONTH = {m: i + 1 for i, m in enumerate(
    "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}


def ym(datestr):
    """(year, month) from a GEDCOM date, ignoring qualifiers. Month may be None."""
    if not datestr:
        return None, None
    s = datestr.upper()
    y = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", s)
    if not y:
        return None, None
    mo = None
    for k, v in MONTH.items():
        if k in s:
            mo = v
            break
    return int(y.group(1)), mo


def approx(datestr):
    """True if the date is hedged - ABT, BEF, AFT, EST, a range."""
    return bool(datestr) and bool(
        re.search(r"\b(ABT|BEF|AFT|EST|CAL|BET|FROM|TO)\b", datestr.upper()))


people, families = load()

# Entries that are labels rather than people; ages computed against them mean nothing.
BUCKET_PARENT = re.compile(
    r"\bbrothers?\b|\bsisters?\b|to be sorted|for sorting|\bsorting\b|"
    r"\bworking\b|it seems|not real|investigation|\d{4}\s*-\s*\d{4}\s*birth", re.I)

# This export carries six families. Scope to the ones this archive publishes,
# plus anyone named in one of its relation lists - otherwise the sweep reports
# the Booyzen and D'Arcy trees' problems as though they were ours.
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "site", "src", "data")
pub = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8")) + \
      json.load(open(os.path.join(DATA, "ancestors.json"), encoding="utf-8"))
SCOPE = {x["id"] for x in pub}
for x in pub:
    for grp in (x.get("rel") or {}).values():
        for r in (grp if isinstance(grp, list) else []):
            if isinstance(r, dict) and r.get("id"):
                SCOPE.add(r["id"])
# and the parents/children of those, so a join is checked from both ends
for fid, f in families.items():
    members = [f.get("husb"), f.get("wife")] + list(f.get("chil") or [])
    if any(m in SCOPE for m in members if m):
        SCOPE.update(m for m in members if m)

def relevant(pid):
    return pid in SCOPE and not JUNK.search(display(people[pid]) or "")

issues = []


SLUG = {x["id"]: x["slug"] for x in pub}


def add(kind, sev, pid, msg):
    issues.append({"kind": kind, "sev": sev, "id": pid,
                   "name": display(people[pid]), "slug": SLUG.get(pid), "msg": msg})


# marriage dates per person
marr = collections.defaultdict(list)
for fid, f in families.items():
    for e in f.get("events", []):
        if e.get("kind") == "marriage" and e.get("date"):
            for role in ("husb", "wife"):
                if f.get(role):
                    marr[f[role]].append(e["date"])

for pid, p in people.items():
    if not relevant(pid):
        continue
    b, d = born(p), died(p)
    by, bm = ym(b.get("date"))
    dy, dm = ym(d.get("date"))

    if by and dy:
        if dy < by:
            add("died-before-born", 1, pid,
                f"born {b['date']}, died {d['date']}")
        elif dy - by > 105:
            add("implausible-age", 3, pid,
                f"born {b['date']}, died {d['date']} — age {dy - by}")

    # married after death, or before birth
    for md in marr.get(pid, []):
        my, _ = ym(md)
        if not my:
            continue
        if dy and my > dy and not approx(d.get("date")):
            add("married-after-death", 1, pid,
                f"died {d['date']}, married {md}")
        elif dy and my > dy:
            add("married-after-death", 2, pid,
                f"died {d['date']} (hedged), married {md}")
        if by and my < by:
            add("married-before-birth", 1, pid, f"born {b['date']}, married {md}")
        elif by and my - by < 12:
            add("married-as-child", 2, pid,
                f"born {b['date']}, married {md} — age {my - by}")

for fid, f in families.items():
    for role, label, grace in (("husb", "father", 1), ("wife", "mother", 0)):
        par = f.get(role)
        if not par or par not in people or not relevant(par):
            continue
        pb, pd = born(people[par]), died(people[par])
        pby, _ = ym(pb.get("date"))
        pdy, _ = ym(pd.get("date"))
        for cid in f.get("chil", []):
            if cid not in people or JUNK.search(display(people[cid]) or ""):
                continue
            cby, _ = ym(born(people[cid]).get("date"))
            if not cby:
                continue
            if pdy and cby > pdy + grace:
                sev = 2 if approx(pd.get("date")) else 1
                add("child-after-parent-death", sev, par,
                    f"died {pd['date']}, but {display(people[cid])} born {cby}")
            if pby:
                if cby < pby:
                    add("child-before-parent-birth", 1, par,
                        f"born {pb['date']}, but {display(people[cid])} born {cby}")
                elif cby - pby < 13:
                    # A sorting label is not a parent, and its "birth year" is
                    # whatever somebody typed. Ages computed against one are
                    # meaningless - two of the six gaps this check used to miss
                    # were against "Brothers of Casparus (It Seems)".
                    if not BUCKET_PARENT.search(display(people[par]) or ""):
                        add("parent-too-young", 2, par,
                            f"born {pb['date']}, {display(people[cid])} born {cby}"
                            f" — age {cby - pby}")
                elif cby - pby < 17 and not BUCKET_PARENT.search(display(people[par]) or ""):
                    # 13 to 16 is possible and uncommon. It is not impossible, so
                    # it sits at the lowest severity rather than moving the line
                    # of what cannot be true. Marija Sojat bearing at 15 and Anton
                    # Blazevic fathering at 16 - the same child, in 1840 - is a
                    # couple who married very young, or a birth year that is wrong.
                    add("parent-under-seventeen", 3, par,
                        f"born {pb['date']}, {display(people[cid])} born {cby}"
                        f" — age {cby - pby}")
                elif role == "wife" and cby - pby > 50:
                    add("mother-too-old", 3, par,
                        f"born {pb['date']}, {display(people[cid])} born {cby}"
                        f" — age {cby - pby}")

# Chains. The pairwise checks need both dates to exist, so a grandparent born
# after a grandchild slips through whenever the generation between them is
# undated - which is exactly how Caetano Bacchi (b. 1779) came to be the
# grandfather of a girl born in 1781.
#
# Only that case is reported. Walking descendants freely produces dozens of
# rows per bad join, because one wrong link propagates down every branch below
# it; those are consequences, not findings, and listing them buries the cause.
kids = collections.defaultdict(list)
for fid, f in families.items():
    for role in ("husb", "wife"):
        if f.get(role):
            for c in f.get("chil") or []:
                kids[f[role]].append(c)

flagged = {i["id"] for i in issues}

for pid in list(people):
    if not relevant(pid) or pid in flagged:
        continue
    ay, _ = ym(born(people[pid]).get("date"))
    if not ay:
        continue
    for mid in kids.get(pid, []):                      # the child
        if mid not in people or JUNK.search(display(people[mid]) or ""):
            continue
        if ym(born(people[mid]).get("date"))[0]:
            continue                                   # dated: pairwise saw it
        for gid in kids.get(mid, []):                  # the grandchild
            if gid not in people or JUNK.search(display(people[gid]) or ""):
                continue
            gy, _ = ym(born(people[gid]).get("date"))
            # two generations need roughly two puberties between them; 24 years
            # is already generous, and anything under it cannot stand.
            if gy and gy - ay < 24:
                add("impossible-generation-gap", 1, pid,
                    f"born {born(people[pid])['date']}, but through undated "
                    f"{display(people[mid])} the grandchild "
                    f"{display(people[gid])} is born {gy}"
                    f" — {gy - ay} years for two generations")

# --- a given name that is overwhelmingly one sex, against a sex that is not --
#
# tools/names.py counts, for every given-name group, how many men and how many
# women in THIS archive bear it - read off people.json and ancestors.json
# rather than asserted. Those counts are the only evidence worth using here.
# given_names.py's SEX table calls "matija" male, and eight of the forty people
# written Matia in these registers are women, because Matija is unisex in
# Croatian and the table has one column for it. A table is a claim; the counts
# are a record.
#
# So: a name borne by at least five people here, at least nine in ten of them
# one sex, and a person recorded as the other sex - that person contradicts the
# archive's own usage.
#
# THE MAJORITY IS COUNTED WITHOUT THE PERSON BEING JUDGED, and that is not a
# refinement, it is the difference between the check working and not working.
# "Ivana" is borne here by 21 women and 3 people recorded M. Counted whole that
# is 87 per cent, under any threshold worth setting, and the check stays silent:
# the three wrong records were holding the name below the line that would have
# caught them. Set the person in hand aside and the other 23 are 91 per cent
# women, and all three are found. An error does not get a vote on whether it is
# an error.
#
# WHAT IT STILL MISSES, so that the gap is on the record rather than in the
# gaps. names.py tallies published people, so a person WITHOUT A PAGE is not in
# the tally and there is nothing of theirs to set aside - they are judged by all
# 24 Ivanas, including the three wrong ones, which is 87 per cent and silence.
# Ivana Juhas, recorded M, is that person, and this check does not find her.
# The archive has made the mistake of forgetting the unpublished three times
# already; this one is at least written down. It errs towards saying nothing,
# which is the right direction for a check that stops a deploy.
#
# Nothing here says WHICH of the two fields is wrong, and it must not pretend
# to. Franciscus Prpic is a Latin nominative and can only be a man, so the F is
# the error. "Ivana" Blazevic, recorded M and recorded as a husband, is more
# likely a man called Ivan whose name was copied out of a register in the
# genitive - what latin_cases.py reports for Latin, happening in Croatian.
# Both are worth publishing. Neither is resolved here, and the tree is not
# touched either way.
NAMES = json.load(open(os.path.join(DATA, "names.json"), encoding="utf-8"))


def fold(s):
    """names.py's comparison key: no diacritics, no case."""
    s = unicodedata.normalize("NFKD", str(s or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# folded form -> the name groups claiming it, and each group's tally. Luca and
# Luce are claimed by both luka and lucija; a form two groups disagree about
# proves nothing about the person carrying it.
FORM_GROUP = collections.defaultdict(set)
BEARERS = {}
for r in NAMES["rows"]:
    BEARERS[r["canon"]] = (r["men"], r["women"])
    for forms in r["langs"].values():
        for f in forms:
            FORM_GROUP[fold(f["form"])].add(r["canon"])

COUNTED = {x["id"] for x in pub}   # exactly who names.py's tallies include


def against_the_name(canon, sex, counted):
    """(majority, men, women) among this group's OTHER bearers, if they object."""
    men, women = BEARERS[canon]
    if counted:                     # the record does not get to judge itself
        men, women = (men - 1, women) if sex == "M" else (men, women - 1)
    total = men + women
    if total < 5:
        return None
    if sex == "M" and women >= 0.9 * total:
        return ("F", men, women)
    if sex == "F" and men >= 0.9 * total:
        return ("M", men, women)
    return None


for pid, p in people.items():
    if not relevant(pid):
        continue
    sex = (p.get("sex") or "").upper()[:1]
    first = re.split(r"[\s(]", (p.get("given") or "").strip())[0].strip('"')
    if sex not in ("M", "F") or not first:
        continue
    groups = sorted(FORM_GROUP.get(fold(first), ()))
    verdicts = [against_the_name(c, sex, pid in COUNTED) for c in groups]
    if not groups or not all(verdicts):
        continue                    # unknown name, or one group does not object
    canon, (_, men, women) = max(zip(groups, verdicts),
                                 key=lambda gv: gv[1][1] + gv[1][2])
    word, n = ("women", women) if sex == "M" else ("men", men)
    add("sex-contradicts-name", 2, pid,
        f"recorded {sex}; \u00ab{first}\u00bb is a form of {canon}, and {n} of "
        f"the {men + women} other people here who bear it are {word}")


order = {1: "IMPOSSIBLE", 2: "very doubtful", 3: "worth a look"}
issues.sort(key=lambda i: (i["sev"], i["kind"], i["name"]))
seen = set()
uniq = []
for i in issues:
    k = (i["kind"], i["id"], i["msg"])
    if k not in seen:
        seen.add(k)
        uniq.append(i)

# --- what KIND of mistake is this? ------------------------------------------
#
# 63 rows is not 63 mistakes. One wrong parent link reports once per child, and
# a page that lists all of them buries the handful of real contradictions under
# their own consequences. Worse, the rows are not the same sort of thing: a
# death recorded as "BEF 1850" contradicting a birth in 1858 is not an error at
# all, it is a hedge doing its job, whereas a girl who died the year before she
# was born is a mistake in the record itself.
#
# So each row is given a cause, and rows sharing a pivot person are collapsed
# into one. The archive should say "these four are one bad link" rather than
# reporting the bad link four times.

HEDGE = re.compile(r"\b(?:BEF|AFT|ABT|ABOUT|CAL|EST|FROM|TO)\b|Maybe|\(hedged\)", re.I)
YEARS = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
AGE = re.compile(r"age (-?\d+)")


def classify(i):
    """sex | hedged | namesake | generation | record"""
    # Not a date at all, so none of the date reasoning below applies to it.
    if i["kind"] == "sex-contradicts-name":
        return "sex"
    msg = i["msg"]
    if HEDGE.search(msg):
        return "hedged"
    ys = [int(y) for y in YEARS.findall(msg)]
    span = max(ys) - min(ys) if ys else 0
    # No amount of slop in a date explains a child born decades after the
    # parent died. A father can manage nine months posthumously; he cannot
    # manage twenty-five years. Past that the link itself is wrong.
    if span > 80 or (i["kind"] == "child-after-parent-death" and span > 25):
        return "namesake"
    m = AGE.search(msg)
    if m and i["kind"] == "parent-too-young" and 0 <= int(m.group(1)) <= 14:
        return "generation"
    return "record"


CAUSE_NOTE = {
    "hedged": "A hedged date (BEF, AFT, Maybe) sitting against a firm one. "
              "The hedge is doing its job; this is imprecision, not error.",
    "namesake": "Too far apart for any slop in the dates to explain — so the "
                "link is wrong, not the dates. Usually a name reused down "
                "the line, or two people merged into one.",
    "generation": "A parent barely older than the child — a generation has "
                  "been skipped, and a grandparent recorded as a parent.",
    "record": "The dates as recorded genuinely cannot both be true.",
    "sex": "The recorded sex and the recorded given name disagree, measured "
           "against how this archive's own records use that name. Which of "
           "the two is wrong is not settled here.",
}

for i in uniq:
    i["cause"] = classify(i)

# collapse rows that share a pivot person AND a cause
groups = {}
for i in uniq:
    groups.setdefault((i["id"], i["cause"]), []).append(i)

causes = []
for (pid, cause), rows in groups.items():
    rows.sort(key=lambda r: r["sev"])
    causes.append({
        "id": pid, "name": rows[0]["name"], "slug": rows[0]["slug"],
        "cause": cause, "sev": rows[0]["sev"], "note": CAUSE_NOTE[cause],
        "kinds": sorted({r["kind"] for r in rows}),
        "rows": [r["msg"] for r in rows],
        "n": len(rows),
    })
causes.sort(key=lambda c: (c["sev"], c["cause"], c["name"]))

by_cause = collections.Counter(c["cause"] for c in causes)
print(f"{len(uniq)} rows collapse to {len(causes)} distinct causes")
for k in ("record", "namesake", "generation", "sex", "hedged"):
    n = by_cause.get(k, 0)
    rows = sum(c["n"] for c in causes if c["cause"] == k)
    print(f"  {k:<11} {n:3d} causes  ({rows} rows)")
print()

cout = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "site", "src", "data", "impossible.json")
json.dump(causes, open(cout, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {os.path.relpath(cout)}")

by_sev = collections.Counter(i["sev"] for i in uniq)
print(f"{sum(1 for x in people if relevant(x))} people in scope; {len(uniq)} internal contradictions")
for s in (1, 2, 3):
    print(f"  {order[s]:<14} {by_sev.get(s, 0)}")
print()
for s in (1, 2, 3):
    rows = [i for i in uniq if i["sev"] == s]
    if not rows:
        continue
    print(f"=== {order[s]} ({len(rows)}) ===")
    for i in rows[:40]:
        print(f"  [{i['kind']}] {i['name'][:36]:<36} {i['msg'][:78]}")
    if len(rows) > 40:
        print(f"  … and {len(rows) - 40} more")
    print()

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "site", "src", "data", "consistency.json")
json.dump(uniq, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {os.path.relpath(out)}")
