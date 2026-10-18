#!/usr/bin/env python3
"""Unpack a browser-pane spill holding [L,R,L,R,...] base64 JPEGs (page columns at deep-zoom level 12)
into OUTDIR/pN-L.jpg and pN-R.jpg, one image per page for direct reading (no sheets).

  python3 tools/fs_unpack_pages.py SPILL OUTDIR n1,n2,...
Level 12 is half of full size: four times fewer tiles than level 13, about 4 s a page, and a Karlobag or
Mrežnica page reads at about 1540 px wide. Use fs_unpack.py (level 13 + sheets) when the hand needs full size.
"""
import json, base64, sys, os
spill, out, nums = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
t = json.load(open(spill, encoding="utf-8"))[0]["text"]
arr = json.loads(t[: t.rindex("]") + 1])
if arr and isinstance(arr[0], list):
    arr = [x for p in arr for x in p]
os.makedirs(out, exist_ok=True)
for k, n in enumerate(nums):
    for j, side in enumerate("LR"):
        open(os.path.join(out, "p%d-%s.jpg" % (n, side)), "wb").write(base64.b64decode(arr[2 * k + j]))
    print("image", n)
