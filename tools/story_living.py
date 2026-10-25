#!/usr/bin/env python3
"""Write the list of living people's NAMES that the kit's story gate (checkfamilystory.py --living) reads.

The story (/story/, site/src/data/story.json) names the living by relationship and town and never beside a date. The gate
knows the living the story flags itself; this list adds everybody the archive publishes as living, so a paragraph that
names one of them within a hundred characters of a year fails even where the story forgot to flag them. The names are
site/src/data/living.json's (the published living, by the kit's rule through tools/livingset.py), written OUTSIDE the
repository beside living-slugs.json, because a list of the living is derived on every run and not committed. It reads
committed data only, so it runs in CI as well.

    python3 tools/story_living.py [path]      default: ../private/blazevic/story-living.json beside the repository
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(ROOT), "private", "blazevic", "story-living.json")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    rows = json.load(open(os.path.join(ROOT, "site", "src", "data", "living.json"), encoding="utf-8"))
    names = set()
    for r in rows:
        nm = " ".join(str(r.get("name") or "").replace('"', " ").split())
        if nm:
            names.add(nm)
    if not names:
        print("story_living: living.json holds nobody: an empty list would let the gate pass on nothing")
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"names": sorted(names)}, fh, ensure_ascii=False)
    print(f"story_living: {len(names)} names, written outside the repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
