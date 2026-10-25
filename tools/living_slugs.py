#!/usr/bin/env python3
"""Write the list of the living people's page slugs that the kit's lines gate (checklines.py --living) reads.

Nobody living may be a member of a pen or a lane of the lines page. The list is site/src/data/living.json's slugs (the
published living, by the kit's rule through tools/livingset.py), written OUTSIDE the repository beside era-living.json,
because a list of the living is not something to commit: it is derived on every run and read by npm run check:lines.

    python3 tools/living_slugs.py [path]      default: ../private/blazevic/living-slugs.json beside the repository
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(ROOT), "private", "blazevic", "living-slugs.json")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    rows = json.load(open(os.path.join(ROOT, "site", "src", "data", "living.json"), encoding="utf-8"))
    slugs = sorted({r["slug"] for r in rows if r.get("slug")})
    if not slugs:
        print("living_slugs: living.json holds nobody: an empty list would let the gate pass on nothing")
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(slugs, fh)
    print(f"living_slugs: {len(slugs)} slugs, written outside the repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
