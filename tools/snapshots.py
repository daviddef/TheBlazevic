#!/usr/bin/env python3
"""Snapshots of the register pages this archive has read, published beside the readings.

WHY. An evidence-first archive that says «the register reads...» and shows nothing is
asking to be taken on trust. Until 11 October 2026 the pages read in this archive's long
FamilySearch and Matricula sittings were transcribed in the notes and the readings, and the
pages themselves were never kept: anyone who wanted to check a reading had to find the film,
the image and the entry again, with a sign-in. A snapshot is the page as the viewer showed it
when it was read - reduced to 800 px wide, about 200 KB - kept in the repository, shown on
/snapshots/, on the person's page and on the /found/ page, and named with the film, the image
number and the link to the viewer.

WHAT IT CHECKS, and refuses to build without:
  * every image file named in a row exists under site/public/snaps/;
  * every slug names somebody the site publishes (people.json, ancestors.json or found.json);
  * every note named exists;
  * every row carries a viewer link and a statement of what the page says;
  * no two rows share an id, and no image file is listed twice.
An image no row names is REPORTED, so a snapshot cannot be saved and left unexplained.

NOT A TRANSCRIPTION AND NOT A LICENCE. The words are in readings.psv, found.psv and the notes;
the image is evidence, reduced, credited, linked to its original, and not a substitute for it.

Reads  sources/snapshots.psv
Writes site/src/data/snapshots.json
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "snapshots.psv")
OUT = os.path.join(ROOT, "site", "src", "data", "snapshots.json")
IMG = os.path.join(ROOT, "site", "public", "snaps")
DATA = os.path.join(ROOT, "site", "src", "data")
REPO = "https://github.com/daviddef/TheBlazevic/blob/main"


def load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))


def main():
    slugs = {}
    for f in ("people.json", "ancestors.json"):
        for p in load(f):
            slugs.setdefault(p["slug"], ("people", p.get("name", p["slug"])))
    for r in load("found.json")["rows"]:
        slugs.setdefault(r["slug"], ("found", r["name"]))

    rows, problems, seen_ids, seen_files = [], [], set(), {}
    for n, line in enumerate(open(SRC, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("|")
        if len(f) != 11:
            problems.append(f"line {n}: expected 11 fields, got {len(f)}")
            continue
        sid, entry, page, title, film, where, view, says, sl, captured, note = [x.strip() for x in f]
        if sid in seen_ids:
            problems.append(f"{sid}: duplicate id")
        seen_ids.add(sid)
        if not (entry or page):
            problems.append(f"{sid}: no image at all")
        for fn in (entry, page):
            if not fn:
                continue
            if not os.path.exists(os.path.join(IMG, fn)):
                problems.append(f"{sid}: image {fn} is not in site/public/snaps/")
            if fn in seen_files:
                problems.append(f"{sid}: image {fn} already listed under {seen_files[fn]}")
            seen_files[fn] = sid
        if not (title and film and where and view and says and captured):
            problems.append(f"{sid}: title, film, where, view, says and captured are all required")
        if not view.startswith("https://"):
            problems.append(f"{sid}: view link must be https")
        people = []
        for s in [x.strip() for x in sl.split(",") if x.strip()]:
            if s not in slugs:
                problems.append(f"{sid}: slug {s} is not a person or found-person the site publishes")
            else:
                people.append({"slug": s, "kind": slugs[s][0], "name": slugs[s][1]})
        if note and not os.path.exists(os.path.join(ROOT, note)):
            problems.append(f"{sid}: note {note} does not exist")
        rows.append({
            "id": sid, "entry": entry, "page": page, "title": title, "film": film,
            "where": where, "view": view, "says": says, "slugs": [p["slug"] for p in people],
            "people": people, "captured": captured,
            "note": note, "noteUrl": f"{REPO}/{note}" if note else "",
        })

    listed = set(seen_files)
    orphans = sorted(f for f in os.listdir(IMG) if f.lower().endswith((".jpg", ".png")) and f not in listed) \
        if os.path.isdir(IMG) else []
    for o in orphans:
        problems.append(f"image {o} is in site/public/snaps/ and no row names it")

    by_slug = {}
    for r in rows:
        for s in r["slugs"]:
            by_slug.setdefault(s, []).append(r["id"])
    out = {
        "note": "Built by tools/snapshots.py from sources/snapshots.psv.",
        "count": len(rows),
        "images": len(seen_files),
        "rows": rows,
        "bySlug": by_slug,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"snapshots: {len(rows)} finds, {len(seen_files)} images, {len(by_slug)} people/found people shown")
    for p in problems:
        print("  FAIL", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
