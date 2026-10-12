#!/usr/bin/env python3
"""Page-level 'seen' rows for the Senj volume walk (13 Oct 2026).

Core-family hits get a zoomed crop and a found person each (senjwalk_process.py). The secondary,
very common Senj surnames (Lončarić, Antić, Marić, Jurčić, Karić, Babić beyond the first, ...)
turn up several times on a page; for those the walk keeps ONE page-scale snapshot per page side
and a snapshots.psv row with no found person, listing the entries seen. They are a finding aid:
each needs a zoom read before it is used in an argument (ledger reread_todo['seen-page-scale']).

  senjwalk_seen.py add ID IMAGE SIDE "TITLE" "SAYS" SRC.jpg      stage a seen row
  senjwalk_seen.py process                                        write snapshots.psv rows
"""
import json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = os.path.join(ROOT, "sources", "senj-walk-ledger.json")
SN = os.path.join(ROOT, "sources", "snapshots.psv")
FILM = "Senj marriages (Vjenčani) 1734–1819, 1820–1858 and deaths 1820–1858 (FamilySearch waypoint 9RK1-W3P, 592 images)"
d = json.load(open(L, encoding="utf-8")); d.setdefault("seen", [])
c = sys.argv[1]
if c == "add":
    id_, img, side, title, says, src = sys.argv[2:8]
    if any(s["id"] == id_ for s in d["seen"]): sys.exit("exists")
    os.makedirs(os.path.join(ROOT, "sources", "senj-walk-snaps"), exist_ok=True)
    shutil.copy(src, os.path.join(ROOT, "sources", "senj-walk-snaps", id_ + "-line.jpg"))
    d["seen"].append({"id": id_, "image": int(img), "side": side, "title": title, "says": says, "processed": False})
elif c == "process":
    arks = json.load(open(os.path.join(ROOT, "sources", "senj-walk-arks.json"), encoding="utf-8"))
    rows = open(SN, encoding="utf-8").read().rstrip("\n").split("\n"); n = 0
    for s in d["seen"]:
        if s["processed"]: continue
        side = "left-hand" if s["side"] == "L" else "right-hand"
        if not any(r.startswith(s["id"] + "|") for r in rows):
            rows.append("|".join([s["id"], s["id"] + "-line.jpg", "", s["title"], FILM,
              "image %d, %s page (whole page, read at page scale)" % (s["image"], side),
              arks.get(str(s["image"]), ""), s["says"], "", "14 October 2026", "notes/senj-marriage-volume-walk.md"]))
        stage = os.path.join(ROOT, "sources", "senj-walk-snaps", s["id"] + "-line.jpg")
        if os.path.exists(stage): os.replace(stage, os.path.join(ROOT, "site", "public", "snaps", s["id"] + "-line.jpg"))
        s["processed"] = True; n += 1
    open(SN, "w", encoding="utf-8").write("\n".join(rows) + "\n"); print(n, "seen rows processed")
json.dump(d, open(L, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
