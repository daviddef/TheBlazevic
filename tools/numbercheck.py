#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse a COUNT that was typed into prose when the page could have asked the data.

Written 22 September 2026, after four of them were found wrong on one afternoon:

  /zubrinic-roots/  «21 sorting buckets … 218 published people … 74 have no other
                    parent» — the real figures were 37, 286 and 144
  /frontier/        «53 people in this tree are born or die here» — 123
  /name/            «79 people this tree writes Papić (Papa)», twice — 75
  /kosina/          stat cards reading «10 people · 1841 · four generations» over a
                    table whose own first row was a man born in 1775

Not one of them was wrong when it was written. Publication grew from 1,460 people
to 1,833, a closure added four hundred ancestors, and the sentences stayed still.
**A number a reader can see is a promise, and prose cannot keep it.**

So: a page that already imports a data file may not also carry a hand-typed count.
Either bind it (`{rows.length}`) or declare it in sources/typed-numbers.psv with the
reason — which is what a genuinely historical figure needs anyway, because «1,460
became 1,903» is a fact about a day and not a live measurement.

Usage:  python3 tools/numbercheck.py [--list]
"""
import os, re, sys

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "site", "src", "pages")
ALLOW = os.path.join(ROOT, "sources", "typed-numbers.psv")

# A count is a number immediately followed by one of these. Deliberately short:
# the point is to catch claims about THE SIZE OF THIS ARCHIVE, not every integer.
NOUNS = (r"(?:published\s+)?people|records|entries|published|names|households|"
         r"ancestors|sorting\s+buckets|loose\s+ends|documents|readings|parishes")
NUM   = r"\d{1,3}(?:,\d{3})+|\d{2,}"
PAT   = re.compile(r"(?<![\w.])(" + NUM + r")\s*(?:</strong>\s*)?(?:</?[a-z][^>]*>\s*)*("
                   + NOUNS + r")\b", re.I)

# Years, ordinals and dates are not counts. 1,000-4,000 are almost always years here.
def is_year(tok):
    t = tok.replace(",", "")
    return len(t) == 4 and t.isdigit() and 1400 <= int(t) <= 2100


def allowed():
    """name|page|number|why — a typed number somebody has signed for."""
    out = set()
    if not os.path.exists(ALLOW):
        return out
    for line in open(ALLOW, encoding="utf-8"):
        if line.startswith("#") or line.count("|") < 3:
            continue
        f = [x.strip() for x in line.split("|")]
        out.add((f[1], f[2].replace(",", "")))
    return out


def main():
    ok = allowed()
    hits, pages = [], 0
    for base, _, files in os.walk(PAGES):
        for fn in sorted(files):
            if not fn.endswith(".astro"):
                continue
            path = os.path.join(base, fn)
            rel  = os.path.relpath(path, PAGES)
            src  = open(path, encoding="utf-8").read()
            # A page with no data import cannot bind anything, so it is not asked to.
            if not re.search(r'^import .*from "\.\./.*data/.*\.json";', src, re.M):
                continue
            pages += 1
            body = src.split("---", 2)[-1]          # frontmatter is code, not prose
            for line_no, line in enumerate(body.splitlines(), src[:src.rfind("---") + 3].count("\n") + 1):
                if "//" in line.strip()[:2]:
                    continue
                for m in PAT.finditer(line):
                    tok, noun = m.group(1), " ".join(m.group(2).split())
                    if is_year(tok):
                        continue
                    if (rel, tok.replace(",", "")) in ok:
                        continue
                    hits.append((rel, line_no, tok, noun, line.strip()[:110]))

    if "--list" in sys.argv or hits:
        for rel, ln, tok, noun, ctx in hits:
            print(f"  {rel}:{ln}  «{tok} {noun}»")
            print(f"      {ctx}")
    if not hits:
        print(f"  ok    numbers    {pages} data-backed page(s), no hand-typed count")
        return 0
    print(f"\n{len(hits)} hand-typed count(s) on pages that import data.\n"
          "Bind it to the data, or add a row to sources/typed-numbers.psv saying why it is\n"
          "a fact about a moment rather than a measurement. See the docstring of this file.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
