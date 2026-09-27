#!/usr/bin/env python3
"""Two link faults that reached the published site, and now cannot again.

Written 28 September 2026, after CI caught the same thing twice in a day and
this archive's own gates could not, because they were reading a sibling
session's `dist`.

FAULT ONE — A RAW ANCHOR IN A DATA FILE. The work list, the corrections and
the questions are JSON whose notes are rendered as Markdown. A Markdown link
`[text](/kosina/)` is rewritten with the site's base path at build time. A
raw `<a href='/kosina'>` is not: it is passed through verbatim and lands on
the published page pointing at `/kosina`, which on GitHub Pages under
`/TheBlazevic/` is a 404. That is exactly what shipped in commit 4c72556 and
exactly what failed the deploy.

FAULT TWO — A LINK TO A /found/ PERSON WHO HAS BEEN RENAMED. `found.psv` rows
become pages at `/found/<slug>/`, and the slug is derived from the name. When
a row is renamed — «Marija Kozina» became «Marija "Mina" Kozina» the moment
her marriage was found — every `.astro` page linking to the old slug breaks
silently. The build's own link check runs against `dist` and catches it, but
only after a full build, and only if the gates are pointed at the right
directory.

This runs in under a second against the sources, before a build, and needs
no `dist` at all.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
PAGES = os.path.join(ROOT, "site", "src", "pages")

# ONLY worklist.json, and the reason is specific rather than cautious.
# The kit's WorkList.astro renders a note with md(), whose one link rule is
#     .replace(/\[([^\]]+)\]\((\/[^)]*)\)/g, (_, t, h) => `<a href="${u(h)}">${t}</a>`)
# — it rewrites a MARKDOWN link through u() and passes a RAW HTML anchor
# through untouched. Every other data file here is rendered by a component
# that applies the base itself: corrections.astro has an explicit
#     base = (html) => html.replace(/href='\//g, `href='${u("/")}`)
# so its raw anchors are correct and must NOT be reported. A gate that
# flags 65 working links to catch one broken one gets switched off.
MARKDOWN_DATA = ["worklist.json"]
# Everything whose /found/ links are worth checking, however they render.
FOUND_DATA = ["worklist.json", "corrections.json", "questions.json",
              "sources.json", "trees.json", "sovereignty.json"]

RAW_ANCHOR = re.compile(r"""<a\s[^>]*href\s*=\s*['"](/[^'"]*)['"]""", re.I)
FOUND_LINK = re.compile(r"""/found/([a-z0-9][a-z0-9-]*)/""")


def walk(obj, path=""):
    """Every string in a nested JSON structure, with a breadcrumb."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, "%s.%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, "%s[%d]" % (path, i))
    elif isinstance(obj, str):
        yield path, obj


def found_slugs():
    p = os.path.join(DATA, "found.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    return {r["slug"] for r in d.get("rows", []) if r.get("slug")}


def main():
    bad = []

    # 1. raw anchors in Markdown-rendered data
    for name in MARKDOWN_DATA:
        p = os.path.join(DATA, name)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for where, text in walk(d, name):
            for href in RAW_ANCHOR.findall(text):
                bad.append(
                    "%s: raw <a href='%s'> in a work-list note — md() rewrites a "
                    "Markdown link through u() and leaves a raw anchor alone, so "
                    "this ships without the base path. Write [text](%s) instead."
                    % (where.lstrip("."), href,
                       href if href.endswith("/") else href + "/"))

    # 2. /found/<slug>/ links from pages and data that no longer resolve
    slugs = found_slugs()
    if slugs is None:
        print("  note  datalinks  found.json is not built yet; slug check skipped")
    else:
        files = sorted(glob.glob(os.path.join(PAGES, "**", "*.astro"), recursive=True))
        files += [os.path.join(DATA, n) for n in FOUND_DATA
                  if os.path.exists(os.path.join(DATA, n))]
        for f in files:
            body = open(f, encoding="utf-8").read()
            for slug in set(FOUND_LINK.findall(body)):
                if slug not in slugs:
                    bad.append("%s: links to /found/%s/ and no row of found.psv "
                               "makes that slug — renamed, or never existed."
                               % (os.path.relpath(f, ROOT), slug))

    if bad:
        print("\n  FAIL  datalinks  %d problem(s)" % len(bad))
        for b in bad:
            print("          " + b)
        sys.exit(1)
    n = len(slugs) if slugs else 0
    print("  ok    datalinks  no raw anchors in Markdown data, %d /found/ slug(s) resolve" % n)


if __name__ == "__main__":
    main()
