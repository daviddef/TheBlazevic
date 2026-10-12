#!/usr/bin/env python3
"""Rewrite the pages/got text of the searched.json row fs/senj-marriage-volume-walk from the ledger (13 Oct 2026)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(ROOT, "sources", "senj-walk-ledger.json"), encoding="utf-8"))
S = os.path.join(ROOT, "sources", "searched.json")
d = json.load(open(S, encoding="utf-8"))
done = sorted(int(k) for k, v in L["images"].items() if v.get("status") == "done")
def ranges(xs):
    out = []; lo = prev = None
    for x in xs:
        if lo is None: lo = prev = x
        elif x == prev + 1: prev = x
        else: out.append((lo, prev)); lo = prev = x
    if lo is not None: out.append((lo, prev))
    return out
def fmt(rs): return ", ".join(str(a) if a == b else "%d–%d" % (a, b) for a, b in rs)
dn = ranges(done)
alln = set(range(1, 593)); notread = ranges(sorted(alln - set(done)))
for sec in d.values():
    if not isinstance(sec, list): continue
    for r in sec:
        if isinstance(r, dict) and r.get("key") == "fs/senj-marriage-volume-walk":
            old = r["pages"]
            head = old.split(" IMAGES 10–79")[0]
            tail = " IMAGES 10–79" + old.split(" IMAGES 10–79", 1)[1].split(" Not read yet:")[0]
            r["pages"] = "images %s read both pages (%d of 592; item 1, the 1734–1819 Latin-prose marriages, images 10–206, is done; item 2, 1820–1858, begins at image 209 and is a bundle of interleaved sequences)." % (fmt(dn), len(done)) + tail + " Not read yet: %s." % fmt(notread)
            r["when"] = "14 October 2026"
            print(r["pages"])
json.dump(d, open(S, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
