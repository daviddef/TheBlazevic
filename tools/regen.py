#!/usr/bin/env python3
"""Regenerate every derived data file, in dependency order, and record a stamp.

Thirteen of these tools need `sources/*.ged`, which is gitignored because the
export carries every living person in full. So CI cannot run them: the JSON they
produce is committed by hand, and nothing has ever checked that the committed
JSON still matches what the tools would produce.

That is a real exposure. A page can go on quoting 232 Zubrinics for weeks after
the tool that counts them was fixed - which is exactly what happened to the
gazetteer.

    python3 tools/regen.py            regenerate everything, write the stamp
    python3 tools/regen.py --check    verify the committed data is current

--check is what CI runs. It cannot re-derive the data without the GEDCOM, so it
compares each committed file against the hash recorded when it was last properly
regenerated. A mismatch means someone edited a data file by hand, or committed a
tool change without rerunning it.

NOT EVERY FILE IN site/src/data IS DERIVED, and until 22 September 2026 this
tool did not know that. It hashed every *.json in the directory and called the
lot "derived". Nine of them are written by hand and by nothing else -- the work
list, the corrections, the Kosina descent arrangement -- and for those the stamp
answered a question nobody had asked. Worse, when one of them was legitimately
edited, --check failed with «Run `python3 tools/regen.py` and commit the result»,
which does not regenerate the file. It re-stamps whatever is on disk. The gate
taught you to run a tool to silence it.

So HAND_KEPT is declared below, those files are excluded from the stamp, and
`check:stamp` now means exactly one thing: EVERY DERIVED FILE MATCHES ITS
GENERATOR.

And the declaration is enforced from the other side. A full regen records which
files its tools actually rewrote; anything in the directory that was NOT written
and is NOT declared hand-kept is refused. That is the case worth catching -- a
generator deleted or renamed, its output left in the tree, stale forever, with
every gate still green because nothing was looking at it.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
STAMP = os.path.join(ROOT, "sources", "derived.json")

# Order matters: build_site_data writes people.json, which nearly everything
# else reads. searchindex needs a completed build and is left to the workflow.
# Written by hand, by a person, and by no tool in ORDER. They are NOT stamped:
# any edit to one of them is legitimate, so a hash would only ever raise a false
# alarm that running regen.py would "fix" without regenerating anything.
#
# A file belongs here when nothing in ORDER writes it. Adding a row is a claim,
# and regen() checks the claim both ways on every full run.
HAND_KEPT = {
    "kosina-descent.json":   "the Kosina descent ladder — which of the six is on "
                             "the line, who is whose brother, and which child "
                             "carried it on. Conclusions somebody reached from a "
                             "document; kosina.py must not write it",
    "worklist.json":         "the work list",
    "corrections.json":      "where this archive disagrees with the tree",
    "questions.json":        "the open questions",
    "sources.json":          "what this archive is built from",
    "trees.json":            "the trees this archive reads",
    "sovereignty.json":      "which state held which place, when",
    "namefold.json":         "surname folding, by hand",
    "namefold-extra.json":   "surname folding, the exceptions",
    "photograph-these.json": "what to photograph next time somebody is at a grave",
    "recent.json":           "what changed lately",
}

ORDER = [
    "build_site_data.py",
    "build_media.py",
    "surnames.py",
    "given_names.py",
    "latin_cases.py",
    "names.py",
    "gazetteer.py",
    "consistency.py",
    "duplicates.py",
    "buckets.py",
    "zubrinic_roots.py",
    "marriedin.py",
    "work.py",
    "placefix.py",
    "targets.py",
    "bynames.py",
    "found.py",
    "register.py",
    "walls.py",
    "graves.py",
    "coverage.py",
    "emigrants.py",
    "searched.py",
    "indexcoverage.py",
    "kosina.py",
    "abroad.py",
    "readingsdata.py",
    "notelinks.py",
    "whoindex.py",
]


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def data_files():
    return sorted(f for f in os.listdir(DATA) if f.endswith(".json"))


def derived_files():
    """Every data file a tool in ORDER writes — which is all of them but HAND_KEPT."""
    return [f for f in data_files() if f not in HAND_KEPT]


def stamp_now():
    return {f: digest(os.path.join(DATA, f)) for f in derived_files()}


def check():
    if not os.path.exists(STAMP):
        print("no stamp recorded — run `python3 tools/regen.py` once")
        return 1
    want = json.load(open(STAMP, encoding="utf-8"))["files"]
    have = stamp_now()
    bad = []
    for f in sorted(set(want) | set(have)):
        if want.get(f) != have.get(f):
            bad.append((f, want.get(f, "missing"), have.get(f, "missing")))
    for f, w, h in bad:
        print(f"  STALE  {f}   recorded {w}, on disk {h}")
    if bad:
        print(f"\n{len(bad)} DERIVED data file(s) do not match the last regeneration.")
        print("Run `python3 tools/regen.py` with the GEDCOM present and commit the result.")
        return 1
    print(f"ok    all {len(have)} derived data files match the last regeneration "
          f"({len(HAND_KEPT)} hand-kept file(s) are not stamped, by declaration)")
    return 0


def regen():
    ged = [f for f in os.listdir(os.path.join(ROOT, "sources")) if f.endswith(".ged")]
    if not ged:
        print("no GEDCOM in sources/ — cannot regenerate. (This is expected in CI.)")
        return 1
    before = {f: os.path.getmtime(os.path.join(DATA, f)) for f in data_files()}
    for tool in ORDER:
        path = os.path.join(ROOT, "tools", tool)
        if not os.path.exists(path):
            print(f"  skip   {tool} (not present)")
            continue
        r = subprocess.run([sys.executable, path], cwd=ROOT,
                           capture_output=True, text=True)
        tail = (r.stdout or r.stderr).strip().splitlines()
        note = tail[-1][:66] if tail else ""
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'}   {tool:<22} {note}")
        if r.returncode != 0:
            print(r.stderr[-1200:])
            return 1
    # THE DECLARATION IS CHECKED FROM BOTH SIDES. A file nothing rewrote and
    # nobody declared is the dangerous case: a generator deleted or renamed,
    # its output left behind and stale forever, every gate still green.
    untouched = [f for f in data_files()
                 if f not in HAND_KEPT
                 and os.path.getmtime(os.path.join(DATA, f)) <= before.get(f, 0)]
    claimed = [f for f in HAND_KEPT
               if f in before
               and os.path.getmtime(os.path.join(DATA, f)) > before[f]]
    if untouched or claimed:
        for f in untouched:
            print(f"  ORPHAN  {f} — no tool in ORDER wrote it, and it is not "
                  f"declared in HAND_KEPT")
        for f in claimed:
            print(f"  CLAIMED {f} — declared hand-kept, but a tool just wrote it")
        print("\nsources/derived.json NOT written. Either restore the generator, "
              "add the file to HAND_KEPT with the reason, or take the stale file out.")
        return 1

    json.dump({"note": "sha256[:16] of each DERIVED file at last full regeneration. "
                       "Hand-kept files are listed separately and deliberately "
                       "not hashed — see HAND_KEPT in tools/regen.py.",
               "handKept": sorted(HAND_KEPT),
               "files": stamp_now()},
              open(STAMP, "w", encoding="utf-8"), indent=1)
    print(f"\nwrote {os.path.relpath(STAMP, ROOT)} — {len(derived_files())} derived "
          f"file(s) stamped, {len(HAND_KEPT)} hand-kept left alone")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else regen())
