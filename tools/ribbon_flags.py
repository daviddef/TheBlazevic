#!/usr/bin/env python3
"""The mini flags on the ribbon cards (27 October 2026; the kit's contract: kit/docs/ribbon-flags.md).

    python3 tools/ribbon_flags.py                 write site/src/data/ribbon-flags.json
    python3 tools/ribbon_flags.py --check         fail if ribbon-flags.json is not what the inputs make (CI: it reads committed JSON only)
    python3 tools/ribbon_flags.py --gate [--dist dist]
                                                  the kit's own gates on the flags: ribbonflags.py --check and checkribbonflags.py
                                                  (with the built pages), run on copies of the cards with the flags put back on them
    python3 tools/ribbon_flags.py --report        print every place line: the flags it draws, or why none

WHAT IT DOES. The kit's generator (kit/tools/ribbonflags.py) chooses each card's flags: for every place a card names (from, at,
spouse) the flag of the state that held it in the card's year, by this archive's era snapshot (era-snapshot.json, the same rules
as the «at the time» notes), and today's country's flag where that is another flag, or alone where the era cannot be said.
Nothing here chooses a flag: this file runs the kit's own `run()` with this archive's inputs, and the kit's gate
(checkribbonflags.py) recomputes every flag on its own.

WHY A FILE OF ITS OWN. The kit's generator writes `flags` onto the cards of story.json and family-lines.json, but at kit 1fa6b54
the kit's own contracts for those files (story-schema.json, family-ribbon-schema.json, enforced by checkfamilystory.py and
checkfamilyribbon.py --strict) do not know the field and fail every flagged card. The kit is not edited here, so the flags live
in site/src/data/ribbon-flags.json (generated, stamped by tools/regen.py) and are put on the cards where the ribbons are drawn
(site/src/lib/ribbonFlags.js: the story page and components/FamilyLine.astro). story.json stays as written by hand and
family-lines.json as tools/family_ribbon.py makes it. When the kit's contracts learn `flags`, the cards can carry them directly.

THIS ARCHIVE'S INPUTS
  site/src/data/era-snapshot.json   the region eras (hand-kept; tools/build_era.py --snapshot)
  site/src/data/flag-countries.json today's country of a card's place where this archive's evidence settles it and the kit's
                                    table cannot, or null where the place is not located (hand-kept, each line with its evidence)
  site/src/data/story.json, family-lines.json   the cards

THE FILE: {"_note", "story": [{"name", "flags"} per ribbon card, in order], "families": {family id: [{"name", "flags"} per card]}}.
A card with no flag has "flags": [].
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "src", "data")
KIT_TOOLS = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
STORY = os.path.join(DATA, "story.json")
FAMILIES = os.path.join(DATA, "family-lines.json")
SNAPSHOT = os.path.join(DATA, "era-snapshot.json")
COUNTRIES = os.path.join(DATA, "flag-countries.json")
OUT = os.path.join(DATA, "ribbon-flags.json")
NOTE = ("Made by tools/ribbon_flags.py with the kit's ribbonflags.py from story.json, family-lines.json, era-snapshot.json and "
        "flag-countries.json; do not edit by hand. The ribbons put these on their cards (src/lib/ribbonFlags.js).")


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def kit():
    if KIT_TOOLS not in sys.path:
        sys.path.insert(0, KIT_TOOLS)
    import ribbonflags
    return ribbonflags


def countries():
    return {k: v for k, v in load(COUNTRIES).items() if not k.startswith("_")}


def flagged():
    """(story, families, report): copies of the two card files with the kit's flags on their cards."""
    story, fams = load(STORY), load(FAMILIES)
    ctx = kit().context(load(SNAPSHOT), {}, None, countries=countries())
    rep = kit().run(ctx, story, fams)
    return story, fams, rep


def table(story, fams):
    return {"_note": NOTE,
            "story": [{"name": c.get("name"), "flags": c.get("flags", [])} for c in story["ribbon"]["cards"]],
            "families": {f["id"]: [{"name": c.get("name"), "flags": c.get("flags", [])} for c in f.get("cards") or []]
                         for f in fams["families"] if f.get("cards")}}


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def summary(rep):
    return "%d flags on %d cards; place lines: %s" % (len(rep["cards"]), len({(c["where"], c["card"]) for c in rep["cards"]}),
                                                     ", ".join("%s %d" % kv for kv in sorted(rep["lines"].items())))


def gate(dist):
    """The kit's generator --check and its independent gate, on copies of the cards with the committed flags put back."""
    have = load(OUT)
    story, fams = load(STORY), load(FAMILIES)
    for c, f in zip(story["ribbon"]["cards"], have["story"]):
        if f["flags"]:
            c["flags"] = f["flags"]
    for fam in fams["families"]:
        for c, f in zip(fam.get("cards") or [], have["families"].get(fam["id"], [])):
            if f["flags"]:
                c["flags"] = f["flags"]
    tmp = tempfile.mkdtemp(prefix="ribbonflags-")
    try:
        sp, fp = os.path.join(tmp, "story.json"), os.path.join(tmp, "family-lines.json")
        open(sp, "w", encoding="utf-8").write(dump(story))
        open(fp, "w", encoding="utf-8").write(dump(fams))
        common = ["--snapshot", SNAPSHOT, "--story", sp, "--family-lines", fp, "--countries", COUNTRIES]
        r1 = subprocess.run([sys.executable, os.path.join(KIT_TOOLS, "ribbonflags.py")] + common + ["--check"], capture_output=True, text=True)
        print((r1.stdout.splitlines() or [""])[0])
        if r1.returncode:
            print(r1.stderr.strip())
            return 1
        r2 = subprocess.run([sys.executable, os.path.join(KIT_TOOLS, "checkribbonflags.py")] + common + (["--dist", dist] if dist else []),
                            capture_output=True, text=True)
        print((r2.stdout + r2.stderr).strip())
        return r2.returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    argv = sys.argv[1:]
    if "--gate" in argv:
        dist = argv[argv.index("--dist") + 1] if "--dist" in argv else None
        return gate(dist)
    story, fams, rep = flagged()
    want = dump(table(story, fams))
    if "--report" in argv:
        kit().print_report(rep)
        return 0
    if "--check" in argv:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
        if have != want:
            print("  STALE  site/src/data/ribbon-flags.json is not what the cards, the era snapshot, flag-countries.json and the kit make; "
                  "run python3 tools/ribbon_flags.py and commit the result")
            return 1
        print("ok    ribbon flags: ribbon-flags.json is what the kit makes (%s)" % summary(rep))
        return 0
    open(OUT, "w", encoding="utf-8").write(want)
    print("ribbon_flags: wrote ribbon-flags.json (%s)" % summary(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
