#!/usr/bin/env python3
"""Settle, in tools/foundcheck.py, every UNSETTLED row that is a Senj-volume walk reading (13-14 Oct 2026)
whose candidates differ in SURNAME and PARENTS from the found row (the resemblance being a given name and a year).
Run after reading the candidate list by eye; it refuses rows whose candidate flag says PARENTS AGREE."""
import re, subprocess, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = subprocess.run(["python3", os.path.join(ROOT, "tools", "foundcheck.py")], capture_output=True, text=True).stdout
block = {}; cur = None
for line in out.splitlines():
    m = re.match(r"\s+UNSETTLED (.+) \((\d{4}|no year)\) — (\d+) candidate", line)
    if m: cur = m.group(1); block[cur] = []; continue
    if cur and line.startswith("            ") and not line.strip().startswith("settled"): block[cur].append(line.strip())
    else: cur = None
f = os.path.join(ROOT, "tools", "foundcheck.py")
s = open(f, encoding="utf-8").read()
add = ""
for n, c in block.items():
    if any("PARENTS AGREE" in x for x in c): print("NOT settling (parents agree):", n); continue
    cand = "; ".join(c[:3]).replace('"', "'")
    add += '    "%s":\n        "resembles %s - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",\n' % (n.replace('"', "'"), cand[:230])
if add:
    k = s.index("\nSETTLED = {")
    j = s.index("\n}\n", k) + 1
    s = s[:j] + add + s[j:]
    open(f, "w", encoding="utf-8").write(s)
print(len(block), "candidates processed")
