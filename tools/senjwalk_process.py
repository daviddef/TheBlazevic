#!/usr/bin/env python3
"""Turn unprocessed hits in sources/senj-walk-ledger.json into snapshots.psv + found.psv rows.
PEOPLE maps hit id -> (found name, headline, event, date, place)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(ROOT, "sources", "senj-walk-ledger.json")
d = json.load(open(L, encoding="utf-8"))
PEOPLE = json.load(open(os.path.join(ROOT, "sources", "senj-walk-people.json"), encoding="utf-8"))
FILM = "Senj marriages (Vjenčani) 1734–1819, 1820–1858 and deaths 1820–1858 (FamilySearch waypoint 9RK1-W3P, 592 images)"
snap = open(os.path.join(ROOT, "sources", "snapshots.psv"), encoding="utf-8").read().rstrip("\n").split("\n")
found = open(os.path.join(ROOT, "sources", "found.psv"), encoding="utf-8").read().rstrip("\n").split("\n")
arks = json.load(open(os.path.join(ROOT, "sources", "senj-walk-arks.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "sources", "senj-walk-arks.json")) else {}
n = 0
for h in d["hits"]:
    if h.get("processed"): continue
    p = PEOPLE.get(h["id"])
    if not p: print("no people entry for", h["id"]); continue
    name, headline, event, date, place = p
    slug = name.lower().replace(" ", "-").replace("«", "").replace("»", "")
    import unicodedata
    slug = "".join(c for c in unicodedata.normalize("NFD", slug) if unicodedata.category(c) != "Mn")
    view = arks.get(str(h["image"]), "")
    side = "left-hand" if h["side"] == "L" else "right-hand"
    where = "image %d, %s page, %s" % (h["image"], side, h.get("where", "see the entry quoted"))
    if not any(r.startswith(h["id"] + "|") for r in snap):
        snap.append("|".join([h["id"], h["id"] + "-line.jpg", "", "Senj, " + h["year"] + " — " + name, FILM, where, view, h["says"], slug, "14 October 2026", "notes/senj-marriage-volume-walk.md"]))
    if not any(r.startswith(name + "|") for r in found):
        cit = "(1) " + FILM + ", " + where + ": " + h["says"] + " (snapshotted; read at about 6x). See notes/senj-marriage-volume-walk.md"
        found.append("|".join([name, "", headline, event, date, place, cit]))
    stage = os.path.join(ROOT, "sources", "senj-walk-snaps", h["id"] + "-line.jpg")
    if os.path.exists(stage):
        os.replace(stage, os.path.join(ROOT, "site", "public", "snaps", h["id"] + "-line.jpg"))
    h["processed"] = True; n += 1
open(os.path.join(ROOT, "sources", "snapshots.psv"), "w", encoding="utf-8").write("\n".join(snap) + "\n")
open(os.path.join(ROOT, "sources", "found.psv"), "w", encoding="utf-8").write("\n".join(found) + "\n")
json.dump(d, open(L, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(n, "hits processed")
