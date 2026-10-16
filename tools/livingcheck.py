#!/usr/bin/env python3
"""Refuse a build that breaks the living-people standard.

THE STANDARD (David, 16 October 2026, for every archive). A living person is
shown by a name, a relationship, and their town and country, and nothing else:
no dates, no records, no sources, no photograph, no structured data. Their page
is `noindex`, which is also what keeps it out of the sitemap and the search
index, and a name page whose every bearer is living is `noindex` too and
carries no canonical pointing elsewhere.

Until that day this archive named no living person at all, and its gate was the
kit's `checkliving.py --policy named-bare`, which reads flags in committed data
and so could never fail here: the data held no living flag and the build held no
living page. That gate still runs. This one enforces the rule the archive now
keeps, and it can fail, which is the point (see --selftest).

WHAT IT READS. The built pages, dist/sitemap.xml, dist/searchindex.json, and
the committed data (living.json, people.json, ancestors.json). It never needs
the GEDCOM, so CI runs all of it. When the GEDCOM IS present (a local build) it
also runs the checks that need the whole tree, and says so; when it is not, it
says that those did not run rather than passing them.

THE RULES (each is a name in the output and in --selftest):

  DATA-KEYS    living.json rows carry only slug, name, town, country, living, rel.
               A living relation entry carries only slug, name, living (so no
               tree id, no year, no marriage date). No `withheld` marker survives.
  DATA-PLACE   a town or country is one place name: no digit, no comma.
  PAGE-MISSING every living row has its page.
  PAGE-NOINDEX a living page says noindex.
  PAGE-CANON   and carries no canonical naming another page (the kit gives every
               page one naming itself).
  PAGE-LDJSON  and no structured data of any kind.
  PAGE-MEDIA   and no image, video, audio, frame or embed.
  PAGE-YEAR    and no year anywhere in <main>, outside a dead relative's own
               dates in the family chart.
  PAGE-ROWS    and only the rows Name and Place, with the place being exactly
               the town and country in the data.
  PAGE-LINKS   and no link out of the archive (no record to follow).
  PAGE-RECORD  and no tree record id.
  WHO-NOINDEX  a name page whose bearers are all living says noindex,
  WHO-CANON    and carries no canonical naming another page.
  SITEMAP      no living page and no all-living name page is in sitemap.xml.
  INDEX-HREF   none is in the search index,
  INDEX-NAME   and no Person row is a living person's name (an exact namesake
               of a dead person cannot be told apart and is counted, not
               failed). Hand-written pages that name somebody the tree calls
               living are the archive's own prose and are not this rule's
               business; the page of a living person is.
  EMPTY        a build with nothing to check does not pass.

  and, only when the GEDCOM is present:

  GED-DATE     no full date of any living person (all of them, published or
               not) appears in the build or in any file the tools derive, in a
               text that also names them. Pages whose HAND-WRITTEN text already
               carries one are counted in sources/living-prose.psv (page and
               number only, never the date); one more than listed fails.
  GED-NAME     (advisory only) living people who are not published but are named
               in the archive's own prose are listed and counted. The standard
               permits a living person's name; this lists where the research
               text already names one the archive gives no page.
  GED-SOURCE   nothing the tree records for a published living person beyond a
               name, a town and a country (a source, a note, an occupation, an
               event detail, a longer birth place) appears in the build.

Usage:  python3 tools/livingcheck.py [--dist DIR] [--selftest] [--selftest-ged] [--advisory] [--quiet]
"""
import argparse
import collections
import copy
import html as htmllib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
sys.path.insert(0, HERE)
import livingnames  # noqa: E402

fold = livingnames.fold

ROW_KEYS = {"slug", "name", "town", "country", "living", "rel"}
REL_LIVING_KEYS = {"slug", "name", "living"}
REL_DEAD_KEYS = {"id", "slug", "name", "born", "died", "marriedDate", "marriedPlace"}
REL_GROUPS = {"parents", "spouses", "siblings", "children"}
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
NOINDEX = re.compile(r'<meta[^>]*name=["\']robots["\'][^>]*noindex', re.I)
CANON = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', re.I)
LDJSON = re.compile(r'application/ld\+json', re.I)
MEDIA = re.compile(r"<(img|picture|video|audio|iframe|object|embed|source)\b", re.I)
EXTLINK = re.compile(r'href=["\'](?:https?:)?//', re.I)
RECORDID = re.compile(r"@I\d+@")
MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
DTSPAN = re.compile(r'<span class="dt">.*?</span>', re.S)
TAGS = re.compile(r"<[^>]+>")


def slugify(s):
    """What who/[slug].astro does, character for character."""
    import unicodedata
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


def text_of(fragment):
    return htmllib.unescape(re.sub(r"\s+", " ", TAGS.sub(" ", fragment))).strip()


# ---- the world the rules read ------------------------------------------------

SERVED_TEXT = (".json", ".xml", ".txt", ".js", ".css", ".svg", ".tsv", ".csv", ".webmanifest", ".psv")
SCANNED_DIRS = ("site/src", "site/public", "data", "sources")
DEAD_ROW_KEYS = {"id", "slug", "name", "given", "surname", "nick", "sex", "born", "bornPlace",
                 "died", "diedPlace", "cause", "burial", "baptised", "baptisedPlace",
                 "occupations", "byear", "dyear", "sources", "notes", "events", "family",
                 "ahn", "gen", "rel"}


def load_rule():
    p = os.path.join(ROOT, "sources", "living-rule.json")
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
    """Files under the scanned directories that git does not track and does not
    ignore: invisible to a scan of tracked files, and about to be published by a
    careless `git add`. None when this is not a git checkout."""
    out = git("ls-files", "-z", "--others", "--exclude-standard")
    if out is None:
        return None
    return [x for x in out.split("\0") if x and x.startswith(tuple(d + "/" for d in SCANNED_DIRS))]


def load_world(dist):
    def J(f):
        with open(os.path.join(DATA, f), encoding="utf-8") as fh:
            return json.load(fh)

    w = {"living": J("living.json"), "people": J("people.json"),
         "ancestors": J("ancestors.json"), "pages": {}, "extra": {},
         "sitemap": "", "index": "", "dist": dist,
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
    for k in ("living", "people", "ancestors"):
        w2[k] = copy.deepcopy(w[k])
    return w2


def page_path(slug):
    return f"people/{slug}/index.html"


def who_path(slug):
    return f"who/{slug}/index.html"


def name_groups(w):
    by = collections.defaultdict(list)
    for r in list(w["people"]) + list(w["living"]):
        if r.get("name") and r.get("slug"):
            by[slugify(r["name"])].append(r)
    return by


def all_living_names(w):
    return sorted(s for s, rows in name_groups(w).items() if rows and all(r.get("living") for r in rows))


def names_of(w):
    return livingnames.Names(*_names(w))


def _names(w):
    living = {r["name"] for r in w["living"]}
    for r in list(w["living"]) + list(w["people"]) + list(w["ancestors"]):
        for g in (r.get("rel") or {}).values():
            for x in g:
                if x.get("living"):
                    living.add(x["name"])
    dead = {p["name"] for p in list(w["people"]) + list(w["ancestors"]) if p.get("name")}
    # and the dead who are only named as somebody's relative: they are on the page
    # as dead people, and a living namesake cannot be told from them
    for r in list(w["living"]) + list(w["people"]) + list(w["ancestors"]):
        for g in (r.get("rel") or {}).values():
            for x in g:
                if not x.get("living") and x.get("name"):
                    dead.add(x["name"])
    return sorted(n for n in living if n), sorted(dead)


# ---- rules -------------------------------------------------------------------

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
    rows = list(w["living"]) + list(w["people"]) + list(w["ancestors"])
    for r in rows:
        for gname, g in (r.get("rel") or {}).items():
            for x in g:
                keys = set(x)
                if x.get("living"):
                    bad = keys - REL_LIVING_KEYS
                    if bad:
                        out.append(("DATA-KEYS", r.get("slug", "?"),
                                    f"a living relative in {gname} carries " + ", ".join(sorted(bad))))
                elif "withheld" in keys:
                    out.append(("DATA-KEYS", r.get("slug", "?"),
                                "a withheld entry: a person held out is not drawn at all"))
                elif r.get("living") and keys & {"marriedDate", "marriedPlace"}:
                    out.append(("DATA-KEYS", r.get("slug", "?"),
                                "a marriage date on a living person's relation"))
                elif keys - REL_DEAD_KEYS:
                    out.append(("DATA-KEYS", r.get("slug", "?"),
                                "a relative carries " + ", ".join(sorted(keys - REL_DEAD_KEYS))))
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
    if MEDIA.search(main):
        out.append(("PAGE-MEDIA", who, "carries an image, frame or embed"))
    if EXTLINK.search(main):
        out.append(("PAGE-LINKS", who, "links out of the archive"))
    if RECORDID.search(html):
        out.append(("PAGE-RECORD", who, "carries a tree record id"))
    visible = text_of(DTSPAN.sub(" ", main))
    ym = YEAR.search(visible)
    if ym:
        i = ym.start()
        out.append(("PAGE-YEAR", who, "a year in the page body: …" + visible[max(0, i - 30):i + 30] + "…"))
    desc = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
    if desc and YEAR.search(desc.group(1)):
        out.append(("PAGE-YEAR", who, "a year in the description"))
    if len(re.findall(r"<table\b", main)) != len(re.findall(r"</table>", main)):
        out.append(("PAGE-ROWS", who, "the record table is malformed (an unclosed table moves the page around)"))
    ths = [text_of(t) for t in re.findall(r"<th[^>]*>(.*?)</th>", main, re.S)]
    if set(ths) - {"Name", "Place"}:
        out.append(("PAGE-ROWS", who, "rows other than Name and Place: " + ", ".join(sorted(set(ths) - {"Name", "Place"}))))
    if row is not None:
        want = ", ".join(x for x in (row.get("town"), row.get("country")) if x)
        got = re.search(r"<th[^>]*>\s*Place\s*</th>\s*<td[^>]*>(.*?)</td>", main, re.S)
        if want and (not got or text_of(got.group(1)) != want):
            out.append(("PAGE-ROWS", who, "the Place row is not exactly the town and country"))
        if not want and got:
            out.append(("PAGE-ROWS", who, "a Place row for a person with no place in the data"))
        nm = re.search(r"<th[^>]*>\s*Name\s*</th>\s*<td[^>]*>(.*?)</td>", main, re.S)
        if not nm or text_of(nm.group(1)) != row.get("name"):
            out.append(("PAGE-ROWS", who, "the Name row is not the name in the data"))
    return out


def rule_pages(w):
    out = []
    for r in w["living"]:
        p = w["pages"].get(page_path(r["slug"]))
        if p is None:
            out.append(("PAGE-MISSING", r["slug"], "no page was built"))
            continue
        out += page_rules(p, r, r["slug"], page_path(r["slug"]))
    groups = name_groups(w)
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
    return out


def sitemap_locs(w):
    return set(re.findall(r"<loc>(.*?)</loc>", w["sitemap"]))


def rule_sitemap(w):
    out = []
    locs = sitemap_locs(w)
    origins = {re.match(r"(https?://[^/]+)", l).group(1) for l in locs if re.match(r"https?://", l)}
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


def rule_empty(w):
    out = []
    if not w["living"]:
        out.append(("EMPTY", "living.json", "no living person to check: the archive publishes some, "
                                              "so an empty list is a broken harvest, not a pass"))
    if len(w["pages"]) < 50:
        out.append(("EMPTY", w["dist"], f"only {len(w['pages'])} page(s) built"))
    if not w["sitemap"]:
        out.append(("EMPTY", "sitemap.xml", "there is no sitemap to check"))
    if not w["index"]:
        out.append(("EMPTY", "searchindex.json", "there is no search index to check"))
    return out


def rule_named(w):
    """EVERY PERSON THE ARCHIVE NAMES HAS A PAGE: every entry of every relation
    list, living or dead, links to a page that was built."""
    out, seen = [], set()
    for r in list(w["living"]) + list(w["people"]) + list(w["ancestors"]):
        for g in (r.get("rel") or {}).values():
            for x in g:
                slug = x.get("slug")
                if not slug:
                    out.append(("NAMED-PAGE", r.get("slug", "?"), "a relative is named and has no page"))
                elif page_path(slug) not in w["pages"] and slug not in seen:
                    out.append(("NAMED-PAGE", slug, "a relative is named and their page was not built"))
                    seen.add(slug)
    return out


def rule_files(w):
    out = []
    if w.get("untracked"):
        out.append(("FILES-UNTRACKED", w["untracked"][0],
                    f"{len(w['untracked'])} file(s) under the scanned directories are neither tracked "
                    "nor ignored, so a scan of tracked files cannot see them: git add them first"))
    r = w.get("rule")
    c = (r or {}).get("counts") or {}
    if not r or not r.get("rules") or c.get("living") is None or c.get("heldOut") is None:
        out.append(("RULE-RECORD", "sources/living-rule.json",
                    "the record of the living rule (by rule, never by person) is missing or malformed"))
    elif set(json.dumps(r)) and re.search(r"@I\d+@", json.dumps(r)):
        out.append(("RULE-RECORD", "sources/living-rule.json", "the record names a tree id: it must record rules and counts only"))
    return out


def run_rules(w):
    out = rule_empty(w)
    if out:
        return out          # nothing else can mean anything on a build with nothing in it
    names = names_of(w)
    return rule_data(w) + rule_named(w) + rule_files(w) + rule_pages(w) + rule_sitemap(w) + rule_index(w, names)


# ---- the rules that need the whole tree (local builds only) -------------------

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


def ged_available():
    d = os.path.join(ROOT, "sources")
    return os.path.isdir(d) and any(f.endswith(".ged") for f in os.listdir(d))


PROSE = os.path.join(ROOT, "sources", "living-prose.psv")


def known_prose():
    """page|count|why — pages whose hand-written text already carries a living
    person's full date, found on 16 October 2026 when this gate first looked.
    The file records the PAGE and HOW MANY, never the date or the person: a
    list of living people's dates is exactly what must not be committed.
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


def generated(key):
    """Pages and files that are WRITTEN BY THE BUILD out of data, as opposed to
    the hand-written pages: a living person's date in one of these is a fault in
    the generator. In a hand-written page it is the research prose, which this
    gate reports and does not rewrite."""
    return (key.startswith("committed:") or key.startswith("dist:people/")
            or key.startswith("dist:who/") or key.endswith(".json")
            or key in ("dist:sitemap.xml",))


def first_dates(text, forbid, owners_names):
    """A living person's date counts only where the text ALSO names them: a date
    is a coincidence between two people far more often than it is a leak, and
    the kit's gate learned the same thing. forbid: date -> tree ids;
    owners_names: id -> folded name phrases."""
    ftext = None
    found = []
    for rx in DATE_TOKENS:
        for m in rx.finditer(text):
            owners = forbid.get(m.group(0))
            if not owners:
                continue
            if ftext is None:
                ftext = fold(htmllib.unescape(TAGS.sub(" ", text)))
            if any(any(ph in ftext for ph in owners_names.get(o, ())) for o in owners):
                found.append(m.group(0))
    return found


DATA_EXT = (".json", ".tsv", ".psv", ".csv", ".txt", ".xml")


def tracked_corpus():
    """Every TRACKED data file (json, tsv, psv, csv, txt, xml), by `git ls-files`
    and not by walking the disk: a file that is not tracked is not one the
    repository will publish, and the gate that scans the disk would pass on files
    the build is about to ship (rule FILES-UNTRACKED closes the other half)."""
    out = {}
    files = tracked_files()
    if files is None:
        return out
    for f in files:
        if not f.endswith(DATA_EXT) or f.endswith("package-lock.json"):
            continue
        try:
            out["tracked:" + f] = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
        except OSError:
            pass
    return out


def living_ids(w):
    """slug -> tree id for the published living, through the frozen slug ledger
    (living.json deliberately carries no id)."""
    inv = {v: k for k, v in w["ledger"].items()}
    return {r["slug"]: inv[r["slug"]] for r in w["living"] if r["slug"] in inv}


def independent_status(people, livingset):
    """(living, held) from the KIT's living_rule.py, written out again here and not
    taken from the generator. Only the lookups for 'recorded dead on another
    record' (a death read, a grave photograph, a stone) are shared with it."""
    import living_rule as lr
    ty = lr.this_year()
    extra, _ = livingset.extra_dead(people)

    def dead(i, p):
        return any(e["kind"] in ("death", "burial") for e in p["events"]) or i in extra

    def by(p):
        ev = lambda k: next((e for e in p["events"] if e["kind"] == k), None)
        m = re.search(r"\b(\d{4})\b", (ev("birth") or ev("christening") or ev("baptism") or {}).get("date", "") or "")
        return int(m.group(1)) if m else None
    living = {i for i, p in people.items() if lr.is_living(by(p), dead(i, p), p.get("cites", ()), ty)}
    held = {i for i, p in people.items() if i not in living and lr.is_held_out(
        i, by(p), dead(i, p), p.get("cites", ()),
        any(par in living for par in p.get("parents", [])), (), ty)}
    return living, held


class Ged:
    """The tree and the living rule, loaded ONCE (it takes seconds), so a
    planted fault costs a scan of the planted text and not a rebuild."""

    def __init__(self, w):
        sys.path.insert(0, HERE)
        import gedcom
        import livingset
        self.gedcom, self.livingset = gedcom, livingset
        self.people, self.families = gedcom.load()
        # WHO IS LIVING, recomputed HERE with the kit's rule and not by the generator.
        self.living, self.held = independent_status(self.people, livingset)
        self.named = self.living - self.held
        self.display = {i: gedcom.display(p) for i, p in self.people.items()}
        self.dead = set(self.people) - self.living - self.held
        pub_living, pub_dead = _names(w)
        pubfold = {fold(n) for n in pub_living}
        self.named_fold = {fold(self.display[i]) for i in self.named}
        # every date of every living person, held out or not
        self.forbid = {}
        for i in self.living:
            for e in self.people[i]["events"]:
                for f in date_forms(e.get("date", "")):
                    self.forbid.setdefault(f, set()).add(i)
        self.owner_names = {i: {fold(x) for x in livingnames.phrases_of(self.display[i])}
                            for i in self.living}
        # a held-out person's name cannot be told from a DEAD person's of the same
        # name, anywhere in the tree: those are subtracted and counted
        all_dead_names = set(pub_dead) | {self.display[i] for i in self.dead}
        self.nm_held = livingnames.Names([self.display[i] for i in self.held], all_dead_names)
        self.nm_unpub = livingnames.Names(
            [self.display[i] for i in self.living - self.held if fold(self.display[i]) not in pubfold],
            pub_dead)
        self.held_ids = set(self.held)
        self.known = known_prose()

    def scan(self, corpus):
        """(failures, advisories) for `corpus`, {key: text}."""
        out, adv = [], []
        for where, text in corpus.items():
            is_data = where.startswith("tracked:") or where.startswith("committed:")
            # --- held-out people: no id, no name, anywhere ---------------------
            ids = {m.group(0) for m in RECORDID.finditer(text)} & self.held_ids
            if ids:
                out.append(("GED-HELD", where, f"{len(ids)} held-out person's tree id is in the file"))
            n = self.nm_held.count_hits(text)
            if n:
                out.append(("GED-HELD", where, f"{n} held-out person's name is in the file"))
            # --- dates of any living person -----------------------------------
            hits = first_dates(text, self.forbid, self.owner_names)
            if hits:
                page = where.split(":", 1)[1]
                key = page[:-len("/index.html")].strip("/") if page.endswith("index.html") else page
                if len(hits) <= self.known.get(key, self.known.get(key + "/", 0)):
                    adv.append(("GED-DATE", where, f"{len(hits)} known date(s) in hand-written text, listed in sources/living-prose.psv"))
                else:
                    out.append(("GED-DATE", where, "a living person's date «%s» is in the file" % hits[0]))
            # --- named living people who are not published (advisory) ----------
            if where.startswith("dist:") and not where.endswith(".json") and not where.endswith(".xml"):
                n = self.nm_unpub.count_hits(text)
                if n:
                    adv.append(("GED-NAME", where, f"{n} living name(s) the archive gives no page, in text it wrote"))
        return out, adv

    def data_rules(self, w):
        """Who is in the data must be who the rule says."""
        out = []
        by_slug = living_ids(w)
        for r in w["living"]:
            i = by_slug.get(r["slug"])
            if i is None:
                out.append(("GED-DEAD", r["slug"], "a living row whose slug is not in the frozen ledger"))
            elif i in self.held:
                out.append(("GED-DEAD", r["slug"], "a person the rule HOLDS OUT has a page"))
            elif i not in self.living:
                out.append(("GED-DEAD", r["slug"], "a person the tree records as dead (or the archive "
                                                   "holds evidence of the death of) has a living page"))
        for r in list(w["living"]) + list(w["people"]) + list(w["ancestors"]):
            for g in (r.get("rel") or {}).values():
                for x in g:
                    if x.get("living") and fold(x["name"]) not in self.named_fold:
                        out.append(("GED-DEAD", r.get("slug", "?"),
                                    "a living relation entry whose name is nobody the rule names"))
                    elif not x.get("living") and x.get("id") in self.living:
                        out.append(("GED-LIVEDEAD", r.get("slug", "?"),
                                    "a relation entry carries a living person's years as if they had died"))
        for r in list(w["people"]) + list(w["ancestors"]):
            if r.get("id") in self.living:
                out.append(("GED-LIVEDEAD", r.get("slug", "?"),
                            "a living person is published as somebody who has died"))
        rule = w.get("rule") or {}
        counts = rule.get("counts") or {}
        want = {"living": len(self.living), "heldOut": len(self.held),
                "livingWithPage": len(w["living"]), "deadWithPage": len(w["people"])}
        for k, v in want.items():
            if counts.get(k) != v:
                out.append(("GED-RULE", "sources/living-rule.json", f"{k} is {counts.get(k)}, the tree and the data give {v}"))
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
    for slug_, i in living_ids(w).items():
        p = ged.people.get(i)
        page = corpus.get("dist:" + page_path(slug_))
        if not p or page is None:
            continue
        strings = set(p["sources"]) | {n[:60] for n in p["notes"]}
        for e in p["events"]:
            for k in ("detail", "note", "agency", "type", "cause"):
                strings.add((e.get(k) or "").strip())
            if "," in (e.get("place") or ""):
                strings.add(e["place"])
        row = next(r for r in w["living"] if r["slug"] == slug_)
        strings.discard(", ".join(x for x in (row.get("town"), row.get("country")) if x))
        for st in {x for x in strings if len(x) >= 12}:
            if st in page or htmllib.escape(st) in page:
                out.append(("GED-SOURCE", "dist:" + page_path(slug_),
                            "something the tree records beyond a name, a town and a country"))
                break
    return out, adv


# ---- the controls ------------------------------------------------------------

def selftest(w, quiet=False):
    """PLANT A FAULT FOR EVERY RULE and show it is caught. And show that a
    clean build passes, that an empty one does not, and that the page rules
    object to the page of somebody who has died (the positive control)."""
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

    results = []
    results.append(plant("noindex taken off a living page", "PAGE-NOINDEX",
                         edit_page(r0["slug"], lambda h: NOINDEX.sub("", h))))
    results.append(plant("a canonical naming another page, on a living page", "PAGE-CANON",
                         edit_page(r0["slug"], lambda h: re.sub(
                             r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*"', r'\1https://x/other/"', h, 1))))
    results.append(plant("JSON-LD Person on a living page", "PAGE-LDJSON",
                         edit_page(r0["slug"], lambda h: h.replace("</head>", '<script type="application/ld+json">{"@type":"Person"}</script></head>', 1))))
    results.append(plant("a photograph on a living page", "PAGE-MEDIA",
                         edit_page(r0["slug"], into_main('<img src="/photos/x.jpg" alt="">'))))
    results.append(plant("a birth date in the page body", "PAGE-YEAR",
                         edit_page(r0["slug"], into_main("<p>Born 3 May 1799</p>"))))
    results.append(plant("a bare year in the page body", "PAGE-YEAR",
                         edit_page(r0["slug"], into_main("<p>b. 1799</p>"))))
    results.append(plant("a Born row in the record table", "PAGE-ROWS",
                         edit_page(r0["slug"], lambda h: h.replace("</table>", "<tr><th>Born</th><td>x</td></tr></table>", 1))))
    results.append(plant("a malformed record table", "PAGE-ROWS",
                         edit_page(r0["slug"], lambda h: h.replace("</table>", "", 1))))
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
    results.append(plant("a place with a street number", "DATA-PLACE",
                         lambda w2: w2["living"].__setitem__(0, {**w2["living"][0], "town": "12 High Street"})))

    def rel_year(w2):
        for r in w2["people"]:
            for g in r["rel"].values():
                for x in g:
                    if x.get("living"):
                        x["born"] = 1799
                        return
    results.append(plant("a birth year on a living relation entry", "DATA-KEYS", rel_year))

    def rel_marr(w2):
        for r in w2["people"]:
            for g in r["rel"].values():
                for x in g:
                    if x.get("living"):
                        x["marriedDate"] = "3 May 1799"
                        return
    results.append(plant("a marriage date on a living spouse", "DATA-KEYS", rel_marr))
    results.append(plant("the old withheld marker coming back", "DATA-KEYS",
                         lambda w2: w2["people"][0]["rel"]["parents"].append({"withheld": True})))
    if s0:
        results.append(plant("an all-living name page without noindex", "WHO-NOINDEX",
                             lambda w2: w2["pages"].__setitem__(who_path(s0), NOINDEX.sub("", w2["pages"][who_path(s0)]))))
        results.append(plant("an all-living name page pointing its canonical elsewhere", "WHO-CANON",
                             lambda w2: w2["pages"].__setitem__(who_path(s0), re.sub(
                                 r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*"', r'\1https://x/other/"', w2["pages"][who_path(s0)], 1))))
        results.append(plant("an all-living name page in the sitemap", "SITEMAP",
                             lambda w2: w2.__setitem__("sitemap", w2["sitemap"].replace(
                                 "</urlset>", f"<url><loc>https://x/who/{s0}/</loc></url></urlset>"))))
    results.append(plant("an empty build", "EMPTY", lambda w2: (w2["pages"].clear(), w2.__setitem__("sitemap", ""))))
    results.append(plant("no living people at all in the data", "EMPTY", lambda w2: w2["living"].clear()))
    results.append(plant("a noindex page left in the sitemap", "SITEMAP",
                         lambda w2: w2.__setitem__("sitemap", w2["sitemap"].replace(
                             "</urlset>", f"<url><loc>https://x/people/{r1['slug']}/</loc></url></urlset>"))))

    def nameless(w2):
        for r in w2["people"]:
            for g in r["rel"].values():
                if g:
                    g[0] = {**g[0], "slug": None}
                    return
    results.append(plant("a relative named on a page with no person page of their own", "NAMED-PAGE", nameless))
    results.append(plant("a relative whose page was never built", "NAMED-PAGE",
                         lambda w2: w2["people"][0]["rel"]["children"].append({"name": "Zz Plant", "slug": "zz-planted-nobody", "living": True})))
    results.append(plant("a file git does not track under the scanned directories", "FILES-UNTRACKED",
                         lambda w2: w2.__setitem__("untracked", ["site/src/data/zz-planted.json"])))
    results.append(plant("the record of the living rule missing", "RULE-RECORD",
                         lambda w2: w2.__setitem__("rule", None)))
    results.append(plant("a withheld entry that carries a name", "DATA-KEYS",
                         lambda w2: w2["people"][0]["rel"]["parents"].append({"withheld": True, "name": "Zz Plant"})))
    results.append(plant("a published person who has died with a field the archive never wrote", "DATA-KEYS",
                         lambda w2: w2["people"][0].__setitem__("zzPlantedField", "x")))
    ok &= all(results)
    rr = selftest_rule()
    for k, v in rr.items():
        print(f"  {'caught ' if v else 'MISSED '}   the rule, on a planted tree: {k}")
    ok &= all(rr.values())

    # POSITIVE CONTROL: the same page rules, aimed at the page of somebody who
    # has died, must object. A check that cannot fire on the thing it is
    # looking for proves nothing.
    dead = next(p for p in w["people"] if (p.get("byear") or 0) >= 1700 and p.get("died") and w["pages"].get(page_path(p["slug"])))
    found = {f[0] for f in page_rules(w["pages"][page_path(dead["slug"])], None, dead["slug"])}
    want = {"PAGE-NOINDEX", "PAGE-LDJSON", "PAGE-YEAR", "PAGE-ROWS"}
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
    """The living rule, run through the generator's classify (livingset) AND through
    this gate's own independent_status on a synthetic tree whose people no real
    person can be, with the planted year 1799 where a date is needed. Every case is
    checked on both, and the two must agree: a generator that drifts from the kit's
    rule, or a gate that does, is caught here. Needs no GEDCOM."""
    sys.path.insert(0, HERE)
    import livingset
    Y = livingset.lr.this_year()

    def person(i, born=None, events=(), parents=(), cites=()):
        ev = [{"kind": k, "date": "", "place": "", "detail": "Y", "note": "", "agency": "",
               "type": "", "cause": "", "tag": k.upper()} for k in events]
        if born is not None:
            ev.insert(0, {"kind": "birth", "date": f"1 JAN {born}", "place": "", "detail": "", "note": "",
                          "agency": "", "type": "", "cause": "", "tag": "BIRT"})
        return {"id": i, "name": "Zzplant Zzperson", "given": "Zzplant", "surname": "Zzperson", "nick": "",
                "events": ev, "notes": [], "sources": [], "cites": list(cites), "famc": [], "fams": [],
                "parents": list(parents), "sex": "", "alt_names": [], "uid": "", "mh": i}

    P = {
        "@IZ1@": person("@IZ1@", born=Y - 40),                                    # an adult, living
        "@IZ2@": person("@IZ2@", born=Y - 40, events=["burial"]),                 # undated burial: dead
        "@IZ3@": person("@IZ3@", born=Y - 40, events=["death"]),                  # undated death: dead
        "@IZ4@": person("@IZ4@", born=Y - 10, parents=["@IZ1@"]),                 # a child with a birth year: NAMED
        "@IZ5@": person("@IZ5@", born=Y - 80),                                    # 80 by year: living
        "@IZ6@": person("@IZ6@", born=Y - 81),                                    # 81 by year: not living
        "@IZ7@": person("@IZ7@", parents=["@IZ1@"]),                              # no birth year, living parent: HELD
        "@IZ8@": person("@IZ8@", parents=["@IZ2@"]),                              # no birth year, dead parent: neither
        "@IZ9@": person("@IZ9@", born=Y - 40, cites=["FamilySearch Family Tree"]),  # a public source: not living
        "@IZA@": person("@IZA@", born=Y - 40, cites=["MyHeritage Family Tree | tree profile"]),  # private tree: living
        "@IZB@": person("@IZB@", parents=["@IZ1@"], cites=["FamilySearch"]),      # undated, public source: not held
        "@IZC@": person("@IZC@", born=1799),                                      # a planted ancient birth: not living
    }
    mine = {}
    for label, (living, held) in (("generator", (lambda c: (c["living"], c["held"]))(livingset.classify(P, {}))),
                                  ("gate", independent_status(P, livingset))):
        mine[label] = {
            "an adult with nothing recorded is living": "@IZ1@" in living and "@IZ1@" not in held,
            "an undated burial is a death": "@IZ2@" not in living,
            "an undated death is a death": "@IZ3@" not in living,
            "a child with a known birth year is living and NOT held out": "@IZ4@" in living and "@IZ4@" not in held,
            "80 by year is living": "@IZ5@" in living,
            "81 by year is not living": "@IZ6@" not in living,
            "no birth year and a living parent is held out": "@IZ7@" in held and "@IZ7@" not in living,
            "no birth year and a dead parent is not held out": "@IZ8@" not in held and "@IZ8@" not in living,
            "a public source means not living": "@IZ9@" not in living,
            "a private tree entry does not": "@IZA@" in living,
            "undated with a public source is not held out": "@IZB@" not in held,
            "a birth in 1799 is not living": "@IZC@" not in living,
        }
    res = {}
    for k in mine["generator"]:
        res[f"{k} (generator, gate)"] = mine["generator"][k] and mine["gate"][k]
    return res


def selftest_ged(w):
    """The same, for the rules that need the GEDCOM. One load of the tree; every
    plant costs a scan of the planted text."""
    ged = Ged(w)
    base, adv = rule_ged(w, ged)
    print(f"  control   the real build against the whole tree: {len(base)} failure(s)  [expect 0]; "
          f"{len(adv)} advisory finding(s) in hand-written pages")
    ok = not base
    G = ged.gedcom
    two = lambda i: len(ged.display[i].split()) >= 2
    held_i = next(i for i in sorted(ged.held) if two(i)
                  and fold(ged.display[i]) not in ged.nm_held.dead_folded and ged.nm_held.forbidden)
    held_name = ged.display[held_i]
    held_dated = next((i for i in sorted(ged.held) if two(i) and any(date_forms(e.get("date", ""))
                                                                    for e in ged.people[i]["events"])), held_i)
    hd = sorted(date_forms(next(e for e in ged.people[held_dated]["events"] if date_forms(e.get("date", "")))["date"]))[0] if held_dated else None
    named_i = next(iter(sorted(ged.named)))
    dead_i = next(i for i in sorted(ged.dead) if two(i)
                  and any(e["kind"] in ("death", "burial") for e in ged.people[i]["events"])
                  and fold(ged.display[i]) not in ged.named_fold)
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
    if hd:
        res.append(scan("a held-out person's date beside their name", "GED-DATE",
                        {"tracked:site/src/data/x.json": f'{{"n":"{ged.display[held_dated]}","d":"{hd}"}}'}))
    res.append(data("a person the rule HOLDS OUT given a living page", "GED-DEAD",
                    lambda w2: (w2["living"].append({"slug": "zzplant", "name": "Zz Plant", "town": "", "country": "",
                                                     "living": True, "rel": {}}), w2["ledger"].__setitem__("zzplant", held_i))))
    res.append(data("a person the tree records as DEAD given a living page", "GED-DEAD",
                    lambda w2: (w2["living"].append({"slug": "zzplant", "name": "Zz Plant", "town": "", "country": "",
                                                     "living": True, "rel": {}}), w2["ledger"].__setitem__("zzplant", dead_i))))
    res.append(data("a recorded-dead person named as a living relative", "GED-DEAD",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": ged.display[dead_i], "slug": None, "living": True})))
    res.append(data("a held-out person named as a living relative", "GED-DEAD",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": held_name, "slug": None, "living": True})))
    res.append(data("a LIVING person published as somebody who has died", "GED-LIVEDEAD",
                    lambda w2: w2["people"].append({"id": named_i, "slug": "zzplant", "name": "Zz Plant", "rel": {}})))
    res.append(data("a held-out person published as somebody who has died", "GED-LIVEDEAD",
                    lambda w2: w2["people"].append({"id": held_i, "slug": "zzplant", "name": "Zz Plant", "rel": {}})))
    res.append(data("a living person given a dead relative's years", "GED-LIVEDEAD",
                    lambda w2: w2["people"][0]["rel"]["children"].append(
                        {"name": "Zz Plant", "slug": None, "id": named_i, "born": 1, "died": 2})))
    res.append(data("the record of the rule saying a different number held out", "GED-RULE",
                    lambda w2: w2.__setitem__("rule", {**w2["rule"], "counts": {**w2["rule"]["counts"], "heldOut": w2["rule"]["counts"]["heldOut"] + 1}})))
    # the old behaviour for dates and sources, still
    dated = next((i for i in sorted(ged.named) for e in ged.people[i]["events"] if date_forms(e.get("date", ""))), None)
    ids = living_ids(w)
    some = next(iter(ids))
    if dated:
        e = next(e for e in ged.people[dated]["events"] if date_forms(e.get("date", "")))
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
    src = next(((i, s_) for i in (ids[k] for k in ids) for s_ in ged.people[i]["sources"] if len(s_) >= 12), None)
    if src:
        slug = next(k for k, v in ids.items() if v == src[0])
        res.append(scan("a source the tree holds for a published living person, on their page", "GED-SOURCE",
                        {"dist:" + page_path(slug): f"<li>{htmllib.escape(src[1])}</li>"}) or
                   hit("a source on their page", "GED-SOURCE", rule_ged(w, ged, {"dist:" + page_path(slug): f"<li>{htmllib.escape(src[1])}</li>"})[0]))
    else:
        print("  note      no published living person has a source string to plant; GED-SOURCE not exercised")
    return ok and all(res)


# ---- main --------------------------------------------------------------------

def report(findings, w, quiet):
    names = names_of(w)
    live_pages = [r for r in w["living"] if r["slug"] in {k.split("/")[1] for k in w["pages"] if k.startswith("people/")}]
    noindexed = sum(1 for r in w["living"] if NOINDEX.search(w["pages"].get(page_path(r["slug"]), "")[:6000]))
    locs = {re.sub(r"^https?://[^/]+", "", l) for l in sitemap_locs(w)}
    in_sitemap = sum(1 for r in w["living"] if f"/people/{r['slug']}/" in locs)
    try:
        idx = json.loads(w["index"]) if w["index"] else []
    except ValueError:
        idx = []
    in_index = sum(1 for r in idx if r.get("h") in {f"/people/{x['slug']}/" for x in w["living"]})
    allv = all_living_names(w)
    allv_noindex = sum(1 for s in allv if NOINDEX.search(w["pages"].get(who_path(s), "")[:6000]))
    if findings:
        print(f"  FAIL  living-standard   {len(findings)} finding(s)")
        seen = collections.Counter()
        for rule, where, what in findings:
            seen[rule] += 1
            if seen[rule] <= 3:
                print(f"          {rule:<13} {where} — {what}")
        for rule, n in seen.items():
            if n > 3:
                print(f"          {rule:<13} … and {n - 3} more")
        return 1
    if not quiet:
        print(f"  ok    living-standard   {len(w['living'])} living pages built ({len(live_pages)} found), "
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
    code = report(findings, w, a.quiet)
    if advisory and not a.quiet:
        kinds = collections.Counter(x[0] for x in advisory)
        print("        note  living-standard   advisory, not a failure: the hand-written pages carry "
              + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items()))
              + " finding(s) (the research prose names and dates people the tree judges living; "
                "not rewritten here). Run with --advisory to list them.")
    if advisory and a.advisory:
        for k, where, what in advisory:
            print(f"          {k:<9} {where} — {what}")
    if not ged and not a.quiet:
        print("        note  living-standard   the checks that need the GEDCOM (GED-DATE, GED-NAME, "
              "GED-SOURCE) did not run: no sources/*.ged here. They run on a local build.")
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
