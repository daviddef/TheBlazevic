#!/usr/bin/env python3
"""The place table behind the "at the time" notes: which Record Atlas region each place on a person's page belongs to.

THE DECISION IS data/era-ground.tsv: one row per place string exactly as the person page prints it (the born, baptised and died places of every
person who is not living, and the places of their dated birth, christening, baptism, death, burial, residence, census, immigration and naturalisation
events), with the Atlas region it belongs to, or '-' for "looked at, and no region clearly covers it", the reason, and the town whose point
(data/era-towns.tsv) lets the kit refuse a place that falls in a neighbouring region's ring. The header of that file says how the rows were decided.
This tool turns those rows into site/src/data/era-places.json and refuses to pass when the rows and the data disagree:

    python3 ../tools/build_era.py                       write src/data/era-places.json
    python3 ../tools/build_era.py --check               build gate: the file is what the rows build, every place string a note could be drawn
                                                        for has a row, and no row is stale
    python3 ../tools/build_era.py --snapshot <Record Atlas>/site/public/context.json [--report drops.json]
                                                        also rebuild src/data/era-snapshot.json (version 4) from the Atlas's versioned
                                                        contract (the deliberate refresh: nothing in a build ever reads the Atlas). The rings and
                                                        bboxes come from the contract (1.8.0 and later). --report writes, per region, how many eras
                                                        were refused and why (counts only).
    python3 ../tools/build_era.py --living-urls <file>  write the page paths the notes must never appear on (the living people's pages)

THE POLICY ON ERAS THE ATLAS HAS NOT ASSESSED. A region era's `contested` and `approx` are null where nobody has assessed it. The kit refuses such an
era by default, which would leave no note on it, so this archive builds its snapshot with --unassessed allow, on purpose and on the record: the
snapshot's policy says so, the gate prints how many notes rest on an unassessed era, and dropping that flag below (then rebuilding) is the whole of going
strict. The other policies are the kit's defaults: --approx margin, --contested scope, --margin-years 5 (an assessed era flagged approximate or contested
about its bounds is used only for a year more than max(5, the Atlas's margin) from each bound; kit/docs/era-notes.md rule l).

Only places of people who are NOT living are read: site/src/data/people.json holds no living person (the living are in living.json and get a page that
prints a town and a country and no event), and a note is never drawn there. The merge of people.json with ancestors.json and line.json, and the decoding of
the tree's HTML entities, follow site/src/lib/people.js; the kinds below are the ones site/src/pages/people/[slug].astro draws a note for.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
KIT_TOOLS = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
DATA = os.path.join(SITE, "src", "data")
GROUND = os.path.join(ROOT, "data", "era-ground.tsv")
TOWNS = os.path.join(ROOT, "data", "era-towns.tsv")
OUT = os.path.join(DATA, "era-places.json")
SNAP = os.path.join(DATA, "era-snapshot.json")
LIVING_OUT = os.path.join(os.path.dirname(ROOT), "private", "blazevic", "era-living.json")

# The event kinds that happen in a place, as the page's events list calls them. Keep in step with ERA_KINDS in site/src/pages/people/[slug].astro.
# Not drawn: "event" (a free-text kind), emigration (the place may be where they left or where they went), education, will, probate, graduation, retirement.
ERA_KINDS = ("birth", "christening", "baptism", "death", "burial", "residence", "census", "immigration", "naturalisation")

NAMED = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "scaron": "š", "Scaron": "Š", "ccaron": "č", "Ccaron": "Č",
         "cacute": "ć", "Cacute": "Ć", "zcaron": "ž", "Zcaron": "Ž", "dstrok": "đ", "Dstrok": "Đ", "deg": "°",
         "laquo": "«", "raquo": "»"}
ENT = re.compile(r"&(?:([A-Za-z]+)|#(\d+)|#x([0-9a-fA-F]+));")


def deent(s):
    """site/src/lib/people.js deent(): decode, until nothing changes, only the entities the tree uses."""
    if not isinstance(s, str) or "&" not in s:
        return s
    while True:
        prev = s

        def one(m):
            if m.group(1):
                return NAMED.get(m.group(1), m.group(0))
            cp = int(m.group(2), 10) if m.group(2) else int(m.group(3), 16)
            return chr(cp) if 0 < cp < 0x110000 else m.group(0)

        s = ENT.sub(one, s)
        if s == prev:
            return s


def clean(v):
    if isinstance(v, list):
        return [clean(x) for x in v]
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    return deent(v)


def load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))


def rows_of(path):
    for line in open(path, encoding="utf-8"):
        if line.startswith("# ") or line.rstrip("\n") == "#" or not line.strip():
            continue
        yield line.rstrip("\n").split("\t")


def ground():
    rows = {}
    for cols in rows_of(GROUND):
        if cols[0] == "place" and cols[1:2] == ["region"]:
            continue
        place, region, why, town = (cols + ["", "", "", ""])[:4]
        if not place or not region or not why:
            raise SystemExit("era-ground.tsv: a row needs a place, a region (or '-') and a reason: %r" % cols[0][:60])
        if place in rows:
            raise SystemExit("era-ground.tsv: a place appears twice (a row must say one thing)")
        rows[place] = (region, why, town)
    return rows


def towns():
    out = {}
    for cols in rows_of(TOWNS):
        if cols[0] == "town" and cols[1:2] == ["lat"]:
            continue
        out[cols[0]] = (float(cols[1]), float(cols[2]))
    return out


def people():
    """site/src/lib/people.js: people.json, then ancestors.json over it, then line.json over that (each decoded except the spine)."""
    by = {}
    for r in load("people.json"):
        by[r["id"]] = clean(r)
    for a in load("ancestors.json"):
        by[a["id"]] = {**by.get(a["id"], {}), **clean(a)}
    for s in load("line.json"):
        by[s["id"]] = {**by.get(s["id"], {}), **s}
    return list(by.values())


def has_name(s):
    """«—» is what a page prints for no place; it folds to nothing, and the kit refuses a table that holds one."""
    return any(c.isalnum() for c in str(s))


def event_places():
    """Every place string a non-living person's page can draw a note beside: the born, baptised and died places, and the place of an eligible event."""
    out = {}
    for p in people():
        if p.get("living"):
            continue
        for k in ("bornPlace", "baptisedPlace", "diedPlace"):
            if p.get(k) and has_name(p[k]):
                out[p[k]] = out.get(p[k], 0) + 1
        for e in p.get("events") or []:
            if e.get("place") and e.get("kind") in ERA_KINDS and has_name(e["place"]):
                out[e["place"]] = out.get(e["place"], 0) + 1
    return out


def build():
    rows = ground()
    used = event_places()
    pts = towns()
    table = {}
    for place in sorted(rows):
        region, _, town = rows[place]
        if region == "-":
            table[place] = None
            continue
        table[place] = {"region": region}
        if town:
            if town not in pts:
                raise SystemExit("era-ground.tsv: town %r has no row in era-towns.tsv" % town)
            table[place].update(lat=pts[town][0], lon=pts[town][1])
    return rows, used, table


def living_urls():
    return sorted("/people/%s/" % p["slug"] for p in load("living.json") if p.get("slug"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--snapshot", default=None, help="a local copy of the Record Atlas's context.json (the versioned contract): also rebuild era-snapshot.json")
    ap.add_argument("--rings", default=None, help="OPTIONAL override: the Atlas's regions.json. By default the rings come from the contract (1.8.0 and later)")
    ap.add_argument("--report", default=None, help="write the per-region count of refused eras (and why) here (JSON)")
    ap.add_argument("--living-urls", nargs="?", const=LIVING_OUT, default=None,
                    help="write the living page paths here (JSON list; default %s, outside the repository) and stop" % os.path.relpath(LIVING_OUT, ROOT))
    a = ap.parse_args()
    if a.living_urls:
        urls = living_urls()
        if not urls:
            raise SystemExit("build_era: no living page found; a list of none would make the living gate a verdict on nothing")
        os.makedirs(os.path.dirname(os.path.abspath(a.living_urls)), exist_ok=True)
        open(a.living_urls, "w", encoding="utf-8").write(json.dumps(urls, indent=0) + "\n")
        print("era living list: %d page path(s)" % len(urls))
        return 0
    rows, used, table = build()
    missing = sorted(set(used) - set(rows))
    stale = sorted(set(rows) - set(used))
    out = {"_about": "Built by tools/build_era.py from data/era-ground.tsv and data/era-towns.tsv. Place as printed -> {region, lat, lon}, or null where no Atlas "
                     "region clearly covers it. Read by kit erasnap.py.", "places": table}
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if a.check:
        bad = False
        if missing:
            print("  FAIL  era-ground  %d place string(s) a note could be drawn beside have no row in data/era-ground.tsv "
                  "(decide a region, or '-', for each)" % len(missing))
            bad = True
        if stale:
            print("  FAIL  era-ground  %d row(s) in data/era-ground.tsv match no place (stale)" % len(stale))
            bad = True
        try:
            have = open(OUT, encoding="utf-8").read()
        except OSError:
            have = None
        if have != text:
            print("  FAIL  era-ground  site/src/data/era-places.json is not what the rows build (run tools/build_era.py)")
            bad = True
        if not bad:
            mapped = sum(1 for v in table.values() if v)
            print("  ok    era-ground  %d place strings decided (%d mapped to a region, %d to none); the table matches" % (len(table), mapped, len(table) - mapped))
        return 1 if bad else 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("era-places.json: %d place strings (%d mapped)" % (len(table), sum(1 for v in table.values() if v)))
    if missing:
        print("  WARNING %d place string(s) have no row in data/era-ground.tsv" % len(missing))
        return 1
    if a.snapshot:
        cmd = [sys.executable, os.path.join(KIT_TOOLS, "erasnap.py"), "--contract", a.snapshot,
               "--places", OUT, "--out", SNAP, "--unassessed", "allow"]
        if a.rings:
            cmd += ["--rings", a.rings]
        if a.report:
            cmd += ["--report", a.report]
        r = subprocess.run(cmd)
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
