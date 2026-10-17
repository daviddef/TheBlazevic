#!/usr/bin/env python3
"""Run the kit's prose gate (kit/tools/checkprose.py) on this archive's hand-written files.

WHY THIS FILE EXISTS. The kit's gate needs to know who is living, and that is in the private GEDCOM
(sources/*.ged, gitignored: it carries every living person in full). This wrapper writes the feed the
gate wants OUTSIDE the repository, from the tree and the kit's own living_rule.py (through
tools/livingset.py, the same classification the build uses), and then runs the gate on the files a person
typed. A living person's name never goes in a tracked file, a log or a commit message: nothing below prints
one.

THE FEED
  living     every person the rule calls living OR holds out (a held-out person is not published at all, so
             their name is as forbidden as a living person's), each with the name phrases a page could use.
  deadNames  from IDENTITY: the display names of the tree's people the rule calls neither living nor held
             out. It is never "every name that is not in the living list".

WHICH FILES. The kit reads site/src/pages, notes/, docs/ and top-level markdown by default. Added here, because
a person edits them by hand and the kit's generated-data gates do not read them: sources.json, corrections.json,
questions.json, errands.json, worklist.json, book.json (the book's part titles, introductions and one-line chapter
blurbs, written by hand) and lib/familyCopy.js. People.json and the other generated data stay
with their generators' own scrub gates (tools/livingcheck.py).

WHAT THIS DOES THAT THE KIT'S GATE CANNOT: it builds the feed (the kit cannot read the GEDCOM), it says plainly
when it cannot run, and it keeps the reasoned allowances OUTSIDE the repository, because an allowance names the
living person. The kit's gate is the only thing that decides pass or fail.

WITHOUT THE GEDCOM (CI) the check says NOT RUN and exits 2: never a pass. `--not-run-ok` (the form `npm run build`
uses) turns that exit into 0 but prints the same NOT RUN line, so the deploy is not blocked by a file the
runner does not have and nobody reads the output as a pass.

    python3 tools/prosecheck.py [--not-run-ok] [--feed-only]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRIVATE = os.path.join(os.path.dirname(ROOT), "private", "blazevic")
FEED = os.path.join(PRIVATE, "living-feed.json")
ALLOW = os.path.join(PRIVATE, "prose-allow.json")
KIT = os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools")
INCLUDE = ["site/src/data/sources.json", "site/src/data/corrections.json", "site/src/data/questions.json",
           "site/src/data/errands.json", "site/src/data/worklist.json", "site/src/data/book.json",
           "site/src/lib/familyCopy.js"]


def ged_available():
    d = os.path.join(ROOT, "sources")
    return os.path.isdir(d) and any(f.endswith(".ged") for f in os.listdir(d))


def write_feed():
    sys.path.insert(0, HERE)
    sys.path.insert(0, KIT)
    import gedcom
    import livingnames
    import livingset
    people, families = gedcom.load()
    cls = livingset.classify(people, families)
    living_ids = set(cls["living"]) | set(cls["held"])
    entries = []
    for i in sorted(living_ids):
        names = sorted(set(livingnames.phrases_of(gedcom.display(people[i]))))
        if names:
            entries.append({"id": i, "names": names})
    dead = sorted({gedcom.display(p) for i, p in people.items() if i not in living_ids and gedcom.display(p)})
    os.makedirs(PRIVATE, exist_ok=True)
    with open(FEED, "w", encoding="utf-8") as f:
        json.dump({"living": entries, "deadNames": dead}, f, ensure_ascii=False)
    os.chmod(FEED, 0o600)
    return len(entries), len(dead)


def selftest():
    """Plant a synthetic living person (a name no one has) beside the year 1899 in a hand-written page,
    in sources.json and in corrections.json, in a temporary tree, and confirm the kit's gate fails on each
    and passes on the same tree without the year. Needs no GEDCOM, so it runs in CI too."""
    import tempfile
    bad = "Zzplant Zzperson, born 1899, lived at Senj."
    good = "Zzplant Zzperson lived at Senj, Croatia."
    files = {"site/src/pages/zz.astro": "<p>%s</p>",
             "site/src/data/sources.json": '[{"what": "%s"}]',
             "site/src/data/corrections.json": '[{"why": "%s"}]'}
    results = []
    for label, text in (("planted year 1899", bad), ("clean", good)):
        with tempfile.TemporaryDirectory() as d:
            for rel, tpl in files.items():
                fp = os.path.join(d, rel)
                os.makedirs(os.path.dirname(fp), exist_ok=True)
                open(fp, "w", encoding="utf-8").write(tpl % text)
            feed = os.path.join(d, "feed.json")
            json.dump({"living": [{"id": "@IZZ@", "names": ["zzplant zzperson"]}], "deadNames": ["Aa Bb Cc"]},
                      open(feed, "w", encoding="utf-8"))
            cmd = [sys.executable, os.path.join(KIT, "checkprose.py"), "--root", d, "--feed", feed, "--no-git"]
            for inc in INCLUDE[:2]:
                cmd += ["--include", inc]
            r = subprocess.run(cmd, capture_output=True, text=True)
            out = r.stdout + r.stderr
            results.append((label, r.returncode, [rel for rel in files if rel in out]))
    ok = (results[0][1] == 1 and len(results[0][2]) == 3 and results[1][1] == 0)
    for label, rc, hit in results:
        print(f"  {label}: exit {rc}, files named {len(hit)} of {len(files)}")
    print("prose  selftest " + ("PASSED: the gate fails on a planted year (1899; the kit reads 1800-2099) in all three kinds of file and passes without it"
                              if ok else "FAILED"))
    return 0 if ok else 1


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    if not ged_available():
        print("prose  NOT RUN: no sources/*.ged here, so nobody can say who is living. "
              "The hand-written pages were NOT checked on this machine.")
        return 0 if "--not-run-ok" in argv else 2
    nliving, ndead = write_feed()
    print(f"prose  feed written outside the repository: {nliving} living or held-out people with names, {ndead} dead names")
    if "--feed-only" in argv:
        return 0
    cmd = [sys.executable, os.path.join(KIT, "checkprose.py"), "--root", ROOT, "--feed", FEED]
    for inc in INCLUDE:
        cmd += ["--include", inc]
    if os.path.exists(ALLOW):
        cmd += ["--allow", ALLOW]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
