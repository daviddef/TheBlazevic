#!/usr/bin/env python3
"""Turn the parsed GEDCOM into the JSON the site reads.

The living-person rule is applied here, once, at the boundary between the
research data and the published build. Anything that reaches site/src/data is
publishable; anything filtered out here never enters the build at all.

THE RULE, SINCE 16 OCTOBER 2026 (David, standard v2): who is living, and who is
held out, is decided by the KIT's living_rule.py through tools/livingset.py, not
here. Living is 80 or younger by year with no death or burial recorded; a public
source means not living; no birth year means not living. A living person is
NAMED, with their relationships and their full town and country, and nothing
more: they get a row in living.json carrying ONLY slug, name, town, country and
relations, and a page. Nothing else about a living person (no date, event,
record, source, note, occupation, burial, cause) ever reaches a file under
site/src/data. The only people published nowhere are those held out: an
undated person with a living parent, who might be a child.

EVERY PERSON THE ARCHIVE NAMES HAS A PAGE. A person who is named in a relation
list of somebody published (or tagged on a published photograph) is published
too, living or dead. That does not cascade: the page of a person who is only
there because somebody named them lists only relatives who already have pages.
"""
import json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year, ev, classify_living
import livingset
from ancestry import ancestors, gen_of, fold, kindred, parents_closure, SURNAMES, ROOT_PERSON

LIVING = {}
HELD = set()      # held out: undated with a living parent. See livingset.py.
def is_living(p): return LIVING.get(p["id"], False)

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

# FAMILY PAGES THAT DO NOT OPEN A DOOR. Added 17 October 2026 (family-pages audit).
# These twelve are names the direct line itself carries - an ancestor of Hedviga
# is a Lončarić, an Uroda, a Smojver - and each has had no page of its own, only a
# row on /connected/. A page here is built from people the archive ALREADY
# publishes (by blood, by the direct line, by the parents closure), so a name in
# this list is NOT a door in `keys_all` below: adding a surname there would
# publish every bearer of it in the GEDCOM, and the brief was to describe the
# archive's people, not to add to them. The keys are the archive's own fold()
# keys (surnames.json already groups the spellings); "Smojver Vukić" is the tree's
# double surname and the lines page says Smojver is the byname of a Vukić
# household at Karlobag; "Shambul Marić" is the tree's name for Marić (notes/
# ana-sumbul-maric.md: "the surname to search is Marić"). Nothing is merged that
# the archive has not already grouped in its own notes.
# (slug, label, gloss, fold keys). The gloss says only what the data says.
PAGE_FAMILIES = [
    ("loncaric",  "Lončarić",  "of Selce and Senj — on the direct line at ahnentafel 49 and 98", ["loncaric"]),
    ("oreskovic", "Orešković", "of Otočac — on the direct line at ahnentafel 21 and 42", ["oreskovic"]),
    ("sekula",    "Sekula",    "on the direct line at ahnentafel 43, 84 and 86", ["sekula"]),
    ("maric",     "Marić",     "ahnentafel 11 and 22, whom the tree files under «Shambul Marić»", ["maric", "shambul maric"]),
    ("antic",     "Antić",     "of Selce — on the direct line at ahnentafel 24, 48 and 96", ["antic"]),
    ("pilipic",   "Pilipić",   "of Karlobag — on the direct line at ahnentafel 13, 26, 52 and 104", ["pilipic"]),
    ("brozovic",  "Brozović",  "on the direct line at ahnentafel 51 and 102", ["brozovic"]),
    ("jellicic",  "Jelličić",  "of Selce — on the direct line at ahnentafel 25, 50 and 100", ["jellicic"]),
    ("uroda",     "Uroda",     "of Karlobag — on the direct line at ahnentafel 27, 54, 108 and 109", ["uroda"]),
    ("luckinic",  "Luckinić",  "of Karlobag — on the direct line at ahnentafel 105, 210 and 211", ["luckinic"]),
    ("gerkacs",   "Gerkacs",   "of Karlobag, written Gerkacs (Gergacs) in the tree — ahnentafel 55, 110 and 220", ["gerkacs"]),
    ("smojver",   "Smojver",   "of Karlobag, called Vukić — ahnentafel 53, 106 and 212", ["smojver", "smojver vukic"]),
]
PAGE_KEYS = {sl: ks for sl, _, _, ks in PAGE_FAMILIES}

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
    return (bool(JUNK.search(n)) or n.strip() in ("", "(unnamed)")
            or is_alphabet(p))


# Filled in by main(): id -> slug, for everybody who reaches the build.
SLUGS = {}


def rel(pid, people):
    """A relative, as the relation lists carry them. None for a sorting stub and
    for anybody held out (no name as anyone's relative).

    A LIVING relative is a name, a slug and the flag: no year, and NO tree id.
    (Every tool that reads this file and then goes back to the GEDCOM does so by
    id; consistency.py widens its scope from the ids in these lists, and a
    living person's id would carry it to the whole of their record.)
    """
    q = people.get(pid)
    if q is None or junk(q) or pid in HELD:
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


def kin(p, people, families):
    """The ids around a person, by relation, and the marriage a spouse came with.
    The walk that relations() draws and that the build uses to decide whom the
    archive names."""
    out = {"parents": [], "spouses": [], "siblings": [], "children": []}
    for fid in p["famc"]:
        f = families.get(fid)
        if not f:
            continue
        for k in ("husb", "wife"):
            if f[k]:
                out["parents"].append((f[k], None))
        for c in f["chil"]:
            if c != p["id"]:
                out["siblings"].append((c, None))
    for fid in p["fams"]:
        f = families.get(fid)
        if not f:
            continue
        other = f["wife"] if f["husb"] == p["id"] else f["husb"]
        m = next((e for e in f["events"] if e["kind"] == "marriage"), {})
        if other and not (not is_living(p) and impossible_marriage(p, other, f, people)):
            out["spouses"].append((other, m))
        for c in f["chil"]:
            out["children"].append((c, None))
    return out


def named_ids(p, people, families):
    """Everybody this person's relation lists would name."""
    out = set()
    for grp in kin(p, people, families).values():
        for pid, _ in grp:
            q = people.get(pid)
            if q is not None and not junk(q) and pid not in HELD:
                out.add(pid)
    return out


def relations(p, people, families, allowed=None):
    """Parents, spouses (with the marriage), siblings and children.

    allowed: when given, only relatives who already have pages are listed. The
    page of somebody who is published only because another page names them uses
    this, so that naming a person does not name their whole family in turn."""
    out = {"parents": [], "spouses": [], "siblings": [], "children": []}
    for gname, grp in kin(p, people, families).items():
        for pid, m in grp:
            if allowed is not None and pid not in allowed:
                continue
            r = rel(pid, people)
            if not r:
                continue
            if gname == "spouses" and not r.get("living") and not is_living(p):
                # a marriage date is a date of a living person's life when either
                # partner is living, so it is only written for two dead people
                r = dict(r, marriedDate=m.get("date", ""), marriedPlace=m.get("place", ""))
            out[gname].append(r)
    return out


def _redactions():
    """data/living-redact.tsv: id|find|replace|why. A dead person's free text (a eulogy kept in the tree's notes) that
    prints the birth year of somebody who is LIVING. `find` is the words around the year with {Y} where the year is
    (so the file itself holds no year); `replace` says «[year withheld]». The text is otherwise untouched. A row that no
    longer matches its notes, or matches a year outside the living window, stops the build (the tree changed: look again)."""
    out = {}
    path = os.path.join(ROOT, "data", "living-redact.tsv")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 3:
                continue
            f = line.rstrip("\n").split("|")
            out.setdefault(f[0].strip(), []).append((f[1], f[2]))
    return out


REDACT = _redactions()


def redacted_notes(p):
    notes = [clean(n) for n in p["notes"] if clean(n)]
    cut = livingset.cutoff_year()
    for find, repl in REDACT.get(p["id"], []):
        rx = re.compile(re.escape(find).replace(re.escape("{Y}"), r"((?:19|20)\d\d)"))
        hit = [i for i, n in enumerate(notes) if rx.search(n)]
        if not hit:
            sys.exit(f"data/living-redact.tsv: a row for {p['id']} no longer matches its notes: {find[:40]!r}")
        for i in hit:
            for m in rx.finditer(notes[i]):
                if not cut <= int(m.group(1)) <= livingset.lr.this_year():
                    sys.exit(f"data/living-redact.tsv: a row for {p['id']} matches a year outside the living window")
            notes[i] = rx.sub(lambda m: repl, notes[i])
    return notes


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
        "notes": redacted_notes(p),
        "events": [
            {"kind": e["kind"], "date": e.get("date", ""), "place": e.get("place", ""),
             "detail": (e.get("detail") or "").strip()[:600], "note": (e.get("note") or "").strip()[:900]}
            for e in p["events"] if e["kind"] not in ("occupation",)
        ],
    }
    out["family"] = next((sl for sl, ks in SURNAMES.items() if fold(p["surname"]) in ks), None) \
        or next((sl for sl, ks in PAGE_KEYS.items() if fold(p["surname"]) in ks), None)
    if ahn:
        out["ahn"], out["gen"] = ahn, gen_of(ahn)
    return out


# ---- the living: name, relationship, town and country ----------------------
#
# A living person's place is their BIRTH place, reduced to a town and a country
# and nothing between. The tree writes "House 12, Town, County, Region, Country"
# and sometimes a hospital or a street; the county, the region and anything that
# looks like an address are dropped here, in the generator, so that no finer
# place than a town ever reaches a committed file. Residence, census and every
# other place of a living person are never read.
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
    "soviet union", "ussr",
}
COUNTRY_ALIAS = {
    "hrvatska": "Croatia", "republic of croatia": "Croatia", "srbija": "Serbia",
    "slovenija": "Slovenia", "osterreich": "Austria", "deutschland": "Germany",
    "italia": "Italy", "usa": "United States", "u.s.a.": "United States",
    "united states of america": "United States", "us": "United States",
    "uk": "United Kingdom", "great britain": "United Kingdom",
    "republic of south africa": "South Africa", "bosna i hercegovina": "Bosnia and Herzegovina",
    "magyarorszag": "Hungary", "crna gora": "Montenegro",
}
COUNTRY_SPECIAL = {"austria-hungary": "Austria-Hungary", "ussr": "USSR"}
ADDRESSY = re.compile(
    r"\d|\b(street|st\.?|road|rd\.?|avenue|ave\.?|drive|lane|place|court|"
    r"hospital|clinic|infirmary|maternity|nursing|home|hotel|farm|"
    r"ulica|ul\.|cesta|trg|bolnica|klinika|porodili[sš]te|"
    r"strasse|stra\u00dfe|platz|spital|krankenhaus)\b", re.I)


def town_country(place):
    """(town, country) out of a tree place string; either may be empty."""
    parts = [x.strip() for x in re.split(r"\s*,\s*", place or "") if x.strip()]
    if not parts:
        return "", ""
    country = ""
    last = parts[-1]
    k = _key(last)
    if COUNTRY_ALIAS.get(k) or k in COUNTRIES:
        country = COUNTRY_ALIAS.get(k) or COUNTRY_SPECIAL.get(k) or " ".join(
            w if w == "and" else w.capitalize() for w in last.lower().split())
        parts = parts[:-1]
    town = ""
    for x in parts:
        if ADDRESSY.search(x) or _key(x) in _COUNTY:
            continue
        town = x
        break
    return town, country


def living_row(p, people, families, allowed=None):
    """The ONLY thing written about a living person who has a page.

    The slug is the key everything joins on (the id of the tree record is not
    written: nothing downstream may be able to find the rest of the record from
    here); nothing else is kept besides the name, the town and country, and the
    relations themselves.
    """
    town, country = town_country(born(p).get("place", ""))
    return {"slug": SLUGS[p["id"]], "name": display(p),
            "town": town, "country": country, "living": True,
            "rel": relations(p, people, families, allowed)}


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

def by_ahn_ids(people, families):
    return list(ancestors(people, families, HEDVIGA).values())


def media_tagged_ids(people):
    """Everybody tagged on a media item the build publishes (sources/media)."""
    ex = {k for k, v in json.load(open(os.path.join(ROOT, "sources", "media", "classification.json"),
                                       encoding="utf-8")).items()
          if not k.startswith("_") and v == "excluded"}
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
            if f[0] in ex:
                continue
            for pid in f[5].split(","):
                try:
                    gid = "@I%d@" % (int(pid) - 4000000)
                except ValueError:
                    continue
                if gid in people:
                    out.add(gid)
    return out


def main():
    global LIVING, HELD
    people, families = load()
    cls = livingset.classify(people, families)
    LIVING = {pid: pid in cls["living"] for pid in people}
    HELD = set(cls["held"])
    os.makedirs(OUT, exist_ok=True)

    # everybody who is not held out and is a person and not a sorting stub
    avail = {pid: p for pid, p in people.items() if pid not in HELD and not junk(p)}
    print(f"{len(people)} people; {len(cls['living'])} living, {len(HELD)} held out, "
          f"{len(avail) - sum(1 for i in avail if LIVING[i])} not living and available")

    # Slugs must exist for everybody the build will emit *before* relationships
    # are written, or a parent link points at a page that has no slug yet.
    keys_all = {k for ks in SURNAMES.values() for k in ks}
    # BLOOD IS PUBLISHED, NOT ONLY THE NAME (see ancestry.kindred()), and a person
    # this archive has opened a page for gets a page (sources/documented.psv).
    BLOOD = kindred(people, families, HEDVIGA)
    DOCUMENTED = documented_ids()
    base = set(by_ahn_ids(people, families)) | DOCUMENTED | {
        pid for pid, p in avail.items()
        if fold(p["surname"]) in keys_all or pid in BLOOD}
    # AND THEN THE PARENTS OF ALL OF THEM, TO THE ROOT, so that a page that says
    # "child of X" can link X (see ancestry.parents_closure()).
    base = {pid for pid in parents_closure(people, families, base) if pid in avail}
    # EVERY PERSON THE ARCHIVE NAMES HAS A PAGE (David, 16 October 2026). A relative
    # named on a published page, and anybody tagged on a published photograph, is
    # published too. This is one step and does not cascade: see relations(allowed=).
    named = set()
    for pid in base:
        named |= named_ids(people[pid], people, families)
    named |= {i for i in media_tagged_ids(people) if i in avail}
    emitted = base | (named & set(avail))
    only_named = emitted - base
    for pid in sorted(emitted):
        SLUGS[pid] = slug(people[pid])
    print(f"  published: {len(base)} by the old doors, {len(only_named)} more because the archive names them "
          f"({sum(1 for i in only_named if LIVING[i])} living, {sum(1 for i in only_named if not LIVING[i])} not)")

    # ---- the direct line and every ancestor -------------------------------
    by_ahn = ancestors(people, families, HEDVIGA)
    anc = []
    for ahn, pid in sorted(by_ahn.items()):
        p = people[pid]
        if is_living(p) or junk(p):
            continue
        r = person(p, ahn)
        r["rel"] = relations(p, people, families, None if pid in base else emitted)
        anc.append(r)
    dump("ancestors.json", anc)

    spine, ahn = [], 1
    while ahn in by_ahn:
        p = people[by_ahn[ahn]]
        if not is_living(p):
            spine.append(person(p, ahn))
        ahn *= 2
    dump("line.json", spine)

    # ---- the register ------------------------------------------------------
    # ONE SOURCE OF TRUTH. This loop used to re-derive the rule — surname or
    # blood — and drifted from `emitted` above the moment a third and fourth
    # door were added (documented.psv, then the parents closure). Now it asks
    # the set that was already computed.
    reg = []
    for pid in sorted(emitted):
        p = people[pid]
        if LIVING[pid]:
            continue
        r = person(p)
        r["rel"] = relations(p, people, families, None if pid in base else emitted)
        reg.append(r)
    reg.sort(key=lambda r: (r["surname"], r["byear"] or 9999, r["name"]))
    dump("people.json", reg)

    fam = []
    for sl, label, dek in FAMILIES + [(s, l, d) for s, l, d, _ in PAGE_FAMILIES]:
        ks = SURNAMES.get(sl) or PAGE_KEYS[sl]
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
    dump("places.json", [{"place": k, "n": v} for k, v in pc.most_common(60)])

    # ---- the living: a name, relationships, a town and a country -----------
    liv = [living_row(people[pid], people, families, None if pid in base else emitted)
           for pid in sorted((i for i in emitted if LIVING[i]),
                             key=lambda i: (display(people[i]).lower(), i))]
    dump("living.json", liv)
    write_living_rule(cls, people, emitted, base)
    print(f"  living: {len(liv)} with a page, {sum(1 for r in liv if r['town'])} with a town, "
          f"{sum(1 for r in liv if r['country'] and not r['town'])} country only, "
          f"{sum(1 for r in liv if not r['town'] and not r['country'])} no place")


def write_living_rule(cls, people, emitted, base):
    """sources/living-rule.json: the rule in force, and counts. BY RULE AND NEVER
    BY PERSON: not an id, a name, a place or a date."""
    import living_rule as lr
    ty = cls["today_year"]
    doc = {
        "_why": ["How this archive decides who is living and who is held out, as David ruled on "
                 "16 October 2026 (standard v2). The test itself is the kit's: "
                 "kit/tools/living_rule.py, through tools/livingset.py. Written by "
                 "tools/build_site_data.py on every full run. It records the RULE AND COUNTS; it "
                 "never records a person: no id, no name, no place, no date.",
                 "tools/livingcheck.py recomputes who is living from the tree with the kit's rule, "
                 "independently of the generator, and refuses the build when this file disagrees."],
        "ruled": "2026-10-16",
        "kitRule": {"livingYears": lr.LIVING_YEARS, "ageByYear": True, "yearOfReckoning": ty},
        "rules": [
            {"id": "living", "rule": "Born 80 years ago or less by year (this year minus the birth "
                                     "year), with no death or burial recorded. A citation from a public "
                                     "record source does NOT release somebody who has a birth year (25 "
                                     "October 2026): a source can show that a person was born or "
                                     "arrived, never that they have died. The window's edge is one "
                                     "derived constant, livingset.cutoff_year()."},
            {"id": "hold", "rule": "A person in the window whose only death is an undated flag in the "
                                   "tree, named in data/living-hold.tsv, is held as living until the "
                                   "death is confirmed."},
            {"id": "recorded-dead", "rule": "A death or burial event in the tree, dated or not, or a "
                                            "death read in sources/documented.psv, or a grave photograph "
                                            "tagged with them, or a surveyed stone with their name, birth "
                                            "year and a death year, means dead."},
            {"id": "no-birth-year", "rule": "Nobody with no birth year is living: it cannot be shown "
                                             "that they are 80 or younger."},
            {"id": "held-out", "rule": "An undated person (no birth year) with a living parent, not "
                                        "recorded dead and with no public source, is held out: no page, "
                                        "no name as anyone's relative."},
            {"id": "children", "rule": "A child with a known birth year under 18 is NOT held out. They "
                                        "follow the standard: name, relationships, town and country, a "
                                        "page, no dates, noindex."},
            {"id": "named-have-pages", "rule": "Every person the archive names (a relative on a "
                                                "published page, or tagged on a published photograph) "
                                                "has a person page. Not recursive."},
        ],
        "counts": {
            "peopleInTree": len(people),
            "living": len(cls["living"]),
            "heldOut": len(cls["held"]),
            "livingWithPage": sum(1 for i in emitted if i in cls["living"]),
            "deadWithPage": sum(1 for i in emitted if i not in cls["living"]),
            "publishedOnlyBecauseNamed": len(emitted) - len(base),
            "deadOnOtherRecord": len(cls["extra_dead"]),
            "heldAsLivingUntilConfirmed": len(cls.get("holds", {})),
        },
    }
    path = os.path.join(ROOT, "sources", "living-rule.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


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
