#!/usr/bin/env python3
"""Turn the MyHeritage media manifest into JSON the site can render.

The manifest is a pipe-separated file written by the media sweep:
  media_id | type | caption | width | height | tagged individual ids | source url

The individual ids are MyHeritage's, which are `4000000 + n` for GEDCOM record
`@In@`. That mapping is the only reason a sweep of this kind is possible at all,
so it is applied here and the GEDCOM ids are what the site stores.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "sources", "media", "manifest.psv")
OUT = os.path.join(ROOT, "site", "src", "data", "media.json")

people, families = load()
try:
    reg = {p["id"]: p for p in json.load(
        open(os.path.join(ROOT, "site", "src", "data", "people.json"), encoding="utf-8"))}
    anc = {p["id"]: p for p in json.load(
        open(os.path.join(ROOT, "site", "src", "data", "ancestors.json"), encoding="utf-8"))}
    reg.update(anc)
except FileNotFoundError:
    reg = {}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:52]


# Which media are documents rather than snapshots. A register scan and a holiday
# photograph are not the same kind of evidence and should not sit in one grid.
DOC = re.compile(r"birth|baptism|marriage|death|certificate|grave|card file|war time|biography",
                 re.I)

# The caption is a poor classifier: a register page uploaded under a camera
# filename reads as a snapshot. Anything that has actually been opened and
# looked at is recorded here and overrides the guess.
OVERRIDE = {k: v for k, v in json.load(
    open(os.path.join(ROOT, "sources", "media", "classification.json"),
         encoding="utf-8")).items() if not k.startswith("_")}

rows = []
for line in open(MAN, encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    mid, typ, name, w, h, ppl, url = line.split("|")
    ext = "pdf" if typ == "document" else "jpg"
    fn = f"{mid}-{slugify(name)}.{ext}".replace(" ", "-")
    tagged = []
    for pid in ppl.split(","):
        gid = f'@I{int(pid) - 4000000}@'
        p = people.get(gid)
        if not p:
            continue
        pub = reg.get(gid)
        tagged.append({"id": gid, "name": display(p),
                       "slug": pub["slug"] if pub else None,
                       "years": f'{year(born(p).get("date","")) or "?"}–{year(died(p).get("date","")) or "?"}'})
    rows.append({"mid": mid, "type": typ, "caption": name,
                 "w": int(w or 0), "h": int(h or 0),
                 "file": fn,
                 "kind": OVERRIDE.get(mid, "document" if DOC.search(name) else "photograph"),
                 "people": tagged})

rows.sort(key=lambda r: (r["kind"] != "document", -(r["w"] * r["h"])))
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(rows)} media items -> {os.path.relpath(OUT, ROOT)}")
print(f'  {sum(1 for r in rows if r["kind"]=="document")} documents, '
      f'{sum(1 for r in rows if r["kind"]=="photograph")} photographs')
