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
import livingset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "sources", "media", "manifest.psv")
# Media the family supplied by hand. Kept in a second file because the next
# MyHeritage sweep rewrites manifest.psv wholesale, and a hand-added row there
# would vanish without anybody noticing. See sources/media/local.psv.
LOCAL = os.path.join(ROOT, "sources", "media", "local.psv")
OUT = os.path.join(ROOT, "site", "src", "data", "media.json")

people, families = load()
# WHO IS LIVING OR HELD OUT is the one rule (tools/livingset.py). A living person has no photograph in
# this archive (David's standard, 16 October 2026), so any item tagged with one is withheld here, before
# it reaches media.json, and so is any item listed in sources/media/withheld.psv: a photograph that SHOWS
# living people although the tree tags only somebody who has died (25 October 2026).
_cls = livingset.classify(people, families)
SHOWS_LIVING = _cls["living"] | _cls["held"]
WITHHELD = {}
_wpath = os.path.join(ROOT, "sources", "media", "withheld.psv")
if os.path.exists(_wpath):
    for _l in open(_wpath, encoding="utf-8"):
        if _l.strip() and not _l.startswith("#") and "|" in _l:
            _f = [x.strip() for x in _l.rstrip("\n").split("|")]
            WITHHELD[_f[0]] = _f[1] if len(_f) > 1 else ""
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

def manifest_lines():
    for path in (MAN, LOCAL):
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line and not line.startswith("#"):
                yield line


rows, dropped = [], []
for line in manifest_lines():
    mid, typ, name, w, h, ppl, url = line.split("|")
    if mid in WITHHELD:
        dropped.append((mid, "withheld: shows living people"))
        continue
    if any(f'@I{int(pid) - 4000000}@' in SHOWS_LIVING for pid in ppl.split(",") if pid.strip().isdigit()):
        dropped.append((mid, "withheld: tagged with a living person"))
        continue
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
    # Outside the per-person loop, deliberately. It sat inside until 21 September
    # 2026, so an item with no resolvable tagged person was silently given the
    # PREVIOUS item's kind. Nothing was wrong on the day it was found — every row
    # had at least one person — but the next sweep need only add one that does not.
    kind = OVERRIDE.get(mid, "document" if DOC.search(name) else "photograph")
    if kind == "excluded":
        # Not a document, not a photograph, and not published: a stock graphic
        # standing in for a person who has no picture. See classification.json.
        dropped.append((mid, name))
        continue
    rows.append({"mid": mid, "type": typ, "caption": name,
                 "w": int(w or 0), "h": int(h or 0),
                 "file": fn,
                 "kind": kind,
                 "people": tagged})

rows.sort(key=lambda r: (r["kind"] != "document", -(r["w"] * r["h"])))
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(rows)} media items -> {os.path.relpath(OUT, ROOT)}")
print(f'  {sum(1 for r in rows if r["kind"]=="document")} documents, '
      f'{sum(1 for r in rows if r["kind"]=="photograph")} photographs')
for mid, name in dropped:
    print(f'  excluded: {mid} {name}')
