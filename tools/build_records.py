#!/usr/bin/env python3
"""The records table for the kit's <Rec> component: where a citation on a narrative page can be followed to the record.

    python3 tools/build_records.py            write site/src/data/records.json
    python3 tools/build_records.py --check    CI-safe: the committed table is what the committed data derives (nothing more)

WHY (the linking standard, L3, 18 October 2026). A narrative page that says "image 306", "sig. 00899" or "ark 1:1:6B47-LG4G"
should let the reader go to that record. The addresses were in the archive all along, in files no page read.

WHAT IT HOLDS, and from what. Every row's address is one the archive already holds in committed data; nothing is composed
from a pattern, nothing is guessed:
  snapshot   sources/snapshots.psv (site/src/data/snapshots.json): the viewer link of each of the 495 snapshots. A
             FamilySearch image ark, or a Matricula page. LINK-ONLY: no row has a plate; the table never asks <Rec> to show
             an image (FamilySearch frames and Matricula pages are link-only everywhere, David's ruling of 18 October 2026).
  trove      sources/trove.psv (trove.json): the 74 articles, each at nla.gov.au.
  matricula  every Matricula address written in site/src/data/searched.json or snapshots.json: a parish (/<parish>/), a volume
             (/<parish>/<sig>/) or a page of one (?pg=N), exactly as written there.
  film       every FamilySearch film address written in searched.json WITHOUT an image index (/search/film/<DGS>): the film,
             never an image of it.
  ark        every FamilySearch record ark written in a find's or a reading's citation as «ark 1:1:XXXX-XXXX»: the record.

A row flagged `hold` is never drawn by <Rec>. A snapshot row whose supporting people include anyone the living list holds
would be flagged; none is (the snapshots are published on /snapshots/ already, every one passed that gate).

Counts only are printed.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(DATA, "records.json")

MATP = re.compile(r"https://data\.matricula-online\.eu/sl/slovenia/ljubljana/([a-z-]+)/(?![\w-])")
MAT = re.compile(r"https://data\.matricula-online\.eu/sl/slovenia/ljubljana/([a-z-]+)/(\d{5})/(\?pg=(\d+))?")
FILM = re.compile(r"https://www\.familysearch\.org/(?:en/)?search/film/(\d{9})(?![\d?])")
ARK_IN_TEXT = re.compile(r"\bark\s+([13]:1:[A-Z0-9]{4}-[A-Z0-9]{3,5}(?:-[A-Z0-9]{1,5})?)(?![A-Z0-9-])")
PARISH = {"kranj-smartin": "Kranj–Šmartin", "nova-oselica": "Nova Oselica"}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def build():
    rows, seen = [], set()

    def add(row):
        if row["id"] in seen:
            raise SystemExit("records: duplicate id %s" % row["id"])
        seen.add(row["id"])
        rows.append(row)

    snaps = load("snapshots.json")["rows"]
    for s in snaps:
        v = s.get("view") or ""
        if not v.startswith("https://"):
            continue
        add({"id": s["id"], "url": v, "label": "Snapshot: " + s["title"], "kind": "snapshot"})
    for t in load("trove.json")["rows"]:
        add({"id": "trove-%s" % t["id"], "url": t["url"], "label": "Trove: %s, %s, p. %s" % (t["paper"], t["date"], t["page"]),
             "kind": "trove"})
    mat = set()
    blob = json.dumps(load("searched.json"), ensure_ascii=False) + json.dumps(load("snapshots.json"), ensure_ascii=False)
    for m in MAT.finditer(blob):
        mat.add((m.group(1), m.group(2), m.group(4)))
    for par in sorted(set(MATP.findall(blob))):
        add({"id": "matricula-%s" % par, "url": "https://data.matricula-online.eu/sl/slovenia/ljubljana/%s/" % par,
             "label": "Matricula: the parish of %s (Nadškofijski arhiv Ljubljana)" % PARISH.get(par, par), "kind": "matricula"})
    for par, sig, pg in sorted(mat, key=lambda x: (x[0], x[1], int(x[2] or 0))):
        url = "https://data.matricula-online.eu/sl/slovenia/ljubljana/%s/%s/%s" % (par, sig, ("?pg=" + pg) if pg else "")
        add({"id": "matricula-%s-%s%s" % (par, sig, ("-p" + pg) if pg else ""), "url": url,
             "label": "Matricula: %s, sig. %s%s" % (PARISH.get(par, par), sig, (", image " + pg) if pg else ""), "kind": "matricula"})
    films = sorted(set(FILM.findall(blob)))
    sblob = json.dumps(load("searched.json"), ensure_ascii=False)
    for f in sorted(set(FILM.findall(sblob))):
        add({"id": "fs-film-%s" % f, "url": "https://www.familysearch.org/search/film/%s" % f,
             "label": "FamilySearch: digital film DGS %d" % int(f), "kind": "film"})
    arks = set()
    for r in load("found.json")["rows"]:
        arks.update(ARK_IN_TEXT.findall(r.get("citation") or ""))
    for r in load("readings.json")["rows"]:
        arks.update(ARK_IN_TEXT.findall(r.get("cite") or ""))
    for a in sorted(arks):
        add({"id": "fs-" + a.replace(":", "-"), "url": "https://www.familysearch.org/ark:/61903/" + a,
             "label": "FamilySearch record " + a, "kind": "ark"})
    return {"records": rows}


def dumps(t):
    return '{"records":[\n' + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in t["records"]) + "\n]}\n"


def main(argv):
    t = build()
    text = dumps(t)
    kinds = {}
    for r in t["records"]:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    if "--check" in argv:
        try:
            have = open(OUT, encoding="utf-8").read()
        except OSError:
            print("records  MISSING: run tools/build_records.py")
            return 1
        if have != text:
            print("records  FAIL  the committed table is not what the committed data derives (run tools/build_records.py)")
            return 1
        print("records  ok  %d rows (%s) are exactly what the committed data derives" % (
            len(t["records"]), ", ".join("%d %s" % (n, k) for k, n in sorted(kinds.items()))))
        return 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("records  %d rows (%s)" % (len(t["records"]), ", ".join("%d %s" % (n, k) for k, n in sorted(kinds.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
