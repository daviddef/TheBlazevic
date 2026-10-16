#!/usr/bin/env python3
"""Refuse a build that breaks the living-people standard, version 2.

THE STANDARD (David, 16 October 2026, for every archive; the one definition of
who is living is the kit's kit/tools/living_rule.py):

  * A living person (80 or younger by year, no death or burial recorded, no
    public source) is shown by a NAME, their RELATIONSHIPS, and their full TOWN
    and COUNTRY. Nothing else: no dates, no records, no sources, no photograph,
    no occupation or notes, no structured data, no table, no year.
  * Their page is noindex, which takes it out of the sitemap and the search
    index. A name page whose every bearer is living is noindex too and names no
    canonical elsewhere.
  * Every person the archive names has a page of their own.
  * A possible minor is held out: no page, and not named as anyone's relative.
    A held-out person must not be derivable from anything the archive publishes.

WHAT THIS GATE READS. The built pages, dist/sitemap.xml, dist/searchindex.json
and the committed data. It never needs the GEDCOM, so CI runs all of that. When
the GEDCOM IS present (a local build) it also works out who is living AGAIN,
from the raw tree and the kit's rule and without the generator's code, compares
the verdicts with what was published, and scans every built and tracked file for
anything of a living or held-out person. When it is not present it says that
those checks did not run, and does not pass them.

THE RULES (each is a name in the output and in --selftest, and each has a
planted fault that must be caught):

  DATA-KEYS     living.json rows carry only slug, name, town, country, living,
                rel. A living relation entry carries only name, slug, living
                (no tree id, no year, no marriage date). No `withheld` marker.
  DATA-PLACE    a town or country is one place name: no digit, no comma.
  LEDGER        every line of the slug ledger is a person who has a page: the ledger
                holds an id and a name-slug, so a line for somebody nobody names would
                publish them.
  NAMED-PAGE    every person a relation list, the register or the Kosina data
                names has a page: a slug that is a published row, and a built page.
  PAGE-*        a living page: noindex, no canonical naming another page, no
                structured data, no table, no image or embed, no link out, no tree
                id, no year outside a dead relative's own dates, exactly the
                lines Name and Place, and the place being the town and country.
  WHO-*         a name page whose bearers are all living says noindex, names no
                canonical elsewhere; one with a bearer who has died does not.
  SITEMAP       no noindex page is in sitemap.xml.
  INDEX-*       no living page is in the search index, and no Person row is a
                living person's name.
  LIVING-ID     a living person's tree id is written only where it must be (the
                slug ledger, the Kosina arrangement).
  EMPTY         a build with nothing to check does not pass.
  FILES-UNTRACKED / RULE-RECORD    the files are in git; the record of the rule
                (by rule, never by person) is present and names nobody.

  and, only when the GEDCOM is present:

  GED-CLASS     who is living, held out and dead, recomputed independently, is
                who the data says: a living page for somebody the rule calls
                dead or holds out, a dead page for somebody it calls living, a
                held-out person in the slug ledger, and the counts in the record.
  GED-HELD      no held-out person's tree id, and no name that only they bear,
                in any built or tracked file. Names a held-out person shares
                with somebody else cannot be told apart and are counted.
  GED-DATE      no full date of any living or held-out person, in a text that
                also names them. Pages whose HAND-WRITTEN text already carries
                one are listed in sources/living-prose.psv (page and number
                only, never the date or the person); one more fails the build.
  GED-YEAR      no birth year of a living or held-out person on the same line
                as their name in a committed data file.
  GED-SOURCE    nothing the tree holds for a published living person beyond a
                name, a town and a country is on their own page.

Usage:  python3 tools/livingcheck.py [--dist DIR] [--selftest] [--selftest-ged]
                                      [--advisory] [--quiet] [--no-ged]
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
import livingnames  # noqa: E402
import living_rule as lr  # noqa: E402

fold = livingnames.fold

ROW_KEYS = {"slug", "name", "town", "country", "living", "rel"}
REL_LIVING_KEYS = {"name", "slug", "living"}
REL_DEAD_KEYS = {"id", "slug", "name", "born", "died", "marriedDate", "marriedPlace"}
REL_GROUPS = {"parents", "spouses", "siblings", "children"}
DEAD_ROW_KEYS = {"id", "slug", "name", "given", "surname", "nick", "sex", "born", "bornPlace",
                 "died", "diedPlace", "cause", "burial", "baptised", "baptisedPlace",
                 "occupations", "byear", "dyear", "sources", "notes", "events", "family",
                 "ahn", "gen", "rel"}
# Where a living person's tree id may be written: the frozen slug ledger (a URL is a
# promise, so it is keyed by the id it was minted for) and the Kosina arrangement
# (the page joins a person to a card by id).
LIVING_ID_OK = ("site/src/data/person-slugs.json", "site/src/data/kosina.json",
                "site/src/data/kosina-descent.json")
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
NOINDEX = re.compile(r'<meta[^>]*name=["\']robots["\'][^>]*noindex', re.I)
CANON = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', re.I)
LDJSON = re.compile(r'application/ld\+json', re.I)
MEDIA = re.compile(r"<(img|picture|video|audio|iframe|object|embed|source|svg)\b", re.I)
EXTLINK = re.compile(r'href=["\'](?:https?:)?//', re.I)
RECORDID = re.compile(r"@I\d+@")
MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
DTSPAN = re.compile(r'<span class="dt">.*?</span>', re.S)
TAGS = re.compile(r"<[^>]+>")


def slugify(s):
    """What who/[slug].astro does, character for character."""
    s = unicodedata.normalize("NFD", str(s or ""))
    s = re.sub(r"[̀-ͯ]", "", s)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s)
    return re.sub(r"^-+|-+$", "", s).lower()


def canonical_is_self(href, path):
    """The kit gives every page a canonical naming itself, which points nowhere
    else; what the standard forbids is one that names another page."""
    if path is None:
        return True
    return re.sub(r"^https?://[^/]+", "", href) == "/" + path[:-len("index.html")]


def ntok(s):
    """A text as its folded words only, so that a nickname in quotes, a JSON escape or a
    comma between two words cannot hide a name from a comparison."""
    return " ".join(re.findall(r"[a-z0-9]+", fold(s)))


def text_of(fragment):
    return htmllib.unescape(re.sub(r"\s+", " ", TAGS.sub(" ", fragment))).strip()


# ---- the world the rules read ------------------------------------------------

SERVED_TEXT = (".json", ".xml", ".txt", ".js", ".css", ".svg", ".tsv", ".csv", ".webmanifest", ".psv")
SCANNED_DIRS = ("site/src", "site/public", "data", "sources")
DATA_EXT = (".json", ".tsv", ".psv", ".csv", ".txt", ".xml", ".md")


def load_rule():
    p = os.path.join(DATA, "livingrule.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def git(*args):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, timeout=120)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def tracked_files():
    out = git("ls-files", "-z")
    return None if out is None else [x for x in out.split("\0") if x]


def untracked_files():
    """Files under the scanned directories that git neither tracks nor ignores:
    invisible to a scan of tracked files, and about to be published by a careless
    `git add`. None when this is not a git checkout."""
    out = git("ls-files", "-z", "--others", "--exclude-standard")
    if out is None:
        return None
    return [x for x in out.split("\0") if x and x.startswith(tuple(d + "/" for d in SCANNED_DIRS))]


def load_world(dist):
    def J(f):
        with open(os.path.join(DATA, f), encoding="utf-8") as fh:
            return json.load(fh)

    w = {"living": J("living.json"), "people": J("people.json"),
         "ancestors": J("ancestors.json"), "kosina": J("kosina.json"), "register": J("register.json"),
         "pages": {}, "extra": {}, "sitemap": "", "index": "", "dist": dist,
         "ledger": dict(J("person-slugs.json")["slugs"]),
         "rule": load_rule(), "untracked": untracked_files()}
    for root, _, files in os.walk(dist):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, dist).replace(os.sep, "/")
            try:
                if f.endswith(".html"):
                    w["pages"][rel] = open(p, encoding="utf-8", errors="replace").read()
                elif f.endswith(SERVED_TEXT) and f != "searchindex.json":
                    w["extra"][rel] = open(p, encoding="utf-8", errors="replace").read()
            except FileNotFoundError:
                pass
    for key, f in (("sitemap", "sitemap.xml"), ("index", "searchindex.json")):
        p = os.path.join(dist, f)
        if os.path.exists(p):
            w[key] = open(p, encoding="utf-8", errors="replace").read()
    return w


def clone(w):
    """A copy cheap enough to plant faults in: the big strings are shared (they
    are immutable), the data rows are copied."""
    w2 = dict(w)
    w2["pages"] = dict(w["pages"])
    w2["extra"] = dict(w["extra"])
    for k in ("living", "people", "ancestors", "kosina", "register", "ledger"):
        w2[k] = copy.deepcopy(w[k])
    return w2


def page_path(slug):
    return f"people/{slug}/index.html"


def who_path(slug):
    return f"who/{slug}/index.html"


def rows_of(w):
    return list(w["living"]) + list(w["people"]) + list(w["ancestors"])


def name_groups(w):
    by = collections.defaultdict(list)
    for r in rows_of(w):
        if r.get("name") and r.get("slug"):
            by[slugify(r["name"])].append(r)
    return by


def all_living_names(w):
    return sorted(s for s, rows in name_groups(w).items() if rows and all(r.get("living") for r in rows))


def mixed_names(w):
    return sorted(s for s, rows in name_groups(w).items()
                  if rows and any(r.get("living") for r in rows) and not all(r.get("living") for r in rows))


def _names(w):
    """(names of the living the archive publishes, names of everybody who has died)."""
    living = {r["name"] for r in w["living"]}
    dead = {p["name"] for p in list(w["people"]) + list(w["ancestors"]) if p.get("name")}
    return sorted(n for n in living if n), sorted(dead)


def names_of(w):
    return livingnames.Names(*_names(w))


# ---- rules that need no GEDCOM (CI runs these) --------------------------------

def rule_data(w):
    out = []
    for r in w["living"]:
        who = r.get("slug") or "?"
        extra = set(r) - ROW_KEYS
        if extra:
            out.append(("DATA-KEYS", who, "living.json row carries " + ", ".join(sorted(extra))))
        if r.get("living") is not True:
            out.append(("DATA-KEYS", who, "living.json row is not flagged living"))
        if not r.get("name") or not r.get("slug"):
            out.append(("DATA-KEYS", who, "living.json row without a name or a slug"))
        for k in ("town", "country"):
            v = str(r.get(k) or "")
            if re.search(r"\d|,", v):
                out.append(("DATA-PLACE", who, f"{k} is not a single place name"))
        if set(r.get("rel") or {}) - REL_GROUPS:
            out.append(("DATA-KEYS", who, "rel carries a group other than parents, spouses, siblings, children"))
    for r in list(w["people"]) + list(w["ancestors"]):
        extra = set(r) - DEAD_ROW_KEYS
        if extra:
            out.append(("DATA-KEYS", r.get("slug", "?"),
                        "a published person who has died carries a field the archive never wrote: "
                        + ", ".join(sorted(extra))))
        if r.get("living"):
            out.append(("DATA-KEYS", r.get("slug", "?"), "a living flag on a person published as having died"))
    for r in rows_of(w):
        for gname, g in (r.get("rel") or {}).items():
            for x in g:
                keys = set(x)
                if "withheld" in keys:
                    out.append(("DATA-KEYS", r.get("slug", "?"),
                                "a withheld entry: a person is either named with a page or not drawn"))
                elif x.get("living"):
                    bad = keys - REL_LIVING_KEYS
                    if bad:
                        out.append(("DATA-KEYS", r.get("slug", "?"),
                                    f"a living relative in {gname} carries " + ", ".join(sorted(bad))))
                elif r.get("living") and keys & {"marriedDate", "marriedPlace"}:
                    out.append(("DATA-KEYS", r.get("slug", "?"), "a marriage date on a living person's relation"))
                elif keys - REL_DEAD_KEYS:
                    out.append(("DATA-KEYS", r.get("slug", "?"),
                                "a relative carries " + ", ".join(sorted(keys - REL_DEAD_KEYS))))
    return out


def rule_ledger(w):
    """The slug ledger is committed and public. A line in it is a tree id and a name.
    It is append-only so that a published URL is a promise; but a line for somebody the
    archive does not publish would name them (the first run of this generator minted
    two thousand such lines before the set was settled, and they had to be taken out)."""
    out = []
    slugs = {r["slug"] for r in rows_of(w) if r.get("slug")}
    stray = [i for i, sl in w["ledger"].items() if sl not in slugs]
    if stray:
        out.append(("LEDGER", "person-slugs.json",
                    f"{len(stray)} line(s) for people who have no page: they would be named by it"))
    return out


def rule_named(w):
    """Standard rule 7: every person the archive names has a page of their own."""
    out = []
    slugs = {r["slug"] for r in rows_of(w) if r.get("slug")}
    for r in rows_of(w):
        for gname, g in (r.get("rel") or {}).items():
            for x in g:
                if not x.get("slug"):
                    out.append(("NAMED-PAGE", r.get("slug", "?"), f"a person named in {gname} has no page"))
                elif x["slug"] not in slugs:
                    out.append(("NAMED-PAGE", r.get("slug", "?"), f"a person named in {gname} has a slug that is nobody published"))
    for s in sorted(slugs):
        if page_path(s) not in w["pages"]:
            out.append(("NAMED-PAGE", s, "a published person whose page was not built"))
    for x in w["register"]:
        if x.get("kind") == "tree" and (not x.get("slug") or x["slug"] not in slugs):
            out.append(("NAMED-PAGE", "register.json", "a register row for a person from the tree who has no page"))
    ids = set(w["ledger"])
    for k in w["kosina"].get("people", []):
        if not k.get("slug") or k["slug"] not in slugs:
            out.append(("NAMED-PAGE", "kosina.json", "a Kosina person with no page"))
        for g in ("parents", "spouses", "children", "siblings"):
            for y in k.get(g, []):
                if y.get("id") not in ids:
                    out.append(("NAMED-PAGE", "kosina.json", f"a person named in {g} has no page"))
    return out


def page_rules(html, row, who="?", path=None):
    """Every rule about ONE living page. Also the control: run it on the page of
    somebody who has died and it must object."""
    out = []
    head = html[:6000]
    if not NOINDEX.search(head):
        out.append(("PAGE-NOINDEX", who, "no noindex"))
    c = CANON.search(html)
    if c and not canonical_is_self(c.group(1), path):
        out.append(("PAGE-CANON", who, "its canonical names another page"))
    if LDJSON.search(html):
        out.append(("PAGE-LDJSON", who, "carries structured data"))
    m = MAIN.search(html)
    main = m.group(1) if m else html
    if re.search(r"<table\b", main, re.I):
        out.append(("PAGE-TABLE", who, "carries a table"))
    if MEDIA.search(main):
        out.append(("PAGE-MEDIA", who, "carries an image, frame or embed"))
    if EXTLINK.search(main):
        out.append(("PAGE-LINKS", who, "links out of the archive"))
    if RECORDID.search(html):
        out.append(("PAGE-RECORD", who, "carries a tree record id"))
    visible = text_of(DTSPAN.sub(" ", main))
    ym = YEAR.search(visible)
    if ym:
        # the year itself is not printed: a gate's log is not the place for a living
        # person's date
        out.append(("PAGE-YEAR", who, "a year in the page body"))
    desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    if desc and YEAR.search(desc.group(1)):
        out.append(("PAGE-YEAR", who, "a year in the description"))
    labs = [text_of(t) for t in re.findall(r'<span class="lab">(.*?)</span>', main, re.S)]
    labs = [x for x in labs if x not in ("A living person",)]
    if set(labs) - {"Name", "Place"}:
        out.append(("PAGE-ROWS", who, "lines other than Name and Place: " + ", ".join(sorted(set(labs) - {"Name", "Place"}))))
    if row is not None:
        want = ", ".join(x for x in (row.get("town"), row.get("country")) if x)
        got = re.search(r'<p class="lede living-place"><span class="lab">Place</span>(.*?)</p>', main, re.S)
        if want and (not got or text_of(got.group(1)) != want):
            out.append(("PAGE-ROWS", who, "the Place line is not exactly the town and country"))
        if not want and got:
            out.append(("PAGE-ROWS", who, "a Place line for a person with no place in the data"))
        nm = re.search(r'<p class="lede living-name"><span class="lab">Name</span>(.*?)</p>', main, re.S)
        if not nm or text_of(nm.group(1)) != row.get("name"):
            out.append(("PAGE-ROWS", who, "the Name line is not the name in the data"))
    return out


def rule_pages(w):
    out = []
    for r in w["living"]:
        p = w["pages"].get(page_path(r["slug"]))
        if p is None:
            out.append(("PAGE-MISSING", r["slug"], "no page was built"))
            continue
        out += page_rules(p, r, r["slug"], page_path(r["slug"]))
    for s in all_living_names(w):
        p = w["pages"].get(who_path(s))
        if p is None:
            out.append(("PAGE-MISSING", "who/" + s, "no name page was built"))
            continue
        if not NOINDEX.search(p[:6000]):
            out.append(("WHO-NOINDEX", "who/" + s, "an all-living name page without noindex"))
        c = CANON.search(p)
        if c and not canonical_is_self(c.group(1), who_path(s)):
            out.append(("WHO-CANON", "who/" + s, "an all-living name page whose canonical names another page"))
    for s in mixed_names(w):
        p = w["pages"].get(who_path(s))
        if p is not None and NOINDEX.search(p[:6000]):
            out.append(("WHO-NOINDEX", "who/" + s, "a name page with a bearer who has died is noindex (it should list them)"))
    return out


def sitemap_locs(w):
    return set(re.findall(r"<loc>(.*?)</loc>", w["sitemap"]))


def rule_sitemap(w):
    out = []
    locs = sitemap_locs(w)
    paths = {re.sub(r"^https?://[^/]+", "", l) for l in locs}
    for r in w["living"]:
        if f"/people/{r['slug']}/" in paths:
            out.append(("SITEMAP", r["slug"], "a living page is in sitemap.xml"))
    for s in all_living_names(w):
        if f"/who/{s}/" in paths:
            out.append(("SITEMAP", "who/" + s, "an all-living name page is in sitemap.xml"))
    # any page that says noindex, living or not, is out of the sitemap
    for rel, p in w["pages"].items():
        if rel.endswith("index.html") and NOINDEX.search(p[:6000]):
            path = "/" + rel[:-len("index.html")]
            path = "/" if path == "//" else path
            if path in paths:
                out.append(("SITEMAP", rel, "a noindex page is in sitemap.xml"))
    return out


_INDEX_CACHE = {}


def rule_index(w, names):
    key = (len(w["index"]), hash(w["index"]), tuple(sorted(r["slug"] for r in w["living"])), len(names.forbidden))
    if key not in _INDEX_CACHE:
        _INDEX_CACHE[key] = _rule_index(w, names)
    return _INDEX_CACHE[key]


def _rule_index(w, names):
    out = []
    try:
        rows = json.loads(w["index"]) if w["index"] else []
    except ValueError:
        return [("INDEX-HREF", "searchindex.json", "cannot be parsed, so cannot be checked")]
    hrefs = {f"/people/{r['slug']}/" for r in w["living"]} | {f"/who/{s}/" for s in all_living_names(w)}
    for row in rows:
        if row.get("h") in hrefs:
            out.append(("INDEX-HREF", row.get("h"), "a living page is in the search index"))
        # a PERSON row is generated from people.json, which holds nobody living;
        # one whose title is a living-only name has come from somewhere it must not
        if row.get("k") == "Person" and names.count_hits(str(row.get("t") or "")):
            out.append(("INDEX-NAME", row.get("h") or "?", "a Person row is a living person's name"))
    return out


def rule_living_ids(w):
    """A living person's tree id is the way back to the whole of their record. It
    is written in the slug ledger and the Kosina arrangement because both key on
    ids, and nowhere else."""
    out = []
    inv = {v: k for k, v in w["ledger"].items()}
    ids = {inv[r["slug"]] for r in w["living"] if r["slug"] in inv}
    if not ids:
        return out
    pat = re.compile("|".join(re.escape(i) for i in sorted(ids)))
    for f in tracked_files() or []:
        if f in LIVING_ID_OK or not f.endswith(DATA_EXT) or f.endswith("package-lock.json"):
            continue
        try:
            t = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if pat.search(t):
            out.append(("LIVING-ID", f, "a living person's tree id is in a committed file"))
    for k, t in list(w["pages"].items()) + list(w["extra"].items()):
        if pat.search(t):
            out.append(("LIVING-ID", "dist:" + k, "a living person's tree id is in a built file"))
    return out


def rule_empty(w):
    out = []
    if not w["living"]:
        out.append(("EMPTY", "living.json", "no living person to check: the archive publishes some, "
                                              "so an empty list is a broken harvest, not a pass"))
    if not w["people"]:
        out.append(("EMPTY", "people.json", "nobody who has died to check"))
    if len(w["pages"]) < 50:
        out.append(("EMPTY", w["dist"], f"only {len(w['pages'])} page(s) built"))
    if not w["sitemap"]:
        out.append(("EMPTY", "sitemap.xml", "there is no sitemap to check"))
    if not w["index"]:
        out.append(("EMPTY", "searchindex.json", "there is no search index to check"))
    return out


def rule_files(w):
    out = []
    if w.get("untracked"):
        out.append(("FILES-UNTRACKED", w["untracked"][0],
                    f"{len(w['untracked'])} file(s) under the scanned directories are neither tracked "
                    "nor ignored, so a scan of tracked files cannot see them: git add them first"))
    r = w.get("rule")
    if not r or not r.get("judged") or r.get("asOfYear") is None:
        out.append(("RULE-RECORD", "site/src/data/livingrule.json",
                    "the record of the living rule (by rule, never by person) is missing or malformed"))
    elif re.search(r"@I\d+@", json.dumps(r)):
        out.append(("RULE-RECORD", "site/src/data/livingrule.json",
                    "the record names a tree id: it must record rules and counts only"))
    elif r["published"]["livingNamed"] != len(w["living"]):
        out.append(("RULE-RECORD", "site/src/data/livingrule.json",
                    "the number of living people named is not the number in living.json"))
    return out


def run_rules(w):
    out = rule_empty(w)
    if out:
        return out          # nothing else can mean anything on a build with nothing in it
    names = names_of(w)
    return (rule_data(w) + rule_ledger(w) + rule_named(w) + rule_files(w) + rule_pages(w) + rule_sitemap(w)
            + rule_index(w, names) + rule_living_ids(w))


# ---- the rules that need the whole tree (local builds only) -------------------
#
# THE LIVING TEST, AGAIN, WITHOUT THE GENERATOR. tools/livingset.py adapts the tree
# to the kit's rule for tools/build_site_data.py. This reads the raw GEDCOM records
# itself and asks the kit's living_rule.py directly, so a mistake in one is not
# also a mistake in the other. They share the kit's rule, which is the point, and
# nothing else.

TREE_WORDS = ("geni", "wikitree", "family tree index", "web site", "website", "family site",
              "23andme", " tree")
HELD_IDS = ()


def offered(cite):
    """Is this citation one the kit may be asked about? FamilySearch always;
    anything that names itself a family tree, a family's site or a DNA profile never."""
    title = cite.split(" — ")[0].lower()
    if title.strip().startswith("familysearch"):
        return True
    return not any(t in title for t in TREE_WORDS)


def judge(recs, today_year):
    """recs: id -> {"by": birth year or None, "dead": bool, "cites": [str], "parents": [id]}
    -> (living, held, counts). Pure: this is what the rule test plants faults in."""
    live = {i for i, r in recs.items()
            if lr.is_living(r["by"], r["dead"], [c for c in r["cites"] if offered(c)], today_year)}
    held = set()
    for i, r in recs.items():
        pl = any(p in live for p in r["parents"])
        if lr.is_held_out(i, r["by"], r["dead"], [c for c in r["cites"] if offered(c)], pl, HELD_IDS, today_year):
            held.add(i)
    return live, held


def extract(records):
    """GEDCOM records (gedcom.parse) -> the rule's inputs, read straight off the nodes."""
    src = {r.xref: (r.val("TITL") or r.val("ABBR") or "") for r in records if r.tag == "SOUR" and r.xref}
    fams = [r for r in records if r.tag == "FAM"]
    parents = collections.defaultdict(set)
    for f in fams:
        pair = [k.value for k in f.kids if k.tag in ("HUSB", "WIFE")]
        for c in (k.value for k in f.kids if k.tag == "CHIL"):
            parents[c].update(pair)

    def walk_cites(n, out):
        for k in n.kids:
            if k.tag == "SOUR":
                v = k.value.strip()
                t = src.get(v, "") if v.startswith("@") else v
                page = k.val("PAGE")
                s = (t + " — " + page).strip(" —") if (t or page) else ""
                if s:
                    out.append(s)
            else:
                walk_cites(k, out)

    def year_of(n):
        for d in n.all("DATE"):
            m = re.search(r"\b(\d{4})\b", d.value)
            if m:
                return int(m.group(1))
        return None

    recs = {}
    for r in records:
        if r.tag != "INDI" or not r.xref:
            continue
        by = None
        for tags in (("BIRT",), ("CHR", "BAPM")):
            for k in r.kids:
                if k.tag in tags and by is None:
                    by = year_of(k)
        cites = []
        walk_cites(r, cites)
        recs[r.xref] = {"by": by, "dead": any(k.tag in ("DEAT", "BURI", "CREM") for k in r.kids),
                        "cites": cites, "parents": sorted(parents.get(r.xref, ()))}
    return recs


def ged_available():
    d = os.path.join(ROOT, "sources")
    return os.path.isdir(d) and any(f.endswith(".ged") for f in os.listdir(d))


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
LONG = ["January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December"]
DATE_TOKENS = [re.compile(r"(?<![\w/-])\d{1,2} [A-Za-z]{3,9} \d{4}(?!\d)"),
               re.compile(r"(?<![\w/-])\d{4}-\d{2}-\d{2}(?!\d)"),
               re.compile(r"(?<![\w/-])\d{1,2}/\d{1,2}/\d{4}(?!\d)")]
GEDDATE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s*$")


def date_forms(d):
    m = GEDDATE.match(d or "")
    if not m or m.group(2).upper() not in MONTHS:
        return set()
    day, mon, yr = int(m.group(1)), MONTHS.index(m.group(2).upper()), m.group(3)
    return {f"{day} {MONTHS[mon]} {yr}", f"{day} {MONTHS[mon].capitalize()} {yr}",
            f"{day} {LONG[mon]} {yr}", f"{yr}-{mon + 1:02d}-{day:02d}",
            f"{day}/{mon + 1}/{yr}", f"{day:02d}/{mon + 1:02d}/{yr}"}


PROSE = os.path.join(ROOT, "sources", "living-prose.psv")


def known_prose():
    """page|count|kind|why — pages whose HAND-WRITTEN text already carries a full
    date that the tree attaches to a person the rule calls living, found on 16
    October 2026 when this gate first looked with the GEDCOM beside it. The file
    records the PAGE, HOW MANY and what KIND of text, never the date or the person.
    A page may carry up to `count` such dates; one more fails the build."""
    out = {}
    if os.path.exists(PROSE):
        for line in open(PROSE, encoding="utf-8"):
            if line.startswith("#") or line.count("|") < 2:
                continue
            f = [x.strip() for x in line.split("|")]
            try:
                out[f[0]] = int(f[1])
            except ValueError:
                pass
    return out


def first_dates(text, forbid, owners_names, window=300):
    """A living person's date counts only where the text ALSO names them NEARBY
    (within `window` characters): a date is a coincidence between two people far
    more often than it is a leak, and the kit's gate learned the same thing; and in
    a long file a name anywhere is not a name beside the date. forbid: date ->
    tree ids; owners_names: id -> folded name phrases. Returns [(date, id)]."""
    found = []
    if not any(forbid.get(m.group(0)) for rx in DATE_TOKENS for m in rx.finditer(text)):
        return found                       # the common case, and cheap
    plain = htmllib.unescape(TAGS.sub(" ", text))
    for rx in DATE_TOKENS:
        for m in rx.finditer(plain):
            owners = forbid.get(m.group(0))
            if not owners:
                continue
            near = ntok(plain[max(0, m.start() - window): m.end() + window])
            for o in owners:
                if any(ph in near for ph in owners_names.get(o, ())):
                    found.append((m.group(0), o))
                    break
    return found


def tracked_corpus():
    """Every TRACKED data file, by `git ls-files` and not by walking the disk: a
    file that is not tracked is not one the repository will publish, and the gate
    that scans the disk would pass on files the build is about to ship (rule
    FILES-UNTRACKED closes the other half)."""
    out = {}
    for f in tracked_files() or []:
        if not f.endswith(DATA_EXT) or f.endswith("package-lock.json"):
            continue
        try:
            out["tracked:" + f] = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
        except OSError:
            pass
    return out


class Ged:
    """The tree and the rule, loaded ONCE (it takes seconds), so a planted fault
    costs a scan of the planted text and not a rebuild."""

    def __init__(self, w):
        import gedcom
        self.gedcom = gedcom
        records = gedcom.parse()
        self.recs = extract(records)
        # NAMES are presentation, not the rule: the build collapses the tree's repeated
        # particles and quotes a nickname, so the names are asked of the same function.
        people_for_names, _ = gedcom.load()
        year = (w.get("rule") or {}).get("asOfYear") or lr.this_year()
        self.year = year
        self.living, self.held = judge(self.recs, year)
        self.named = self.living - self.held
        self.display = {}
        self.events = {}
        for r in records:
            if r.tag != "INDI" or not r.xref:
                continue
            self.display[r.xref] = gedcom.display(people_for_names[r.xref])
            evs = []
            for k in r.kids:
                if k.tag in ("BIRT", "DEAT", "BURI", "CHR", "BAPM", "MARR", "RESI", "OCCU", "EVEN", "CENS", "IMMI", "EMIG"):
                    evs.append({"tag": k.tag, "date": k.val("DATE"), "place": k.val("PLAC"),
                                "text": " ".join(x for x in (k.value.strip(), k.val("NOTE"), k.val("CAUS"), k.val("TYPE")) if x and x != "Y")})
            self.events[r.xref] = {"events": evs,
                                   "notes": [k.value.strip()[:60] for k in r.kids if k.tag == "NOTE" and len(k.value.strip()) > 14],
                                   "cites": self.recs[r.xref]["cites"]}
        self.dead = set(self.recs) - self.living
        pub_living, pub_dead = _names(w)
        # every date and birth year of every living person, published or held out
        self.forbid = {}
        self.date_kind = {}
        KIND = {"BIRT": "birth", "CHR": "christening", "BAPM": "baptism", "MARR": "marriage", "RESI": "residence"}
        self.years = collections.defaultdict(set)
        for i in self.living | self.held:
            by = self.recs[i]["by"]
            if by:
                self.years[i].add(str(by))
            for e in self.events[i]["events"]:
                for f in date_forms(e.get("date", "")):
                    self.forbid.setdefault(f, set()).add(i)
                    self.date_kind[(i, f)] = KIND.get(e["tag"], "other event")
        self.owner_names = {i: {ntok(x) for x in livingnames.phrases_of(self.display[i])}
                            for i in self.living | self.held}
        # A held-out person's name cannot be told from anybody else's of the same
        # name: those are subtracted and COUNTED. "Anybody else" is every other
        # person in the tree, held out or not.
        others = {self.display[i] for i in self.recs if i not in self.held} | set(pub_dead) | set(pub_living)
        self.nm_held = livingnames.Names([self.display[i] for i in self.held], others)
        self.nm_unpub = livingnames.Names(
            [self.display[i] for i in self.named if self.display[i] not in set(pub_living)], pub_dead)
        self.held_ids = set(self.held)
        self.known = known_prose()

    def scan(self, corpus):
        """(failures, advisories) for `corpus`, {key: text}."""
        out, adv = [], []
        for where, text in corpus.items():
            # --- held-out people: no id, no name, anywhere ---------------------
            ids = {m.group(0) for m in RECORDID.finditer(text)} & self.held_ids
            if ids:
                out.append(("GED-HELD", where, f"{len(ids)} held-out person's tree id is in the file"))
            n = self.nm_held.count_hits(text)
            if n:
                out.append(("GED-HELD", where, f"{n} held-out person's name is in the file"))
            # --- dates of any living or held-out person ------------------------
            hits = first_dates(text, self.forbid, self.owner_names)
            key = self.key_of(where)
            if hits:
                kinds = sorted({self.date_kind.get((o, d), "event") for d, o in hits})
                if len(hits) <= self.known.get(key, 0):
                    adv.append(("GED-DATE", where, f"{len(hits)} known date(s) in hand-written text ({', '.join(kinds)}), listed in sources/living-prose.psv"))
                else:
                    out.append(("GED-DATE", where, f"{len(hits)} date(s) of a living or held-out person in the file ({', '.join(kinds)})"))
            # --- a birth year beside a name, in a data file --------------------
            if where.startswith("tracked:") and where.endswith((".json", ".tsv", ".psv", ".csv")) \
                    and not where.endswith("searchindex.json"):
                n = self.year_beside_name(text)
                if n:
                    if n <= self.known.get(key, 0):
                        adv.append(("GED-YEAR", where, f"{n} known line(s) in hand-written data, listed in sources/living-prose.psv"))
                    else:
                        out.append(("GED-YEAR", where, f"{n} line(s) where a living or held-out person's birth year is beside their name"))
            # --- named living people who are not published (advisory) ----------
            if where.startswith("dist:") and not where.endswith((".json", ".xml")):
                n = self.nm_unpub.count_hits(text)
                if n:
                    adv.append(("GED-NAME", where, f"{n} living name(s) the archive gives no page, in text it wrote"))
        return out, adv

    @staticmethod
    def key_of(where):
        """The key sources/living-prose.psv uses: the page (people/x, corrections) or,
        for a tracked file, its path."""
        page = where.split(":", 1)[1]
        if where.startswith("dist:"):
            return page[:-len("/index.html")].strip("/") if page.endswith("index.html") else page
        return page

    def year_beside_name(self, text):
        if not hasattr(self, "_name_year"):
            self._name_year = {}
            for i in self.living | self.held:
                for ph in livingnames.folded_phrases(self.display[i]):
                    if len(ph) >= livingnames.MIN_PHRASE:
                        self._name_year.setdefault(ntok(ph), set()).update(self.years.get(i, ()))
            # a phrase borne by a person who has died cannot be told apart: dropped
            for i in self.dead:
                for ph in livingnames.folded_phrases(self.display[i]):
                    self._name_year.pop(ntok(ph), None)
        if not self._name_year:
            return 0
        n = 0
        lines = text.split("\n")
        if len(lines) < 3 and len(text) > 5000:          # a minified file: one row per object
            lines = text.replace("},{", "},\n{").split("\n")
        for line in lines:
            if not YEAR.search(line) or len(line) > 1500:
                continue
            fl = ntok(line)
            for ph, yrs in self._name_year.items():
                if yrs and ph in fl and any(re.search(r"(?<!\d)%s(?!\d)" % y, line) for y in yrs):
                    n += 1
                    break
        return n

    def data_rules(self, w):
        """Who is in the data must be who the rule says."""
        out = []
        inv = {v: k for k, v in w["ledger"].items()}
        for r in w["living"]:
            i = inv.get(r["slug"])
            if i is None:
                out.append(("GED-CLASS", r["slug"], "a living row whose slug is not in the frozen ledger"))
            elif i in self.held:
                out.append(("GED-CLASS", r["slug"], "a person the rule HOLDS OUT has a page"))
            elif i not in self.living:
                out.append(("GED-CLASS", r["slug"], "a person the rule calls dead has a living page"))
        for r in list(w["people"]) + list(w["ancestors"]):
            if r.get("id") in self.living:
                out.append(("GED-CLASS", r.get("slug", "?"), "a person the rule calls living is published as somebody who has died"))
            if r.get("id") in self.held:
                out.append(("GED-CLASS", r.get("slug", "?"), "a person the rule HOLDS OUT is published"))
        for r in rows_of(w):
            for g in (r.get("rel") or {}).values():
                for x in g:
                    if not x.get("living") and x.get("id") in self.living:
                        out.append(("GED-CLASS", r.get("slug", "?"),
                                    "a relation entry carries a living person's years as if they had died"))
                    if x.get("id") in self.held:
                        out.append(("GED-CLASS", r.get("slug", "?"), "a held-out person is named as a relative"))
                    if x.get("living"):
                        if fold(x.get("name", "")) not in {fold(self.display[i]) for i in self.named}:
                            out.append(("GED-CLASS", r.get("slug", "?"),
                                        "a living relation entry whose name is nobody the rule names"))
        for i in w["ledger"]:
            if i in self.held:
                out.append(("GED-CLASS", "person-slugs.json", "a held-out person has a slug"))
        rule = w.get("rule") or {}
        j = rule.get("judged") or {}
        want = {"living": len(self.living), "heldOut": len(self.held)}
        for k, v in want.items():
            if j.get(k) != v:
                out.append(("GED-CLASS", "livingrule.json", f"{k} is {j.get(k)}, the tree gives {v}"))
        return out


def rule_ged(w, ged=None, corpus_extra=None):
    """(failures, advisories). The corpus is every built file, every served file
    and every tracked data file."""
    ged = ged or Ged(w)
    corpus = {("dist:" + k): v for k, v in w["pages"].items()}
    corpus.update({("dist:" + k): v for k, v in w["extra"].items()})
    corpus["dist:sitemap.xml"] = w["sitemap"]
    corpus["dist:searchindex.json"] = w["index"]
    corpus.update(tracked_corpus())
    if corpus_extra:
        corpus.update(corpus_extra)
    out, adv = ged.scan(corpus)
    out += ged.data_rules(w)
    # GED-SOURCE: the rest of what the tree holds for a published living person
    # must not be on their own page
    inv = {v: k for k, v in w["ledger"].items()}
    for r in w["living"]:
        i = inv.get(r["slug"])
        page = corpus.get("dist:" + page_path(r["slug"]))
        if i is None or i not in ged.events or page is None:
            continue
        strings = set(ged.events[i]["cites"]) | set(ged.events[i]["notes"])
        for e in ged.events[i]["events"]:
            strings.add(e["text"])
            if "," in (e.get("place") or ""):
                strings.add(e["place"])
        strings.discard(", ".join(x for x in (r.get("town"), r.get("country")) if x))
        for st in {x for x in strings if len(x) >= 12}:
            if st in page or htmllib.escape(st) in page:
                out.append(("GED-SOURCE", "dist:" + page_path(r["slug"]),
                            "something the tree records beyond a name, a town and a country"))
                break
    return out, adv


# ---- the controls ------------------------------------------------------------

def selftest(w, quiet=False):
    """PLANT A FAULT FOR EVERY RULE and show it is caught. And show that a clean
    build passes, that an empty one does not, and that the page rules object to
    the page of somebody who has died (the positive control)."""
    base = run_rules(w)
    ok = True
    print(f"  control   the real build: {len(base)} finding(s)  [expect 0]")
    ok &= not base

    r0 = next(r for r in w["living"] if r.get("town"))            # a living person with a town
    r1 = next(r for r in w["living"])
    names_only = livingnames.Names(*_names(w))
    nonsake = next((n for n in names_only.living
                    if n not in names_only.namesakes and len(livingnames.norm(n).split()) >= 2), None)
    allv = all_living_names(w)
    s0 = allv[0] if allv else None
    mixed = mixed_names(w)
    m0 = mixed[0] if mixed else None

    def plant(label, rule, fn):
        w2 = clone(w)
        fn(w2)
        found = {f[0] for f in run_rules(w2)}
        hit = rule in found
        print(f"  {'caught ' if hit else 'MISSED '}   {label}  [{rule}]")
        return hit

    def edit_page(slug, fn):
        def go(w2):
            k = page_path(slug)
            w2["pages"][k] = fn(w2["pages"][k])
        return go

    def into_main(frag):
        return lambda h: h.replace("</main>", frag + "</main>", 1)

    def first_rel(w2, key, pred):
        for r in w2["people"]:
            for g in r["rel"].values():
                for x in g:
                    if pred(x):
                        return x
        raise RuntimeError("nothing to plant in")

    results = []
    results.append(plant("noindex taken off a living page", "PAGE-NOINDEX",
                         edit_page(r0["slug"], lambda h: NOINDEX.sub("", h))))
    results.append(plant("a canonical naming another page, on a living page", "PAGE-CANON",
                         edit_page(r0["slug"], lambda h: re.sub(
                             r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*"', r'\1https://x/other/"', h, count=1))))
    results.append(plant("JSON-LD Person on a living page", "PAGE-LDJSON",
                         edit_page(r0["slug"], lambda h: h.replace("</head>", '<script type="application/ld+json">{"@type":"Person"}</script></head>', 1))))
    results.append(plant("a table on a living page", "PAGE-TABLE",
                         edit_page(r0["slug"], into_main("<table><tr><td>x</td></tr></table>"))))
    results.append(plant("a photograph on a living page", "PAGE-MEDIA",
                         edit_page(r0["slug"], into_main('<img src="/photos/x.jpg" alt="">'))))
    results.append(plant("a birth date in the page body", "PAGE-YEAR",
                         edit_page(r0["slug"], into_main("<p>Born 3 May 1799</p>"))))
    results.append(plant("a bare year in the page body", "PAGE-YEAR",
                         edit_page(r0["slug"], into_main("<p>b. 1799</p>"))))
    results.append(plant("a Born line beside Name and Place", "PAGE-ROWS",
                         edit_page(r0["slug"], into_main('<p class="lede"><span class="lab">Born</span> x</p>'))))
    results.append(plant("a longer place than town and country", "PAGE-ROWS",
                         edit_page(r0["slug"], lambda h: h.replace(r0["town"], "12 High Street, " + r0["town"], 1))))
    results.append(plant("a link to a record out of the archive", "PAGE-LINKS",
                         edit_page(r0["slug"], into_main('<a href="https://www.myheritage.com/x">record</a>'))))
    results.append(plant("a tree record id in a living page", "PAGE-RECORD",
                         edit_page(r0["slug"], into_main("<!-- @I123456@ -->"))))
    results.append(plant("a living page that was not built", "PAGE-MISSING",
                         lambda w2: w2["pages"].pop(page_path(r0["slug"]))))
    results.append(plant("a living page listed in the sitemap", "SITEMAP",
                         lambda w2: w2.__setitem__("sitemap", w2["sitemap"].replace(
                             "</urlset>", f"<url><loc>https://x/people/{r0['slug']}/</loc></url></urlset>"))))
    results.append(plant("a living page in the search index", "INDEX-HREF",
                         lambda w2: w2.__setitem__("index", w2["index"][:-1] + ',{"k":"Person","t":"x","s":"","h":"/people/%s/","q":"x"}]' % r0["slug"])))
    if nonsake:
        results.append(plant("a living person as a Person row", "INDEX-NAME",
                             lambda w2: w2.__setitem__("index", w2["index"][:-1] + ',{"k":"Person","t":"%s","s":"","h":"/x/","q":"x"}]' % nonsake)))
    results.append(plant("a birth date added to a living.json row", "DATA-KEYS",
                         lambda w2: w2["living"][0].__setitem__("born", "3 May 1799")))
    results.append(plant("an occupation added to a living.json row", "DATA-KEYS",
                         lambda w2: w2["living"][0].__setitem__("occupations", [{"what": "x"}])))
    results.append(plant("a place with a street number", "DATA-PLACE",
                         lambda w2: w2["living"].__setitem__(0, {**w2["living"][0], "town": "12 High Street"})))

    def living_rel(w2):
        return first_rel(w2, None, lambda x: x.get("living"))
    results.append(plant("a birth year on a living relation entry", "DATA-KEYS",
                         lambda w2: living_rel(w2).__setitem__("born", 1799)))
    results.append(plant("a tree id on a living relation entry", "DATA-KEYS",
                         lambda w2: living_rel(w2).__setitem__("id", "@I1@")))
    results.append(plant("a marriage date on a living spouse", "DATA-KEYS",
                         lambda w2: living_rel(w2).__setitem__("marriedDate", "3 May 1799")))
    results.append(plant("the old withheld marker coming back", "DATA-KEYS",
                         lambda w2: w2["people"][0]["rel"]["parents"].append({"withheld": True})))
    results.append(plant("a published person who has died with a field the archive never wrote", "DATA-KEYS",
                         lambda w2: w2["people"][0].__setitem__("zzPlantedField", "x")))
    results.append(plant("a ledger line for somebody who has no page", "LEDGER",
                         lambda w2: w2["ledger"].__setitem__("@IZZ1@", "zz-plant-nobody")))
    results.append(plant("a person named with no page (no slug)", "NAMED-PAGE",
                         lambda w2: w2["people"][0]["rel"]["children"].append({"name": "Zz Plant", "slug": None, "id": "@I1@"})))
    results.append(plant("a person named with a slug nobody published", "NAMED-PAGE",
                         lambda w2: w2["people"][0]["rel"]["children"].append({"name": "Zz Plant", "slug": "zz-plant-nobody", "id": "@I1@"})))
    results.append(plant("a published person whose page was not built", "NAMED-PAGE",
                         lambda w2: w2["pages"].pop(page_path(w2["people"][0]["slug"]))))
    results.append(plant("a Kosina person with no page", "NAMED-PAGE",
                         lambda w2: w2["kosina"]["people"][0].__setitem__("slug", "")))
    results.append(plant("a register row for a tree person with no page", "NAMED-PAGE",
                         lambda w2: next(x for x in w2["register"] if x["kind"] == "tree").__setitem__("slug", None)))
    if s0:
        results.append(plant("an all-living name page without noindex", "WHO-NOINDEX",
                             lambda w2: w2["pages"].__setitem__(who_path(s0), NOINDEX.sub("", w2["pages"][who_path(s0)]))))
        results.append(plant("an all-living name page pointing its canonical elsewhere", "WHO-CANON",
                             lambda w2: w2["pages"].__setitem__(who_path(s0), re.sub(
                                 r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*"', r'\1https://x/other/"', w2["pages"][who_path(s0)], count=1))))
        results.append(plant("an all-living name page in the sitemap", "SITEMAP",
                             lambda w2: w2.__setitem__("sitemap", w2["sitemap"].replace(
                                 "</urlset>", f"<url><loc>https://x/who/{s0}/</loc></url></urlset>"))))
    if m0:
        results.append(plant("a name page with a bearer who has died made noindex", "WHO-NOINDEX",
                             lambda w2: w2["pages"].__setitem__(who_path(m0), w2["pages"][who_path(m0)].replace(
                                 "</head>", '<meta name="robots" content="noindex"></head>', 1))))
    results.append(plant("an empty build", "EMPTY", lambda w2: (w2["pages"].clear(), w2.__setitem__("sitemap", ""))))
    results.append(plant("no living people at all in the data", "EMPTY", lambda w2: w2["living"].clear()))
    results.append(plant("a noindex page left in the sitemap", "SITEMAP",
                         lambda w2: w2.__setitem__("sitemap", w2["sitemap"].replace(
                             "</urlset>", f"<url><loc>https://x/people/{r1['slug']}/</loc></url></urlset>"))))
    results.append(plant("a file git does not track under the scanned directories", "FILES-UNTRACKED",
                         lambda w2: w2.__setitem__("untracked", ["site/src/data/zz-planted.json"])))
    results.append(plant("the record of the living rule missing", "RULE-RECORD",
                         lambda w2: w2.__setitem__("rule", None)))
    results.append(plant("the record of the living rule naming a tree id", "RULE-RECORD",
                         lambda w2: w2["rule"].__setitem__("note", "@I1@")))
    ok &= all(results)
    rr = selftest_rule()
    for k, v in rr.items():
        print(f"  {'caught ' if v else 'MISSED '}   the rule, on a planted tree: {k}")
    ok &= all(rr.values())

    # POSITIVE CONTROL: the same page rules, aimed at the page of somebody who has
    # died, must object. A check that cannot fire on the thing it is looking for
    # proves nothing.
    dead = next(p for p in w["people"] if p.get("died") and w["pages"].get(page_path(p["slug"])))
    found = {f[0] for f in page_rules(w["pages"][page_path(dead["slug"])], None, dead["slug"])}
    want = {"PAGE-NOINDEX", "PAGE-LDJSON", "PAGE-YEAR", "PAGE-TABLE", "PAGE-ROWS"}
    print(f"  control   the page rules on a page of someone who has died object: {sorted(found)}  "
          f"[expect {sorted(want)} among them]")
    ok &= want <= found
    paths = {re.sub(r"^https?://[^/]+", "", l) for l in sitemap_locs(w)}
    dead_in_sitemap = sum(1 for p in w["people"] if f"/people/{p['slug']}/" in paths)
    print(f"  control   dead people's pages in the sitemap: {dead_in_sitemap} of {len(w['people'])}  [expect most]")
    ok &= dead_in_sitemap > len(w["people"]) * 0.9
    idx = json.loads(w["index"])
    npers = sum(1 for r in idx if r.get("k") == "Person")
    print(f"  control   Person rows in the search index: {npers}  [expect > 0]")
    ok &= npers > 0
    return ok


def selftest_rule():
    """The living rule itself, run through the gate's OWN judge() and the kit's
    living_rule on a synthetic tree whose people no real person can be."""
    Y = 2026

    def rec(by=None, dead=False, cites=(), parents=()):
        return {"by": by, "dead": dead, "cites": list(cites), "parents": list(parents)}

    P = {
        "A": rec(Y - 40),                                          # an adult, living
        "B": rec(Y - 40, dead=True),                               # recorded dead (even undated)
        "C": rec(Y - 80),                                          # 80: still living
        "D": rec(Y - 81),                                          # 81: not living
        "E": rec(Y - 10, parents=["A"]),                           # a child: living, held out
        "F": rec(Y - 17, parents=["A"]),                           # 17 by year: held out
        "G": rec(Y - 18, parents=["A"]),                           # 18 by year: an adult, named
        "H": rec(None, parents=["A"]),                             # no birth year, living parent: held out
        "I": rec(None, parents=["B"]),                             # no birth year, parent dead: not held, not living
        "J": rec(Y - 40, cites=["FamilySearch Family Tree — https://x"]),     # public source: not living
        "K": rec(Y - 40, cites=["Geni World Family Tree — https://www.myheritage.com/research/record-1-geni"]),  # a tree: still living
        "L": rec(Y - 10, cites=["FamilySearch Family Tree"], parents=["A"]),       # a child with a public source: not held
        "M": rec(Y - 40, cites=["1851 England & Wales Census — https://www.myheritage.com/research/record-1-census"]),  # a record collection
        "N": rec(Y - 150),                                         # long dead
    }
    live, held = judge(P, Y)
    return {
        "an adult with nothing recorded is living": "A" in live and "A" not in held,
        "a recorded death is a death": "B" not in live,
        "eighty years by year is still living": "C" in live,
        "eighty-one is not": "D" not in live,
        "a child is held out": "E" in held,
        "seventeen by year is held out": "F" in held,
        "eighteen by year is named": "G" in live and "G" not in held,
        "no birth year and a living parent is held out": "H" in held and "H" not in live,
        "no birth year and a dead parent is not held out": "I" not in held and "I" not in live,
        "a public source means not living": "J" not in live,
        "a family-tree citation does not": "K" in live,
        "a public source lifts the hold on a child": "L" not in held and "L" not in live,
        "a record collection counts": "M" not in live,
        "long dead is not living": "N" not in live,
    }


def selftest_ged(w):
    """The same, for the rules that need the GEDCOM. One load of the tree; every
    plant costs a scan of the planted text."""
    ged = Ged(w)
    base, adv = rule_ged(w, ged)
    print(f"  control   the real build against the whole tree: {len(base)} failure(s)  [expect 0]; "
          f"{len(adv)} advisory finding(s) in hand-written pages")
    ok = not base
    two = lambda i: len(ged.display[i].split()) >= 2
    held_i = next(i for i in sorted(ged.held) if two(i) and fold(ged.display[i]) in
                  {fold(n) for n in ged.nm_held.living if n not in ged.nm_held.namesakes})
    held_name = ged.display[held_i]
    held_dated = next((i for i in sorted(ged.held) if two(i) and any(date_forms(e.get("date", ""))
                                                                    for e in ged.events[i]["events"])), None)
    named_i = next(iter(sorted(ged.named)))
    dead_i = next(i for i in sorted(ged.dead) if two(i))
    res = []

    def hit(label, rule, found):
        got = rule in {f[0] for f in found}
        print(f"  {'caught ' if got else 'MISSED '}   {label}  [{rule}]")
        return got

    def scan(label, rule, extra, adv_ok=False):
        f, a = ged.scan(extra)
        return hit(label, rule, a if adv_ok else f)

    def data(label, rule, mut):
        w2 = clone(w)
        mut(w2)
        return hit(label, rule, ged.data_rules(w2))

    res.append(scan("a held-out person's NAME in a derived data file", "GED-HELD",
                    {"tracked:site/src/data/x.json": '{"name":"%s"}' % held_name}))
    res.append(scan("a held-out person's TREE ID in a served page", "GED-HELD",
                    {"dist:index.html": "<!-- %s -->" % held_i}))
    res.append(scan("a held-out person's name on a built page", "GED-HELD",
                    {"dist:people/x/index.html": f"<p>{held_name}</p>"}))
    res.append(scan("a held-out person's name in a tsv", "GED-HELD",
                    {"tracked:data/x.tsv": f"{held_name}\t1"}))
    if held_dated:
        e = next(e for e in ged.events[held_dated]["events"] if date_forms(e.get("date", "")))
        hd = sorted(date_forms(e["date"]))[0]
        res.append(scan("a held-out person's date beside their name", "GED-DATE",
                        {"tracked:site/src/data/x.json": f'{{"n":"{ged.display[held_dated]}","d":"{hd}"}}'}))
    ged.year_beside_name("")          # builds the table of name phrases and years
    yi = next((i for i in sorted(ged.living | ged.held) if ged.recs[i]["by"] and two(i)
               and set(livingnames.folded_phrases(ged.display[i])) & set(ged._name_year)), None)
    if yi:
        res.append(scan("a living person's birth year on the line that names them", "GED-YEAR",
                        {"tracked:site/src/data/x.json": '  "line": "%s born %s",' % (ged.display[yi], ged.recs[yi]["by"])}))
    res.append(data("a person the rule HOLDS OUT given a living page", "GED-CLASS",
                    lambda w2: (w2["living"].append({"slug": "zzplant", "name": "Zz Plant", "town": "", "country": "",
                                                     "living": True, "rel": {}}), w2["ledger"].__setitem__(held_i, "zzplant"))))
    res.append(data("a person the tree records as DEAD given a living page", "GED-CLASS",
                    lambda w2: (w2["living"].append({"slug": "zzplant", "name": "Zz Plant", "town": "", "country": "",
                                                     "living": True, "rel": {}}), w2["ledger"].__setitem__(dead_i, "zzplant"))))
    res.append(data("a held-out person named as a relative", "GED-CLASS",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": "Zz Plant", "slug": "zz", "id": held_i, "born": 1, "died": 2})))
    res.append(data("a living relation entry whose name is nobody the rule names", "GED-CLASS",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": ged.display[dead_i], "slug": "zz", "living": True})))
    res.append(data("a LIVING person published as somebody who has died", "GED-CLASS",
                    lambda w2: w2["people"].append({"id": named_i, "slug": "zzplant", "name": "Zz Plant", "rel": {}})))
    res.append(data("a held-out person published as somebody who has died", "GED-CLASS",
                    lambda w2: w2["people"].append({"id": held_i, "slug": "zzplant", "name": "Zz Plant", "rel": {}})))
    res.append(data("a living person given a dead relative's years", "GED-CLASS",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": "Zz Plant", "slug": "zz", "id": named_i, "born": 1, "died": 2})))
    res.append(data("a held-out person with a slug in the ledger", "GED-CLASS",
                    lambda w2: w2["ledger"].__setitem__(held_i, "zzplant")))
    res.append(data("the record of the rule saying a different number living", "GED-CLASS",
                    lambda w2: w2["rule"]["judged"].__setitem__("living", w2["rule"]["judged"]["living"] + 1)))
    # dates and sources
    inv = {v: k for k, v in w["ledger"].items()}
    dated = next((i for i in sorted(ged.named) for e in ged.events[i]["events"] if date_forms(e.get("date", ""))), None)
    some = next((r["slug"] for r in w["living"]), None)
    if dated:
        e = next(e for e in ged.events[dated]["events"] if date_forms(e.get("date", "")))
        d = sorted(date_forms(e["date"]))[0]
        nm = ged.display[dated]
        res.append(scan("a named living person's real date on their own page", "GED-DATE",
                        {"dist:" + page_path(some): f"<p>{nm} born {d}</p>"}))
        res.append(scan("a living person's real date in a name page", "GED-DATE",
                        {"dist:who/x/index.html": f"<p>{nm} {d}</p>"}))
        res.append(scan("a living person's real date in a derived data file", "GED-DATE",
                        {"tracked:site/src/data/x.json": '{"name":"%s","d":"%s"}' % (nm, d)}))
        saved = ged.known
        ged.known = {"x-prose": 1}
        try:
            res.append(scan("one listed date in a listed hand-written page is known, not a failure", "GED-DATE",
                            {"dist:x-prose/index.html": f"<p>{nm} {d}</p>"}, adv_ok=True))
            res.append(scan("a second date in that page fails the build", "GED-DATE",
                            {"dist:x-prose/index.html": f"<p>{nm} {d} {d.upper()} and again {d}</p>"}))
        finally:
            ged.known = saved
    src = next(((r["slug"], s_) for r in w["living"] for s_ in ged.events.get(inv.get(r["slug"]), {}).get("cites", []) if len(s_) >= 12), None)
    if src:
        res.append(hit("a source the tree holds for a published living person, on their page", "GED-SOURCE",
                       rule_ged(w, ged, {"dist:" + page_path(src[0]): f"<li>{htmllib.escape(src[1])}</li>"})[0]))
    else:
        print("  note      no published living person has a source string to plant; GED-SOURCE not exercised")
    return ok and all(res)


# ---- main --------------------------------------------------------------------

def report(findings, w, quiet, every=False):
    names = names_of(w)
    live_pages = sum(1 for r in w["living"] if page_path(r["slug"]) in w["pages"])
    noindexed = sum(1 for r in w["living"] if NOINDEX.search(w["pages"].get(page_path(r["slug"]), "")[:6000]))
    locs = {re.sub(r"^https?://[^/]+", "", l) for l in sitemap_locs(w)}
    in_sitemap = sum(1 for r in w["living"] if f"/people/{r['slug']}/" in locs)
    try:
        idx = json.loads(w["index"]) if w["index"] else []
    except ValueError:
        idx = []
    liv_h = {f"/people/{x['slug']}/" for x in w["living"]}
    in_index = sum(1 for r in idx if r.get("h") in liv_h)
    allv = all_living_names(w)
    allv_noindex = sum(1 for s in allv if NOINDEX.search(w["pages"].get(who_path(s), "")[:6000]))
    if findings:
        print(f"  FAIL  living-standard   {len(findings)} finding(s)")
        seen = collections.Counter()
        for rule, where, what in findings:
            seen[rule] += 1
            if every or seen[rule] <= 3:
                print(f"          {rule:<13} {where} — {what}")
        for rule, n in seen.items():
            if n > 3 and not every:
                print(f"          {rule:<13} … and {n - 3} more")
        return 1
    if not quiet:
        print(f"  ok    living-standard   {len(w['living'])} living pages ({live_pages} built), "
              f"{noindexed} noindex, {in_sitemap} in the sitemap, {in_index} in the search index; "
              f"{len(allv)} all-living name pages, {allv_noindex} noindex; "
              f"{len(names.namesakes)} living names are also a dead person's and are not told apart")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=None)
    ap.add_argument("--selftest", action="store_true",
                    help="plant a fault for every rule that needs no GEDCOM and show each is caught (seconds; runs in the build)")
    ap.add_argument("--selftest-ged", action="store_true",
                    help="the same for the rules that need the GEDCOM (minutes; local only)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--advisory", action="store_true", help="list the advisory findings")
    ap.add_argument("--all", action="store_true", help="print every finding, not the first three of each rule")
    ap.add_argument("--no-ged", action="store_true", help="skip the checks that need the GEDCOM")
    a = ap.parse_args()
    dist = a.dist or os.path.join(ROOT, "site", os.environ.get("ARCHIVE_OUT") or "dist")
    if not os.path.isdir(dist):
        print(f"livingcheck: no {dist} — build first")
        return 1
    w = load_world(dist)
    findings = run_rules(w)
    ged = ged_available() and not a.no_ged
    advisory = []
    if ged and not findings:
        f2, advisory = rule_ged(w)
        findings += f2
    code = report(findings, w, a.quiet, a.all)
    if advisory and not a.quiet:
        kinds = collections.Counter(x[0] for x in advisory)
        print("        note  living-standard   advisory, not a failure: the hand-written pages carry "
              + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()))
              + " finding(s) (research prose that names or dates a person the rule calls living; "
                "not rewritten here). Run with --advisory to list them.")
    if advisory and a.advisory:
        for k, where, what in advisory:
            print(f"          {k:<9} {where} — {what}")
    if not ged and not a.quiet:
        print("        note  living-standard   the checks that need the GEDCOM (GED-CLASS, GED-HELD, GED-DATE, "
              "GED-YEAR, GED-SOURCE) did not run: no sources/*.ged here. They run on a local build.")
    if a.selftest or a.selftest_ged:
        print("  --selftest")
        ok = True
        if a.selftest:
            ok &= selftest(w, a.quiet)
        if a.selftest_ged:
            if not ged:
                print("  FAIL      --selftest-ged needs sources/*.ged, which is not here")
                ok = False
            else:
                ok &= selftest_ged(w)
        print("  selftest " + ("PASSED: every planted fault was caught" if ok else "FAILED"))
        code = code or (0 if ok else 1)
    return code


if __name__ == "__main__":
    sys.exit(main())
