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
import json, re, os, sys, glob

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
try:
    con = load("consistency.json")
    noted = {c["id"] for c in load("corrections.json")}
    silent = sorted({(i["name"], i["slug"]) for i in con
                     if i.get("slug") and i["id"] not in noted})
    check("contradictions annotated on the person", silent,
          lambda b: f"{b[0]}  /people/{b[1]}")
except FileNotFoundError:
    print("skip  contradictions — consistency.json not built")

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
