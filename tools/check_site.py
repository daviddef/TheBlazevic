#!/usr/bin/env python3
"""Everything that must be true before this archive is published.

Runs on the committed JSON and the built HTML only — never on the GEDCOM, which
is gitignored and so is not present in CI. Each check exists because the thing
it tests actually went wrong here at least once:

  links     a page linked to a person slug that was never generated
  base      open-questions rewrote the site base path in one field and not the
            other, and shipped five dead links
  annotated a person carried a contradiction on /impossible with nothing on
            their own page to say so
  buckets   four sorting buckets were published as ancestors

Exit non-zero on any failure, so it can gate a deploy.
"""
import json, re, os, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
DIST = os.path.join(ROOT, "site", "dist")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


fails = []


def check(label, bad, fmt):
    if bad:
        fails.append(label)
        print(f"FAIL  {label}: {len(bad)}")
        for b in list(bad)[:12]:
            print("        " + fmt(b))
    else:
        print(f"ok    {label}")


# ---- links ---------------------------------------------------------------
slugs = {p["slug"] for f in ("people.json", "ancestors.json", "line.json")
         for p in load(f)}
bad = set()
for f in glob.glob(os.path.join(ROOT, "site", "src", "pages", "**", "*.astro"),
                   recursive=True):
    src = open(f, encoding="utf-8").read()
    for m in re.finditer(r"/people/([a-z0-9\-]+)", src):
        if m.group(1) not in slugs and m.group(1) != "index":
            bad.add((os.path.relpath(f, ROOT), m.group(1)))
check("person links resolve", bad, lambda b: f"{b[0]} -> /people/{b[1]}")

# ---- sorting buckets -----------------------------------------------------
JUNK = re.compile(r"\bto be sort|\bsorting\b|\bfor sorting\b|\bworking\b|"
                  r"\bunknown\b|\bbrothers?\s+of\b|\bit seems\b|"
                  r"^\s*\d{4}(\s*[-–]\s*\d{4})?\s+(birth|death|marriage)", re.I)
buckets = [p["name"] for p in load("people.json") + load("ancestors.json")
           if JUNK.search(p["name"] or "")]
check("no sorting buckets published", buckets, lambda b: b)

# ---- every contradiction is answered on the person's own page ------------
# This check used to read «if i.get("slug") and ...», which quietly excused
# every contradiction about a person with NO PAGE. That was 47 of 71 rows and
# 25 people, none of them answered, and the check printed ok for months.
#
# It is the same blindness that put six Karlobag wives outside the tree and
# filed Hedviga's husband's gravestone as a stranger's: AN UNPUBLISHED PERSON
# IS INVISIBLE. Three times, in three different tools. A person without a page
# is still a person, and a contradiction about them is still unanswered.
#
# The slugged ones failed the build from the start. The slug-less ones were
# printed and counted rather than failing, so the hole could be closed before
# the archive went red — the same bargain checkcovers struck. All 47 rows were
# answered on 15 September 2026, so the bargain is over and both halves fail
# alike. A person without a page is a person.
try:
    con = load("consistency.json")
    noted = {c["id"] for c in load("corrections.json")}
    silent = sorted({(i["name"], i["slug"]) for i in con
                     if i.get("slug") and i["id"] not in noted})
    check("contradictions annotated on the person", silent,
          lambda b: f"{b[0]}  /people/{b[1]}")
    pageless = sorted({i["name"] for i in con
                       if not i.get("slug") and i["id"] not in noted})
    check("contradictions answered for people with no page", pageless,
          lambda b: b)
except FileNotFoundError:
    print("skip  contradictions — consistency.json not built")

# ---- evidence must actually reach the person it is about ------------------
#
# Every file below attaches evidence to a NAMED SLUG. On 17 September 2026 none
# of the first three reached the page: tools/coverage.py, which decides what a
# person page may claim, read readings.psv and media and nothing else. Twenty-
# two people whose evidence is a photographed gravestone, a memorial index or a
# trade read out of a register carried «Tree only — everything here comes from
# the family tree, and is unverified» on their own page.
#
# The data was right. The build dropped it, and nothing refused. This refuses.
#
# The test is deliberately weak: the page must claim SOMETHING other than «the
# tree says so» — a record, an index, a scan, a dispute, or a correction written
# about them. It does not check that the wording is good, only that the evidence
# arrived at all.
try:
    ev = load("evidence.json")
    noted_ids = {c["id"] for c in load("corrections.json")}
    by_slug = {p["slug"]: p for f in ("people.json", "ancestors.json")
               for p in load(f)}
    g = load("graves.json")
    w = load("work.json")

    claimed = {}   # slug -> which evidence file names them
    for r in g.get("stones", {}).get("rows", []):
        if r.get("slug"):
            claimed.setdefault(r["slug"], "a photographed gravestone")
    for r in g.get("rows", []):
        if r.get("slug"):
            claimed.setdefault(r["slug"], "a Find a Grave memorial")
    for st in w.get("strata", []):
        for row in st.get("rows", []):
            if row.get("slug") and row.get("from") == "register":
                claimed.setdefault(row["slug"], "an occupation read from a register")
    rp = os.path.join(ROOT, "sources", "readings.psv")
    if os.path.exists(rp):
        for line in open(rp, encoding="utf-8"):
            if line.strip() and not line.startswith("#") and line.count("|") >= 4:
                claimed.setdefault(line.split("|")[0].strip(), "sources/readings.psv")

    SILENT = {"tree", "line"}
    mute = []
    for slug, where in sorted(claimed.items()):
        person = by_slug.get(slug)
        if not person:
            continue          # no page to be wrong about
        state = (ev.get(slug) or {}).get("state", "tree")
        if state in SILENT and person.get("id") not in noted_ids:
            mute.append((slug, where, state))
    check("evidence reaches the person it is about", mute,
          lambda b: f"/people/{b[0]}  has {b[1]}  but the page says «{b[2]}»")
except FileNotFoundError as e:
    print(f"skip  evidence reaches the person - {e.filename} not built")

# ---- the auto-linker's index -------------------------------------------
# whoindex.json is read at runtime by wholink.js, so nothing in the build
# catches a slug that has gone. Every target must be a page that exists, and
# no name may claim two people - that is the whole premise of the index.
WHO = os.path.join(ROOT, "site", "public", "whoindex.json")
if os.path.exists(WHO):
    who = json.load(open(WHO, encoding="utf-8"))
    dead = sorted({(n, sl) for n, sl, _ in who if sl not in slugs})
    check("auto-linker targets exist", dead, lambda b: f"{b[0]} -> /people/{b[1]}")
    dupes = collections.Counter(n.lower() for n, _, _ in who)
    clash = sorted(n for n, c in dupes.items() if c > 1)
    check("no name in the auto-linker claims two people", clash, lambda b: b)
else:
    print("skip  auto-linker - whoindex.json not built")

# ---- the built site, if it is there --------------------------------------
if os.path.isdir(DIST):
    base = None
    for f in glob.glob(os.path.join(DIST, "**", "*.html"), recursive=True):
        m = re.search(r'data-base="([^"]*)"', open(f, encoding="utf-8").read())
        if m:
            base = m.group(1).rstrip("/")
            break
    dead = set()
    if base:
        for f in glob.glob(os.path.join(DIST, "**", "*.html"), recursive=True):
            html = open(f, encoding="utf-8").read()
            # A code sample quoting an href is not a link. /changed shows the
            # very pattern this check tests for, inside <code>.
            html = re.sub(r"<code\b.*?</code>", "", html, flags=re.S)
            for h in set(re.findall(r'href=[\'"](/[^\'"#?]*)[\'"]', html)):
                if h.startswith(base + "/") or h == base or h == "/":
                    rel = h[len(base):].strip("/")
                    if rel and not (os.path.exists(os.path.join(DIST, rel, "index.html"))
                                    or os.path.exists(os.path.join(DIST, rel))):
                        dead.add((os.path.basename(os.path.dirname(f)), h))
                elif not h.startswith(("http", "//")):
                    dead.add((os.path.basename(os.path.dirname(f)), h + "  (missing base)"))
    check("built links carry the base and resolve", dead,
          lambda b: f"{b[0]}  {b[1]}")
else:
    print("skip  built links — site/dist not present")

print()
if fails:
    print(f"{len(fails)} check(s) failed: " + ", ".join(fails))
    sys.exit(1)
print("all checks passed")
