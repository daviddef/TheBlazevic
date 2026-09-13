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
ORDER = [
    "build_site_data.py",
    "build_media.py",
    "surnames.py",
    "given_names.py",
    "latin_cases.py",
    "gazetteer.py",
    "consistency.py",
    "duplicates.py",
    "buckets.py",
    "zubrinic_roots.py",
    "marriedin.py",
    "work.py",
    "register.py",
    "coverage.py",
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


def stamp_now():
    return {f: digest(os.path.join(DATA, f)) for f in data_files()}


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
        print(f"\n{len(bad)} data file(s) do not match the last regeneration.")
        print("Run `python3 tools/regen.py` with the GEDCOM present and commit the result.")
        return 1
    print(f"ok    all {len(have)} derived data files match the last regeneration")
    return 0


def regen():
    ged = [f for f in os.listdir(os.path.join(ROOT, "sources")) if f.endswith(".ged")]
    if not ged:
        print("no GEDCOM in sources/ — cannot regenerate. (This is expected in CI.)")
        return 1
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
    json.dump({"note": "sha256[:16] of each derived file at last full regeneration",
               "files": stamp_now()},
              open(STAMP, "w", encoding="utf-8"), indent=1)
    print(f"\nwrote {os.path.relpath(STAMP, ROOT)} — {len(data_files())} files stamped")
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else regen())
