#!/usr/bin/env python3
"""Control file helper for the full read of the Senj volume 9RK1-W3P (13 Oct 2026).

  senjwalk.py done 10 11 12-14 ...        mark images done (ranges ok)
  senjwalk.py note 13 "text"              attach a note to an image
  senjwalk.py hit ID IMAGE SIDE "YEAR" "NAMES" "SAYS" [CROP_H CROP_FILE]
        records a hit and, with a crop, copies the cropped jpg into site/public/snaps/ID-line.jpg
  senjwalk.py next                        first image not done
  senjwalk.py status
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "sources", "senj-walk-ledger.json")
def load(): return json.load(open(F, encoding="utf-8"))
def save(d): json.dump(d, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def rng(a):
    for x in a:
        if "-" in x:
            lo, hi = x.split("-"); yield from range(int(lo), int(hi) + 1)
        else: yield int(x)
c = sys.argv[1]; d = load()
if c == "done":
    for n in rng(sys.argv[2:]): d["images"].setdefault(str(n), {})["status"] = "done"
    save(d)
elif c == "note":
    d["images"].setdefault(sys.argv[2], {})["note"] = sys.argv[3]; save(d)
elif c == "hit":
    id_, img, side, year, names, says = sys.argv[2:8]
    if any(h["id"] == id_ for h in d["hits"]): sys.exit("hit exists")
    d["hits"].append({"id": id_, "image": int(img), "side": side, "year": year, "names": names, "says": says, "snapshot": False, "processed": False})
    if len(sys.argv) >= 10:
        h, src = sys.argv[8], sys.argv[9]
        os.makedirs(os.path.join(ROOT, "sources", "senj-walk-snaps"), exist_ok=True)
        out = os.path.join(ROOT, "sources", "senj-walk-snaps", id_ + "-line.jpg")
        subprocess.check_call(["sips", "-c", h, "800", "--cropOffset", "0", "0", src, "--out", out], stdout=subprocess.DEVNULL)
        d["hits"][-1]["snapshot"] = True
    save(d)
elif c == "strip":
    todo = d.get("strip_todo", [])
    print("strip pass: %d images left; next %s" % (len(todo), todo[:6]))
elif c == "stripdone":
    for n in rng(sys.argv[2:]):
        if n in d.get("strip_todo", []): d["strip_todo"].remove(n)
    save(d)
elif c == "next":
    done = {int(k) for k, v in d["images"].items() if v.get("status") == "done"}
    print(next(n for n in range(1, 593) if n not in done))
elif c == "status":
    done = {int(k) for k, v in d["images"].items() if v.get("status") == "done"}
    print(len(done), "images done of 592; strip pass left:", len(d.get("strip_todo", [])), ";", len(d["hits"]), "hits,", sum(1 for h in d["hits"] if not h["processed"]), "unprocessed")
