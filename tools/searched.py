#!/usr/bin/env python3
"""Validate the hand-kept search register and publish it to the site.

Every other data file here is derived from the GEDCOM. This one cannot be: what
has been *looked for* is not in the tree. So it is written by hand in
`sources/searched.json` and this tool is the gate — it checks the vocabulary,
the shape and the internal links, then copies it to site/src/data/.

Why the gate matters: the register's value is that a null is recorded as
carefully as a find. An outcome spelled six different ways quietly splits the
nulls into piles nobody counts, which is how "we never searched that" turns into
"there is nothing there".

    python3 tools/searched.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "searched.json")
OUT = os.path.join(ROOT, "site", "src", "data", "searched.json")
PAGES = os.path.join(ROOT, "site", "src", "pages")

# Five outcomes, and no synonyms. "yield" gave something; "partial" gave
# something and left most of the source unread; "nothing" was searched properly
# and held nothing (or held the wrong family); "blocked" is a wall this archive
# chose not to climb; "pending" is known, wanted and not yet got.
OUTCOMES = {"yield", "partial", "nothing", "blocked", "pending"}
REQUIRED = ("src", "what", "when", "outcome", "got")


def page_exists(href):
    slug = href.strip("/")
    if not slug:
        return True
    for cand in (f"{slug}.astro", os.path.join(slug, "index.astro")):
        if os.path.exists(os.path.join(PAGES, cand)):
            return True
    # /who/… and /people/… are generated from the tree
    return slug.split("/")[0] in {"who", "people"}


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    rows, bad = d["rows"], []

    seen = set()
    for i, r in enumerate(rows):
        where = f"row {i + 1} ({r.get('src', '?')[:48]})"
        for k in REQUIRED:
            if not r.get(k):
                bad.append(f"{where}: missing {k}")
        if r.get("outcome") not in OUTCOMES:
            bad.append(f"{where}: outcome {r.get('outcome')!r} is not one of "
                       + ", ".join(sorted(OUTCOMES)))
        if r.get("src") in seen:
            bad.append(f"{where}: duplicate source name")
        seen.add(r.get("src"))
        if r.get("when") not in ("never", "not yet") and not re.search(r"\d{4}", r.get("when", "")):
            bad.append(f"{where}: when={r.get('when')!r} carries no year")
        for href in [r.get("url")] + [e[0] for e in r.get("ev", [])]:
            if href and href.startswith("/") and not page_exists(href):
                bad.append(f"{where}: link {href} has no page")
        for e in r.get("ev", []):
            if len(e) != 2:
                bad.append(f"{where}: ev entry is not [href, label]")

    if bad:
        for b in bad:
            print("  " + b)
        print(f"\n{len(bad)} problem(s) in {os.path.relpath(SRC, ROOT)}")
        return 1

    # The three lists the /searched page used to carry hardcoded in its own
    # frontmatter. They live here now so the register and the holdings table
    # cannot drift apart — which they could, and briefly did.
    for key, need in (("read", ("book", "pages", "years", "n", "got", "missed")),
                      ("holdings", ("parish", "books", "checked")),
                      ("unreachable", ("q", "want", "why"))):
        for i, row in enumerate(d.get(key, [])):
            for f in need:
                if f not in row:
                    bad.append(f"{key}[{i}]: missing {f}")
    if bad:
        for b in bad:
            print("  " + b)
        print(f"\n{len(bad)} problem(s) in {os.path.relpath(SRC, ROOT)}")
        return 1

    counts = {o: sum(1 for r in rows if r["outcome"] == o) for o in sorted(OUTCOMES)}
    out = {"note": d["note"], "cols": d["cols"], "counts": counts,
           "read": d.get("read", []), "holdings": d.get("holdings", []),
           "unreachable": d.get("unreachable", []), "rows": rows}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"searched.json — {len(rows)} sources: "
          + ", ".join(f"{n} {o}" for o, n in counts.items() if n)
          + f" · {len(out['read'])} books read, {len(out['holdings'])} parishes checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
