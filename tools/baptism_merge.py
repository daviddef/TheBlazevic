#!/usr/bin/env python3
"""Merge one saved javascript_tool result (a JSON {n,q,log,lines}) into sources/senj-baptism-index2.tsv.

The FamilySearch sweep lives in a browser pane that can close between turns, so every poll is written
to disk here before the next one. Only lines whose place is the parish of Senj ('@Senj') are kept —
«Otočac, Lika-Senj» is the county, not the parish. One row per record ark.

  baptism_merge.py RESULT.json
"""
import json, os, re, sys
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sources", "senj-baptism-index2.tsv")
t = json.load(open(sys.argv[1]))[0]["text"]
t, _ = json.JSONDecoder().raw_decode(t)
d = json.loads(t)
have = set()
if os.path.exists(OUT):
    have = {l.split("\t")[0] for l in open(OUT, encoding="utf-8") if l.strip()}
new = [l for l in d["lines"] if re.search(r"@Senj\b", l) and l.split("\t")[0] not in have]
with open(OUT, "a", encoding="utf-8") as f:
    for l in new: f.write(l + "\n")
print("polled %d, new Senj %d, total %d, queue %s, done %s" % (d["n"], len(new), len(have) + len(new), d["q"],
      sorted(k for k, v in d["log"].items() if v == "done")[-3:]))
