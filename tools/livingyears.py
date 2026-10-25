#!/usr/bin/env python3
"""THE LIVING WINDOW, enforced on EVERY page and EVERY data file (25 October 2026).

THE RULE (David, 16 October 2026): somebody born within the last 80 years with no death recorded is living,
and is named with relationships and town/country only: no date, no year, no record, no photograph. This
gate asks one question of the whole build, and of the data it is built from:

    does anything printed, on any page or in any file the site serves, give a birth year or date inside
    the window (CUT .. this year) for somebody who has not died?

CUT is never written down as a number here: it is `livingset.cutoff_year()` (this year minus the kit's
LIVING_YEARS), the one place the edge is computed, shared with the generators.

WHY THIS GATE EXISTS. On 25 October 2026 a sweep found a living person's year on one page, a living
person's birth year and town on five pages, a full birth date with hospital and parents and a newspaper
record of somebody the tree does not hold, a stone row with no death, and a flagged-living person's
relatives printing their years. The older gate (livingcheck.py) could not see any of it:

  * It started from the PERSON: a living page's own rules, and the full dates of the people the tree
    judges living. A year alone is not a date; hand-written prose, derived data and lists were never
    its business; and somebody who is not in the tree at all (a newspaper's birth notice, a stone
    survey, a naturalisation household) has no id to check anybody against.
  * Its test of who is living was the kit's `living_rule.is_living`, which returns False for anybody
    carrying a citation from a PUBLIC source (FamilySearch, a passenger index) whatever their birth year.
    A source can show that somebody was born or arrived; it cannot show that they are dead. The same
    hole was found in the Mazza archive the same day. livingset.cites_for_living closes it (a dated
    person is judged by year and death alone); RULE below pins it with planted cases. KIT GAP: the
    exemption belongs in kit/tools/living_rule.py and kit/lib/person.js, not in each archive.

So nothing here starts from a person's flag. It starts from what is PRINTED.

THE RULES (each is a name in the output and in --selftest):

  ROW-BIRTH   a data row (any JSON under site/src/data, site/public or the build) with a birth year in the
              window and no death field, no death event and no recorded death for the same slug elsewhere.
  ROW-OPEN    a string such as «<year>–?» or «(<year>–)»: a window year opening a range that never closes.
  TXT-BDOT    «b. <year>», «b. <day> <month> <year>»: a window year after the abbreviation, no death beside it.
  TXT-BORN    «born in <year>», «born at <town> in <year>», «born in <country> after <month> <year>»: the
              word born, up to three plain words, an optional month and a window year; no death beside it.
  MEDIA       a photograph tagged with somebody who is living (or held out); a file the withheld list
              names that is still in site/public or in the build.
  HOLD        a row of data/living-hold.tsv for somebody with a dated death, or outside the window.
  PUBDEATH    (needs the tree) a person in the window whose only death is a bare FLAG (a DEAT event that is only «Y»)
              published AS DEAD, who is neither held (data/living-hold.tsv) nor decided (data/living-year-allow.tsv).
              The kit's rule (341af33) keeps such a person living, so none should be found.
  RULE        the living rule itself, on a synthetic tree: the Mazza case (a dated person with a public
              source is living), the edge year, a recorded death, the hold. Generator and gate must agree.
  EMPTY       a build with nothing to check does not pass.

  and, only when the tree (sources/*.ged) is present:

  TREE-NAME   the name of somebody in the window with no death, followed or preceded closely by their own
              birth year.
  TREE-GIVEN  a given name directly followed by the birth year of somebody in the window («<name> in <year>»,
              «<name> <year>»): lists and eulogies name children by their first name alone.
  TREE-DATE   their full birth date (all spellings) beside their name.

DECISIONS. data/living-year-allow.tsv: `id|year|near|why`. A hit is allowed when its year is the row's year and
one of its `near` tokens (separated by ;) is within 150 characters of it. A row is a decision, with a reason;
it is how a typo in the tree (a birth year the archive's own pages call impossible) is kept out of the gate
without being hidden. No living person's name belongs in it.

Usage:  python3 tools/livingyears.py [--dist DIR] [--selftest] [--no-tree] [--quiet] [--list]
"""
import argparse
import collections
import copy
import html as htmllib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
PUBLIC = os.path.join(ROOT, "site", "public")
sys.path.insert(0, HERE)
import livingset  # noqa: E402
lr = livingset.lr

CUT = livingset.cutoff_year()
TODAY = lr.this_year()
YR = r"((?:19|20)\d\d)"
MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
BDOT = re.compile(r"(?<![A-Za-z])b\.\s*(?:\d{1,2}\s+(?:%s)\s+|(?:%s)\s+)?%s(?!\d)" % (MON, MON, YR), re.I)
BORN = re.compile(r"\bborn\b(?:[ \t]+(?:in|on|at|about|around|circa|c\.|after|before|by|near))?(?:[ \t]+[^\W\d_]+){0,3}?[ \t]+"
                  r"(?:(?:\d{1,2}[ \t]+)?(?:%s)[ \t]+)?%s(?!\d)" % (MON, YR), re.I)
OPEN = re.compile(r"(?<![\d\u2013\-/.])%s(?:[\u2013\-](?:\?|\)|$)|[ \t]\u2013[ \t]?(?:\?|\)))" % YR)
DEATH_BESIDE = re.compile(r"(\bd\.|\bdied\b|\bdeath\b|\bdead\b|†|\bburied\b|\bfuneral\b|\bwidow)", re.I)
DASH_YEAR = re.compile(r"^[^A-Za-z0-9]{0,12}[–\-]\s*(?:19|20)\d\d")
NO_BORN_LABEL = ("people/", "who/")          # generated person and name pages carry a Born label row (see TXT-BORN)
BIRTH_KEYS = ("born", "byear", "birth", "birthYear", "bornYear")
DEATH_KEYS = ("died", "dyear", "death", "diedYear", "deathYear", "buried", "burial", "diedPlace")
SERVED = (".json", ".xml", ".txt")
ALLOW = os.path.join(ROOT, "data", "living-year-allow.tsv")
WITHHELD = os.path.join(ROOT, "sources", "media", "withheld.psv")
TAGS = re.compile(r"<[^>]+>")


_MARKS = re.compile("[\u0300-\u036f]+")


def fold(s):
    s = unicodedata.normalize("NFD", str(s or "").lower().replace("\u0111", "d"))
    return re.sub(r"[^a-z0-9]+", " ", _MARKS.sub("", s)).strip()


def window(y):
    return isinstance(y, int) and CUT <= y <= TODAY


def year_of(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        m = re.match(r"^\s*(?:ABT |FROM |BEF |AFT |c\.\s?)?(?:\d{1,2} [A-Za-z]{3,9} )?((?:1[5-9]|20)\d\d)\b", v)
        return int(m.group(1)) if m else None
    return None


def page_text(h):
    h = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", h)
    return re.sub(r"\s+", " ", htmllib.unescape(TAGS.sub(" ", h)))


def strings_in(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings_in(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings_in(v)


def allowances():
    """[(id, year, near-tokens, why)] from data/living-year-allow.tsv."""
    out = []
    if os.path.exists(ALLOW):
        for line in open(ALLOW, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 3:
                continue
            f = [x.strip() for x in line.rstrip("\n").split("|")]
            try:
                out.append((f[0], int(f[1]), [fold(t) for t in f[2].split(";") if t.strip()], f[3]))
            except ValueError:
                pass
    return out


# ---- the world ---------------------------------------------------------------

def load_world(dist):
    """pages {rel: text}, json {where: parsed}, extra {rel: text}: the built site and the data it is built from."""
    w = {"pages": {}, "json": {}, "extra": {}, "dist": dist, "sitemap": ""}
    for root, _, files in os.walk(dist):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, dist).replace(os.sep, "/")
            try:
                if f.endswith(".html"):
                    w["pages"][rel] = open(p, encoding="utf-8", errors="replace").read()
                elif f.endswith(".json"):
                    w["json"]["dist:" + rel] = json.load(open(p, encoding="utf-8"))
                elif f.endswith(SERVED):
                    w["extra"][rel] = open(p, encoding="utf-8", errors="replace").read()
            except (OSError, ValueError):
                pass
    for d, tag in ((DATA, "data:"), (PUBLIC, "public:")):
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith(".json") and f != "atlas-data.json":
                try:
                    w["json"][tag + f] = json.load(open(os.path.join(d, f), encoding="utf-8"))
                except ValueError:
                    pass
    sm = os.path.join(dist, "sitemap.xml")
    w["sitemap"] = open(sm, encoding="utf-8").read() if os.path.exists(sm) else ""
    return w


def clone(w):
    w2 = dict(w)
    for k in ("pages", "json", "extra"):
        w2[k] = dict(w[k])
    return w2


# ---- rules -------------------------------------------------------------------

def dead_slugs(w):
    """Slugs the published data records as dead: a death field or a death or burial event."""
    out = set()
    for key in ("data:people.json", "data:ancestors.json"):
        for r in w["json"].get(key, []) or []:
            if isinstance(r, dict) and r.get("slug") and row_has_death(r):
                out.add(r["slug"])
    return out


def row_has_death(r):
    if any(r.get(k) not in (None, "", [], {}, False) for k in DEATH_KEYS) or r.get("deathRecorded") is True:
        return True
    return any(isinstance(e, dict) and e.get("kind") in ("death", "burial") for e in (r.get("events") or []))


def rows_in(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from rows_in(v)
    elif isinstance(o, list):
        for v in o:
            yield from rows_in(v)


def allowed_here(text, pos, year, allow, ident=None):
    seg = fold(text[max(0, pos - 150): pos + 150])
    for i, y, near, _ in allow:
        if y == year and (ident is not None and i == ident or any(t in seg for t in near)):
            return True
    return False


def rule_rows(w, allow):
    out = []
    dead = dead_slugs(w)
    allow_ids = {i for i, _, _, _ in allow}
    for where, doc in w["json"].items():
        for r in rows_in(doc):
            b = next((year_of(r[k]) for k in BIRTH_KEYS if k in r and year_of(r[k])), None)
            if not window(b) or row_has_death(r):
                continue
            ident = r.get("id") if isinstance(r.get("id"), str) else None
            if (r.get("slug") in dead) or (ident in allow_ids):
                continue
            who = r.get("slug") or ident or r.get("name") or r.get("given") or "?"
            out.append(("ROW-BIRTH", f"{where} [{who}]", "a birth year in the window and no death in the row"))
    return out


def dead_in_window(w):
    """[(folded name, birth year)] for every published row of somebody born inside the window whose data records a death
    (a death year, a death place, a death event, the kit's deathRecorded). Their birth year may be printed beside their own
    name even when the death has no date (26 October 2026: a death confirmed by the family has a place and no date, so the
    page reads «1953–?» and the relatives' chips «b. 1953», and no death word follows the year)."""
    out = set()
    for doc in w["json"].values():
        for r in rows_in(doc):
            if not isinstance(r, dict):
                continue
            nm = fold(r.get("name") or "")
            b = next((year_of(r[k]) for k in BIRTH_KEYS if k in r and year_of(r[k])), None)
            if len(nm) >= 7 and " " in nm and window(b) and (row_has_death(r) or r.get("deathRecorded") is True):
                out.add((nm, b))
    return sorted(out)


def scan_text(where, text, allow, born_label_ok=False, deadwin=()):
    """TXT-BDOT, TXT-BORN, ROW-OPEN over one text. `deadwin` is dead_in_window(): a window year directly after the
    NAME of a person whose data records a death, and equal to that person's birth year, is not a living person's year."""
    out = []

    def skip(m, tail_len=70, check_death=True):
        y = int(m.group(1))
        if not window(y):
            return True
        if deadwin:
            before = fold(text[max(0, m.start() - 70): m.start()])
            if any(by == y and nm in before for nm, by in deadwin):
                return True
        if check_death:
            tail = text[m.end(): m.end() + tail_len]
            if DEATH_BESIDE.search(tail) or DASH_YEAR.match(tail):
                return True
        return allowed_here(text, m.start(), y, allow)

    for m in BDOT.finditer(text):
        if not skip(m):
            out.append(("TXT-BDOT", where, "«%s»" % text[max(0, m.start() - 25): m.end() + 10].strip()))
    if not born_label_ok:
        for m in BORN.finditer(text):
            if not skip(m):
                out.append(("TXT-BORN", where, "«%s»" % text[max(0, m.start() - 15): m.end() + 10].strip()))
    for m in OPEN.finditer(text):
        if not skip(m, check_death=False):
            out.append(("ROW-OPEN", where, "«%s»" % text[max(0, m.start() - 25): m.end() + 5].strip()))
    return out


def corpus(w):
    """{where: (text, born_label_ok)}: every page (visible text), every JSON string, every other served text."""
    c = {}
    for rel, h in w["pages"].items():
        c["dist:" + rel] = (page_text(h), rel.startswith(NO_BORN_LABEL))
    for where, doc in w["json"].items():
        c[where] = ("\n".join(strings_in(doc)), False)
    for rel, t in w["extra"].items():
        if rel != "sitemap.xml":
            c["dist:" + rel] = (t, False)
    return c


def rule_text(w, allow, corp=None):
    out = []
    dw = dead_in_window(w)
    for where, (text, label_ok) in (corp or corpus(w)).items():
        out += scan_text(where, text, allow, label_ok, dw)
    return out


def withheld_ids():
    out = {}
    if os.path.exists(WITHHELD):
        for line in open(WITHHELD, encoding="utf-8"):
            if line.strip() and not line.startswith("#") and "|" in line:
                f = [x.strip() for x in line.rstrip("\n").split("|")]
                out[f[0]] = f[1] if len(f) > 1 else ""
    return out


def rule_media(w, living_slugs=None, files=None):
    out = []
    media = w["json"].get("data:media.json") or []
    living = living_slugs if living_slugs is not None else {
        r["slug"] for r in (w["json"].get("data:living.json") or []) if isinstance(r, dict)}
    wh = withheld_ids()
    for it in media:
        for t in it.get("people", []):
            if t.get("slug") in living or t.get("living"):
                out.append(("MEDIA", it.get("mid"), "a photograph tagged with somebody who is living"))
        if it.get("mid") in wh:
            out.append(("MEDIA", it.get("mid"), "a withheld photograph is in media.json"))
    # a withheld id's file anywhere under the photo directories
    names = files if files is not None else {os.path.basename(p) for p in _all_files()}
    for fn in names:
        if any(m in fn or m[1:] in fn for m in wh):
            out.append(("MEDIA", fn, "the file of a withheld photograph is in site/public"))
    return out


def _all_files():
    out = []
    base = os.path.join(PUBLIC, "photos")
    for dp, _, fs in os.walk(base):
        out += [os.path.join(dp, f) for f in fs]
    return out


def rule_dist_files(w):
    out = []
    wh = withheld_ids()
    for dp, _, fs in os.walk(w["dist"]):
        for f in fs:
            if any(m in f or m[1:] in f for m in wh):
                out.append(("MEDIA", f, "the file of a withheld photograph is in the build"))
    return out


def rule_hold(people=None):
    """HOLD: every row of data/living-hold.tsv names somebody in the window with no dated death."""
    out = []
    holds = livingset.hold_ids()
    if people is None:
        return out
    for i in holds:
        p = people.get(i)
        if p is None:
            out.append(("HOLD", i, "a hold on somebody who is not in the tree"))
            continue
        b = livingset.birth_year(p)
        if b is None or not window(b):
            out.append(("HOLD", i, "a hold on somebody outside the window"))
        if livingset.dated_death(p):
            out.append(("HOLD", i, "a hold on somebody with a dated death or burial"))
    return out


def rule_empty(w):
    out = []
    if len(w["pages"]) < 50:
        out.append(("EMPTY", w["dist"], f"only {len(w['pages'])} page(s) built"))
    if not w["json"].get("data:people.json"):
        out.append(("EMPTY", "people.json", "no published people to check"))
    if not w["json"].get("data:living.json"):
        out.append(("EMPTY", "living.json", "no living person: an empty list is a broken harvest, not a pass"))
    return out


# ---- the rule, pinned --------------------------------------------------------

def independent_status(people, tuned=True):
    """(living, held) from the KIT's living_rule.py, written out again here and not taken from the generator.
    A dated person is judged by year and death alone: no citation is passed for them. `tuned=False` is the
    behaviour before 25 October 2026 (every citation passed), kept so the gate can SHOW it differs."""
    ty = lr.this_year()
    extra, _ = livingset.extra_dead(people)
    holds = livingset.hold_ids()

    def dkind(p):
        # the kit's own classifier, called here again and not taken from the generator: a burial, a date, a place,
        # a cause or a note on a death is a RECORD; a death that is only «Y» is a bare FLAG (kit 341af33)
        ks = []
        for e in p["events"]:
            if e["kind"] == "burial":
                ks.append("record")
            elif e["kind"] == "death":
                more = any(e.get(k) for k in ("cause", "note", "agency", "type"))
                ks.append(lr.death_kind(died=e.get("date", ""), death_place=e.get("place", ""), dead_flag=True,
                                        death_recorded=more))
        return "record" if "record" in ks else ("flag" if ks else None)

    def dead(i, p):
        return (dkind(p) == "record" and i not in holds) or i in extra

    def flag(i, p):
        return dkind(p) == "flag" and i not in holds and i not in extra

    def by(p):
        ev = lambda k: next((e for e in p["events"] if e["kind"] == k), None)
        m = re.search(r"\b(\d{4})\b", (ev("birth") or ev("christening") or ev("baptism") or {}).get("date", "") or "")
        return int(m.group(1)) if m else None
    cites = (lambda p: () if by(p) is not None else p.get("cites", ())) if tuned else (lambda p: p.get("cites", ()))
    living = {i for i, p in people.items() if lr.is_living(by(p), dead(i, p), cites(p), ty, undated_dead=flag(i, p))}
    # POSSIBLE MINORS (David, 25 October 2026), written out again here and not taken from livingset.minor_ids: no death
    # record, and born this year minus 18 or later, or undated (no bare death flag) with a parent born in 1975 or later.
    # They are living and are held out (published nowhere); the kit's is_held_out is given them as held_ids.
    minors = set()
    for i, p in people.items():
        if dead(i, p):
            continue
        b = by(p)
        if b is not None:
            if b >= ty - 18:
                minors.add(i)
        elif dkind(p) != "flag" and any((by(people[q]) or 0) >= 1975 for q in p.get("parents", []) if q in people):
            minors.add(i)
    held = {i for i, p in people.items() if (i not in living or i in minors) and lr.is_held_out(
        i, by(p), dkind(p) == "record" or i in extra, p.get("cites", ()),
        any(par in living for par in p.get("parents", [])), minors, ty,
        undated_dead=dkind(p) == "flag" and i not in extra)}
    return living, held


def synthetic_tree():
    Y = TODAY

    def person(i, born=None, events=(), parents=(), cites=(), death_date=None):
        ev = [{"kind": k, "date": "", "place": "", "detail": "Y", "note": "", "agency": "", "type": "",
               "cause": "", "tag": k.upper()} for k in events]
        if death_date is not None:
            ev.append({"kind": "death", "date": death_date, "place": "", "detail": "Y", "note": "", "agency": "",
                       "type": "", "cause": "", "tag": "DEAT"})
        if born is not None:
            ev.insert(0, {"kind": "birth", "date": f"1 JAN {born}", "place": "", "detail": "", "note": "",
                          "agency": "", "type": "", "cause": "", "tag": "BIRT"})
        return {"id": i, "name": "Zzplant Zzperson", "given": "Zzplant", "surname": "Zzperson", "nick": "",
                "events": ev, "notes": [], "sources": [], "cites": list(cites), "famc": [], "fams": [],
                "parents": list(parents), "sex": "", "alt_names": [], "uid": "", "mh": i}
    pub = ["FamilySearch Family Tree", "recordsearch.naa.gov.au passenger index"]
    return {
        "@IZ1@": person("@IZ1@", born=Y - 78, cites=pub),                 # THE MAZZA CASE: 78, no death, public sources
        "@IZ2@": person("@IZ2@", born=Y - 78, cites=pub, death_date="2 FEB %d" % (Y - 3)),  # the same, with a death recorded: dead
        "@IZ3@": person("@IZ3@", born=Y - 80),                            # the edge: 80 by year is living
        "@IZ4@": person("@IZ4@", born=Y - 81),                            # 81 is not
        "@IZ5@": person("@IZ5@", born=Y - 40),                            # an adult with nothing recorded
        "@IZ6@": person("@IZ6@", parents=["@IZ5@"], cites=["FamilySearch"]),  # undated, public source, parent born Y-40: HELD (possible minor, 25 Oct 2026)
        "@IZL@": person("@IZL@", born=1950, events=["burial"]),            # a parent born 1950, dead
        "@IZM@": person("@IZM@", parents=["@IZL@"], cites=["FamilySearch"]),  # undated, public source, old parent: neither
        "@IZ7@": person("@IZ7@", parents=["@IZ5@"]),                      # undated, living parent: held out
        "@IZ8@": person("@IZ8@", born=Y - 60, events=["death"]),          # a bare death FLAG, born in the window: LIVING (kit 341af33)
        "@IZ9@": person("@IZ9@", born=CUT - 1),                           # one year outside the window
        "@IZA@": person("@IZA@", born=CUT - 1, events=["death"]),         # a bare flag, born one year outside: dead
        "@IZB@": person("@IZB@", events=["death"]),                       # a bare flag and no birth year: dead
        # POSSIBLE MINORS (25 October 2026)
        "@IZC@": person("@IZC@", born=Y - 10, parents=["@IZ5@"]),         # a child with a birth year: living AND held out
        "@IZD@": person("@IZD@", born=Y - 18),                            # the edge: this year minus 18 is a possible minor
        "@IZE@": person("@IZE@", born=Y - 19),                            # one year older: an adult, not held
        "@IZF@": person("@IZF@", born=Y - 3, events=["burial"]),          # a child who has died: not living, not held
        "@IZG@": person("@IZG@", born=1976, death_date="3 MAR 2001"),     # a parent born in 1976, dead
        "@IZH@": person("@IZH@", parents=["@IZG@"]),                      # undated, parent born 1976 though dead: held (no living parent for the kit)
        "@IZI@": person("@IZI@", born=1974, death_date="3 MAR 2001"),     # a parent born in 1974, dead
        "@IZJ@": person("@IZJ@", parents=["@IZI@"]),                      # undated, parent born 1974, dead: not held
        "@IZK@": person("@IZK@", events=["death"], parents=["@IZ5@"]),    # undated, bare flag, parent born 1986: dead, not held
    }


def selftest_rule():
    """The rule, through the generator's classify AND this gate's independent_status, on a tree no real person can
    be. The two must agree on every case. The gate's own old behaviour (`tuned=False`) is run too, to show the
    public-source case is exactly where it differs: a gate that cannot tell the two apart proves nothing."""
    P = synthetic_tree()
    gen = livingset.classify(P, {})
    g_l, g_h = gen["living"], gen["held"]
    k_l, k_h = independent_status(P)
    old_l, _ = independent_status(P, tuned=False)
    want = {
        "a dated person, 78, no death, public sources, IS living (the Mazza case)": ("@IZ1@" in g_l, "@IZ1@" in k_l),
        "the same with a death recorded is not living": ("@IZ2@" not in g_l, "@IZ2@" not in k_l),
        "80 by year is living (the edge)": ("@IZ3@" in g_l, "@IZ3@" in k_l),
        "81 by year is not living": ("@IZ4@" not in g_l, "@IZ4@" not in k_l),
        "an adult with nothing recorded is living": ("@IZ5@" in g_l, "@IZ5@" in k_l),
        "undated with a public source and an old parent is neither living nor held": ("@IZM@" not in g_l and "@IZM@" not in g_h,
                                                                                      "@IZM@" not in k_l and "@IZM@" not in k_h),
        "undated with a public source but a parent born 1975 or later IS held out": ("@IZ6@" in g_h, "@IZ6@" in k_h),
        "undated with a living parent is held out": ("@IZ7@" in g_h, "@IZ7@" in k_h),
        "a bare death flag does NOT make somebody born inside the window dead": ("@IZ8@" in g_l, "@IZ8@" in k_l),
        "a bare flag one year outside the window is a death": ("@IZA@" not in g_l, "@IZA@" not in k_l),
        "a bare flag and no birth year is a death": ("@IZB@" not in g_l and "@IZB@" not in g_h,
                                                     "@IZB@" not in k_l and "@IZB@" not in k_h),
        "one year outside the window is not living": ("@IZ9@" not in g_l, "@IZ9@" not in k_l),
        "a child with a birth year is living AND held out (possible minor)": ("@IZC@" in g_l and "@IZC@" in g_h,
                                                                              "@IZC@" in k_l and "@IZC@" in k_h),
        "born this year minus 18 is a possible minor": ("@IZD@" in g_h, "@IZD@" in k_h),
        "born this year minus 19 is not": ("@IZE@" not in g_h, "@IZE@" not in k_h),
        "a child who has died is neither living nor held out": ("@IZF@" not in g_l and "@IZF@" not in g_h,
                                                                "@IZF@" not in k_l and "@IZF@" not in k_h),
        "undated with a parent born in 1975 or later is held out even when that parent has died":
            ("@IZH@" in g_h, "@IZH@" in k_h),
        "undated with a parent born in 1974 and dead is not held out": ("@IZJ@" not in g_h, "@IZJ@" not in k_h),
        "undated with a bare death flag is dead, not a minor": ("@IZK@" not in g_h and "@IZK@" not in g_l,
                                                                "@IZK@" not in k_h and "@IZK@" not in k_l),
        "the cutoff is derived, not typed": (livingset.cutoff_year() == TODAY - lr.LIVING_YEARS,
                                             livingset.cutoff_year(TODAY + 1) == TODAY + 1 - lr.LIVING_YEARS),
    }
    res = {f"{k} (generator, gate)": a and b for k, (a, b) in want.items()}
    # Before kit 341af33 this control showed that the kit's rule, given every citation, called the Mazza case NOT living,
    # so the archive withheld the citations itself. The kit does it now: the two answers AGREE, and the control pins that.
    res["the kit's rule alone, given every citation, now also keeps the Mazza case living (kit 341af33): the control agrees"] = "@IZ1@" in old_l
    # a hold: the generator must refuse a hold on somebody with a dated death
    return res


# ---- the tree (local builds) ---------------------------------------------------

def ged_available():
    d = os.path.join(ROOT, "sources")
    return os.path.isdir(d) and any(f.endswith(".ged") for f in os.listdir(d))


class Tree:
    def __init__(self):
        import gedcom
        self.gedcom = gedcom
        self.people, self.families = gedcom.load()
        living, held = independent_status(self.people)
        self.living, self.held = living, held
        holds = livingset.hold_ids()
        self.window = {}
        for i in living:
            b = livingset.birth_year(self.people[i])
            if window(b):
                self.window[i] = b
        self.names = {}
        for i, b in self.window.items():
            p = self.people[i]
            g, s, k = fold(p["given"]), fold(p["surname"]), fold(p["nick"])
            ph = set()
            if g and s:
                ph.add(g + " " + s)
                ph.add(g.split()[0] + " " + s.split()[-1])
                if k:
                    ph.add(k + " " + s.split()[-1])
            self.names[i] = {x for x in ph if len(x) >= 7}
        self.given = collections.defaultdict(set)
        for i, b in self.window.items():
            p = self.people[i]
            for nm in (p["given"], p["nick"]):
                t = fold(nm).split()
                if t and len(t[0]) >= 3:
                    self.given[t[0]].add(b)
        self.by_year = collections.defaultdict(list)
        for i, b in self.window.items():
            self.by_year[b].append(i)
        self.dates = {}
        for i in self.window:
            b = next((e for e in self.people[i]["events"] if e["kind"] == "birth"), None)
            for f in date_forms((b or {}).get("date", "")):
                self.dates.setdefault(f, set()).add(i)
        self.holds = holds

    def hits(self, where, text, allow):
        out = []
        ft = fold(text)
        years = {int(m) for m in re.findall(r"(?<!\d)((?:19|20)\d\d)(?!\d)", ft) if window(int(m))}
        if not years:
            return out
        # TREE-NAME: a name with the person's own year close by (only persons whose year the text contains)
        named = False
        for y in sorted(years):
            for i in self.by_year.get(y, ()):
                for ph in self.names.get(i, ()):
                    start = 0
                    while not named:
                        k = ft.find(ph, start)
                        if k < 0:
                            break
                        seg = ft[max(0, k - 20): k + len(ph) + 45]
                        if re.search(r"\b%d\b" % y, seg) and not allowed_fold(seg, y, allow):
                            out.append(("TREE-NAME", where, "a name and that person's own birth year, close together (tree id %s)%s"
                                    % (i, EXPLAIN(seg))))
                            named = True
                        start = k + len(ph)
                    if named:
                        break
                if named:
                    break
            if named:
                break
        # TREE-GIVEN: a given name, a few filler words, the year
        for m in re.finditer(r"(?<!\d)%s(?!\d)" % YR, ft):
            y = int(m.group(1))
            if y not in years:
                continue
            toks = ft[max(0, m.start() - 40): m.start()].split()[-4:]
            cands = []
            if toks:
                cands.append(toks[-1])
            if len(toks) > 1 and toks[-1] in ("in", "b", "born", "was", "aged"):
                cands.append(toks[-2])
            if len(toks) > 2 and toks[-1] in ("in", "born") and toks[-2] in ("b", "was", "born"):
                cands.append(toks[-3])
            if any(c in self.given and y in self.given[c] for c in cands):
                seg = ft[max(0, m.start() - 150): m.end() + 150]
                if not allowed_fold(seg, y, allow):
                    out.append(("TREE-GIVEN", where, "a first name directly followed by that person's birth year%s"
                                % EXPLAIN(seg)))
                    break
        # TREE-DATE: the full date, beside the name
        low = text.lower().replace("\u00a0", " ")
        for form, ids in self.dates.items():
            fy = int(re.search(r"\d{4}", form).group(0))
            if str(fy) in ft and (form in low or fold(form) in ft):
                # a decision in data/living-year-allow.tsv (a typo in the tree) allows its own year beside its own token
                k = ft.find(fold(form))
                seg = ft[max(0, k - 150): k + len(form) + 150] if k >= 0 else ft
                if allowed_fold(seg, fy, allow):
                    continue
                for i in ids:
                    if any(ph in ft for ph in self.names.get(i, ())):
                        out.append(("TREE-DATE", where, "a full birth date beside the person's name"))
                        break
        return out

    def pubdeath(self, w, allow):
        """PUBDEATH: published people in the window whose only death is an undated flag."""
        out = []
        allow_ids = {i for i, _, _, _ in allow}
        inv = {}
        for key in ("data:people.json", "data:ancestors.json"):
            for r in w["json"].get(key, []) or []:
                if r.get("id"):
                    inv[r["id"]] = r
        extra, _ = livingset.extra_dead(self.people)
        for i, r in inv.items():
            p = self.people.get(i)
            if not p:
                continue
            b = livingset.birth_year(p)
            if not window(b):
                continue
            if livingset.death_evidence(p) == "flag" \
                    and i not in extra and i not in self.holds and i not in allow_ids:
                out.append(("PUBDEATH", r.get("slug", i), "in the window, published AS DEAD, and the only death is a bare flag "
                            "(the kit's rule keeps them living: a page of the living form, no year)"))
        return out


EXPLAINING = False


def EXPLAIN(seg):
    """Only with --explain, and only on a local run (the tree layers need the GEDCOM): the text, so it can be fixed.
    Never printed by default: a CI log is public and the text may name somebody."""
    return " \u2014 «%s»" % seg[:140] if EXPLAINING else ""


def allowed_fold(seg, year, allow):
    return any(y == year and any(t in seg for t in near) for _, y, near, _ in allow)


def date_forms(d):
    m = re.match(r"\s*(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})", d or "")
    mons = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    longm = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
             "november", "december"]
    if not m or m.group(2).lower() not in mons:
        return set()
    dd, mm, yy = int(m.group(1)), mons.index(m.group(2).lower()), m.group(3)
    return {f"{dd} {longm[mm]} {yy}", f"{dd} {mons[mm]} {yy}", f"{yy}-{mm + 1:02d}-{dd:02d}", f"{dd}/{mm + 1}/{yy}"}


def tree_corpus(w, corp):
    """Everything the tree layers read: the built text, plus every tracked text file (the repository is public)."""
    c = {k: v[0] for k, v in corp.items()}
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True, timeout=60)
        files = [x for x in r.stdout.split("\0") if x] if r.returncode == 0 else []
    except Exception:
        files = []
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".zip")) \
                or f.endswith("package-lock.json") or f.startswith("site/src/data/") or f == "site/public/searchindex.json":
            continue
        try:
            c["tracked:" + f] = open(os.path.join(ROOT, f), encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            pass
    return c


# ---- run ---------------------------------------------------------------------

def run_rules(w, allow, tree=None, corp=None, tcorp=None):
    out = rule_empty(w)
    if out:
        return out
    out += rule_rows(w, allow)
    out += rule_text(w, allow, corp)
    out += rule_media(w)
    out += rule_dist_files(w)
    if tree is not None:
        out += rule_hold(tree.people)
        out += tree.pubdeath(w, allow)
        for where, text in (tcorp or tree_corpus(w, corp or corpus(w))).items():
            out += tree.hits(where, text, allow)
    return out


def report(findings, w, tree, quiet, list_all=False):
    if findings:
        print(f"  FAIL  living-years   {len(findings)} finding(s)  (window {CUT}..{TODAY})")
        seen = collections.Counter()
        for rule, where, what in findings:
            seen[rule] += 1
            if list_all or seen[rule] <= 4:
                print(f"          {rule:<10} {where} — {what}")
                if where.endswith("searchindex.json"):
                    print("                     (the search index is built from the pages: after a build run "
                          "python3 tools/searchindex.py and commit site/public/searchindex.json)")
        for rule, n in seen.items():
            if n > 4 and not list_all:
                print(f"          {rule:<10} … and {n - 4} more")
        return 1
    if not quiet:
        print(f"  ok    living-years   no birth year in {CUT}..{TODAY} is printed for anybody without a death: "
              f"{len(w['pages'])} pages, {len(w['json'])} data files"
              + (f"; tree checked ({len(tree.window)} people in the window)" if tree else
                 "; the tree layers (TREE-NAME, TREE-GIVEN, TREE-DATE, PUBDEATH, HOLD) did not run: no sources/*.ged here"))
    return 0


# ---- the controls ------------------------------------------------------------

def selftest(w, allow, tree, findings, quiet=False):
    """PLANT A FAULT FOR EVERY RULE and show it is caught; show the real build is clean; show the controls
    (a dead person's range, a registered decision, a Born label) pass. Every planted person is synthetic and the
    planted year is derived from the cutoff (CUT + 3), never typed."""
    ok = True
    y_in = CUT + 3
    y_out = CUT - 1
    base = findings
    print(f"  control   the real build: {len(base)} finding(s)  [expect 0]")
    ok &= not base

    def planted_page(frag):
        def go(w2, c2):
            rel = "zz-planted/index.html"
            w2["pages"][rel] = f"<html><head></head><body><main>{frag}</main></body></html>"
            c2["dist:" + rel] = (page_text(w2["pages"][rel]), False)
        return go

    def planted_json(doc):
        def go(w2, c2):
            w2["json"]["data:zz-planted.json"] = doc
            c2["data:zz-planted.json"] = ("\n".join(strings_in(doc)), False)
        return go

    # A planted fault is checked against the PLANTED entry and the small context documents the rules read (the
    # published people, the living rows, the media list), never against the whole build again: the real build is
    # scanned once, above. Seconds, not minutes, in a build chain.
    KEEP = ("data:people.json", "data:ancestors.json", "data:living.json", "data:media.json")

    def minimal():
        return {"pages": {}, "json": {k: w["json"][k] for k in KEEP if k in w["json"]}, "extra": {},
                "dist": w["dist"], "sitemap": ""}

    def findings_of(w2, c2, rule=None):
        if rule == "EMPTY":
            return rule_empty(w2)
        return rule_rows(w2, allow) + rule_text(w2, allow, c2) + rule_media(w2)

    def plant(label, rule, mut):
        w2 = minimal()
        c2 = {}
        mut(w2, c2)
        got = rule in {f[0] for f in findings_of(w2, c2, rule)}
        print(f"  {'caught ' if got else 'MISSED '}   {label}  [{rule}]")
        return got

    res = []
    res.append(plant("«b. YYYY» in the window on a built page", "TXT-BDOT", planted_page(f"<p>Zz Planted (b. {y_in}, Town)</p>")))
    res.append(plant("«b. 21 JUL YYYY» with a day and a month", "TXT-BDOT", planted_page(f"<p>Zz Planted b. 21 JUL {y_in}</p>")))
    res.append(plant("«born in YYYY» in prose", "TXT-BORN", planted_page(f"<p>Her brother was born in {y_in} and lives abroad.</p>")))
    res.append(plant("«born at a town in YYYY»", "TXT-BORN", planted_page(f"<p>Zz was born at Zzville in {y_in}.</p>")))
    res.append(plant("«born in a country after Month YYYY» (an approximate year)", "TXT-BORN",
                     planted_page(f"<p>His son was born in Argentina after October {y_in}; the names collide.</p>")))
    res.append(plant("a full date: «born 21 July YYYY at the hospital»", "TXT-BORN",
                     planted_page(f"<p>A son, Zz, was born 21 July {y_in} at the District Hospital.</p>")))
    res.append(plant("an open range «YYYY–?» on a page", "ROW-OPEN", planted_page(f"<p>Zz Planted {y_in}–? Town</p>")))
    res.append(plant("an open range «(YYYY–)» in a data string", "ROW-OPEN", planted_json({"t": f"Zz Planted ({y_in}–)"})))
    res.append(plant("a data row with a birth year in the window and no death", "ROW-BIRTH",
                     planted_json([{"name": "Zz Planted", "born": y_in, "died": None}])))
    res.append(plant("a stone row: born in the window, no death year", "ROW-BIRTH",
                     planted_json({"stones": [{"surname": "Zz", "given": "Planted", "born": str(y_in), "died": ""}]})))
    res.append(plant("a birth row in a derived list that does not say died", "ROW-BIRTH",
                     planted_json([{"slug": "zz-planted-nobody", "name": "Zz Planted", "byear": y_in}])))
    res.append(plant("a window year in a search-index entry", "TXT-BDOT",
                     lambda w2, c2: c2.__setitem__("dist:zz-searchindex.json",
                                                   (f"zz planted (b. {y_in}, town)", False))))
    res.append(plant("a photograph tagged with a living person", "MEDIA",
                     planted_json([]) if False else (lambda w2, c2: w2["json"].__setitem__(
                         "data:media.json", list(w2["json"]["data:media.json"]) + [
                             {"mid": "9999999", "kind": "photograph",
                              "people": [{"slug": next(iter(r["slug"] for r in w2["json"]["data:living.json"])),
                                          "name": "Zz Planted"}]}]))))
    wh = withheld_ids()
    if wh:
        mid = sorted(wh)[0]
        res.append(plant("a withheld photograph back in media.json", "MEDIA",
                         lambda w2, c2: w2["json"].__setitem__(
                             "data:media.json", list(w2["json"]["data:media.json"]) + [{"mid": mid, "people": []}])))
    if wh:
        mid0 = sorted(wh)[0]
        got = "MEDIA" in {f[0] for f in rule_media(minimal(), files={mid0 + "-planted.jpg", "x-" + mid0[1:] + ".jpg"})}
        print(f"  {'caught ' if got else 'MISSED '}   the file of a withheld photograph left in site/public  [MEDIA]")
        res.append(got)
    res.append(plant("an empty build", "EMPTY", lambda w2, c2: None))
    # controls that must PASS
    def passes(label, mut):
        w2 = minimal()
        c2 = {}
        mut(w2, c2)
        found = findings_of(w2, c2)
        good = not found
        print(f"  {'passes ' if good else 'FAILED '}   {label}  [expect no finding]")
        return good
    res.append(passes("a dead person's range and «b. YYYY d. YYYY» pass", planted_page(
        f"<p>Zz Planted ({y_in}–{y_in + 1}) and Zz Other b. {y_in} d. {y_in + 2}</p>")))
    def dead_undated(w2, c2):
        planted_json([{"name": "Zz Planted", "born": f"23 APR {y_in}", "deathRecorded": True, "diedPlace": "Town"}])(w2, c2)
        planted_page(f"<p>Zz Planted {y_in}–? Town</p><p>Zz Planted b. {y_in}</p>")(w2, c2)
    res.append(passes("a death recorded without a date lets its own name carry its own birth year", dead_undated))
    def not_this_name(w2, c2):
        planted_json([{"name": "Zz Planted", "born": f"23 APR {y_in}", "deathRecorded": True}])(w2, c2)
        planted_page(f"<p>Zz Another b. {y_in}</p>")(w2, c2)
    res.append(plant("the dead person's year beside somebody else's name", "TXT-BDOT", not_this_name))
    res.append(passes("a year just outside the window passes", planted_page(f"<p>Zz was born in {y_out} and b. {y_out}.</p>")))
    res.append(passes("a recorded death in the row passes", planted_json([{"name": "Zz", "born": y_in, "died": y_in + 1}])))
    res.append(passes("a death event in the row passes", planted_json(
        [{"name": "Zz", "born": y_in, "events": [{"kind": "death", "date": ""}]}])))
    res.append(passes("a Born label on a generated person page is the generator's, checked as a row",
                      lambda w2, c2: c2.__setitem__("dist:people/zz/index.html", (f"Born 21 JUL {y_in} Died {y_in + 9}", True))))
    # an allowance is honoured, and only for its own year
    w_allow = [("@IZZ@", y_in, ["zzallowed"], "planted")]
    w2 = minimal()
    c2 = {}
    planted_page(f"<p>Zzallowed (b. {y_in})</p><p>{'x ' * 150}</p><p>Zzother (b. {y_in})</p>")(w2, c2)
    only = rule_text(w2, allow + w_allow, c2)
    # the second name is further than 150 characters from the token and has no allowance: one finding stays
    print(f"  {'passes ' if len(only) == 1 else 'FAILED '}   a registered decision allows its own year beside its own token only  [expect 1 finding]")
    res.append(len(only) == 1)
    # the rule itself
    for k, v in selftest_rule().items():
        print(f"  {'caught ' if v else 'MISSED '}   the rule, on a synthetic tree: {k}")
        res.append(v)
    if tree is not None:
        t = tree
        i0 = next(iter(sorted(t.window)))
        p0 = t.people[i0]
        nm = (p0["given"] + " " + p0["surname"]).strip()
        yb = t.window[i0]
        gname = next(g for g in sorted(t.given) if t.given[g])
        gy = sorted(t.given[gname])[0]

        def tplant(label, rule, text):
            f = t.hits("dist:zz-planted/index.html", text, allow)
            got = rule in {x[0] for x in f}
            print(f"  {'caught ' if got else 'MISSED '}   {label}  [{rule}]")
            return got
        res.append(tplant("a living person's name beside their own birth year", "TREE-NAME", f"{nm} ({yb}, Town)"))
        res.append(tplant("a first name directly followed by that person's year", "TREE-GIVEN", f"{gname.title()} in {gy} and others"))
        d0 = next((i for i in sorted(t.window) if any(date_forms(e.get("date", "")) for e in t.people[i]["events"]
                                                       if e["kind"] == "birth")), None)
        if d0:
            e = next(e for e in t.people[d0]["events"] if e["kind"] == "birth" and date_forms(e.get("date", "")))
            n2 = (t.people[d0]["given"] + " " + t.people[d0]["surname"]).strip()
            res.append(tplant("a living person's full date beside their name", "TREE-DATE", f"{n2} was born {sorted(date_forms(e['date']))[0]}"))
        # a HOLD on somebody with a dated death is refused
        dead_dated = next(i for i, p in t.people.items() if livingset.dated_death(p) and window(livingset.birth_year(p)))
        saved = livingset.hold_ids
        livingset.hold_ids = lambda: {dead_dated: "planted"}
        try:
            got = "HOLD" in {x[0] for x in rule_hold(t.people)}
        finally:
            livingset.hold_ids = saved
        print(f"  {'caught ' if got else 'MISSED '}   a hold on somebody with a dated death  [HOLD]")
        res.append(got)
        # PUBDEATH: an undated-flag death in the window, published, neither held nor decided
        und = next((i for i, p in t.people.items() if window(livingset.birth_year(p)) and
                    livingset.death_evidence(p) == "flag"
                    and i not in t.holds and i not in {a[0] for a in allow}), None)
        if und:
            w3 = clone(w)
            w3["json"]["data:people.json"] = list(w3["json"]["data:people.json"]) + [{"id": und, "slug": "zz-planted", "name": "Zz"}]
            got = "PUBDEATH" in {x[0] for x in t.pubdeath(w3, allow)}
            print(f"  {'caught ' if got else 'MISSED '}   a published person whose only death is an undated flag  [PUBDEATH]")
            res.append(got)
    return ok and all(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-tree", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--list", action="store_true", help="list every finding")
    ap.add_argument("--explain", action="store_true", help="local only: show the text of a TREE-* finding")
    a = ap.parse_args()
    global EXPLAINING
    EXPLAINING = a.explain
    dist = a.dist or os.path.join(ROOT, "site", os.environ.get("ARCHIVE_OUT") or "dist")
    if not os.path.isdir(dist):
        print(f"livingyears: no {dist} — build first")
        return 1
    w = load_world(dist)
    allow = allowances()
    corp = corpus(w)
    tree = Tree() if (ged_available() and not a.no_tree) else None
    tcorp = tree_corpus(w, corp) if tree else None
    findings = run_rules(w, allow, tree, corp, tcorp)
    code = report(findings, w, tree, a.quiet, a.list)
    if a.selftest:
        print("  --selftest")
        good = selftest(w, allow, tree, findings, a.quiet)
        print("  selftest " + ("PASSED: every planted fault was caught" if good else "FAILED"))
        code = code or (0 if good else 1)
    return code


if __name__ == "__main__":
    sys.exit(main())
