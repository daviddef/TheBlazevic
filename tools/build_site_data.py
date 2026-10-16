#!/usr/bin/env python3
"""Turn the parsed GEDCOM into the JSON the site reads.

The living-person rule is applied here, once, at the boundary between the
research data and the published build. Anything that reaches site/src/data is
publishable; anything filtered out here never enters the build at all.

THE RULE, SINCE 16 OCTOBER 2026 (David; the one definition is the kit's
living_rule.py, adapted to this tree in tools/livingset.py):

  * A LIVING PERSON (80 or younger by year, no death or burial recorded, no
    public source) is NAMED, with their relationships and their town and country,
    and nothing more. They are written to living.json as a slug, a name, a town,
    a country and relation lists, and to nothing else: no date, event, record,
    source, note, occupation, cause, burial or photograph is ever read into any
    file under site/src/data, and no tree id is written for them.
  * A recorded death or burial is a death. A person with a citation from a public
    record source is not living. A person with no birth year cannot be shown to be
    80 or younger, so is not living.
  * A POSSIBLE MINOR is held out: not published at all, no page, and not named as
    anyone's relative. So is anyone promised privacy by id (nobody here).
  * EVERY PERSON NAMED HAS A PAGE. A relative who is named on someone's page has a
    page of their own; the relatives of THAT person are named on their page only
    where they already have one, so naming never walks on across the tree.
"""
import json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year, ev
import livingset
from ancestry import ancestors, gen_of, fold, kindred, parents_closure, SURNAMES, ROOT_PERSON

LIVING = {}
HELD = set()      # possible minors (and promised ids): not published at all
def is_living(p): return LIVING.get(p["id"], True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "src", "data")

HEDVIGA = "@I17@"

# The families this archive treats as its own, in the order they matter.
FAMILIES = [
    ("blazevic", "Blažević", "the name the archive carries — out of Smokvica Krmpotska"),
    ("zubrinic", "Žubrinić", "Tereza's people of Otočac, written Xubrinich before it was written Žubrinić"),
    ("papic",    "Papić",    "Milka's people of Senj and Selce, porters and innkeepers"),
    ("prpic",    "Prpić",    "Antonija's people of Krivi Put, Bunjevci of the Senj mountain"),
    # Three of these descriptions were checked against the data on 13 September
    # 2026 and did not survive it. Kalanj was said to have married into the
    # Blazevic line, which is true of exactly one marriage - the connection that
    # actually carries the family is Ana Kalanj of Klenovica 22 marrying Josip de
    # Franceschi, on Hedviga's HUSBAND's side, and that chain is documented.
    # Boras was said to have married into the Senj Blazevici; its marriages are
    # into Papic and Prpic. Vukelic was called "of Lika"; its published people
    # are at Senj, and its significance is that Zvonimir Vukelic was Milka
    # Papic's first husband. Sestan was called "of the Croatian Littoral" and is
    # in Istria.
    ("kalanj",   "Kalanj",   "of Klenovica and Povile — into this family through Ana Kalanj, who married a de Franceschi"),
    ("vukelic",  "Vukelić",  "of Senj — Milka Papić's first husband's people"),
    ("boras",    "Boras",    "of Senj, married into the Papići and the Prpići"),
    ("sestan",   "Šestan",   "of Gologorica in Istria — and connected to this family only through a sorting label"),
    # Five names added 14 October 2026, each with a real register behind it.
    ("pavelic",     "Pavelić",     "of Mrzli Dol above Senj — the in-laws the Blaževići kept marrying, and a branch that went to Minnesota"),
    ("tomljanovic", "Tomljanović", "of Karlobag and Senj — ahnentafel 111, and the canons of Senj cathedral"),
    ("krmpotic",    "Krmpotić",    "of Senj, Krivi Put and Krmpote — a Frontier name read in the Senj registers"),
    ("babic",       "Babić",       "of Senj, porters and mariners — and the cholera of August 1855"),
    ("spalj",       "Špalj",       "of Senj and Krmpote — a lieutenant of 1747 and the women who outlived him"),
]

# Placeholder rows the working tree carries that are not people at all: sorting
# buckets, "to be sorted" stubs, and bracketed group labels. These are research
# scaffolding, not ancestors, and publishing them as people would be a lie.
JUNK = re.compile(
    r"(\bto be sort|\bsorting\b|\bfor sorting\b|\bworking\b|\bunknown\b|"
    r"\bfree text\b|\bbrothers?\s*[\[(]|\bsisters?\s*[\[(]|^\s*nn\b|\bplaceholder\b|"
    # "Brothers of Casparus (It Seems)", "Joannes [Brothers of] Zubrinic"
    r"\bbrothers?\s+of\b|\bsisters?\s+of\b|\bit seems\b|"
    # "1800-1830 Birth - Selce Papic (Papa)", "1700 Birth - Selce ..." - a name
    # that opens with a year and a record-word is a bucket, not a person
    r"^\s*\d{4}\s*([-\u2013]\s*\d{4})?\s+(birth|death|marriage|baptism)\b)", re.I)


# The alphabet. Fifteen Zubrinic nodes are named with one capital letter and a
# surname -- "M Zubrinic Xubrinich Zubrinic" -- and each is the tree's parent for
# every Zubrinic whose name begins with that letter. They are also one another's
# siblings, so the tree asserts fifteen brothers and sisters called A through W,
# hanging from nothing, with 75 real people beneath them.
#
# JUNK above cannot see them: a drawer labelled "M" contains none of the words a
# researcher writes when they know they are guessing. The test here is strict on
# purpose -- one letter, then a surname, and NO date of any kind -- so that a real
# person recorded only by an initial is not mistaken for a drawer.
ALPHABET = re.compile(r"^\s*[A-Z\u017d\u010c\u0106\u0160\u0110]\s+\S")


def is_alphabet(p):
    if not ALPHABET.match(display(p) or ""):
        return False
    return not any((p.get(k) or {}).get("date") for k in ("birt", "deat", "bapm", "buri"))


def junk(p):
    n = display(p)
    # A name with no letter in it («? ?») is the tree's placeholder for somebody it
    # could not name. It is not a name, and a page needs one: the URL and the
    # name page are made from it. Before the living standard of 16 October 2026
    # such a person was judged living and withheld; now that a recorded death
    # makes them dead, they would be named.
    return (bool(JUNK.search(n)) or n.strip() in ("", "(unnamed)")
            or not re.search(r"[^\W\d_]", n)
            or is_alphabet(p))


# Filled in by main(): id -> slug, for everybody who reaches the build.
SLUGS = {}


# The ids that may be NAMED, as a relative, in this run: set by main() first to
# everybody not held out and not a sorting stub (to find out who is named at all),
# then to the people who have a page. A relative outside it is simply not drawn.
NAMEABLE = set()


def rel(pid, people):
    """A relative, as the relation lists carry them, or None if not drawn.

    A held-out person (a possible minor), a sorting stub, and anybody who has no
    page are not drawn. A living relative is a name and a slug and the flag: no
    year, and NO tree id, because every tool that reads these lists and then goes
    back to the GEDCOM does so by id, and a living person's id would carry it
    straight to the whole of their record.
    """
    q = people.get(pid)
    if q is None or pid not in NAMEABLE:
        return None
    if is_living(q):
        return {"name": display(q), "slug": SLUGS.get(pid), "living": True}
    return {"name": display(q), "slug": SLUGS.get(pid), "id": q["id"],
            "born": year(born(q).get("date", "")),
            "died": year(died(q).get("date", ""))}


def impossible_marriage(p, other, f, people):
    """An EMPTY family record joined to somebody who died a child is not a marriage.

    27 September 2026, from a kit gate and a peer session. @I508727@ PETRA PAPIĆ
    was born in 1900 and died in 1902, and the tree gives her a husband: a record
    with no name, no dates and no events, in a family with no children and no
    marriage entry. Nothing in it is information.

    It was still drawn — and because the husband record has no birth date, the
    living rule cannot prove him dead and withholds him. So the chart stated
    that SOMEBODY ALIVE TODAY IS MARRIED TO A GIRL WHO DIED AT TWO. The living
    rule was working exactly as written; the edge underneath it was false.

    This is deliberately the narrowest rule that removes it:
      * the partner has no usable name AND no events at all, and
      * the family holds no children and no marriage event, and
      * this person died before twelve.
    An unnamed partner WITH children is real — it is how a tree records the
    other parent of a known child — and those are untouched. Across 1,833
    published people exactly TWO families are wholly empty, and only this one
    joins a child; the other is a woman who lived to 93, where a marriage is
    merely unevidenced rather than impossible, and it stays.

    This archive does not edit the GEDCOM. The record is left alone and the
    disagreement is written down in corrections.json, which is where this
    archive puts everything it will not silently repair.
    """
    q = people.get(other)
    if not q:
        return False
    named = (q.get("name") or "").strip().strip("()").replace("unnamed", "").strip()
    if named or q.get("events"):
        return False
    if f.get("chil") or f.get("events"):
        return False
    b, d = year(born(p).get("date", "")), year(died(p).get("date", ""))
    return bool(b and d and (d - b) < 12)


def relations(p, people, families):
    """Parents, spouses (with the marriage), siblings and children."""
    out = {"parents": [], "spouses": [], "siblings": [], "children": []}
    mine_living = is_living(p)
    for fid in p["famc"]:
        f = families.get(fid)
        if not f:
            continue
        for k in ("husb", "wife"):
            r = rel(f[k], people) if f[k] else None
            if r:
                out["parents"].append(r)
        for c in f["chil"]:
            if c == p["id"]:
                continue
            r = rel(c, people)
            if r:
                out["siblings"].append(r)
    for fid in p["fams"]:
        f = families.get(fid)
        if not f:
            continue
        other = f["wife"] if f["husb"] == p["id"] else f["husb"]
        m = next((e for e in f["events"] if e["kind"] == "marriage"), {})
        r = rel(other, people) if other else None
        if r and not mine_living and impossible_marriage(p, other, f, people):
            r = None
        if r and not r.get("living") and not mine_living:
            # A marriage date is a date of a living person's life when either
            # partner is living, so it is only ever written for two dead people.
            r = dict(r, marriedDate=m.get("date", ""), marriedPlace=m.get("place", ""))
        if r:
            out["spouses"].append(r)
        for c in f["chil"]:
            r = rel(c, people)
            if r:
                out["children"].append(r)
    return out


def relative_ids(p, families):
    """Every id the relation lists of `p` could name, before anything is dropped
    for having no page: parents, brothers and sisters, partners and children."""
    ids = []
    for fid in p["famc"]:
        f = families.get(fid)
        if f:
            ids += [x for x in (f["husb"], f["wife"]) if x]
            ids += [c for c in f["chil"] if c != p["id"]]
    for fid in p["fams"]:
        f = families.get(fid)
        if f:
            ids += [x for x in (f["husb"], f["wife"]) if x and x != p["id"]]
            ids += list(f["chil"])
    return ids


def person(p, ahn=None):
    b, d = born(p), died(p)
    bur, chr_ = ev(p, "burial") or {}, ev(p, "christening") or ev(p, "baptism") or {}
    occs = [e for e in p["events"] if e["kind"] == "occupation"]
    out = {
        "id": p["id"], "slug": slug(p), "name": display(p),
        "given": p["given"], "surname": p["surname"], "nick": p["nick"], "sex": p["sex"],
        "born": b.get("date", ""), "bornPlace": b.get("place", ""),
        "died": d.get("date", ""), "diedPlace": d.get("place", ""),
        "cause": d.get("cause", ""), "burial": bur.get("place", ""),
        "baptised": chr_.get("date", ""), "baptisedPlace": chr_.get("place", ""),
        "occupations": [
            {"what": (o.get("detail") or "").strip(), "where": (o.get("place") or "").strip()}
            for o in occs if (o.get("detail") or o.get("place"))
        ],
        "byear": year(b.get("date", "")), "dyear": year(d.get("date", "")),
        "sources": p["sources"][:6],
        "notes": [clean(n) for n in p["notes"] if clean(n)],
        "events": [
            {"kind": e["kind"], "date": e.get("date", ""), "place": e.get("place", ""),
             "detail": (e.get("detail") or "").strip()[:600], "note": (e.get("note") or "").strip()[:900]}
            for e in p["events"] if e["kind"] not in ("occupation",)
        ],
    }
    out["family"] = next((sl for sl, ks in SURNAMES.items() if fold(p["surname"]) in ks), None)
    if ahn:
        out["ahn"], out["gen"] = ahn, gen_of(ahn)
    return out


# ---- the living: name, relationship, town and country ----------------------
#
# A living person's place is their BIRTH place (their christening or baptism
# place if no birth place is recorded), reduced to a town and a country and
# nothing between. The tree writes "House 12, Town, County, Region, Country" and
# sometimes a hospital or a street; the county, the region and anything that
# looks like an address or an institution are dropped here, in the generator, so
# that no finer place than a town ever reaches a committed file. Residence,
# census and every other place of a living person are never read.
COUNTRIES = {
    "croatia", "serbia", "bosnia and herzegovina", "slovenia", "montenegro",
    "north macedonia", "macedonia", "kosovo", "austria", "germany", "italy",
    "hungary", "switzerland", "france", "netherlands", "belgium", "luxembourg",
    "united kingdom", "england", "scotland", "wales", "ireland", "sweden",
    "norway", "denmark", "finland", "poland", "czech republic", "slovakia",
    "romania", "bulgaria", "greece", "turkey", "russia", "ukraine", "israel",
    "spain", "portugal", "south africa", "zimbabwe", "zambia", "namibia",
    "botswana", "mozambique", "kenya", "australia", "new zealand", "canada",
    "united states", "argentina", "chile", "brazil", "uruguay", "venezuela",
    "yugoslavia", "austria-hungary", "czechoslovakia", "rhodesia",
    "soviet union", "ussr", "malawi", "tanzania", "angola", "lesotho", "eswatini",
    "swaziland", "mexico", "peru", "colombia", "paraguay", "bolivia", "ecuador",
    "india", "china", "japan", "singapore", "united arab emirates", "thailand",
    "philippines", "egypt", "morocco", "nigeria", "ghana", "mauritius",
}
COUNTRY_ALIAS = {
    "hrvatska": "Croatia", "republic of croatia": "Croatia", "srbija": "Serbia",
    "slovenija": "Slovenia", "osterreich": "Austria", "deutschland": "Germany",
    "italia": "Italy", "usa": "United States", "u.s.a.": "United States",
    "united states of america": "United States", "us": "United States",
    "uk": "United Kingdom", "great britain": "United Kingdom",
    "republic of south africa": "South Africa", "bosna i hercegovina": "Bosnia and Herzegovina",
    "magyarorszag": "Hungary", "crna gora": "Montenegro", "holland": "Netherlands",
}
COUNTRY_SPECIAL = {"austria-hungary": "Austria-Hungary", "ussr": "USSR"}
# A part that is a street, a house, an institution or a number is not a town.
ADDRESSY = re.compile(
    r"\d|\b(street|road|rd\.?|avenue|ave\.?|drive|lane|boulevard|blvd|"
    r"hospital|clinic|infirmary|maternity|nursing|care|home|hotel|farm|sanatorium|"
    r"hospice|orphanage|prison|barracks|school|college|university|church|"
    r"ulica|ul\.|cesta|trg|bolnica|klinika|porodili[sš]te|dom|"
    r"strasse|stra\u00dfe|platz|spital|krankenhaus|"
    r"hospitaal|kliniek|kraankamer)\b", re.I)
# Not towns: the tree puts these between the town and the country.
NOT_TOWN = re.compile(
    r"\b(county|province|region|state|district|municipality|metropolitan|"
    r"zupanija|\u017eupanija|opcina|op\u0107ina|oblast|kanton|bezirk|gemeinde|"
    r"parish|shire|prefecture|territory)\b", re.I)


def town_country(place):
    """(town, country, how) out of a tree place string; any may be empty.
    `how` names what had to be dropped, for the build's counts only."""
    parts = [x.strip() for x in re.split(r"\s*,\s*", place or "") if x.strip()]
    if not parts:
        return "", "", ""
    country = ""
    last = parts[-1]
    k = _key(last)
    if COUNTRY_ALIAS.get(k) or k in COUNTRIES:
        country = COUNTRY_ALIAS.get(k) or COUNTRY_SPECIAL.get(k) or " ".join(
            w if w == "and" else w.capitalize() for w in last.lower().split())
        parts = parts[:-1]
    town, how = "", ""
    for i, x in enumerate(parts):
        if ADDRESSY.search(x):
            how = "address-like"
            continue
        if _key(x) in _COUNTY or NOT_TOWN.search(x):
            continue
        town = x
        break
    return town, country, how


def living_row(p, people, families):
    """The ONLY thing written about a living person who has a page.

    The slug is the key everything joins on (the id of the tree record is not
    written: nothing downstream may be able to find the rest of the record from
    here); nothing else is kept besides the name, the town and country, and the
    relations themselves.
    """
    b = born(p) if born(p).get("place") else (ev(p, "christening") or ev(p, "baptism") or {})
    town, country, how = town_country(b.get("place", ""))
    return {"slug": SLUGS[p["id"]], "name": display(p),
            "town": town, "country": country, "living": True,
            "rel": relations(p, people, families)}, how


TAG = re.compile(r"<[^>]+>")
REF = re.compile(r"\*?\s*Reference:.*?SmartCopy\]:\s*''[^']*''", re.S)
UPD = re.compile(r"\*?\s*Updated from.*?SmartCopy\]:\s*''[^']*''", re.S)


def clean(n):
    """Strip the SmartCopy boilerplate and HTML the tree carries, keep the prose."""
    if not n:
        return ""
    n = REF.sub("", n)
    n = UPD.sub("", n)
    n = n.replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n")
    n = TAG.sub("", n)
    n = n.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    n = re.sub(r"-{3,}", "", n)
    n = re.sub(r"\n{2,}", "\n", n)
    n = re.sub(r"[ \t]{2,}", " ", n)
    return n.strip()


# A PERSON'S URL IS MINTED ONCE AND NEVER RECOMPUTED.
#
# This used to build a fresh dict on every run and resolve a collision with
# `while s in _slugs.values(): s = base-N`. The N was ITERATION ORDER, so the
# moment a namesake was added, corrected or removed, every later namesake's
# URL shifted. Not a risk — a thing that happened here: between faa46cd and
# 73d36bf six men swapped URLs with each other, and anybody who had cited
# /people/anton-blazevic-2/ was sent to a different man.
#
# data/person-slugs.json is the ledger. It is read first, used unchanged, and
# appended to only for an id it has never seen. It is never edited, because a
# URL that has been published is a promise; a removed person keeps their line
# so the slug is not handed on to somebody else.
_LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "site", "src", "data", "person-slugs.json")
try:
    _ledger = json.load(open(_LEDGER_PATH, encoding="utf-8")).get("slugs", {})
except Exception:
    _ledger = {}
_slugs = dict(_ledger)
_minted = []


def slug(p):
    if p["id"] in _slugs:
        return _slugs[p["id"]]
    base = re.sub(r"[^a-z0-9]+", "-",
                  f'{p["given"]} {p["surname"]}'.lower().translate(
                      str.maketrans("žćčšđáéíóúü", "zccsdaeiouu"))).strip("-") or "unknown"
    taken = set(_slugs.values())
    s, n = base, 2
    while s in taken:
        s, n = f"{base}-{n}", n + 1
    _slugs[p["id"]] = s
    _minted.append((p["id"], s))
    return s


def write_slug_ledger():
    """Append what was minted this run, and write the file EVERY run.

    The first version returned early when nothing had been minted, which is
    the obvious thing for an append-only file and was wrong here. regen.py
    records which files each tool actually rewrote and refuses anything it
    cannot account for — «ORPHAN: no tool in ORDER wrote it» — so a file that
    exists and is only sometimes written looks exactly like a file whose
    generator has been deleted. That check is right and it caught this.

    So the ledger is rewritten on every run and its content is deterministic:
    sorted by id, and byte-identical when nothing new was minted. It remains
    append-only in the sense that matters — an id already in the file keeps
    the slug it has, for ever.
    """
    try:
        doc = json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        doc = {"_why": ["Seeded by build_site_data.py"], "slugs": {}}
    for pid, sl in _minted:
        doc["slugs"].setdefault(pid, sl)   # setdefault: never overwrite
    doc["slugs"] = dict(sorted(doc["slugs"].items()))
    open(_LEDGER_PATH, "w", encoding="utf-8").write(
        json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    return len(_minted)


# The tree writes the same Croatian place many ways, because the county names
# changed twice in a century and MyHeritage re-geocodes on every edit. Only
# literally-identical parts are merged; nothing distinct is collapsed.
_DROP = {"austria-hungary", "austria", "hrvatska", "yugoslavia", "kingdom of yugoslavia"}
_COUNTY = {"opcina senj": "", "licko-senjska zupanija": "Lika-Senj County",
           "lika-senj county": "Lika-Senj County", "lika": "Lika-Senj County",
           "primorsko-goranska zupanija": "Primorje-Gorski Kotar County",
           "primorje-gorski kotar county": "Primorje-Gorski Kotar County"}
_FOLD = str.maketrans("zccsd", "zccsd")


def _key(x):
    return (x.lower().replace("\u017e", "z").replace("\u0107", "c").replace("\u010d", "c")
             .replace("\u0161", "s").replace("\u0111", "d").strip())


def canonical_place(place):
    """Collapse the tree's spelling variants so that a count counts places.

    Four safe moves: a leading house number is kept but split off, repeated
    parts are dropped wherever they appear (not only adjacent), the vanished
    empires are dropped, and county names are put in one form.
    """
    parts = [x.strip() for x in re.split(r"\s*,\s*", place) if x.strip()]
    out, seen = [], set()
    for x in parts:
        k = _key(x)
        if k in _DROP or not k:
            continue
        k2 = _COUNTY.get(k, None)
        if k2 is not None:
            if not k2:
                continue
            x, k = k2, _key(k2)
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    # Put the country last, once, if a Croatian county is named at all.
    if "croatia" in seen:
        out = [o for o in out if _key(o) != "croatia"] + ["Croatia"]
    elif any(_key(o) in ("lika-senj county", "primorje-gorski kotar county") for o in out):
        out.append("Croatia")
    return ", ".join(out)



def documented_ids():
    """GEDCOM ids published because a document has been read for them.

    sources/documented.psv, one id per line with the reason. See that file.
    """
    import os as _os
    path = _os.path.join(ROOT, "sources", "documented.psv")
    out = set()
    if not _os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line.split("|")[0].strip())
    return out

def media_tagged_ids():
    """GEDCOM ids tagged on a photograph or document the site shows: a tag is a name
    on a page (/pictures/, 'also tagged'), so each of them has a page too."""
    out = set()
    for name in ("manifest.psv", "local.psv"):
        path = os.path.join(ROOT, "sources", "media", name)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#") or line.count("|") < 6:
                continue
            for pid in line.split("|")[5].split(","):
                if pid.strip().isdigit():
                    out.add("@I%d@" % (int(pid) - 4000000))
    return out


def by_ahn_ids(people, families):
    return list(ancestors(people, families, HEDVIGA).values())


def main():
    global LIVING, HELD, NAMEABLE
    people, families = load()
    cls = livingset.classify(people, families)
    LIVING = {pid: pid in cls["living"] for pid in people}
    HELD = set(cls["held"])
    os.makedirs(OUT, exist_ok=True)

    # Everybody who may be PUBLISHED: not a sorting stub, not held out. The living
    # are in it (they are named), and so is everybody the rule calls dead.
    pub = {pid: p for pid, p in people.items() if pid not in HELD and not junk(p)}
    print(f"{len(people)} people; {len(cls['living'])} living, {len(HELD)} held out, "
          f"{len(pub)} publishable")

    # Slugs must exist for everybody the build will emit *before* relationships
    # are written, or a parent link points at a page that has no slug yet.
    keys_all = {k for ks in SURNAMES.values() for k in ks}
    # BLOOD IS PUBLISHED, NOT ONLY THE NAME. Until 21 September 2026 the test was
    # «is the surname one of the eight», which is how a family is FILED and not
    # what a family IS. Hedviga's aunt married a Kosina and her five children —
    # Hedviga's first cousins — appeared nowhere, because a daughter's children
    # take their father's name. Across the tree that hid 258 blood relatives,
    # 234 of them publishable. See ancestry.kindred().
    BLOOD = kindred(people, families, HEDVIGA)
    # AND A PERSON THIS ARCHIVE HAS OPENED A PAGE FOR GETS A PAGE. Blood is the
    # rule and sources/documented.psv is the exception it needed: Pavao Kosina
    # stood unlinked beside his own linked daughter because he married in, with
    # three documents read for him against her one. See the file's own header
    # for why this is a list and not a query.
    DOCUMENTED = documented_ids()
    core = set(by_ahn_ids(people, families)) | DOCUMENTED | {
        pid for pid, p in pub.items()
        if fold(p["surname"]) in keys_all or pid in BLOOD}
    # AND THEN THE PARENTS OF ALL OF THEM, TO THE ROOT. A page that says
    # «child of X» must be able to link X. One pass moves the fault one
    # generation out; the closure is the only form of the rule that is true of
    # every page. See ancestry.parents_closure().
    # THE CLOSURE RUNS FROM THE DEAD ONLY, as it always did (it ran over people the old
    # rule had judged dead, so no living person ever seeded it). A living person's
    # parents are named on their page and so get pages by the step below, but their
    # ancestors to the root are not: David Defranceski, a blood descendant of
    # Hedviga's ancestors, would otherwise pull in his mother's whole line, every
    # Booyzen, Coetzer and Louw back to 1160, because he is now named instead of
    # withheld. A person page that names a parent needs the parent's page, not the
    # parent's parents'.
    seed = {pid for pid in core if pid in pub and not is_living(pub[pid])}
    core = {pid for pid in core | parents_closure(people, families, seed) if pid in pub}
    # AND EVERYBODY THESE PAGES NAME. Standard v2, rule 7: no name appears without
    # a page. A parent, brother, sister, partner or child drawn on a page above is
    # named, so they have a page too. One step only: the relatives of THESE people
    # are drawn on their pages only where they already have one, so that naming
    # does not walk on across a tree of 15,643 and publish all of it. A person in
    # the tree who nobody here names stays unpublished.
    named = set()
    for pid in core:
        for r in relative_ids(people[pid], families):
            if r in pub and r not in core:
                named.add(r)
    for pid in media_tagged_ids():
        if pid in pub and pid not in core:
            named.add(pid)
    emitted = core | named
    NAMEABLE = set(emitted)
    for pid in sorted(emitted):
        SLUGS[pid] = slug(pub[pid])

    dead_emitted = {pid for pid in emitted if not is_living(pub[pid])}
    living_emit = sorted((pid for pid in emitted if is_living(pub[pid])),
                         key=lambda pid: (display(people[pid]).lower(), pid))

    # ---- the direct line and every ancestor -------------------------------
    by_ahn = ancestors(people, families, HEDVIGA)
    anc = []
    for ahn, pid in sorted(by_ahn.items()):
        p = people[pid]
        if junk(p):
            continue
        assert not is_living(p) and pid not in HELD, "an ancestor of the root is living or held out"
        r = person(p, ahn)
        r["rel"] = relations(p, people, families)
        anc.append(r)
    dump("ancestors.json", anc)

    spine, ahn = [], 1
    while ahn in by_ahn:
        p = people[by_ahn[ahn]]
        assert not is_living(p), "a spine ancestor is living"
        spine.append(person(p, ahn))
        ahn *= 2
    dump("line.json", spine)

    # ---- the register ------------------------------------------------------
    # ONE SOURCE OF TRUTH. This loop used to re-derive the rule — surname or
    # blood — and drifted from `emitted` above the moment a third and fourth
    # door were added (documented.psv, then the parents closure). Now it asks
    # the set that was already computed.
    reg = []
    for pid, p in pub.items():
        if pid not in dead_emitted:
            continue
        r = person(p)
        r["rel"] = relations(p, people, families)
        reg.append(r)
    reg.sort(key=lambda r: (r["surname"], r["byear"] or 9999, r["name"]))
    dump("people.json", reg)

    fam = []
    for sl, label, dek in FAMILIES:
        ks = SURNAMES[sl]
        rows = [r for r in reg if fold(r["surname"]) in ks]
        yrs = [r["byear"] for r in rows if r["byear"]]
        pls = collections.Counter(canonical_place(r["bornPlace"]) for r in rows if r["bornPlace"])
        fam.append({"slug": sl, "label": label, "dek": dek, "count": len(rows),
                    "earliest": min(yrs) if yrs else None, "latest": max(yrs) if yrs else None,
                    "places": pls.most_common(8),
                    "spellings": collections.Counter(
                        r["surname"] for r in rows).most_common(12)})
    dump("families.json", fam)

    # ---- places ------------------------------------------------------------
    pc = collections.Counter()
    for r in reg:
        for k in ("bornPlace", "diedPlace"):
            if r[k]:
                pc[canonical_place(r[k])] += 1
    dump("places.json", [{"place": k, "n": v} for k, v in pc.most_common(75)])

    # ---- the living, named: see the docstring and living_row() -------------
    liv, addr = [], 0
    for pid in living_emit:
        row, how = living_row(people[pid], people, families)
        liv.append(row)
        addr += bool(how)
    dump("living.json", liv)
    nrel = sum(1 for r in reg + anc for g in r["rel"].values() for x in g if x.get("living"))
    print(f"  living: {len(liv)} with a page, {sum(1 for r in liv if r['town'] and r['country'])} "
          f"with a town and a country, {sum(1 for r in liv if r['town'] and not r['country'])} town only, "
          f"{sum(1 for r in liv if r['country'] and not r['town'])} country only, "
          f"{sum(1 for r in liv if not r['town'] and not r['country'])} no place; "
          f"{addr} place(s) cut down from an address-like part; "
          f"{nrel} living names in the relation lists of people who have died")
    print(f"  named only (given a page because a page names them): "
          f"{len(named)} ({len(named & set(living_emit))} living)")
    write_living_rule(cls, people, len(core), len(named), liv, addr)


def write_living_rule(cls, people, ncore, nnamed, liv, addr):
    """site/src/data/livingrule.json: the rule, the year it was applied for, and how
    many people each part of it moved or held out. BY RULE AND NEVER BY PERSON:
    not an id, a name, a place or a date."""
    c = cls["counts"]
    doc = {
        "_why": ["How this archive decides who is living and who is held out of the build, as "
                 "David ruled on 16 October 2026 (the living-people standard, version 2). The test "
                 "itself is kit/tools/living_rule.py; tools/livingset.py only adapts this tree to "
                 "it. Written by tools/build_site_data.py on every full run. It records RULES AND "
                 "COUNTS. It never records a person: no id, no name, no place, no date.",
                 "The method page reads this file for its counts. tools/livingcheck.py reads it; with the GEDCOM present it also recomputes "
                 "who is living from the tree, with the kit's rule and without this generator, and "
                 "refuses the build when the two disagree."],
        "ruled": "2026-10-16",
        "asOfYear": cls["year"],
        "rule": {"livingIfBornWithinYears": 80, "minorUnderYears": 18,
                 "recordedDeathOrBurialMeansDead": True,
                 "publicSourceMeansNotLiving": True,
                 "noBirthYearMeansNotLiving": True,
                 "heldOutIds": 0},
        "peopleInTree": len(people),
        "judged": {"living": len(cls["living"]), "heldOut": len(cls["held"]),
                   "heldOutMinorByYear": sum(1 for i in cls["held"] if cls["by"][i] is not None),
                   "heldOutNoBirthYearWithLivingParent": sum(1 for i in cls["held"] if cls["by"][i] is None),
                   "deadByRecordedDeathWithinEightyYears": c["recorded_death_within_80"],
                   "notLivingByPublicSource": c["public_source"],
                   "notLivingNoBirthYear": c["no_birth_year"],
                   "notLivingOverEightyYears": c["over_80"],
                   "kitWouldCallPublicButCitationIsATree": c["kept_living_by_tree_titles"]},
        "published": {"livingNamed": len(liv), "pagesGivenBecauseANamedPageNamesThem": nnamed,
                      "pagesByTheArchivesOwnTest": ncore,
                      "livingWithTownAndCountry": sum(1 for r in liv if r["town"] and r["country"]),
                      "livingTownOnly": sum(1 for r in liv if r["town"] and not r["country"]),
                      "livingCountryOnly": sum(1 for r in liv if r["country"] and not r["town"]),
                      "livingNoPlace": sum(1 for r in liv if not r["town"] and not r["country"]),
                      "livingPlaceCutDownFromAnAddressLikePart": addr},
    }
    path = os.path.join(OUT, "livingrule.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"  wrote {os.path.relpath(path, ROOT)}")


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    print(f"  {len(obj):>5}  {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
    # AFTER main(), not at module level: module-level code runs at
    # import, before anything has been minted, and the first version
    # of this wrote an empty ledger every run.
    _n = write_slug_ledger()
    if _n:
        print(f"  person-slugs.json: {_n} new slug(s) frozen")
