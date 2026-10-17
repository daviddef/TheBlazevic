#!/usr/bin/env python3
"""Unpack a browser-pane spill file holding an array of base64 JPEG columns into page files + sheets.

  python3 tools/fs_unpack.py SPILL OUTDIR FIRST_IMAGE [SCALE] [SPLIT]
Array order is [L,R] per image, starting at FIRST_IMAGE and counting up by one unless the images
are listed explicitly as 4th.. args after the numbers "n1,n2,...": pass a comma list as FIRST_IMAGE.
Writes OUTDIR/pNNN-L.jpg, pNNN-R.jpg and sheet-NNN.jpg (tools/fs_sheet.py). For candidate flags only,
run the macOS Vision OCR on a column: swiftc -O tools/vision_ocr.swift -o /tmp/vision_ocr; it reads this
handwriting for about half the lines, so it can point at a name but can never clear a page.
"""
import json, base64, sys, os, subprocess
spill, out, first = sys.argv[1:4]
sc = sys.argv[4] if len(sys.argv) > 4 else "0.5"; n = sys.argv[5] if len(sys.argv) > 5 else "2"; grid = sys.argv[6:7]
t = json.load(open(spill, encoding="utf-8"))[0]["text"]
arr = json.loads(t[: t.rindex("]") + 1])
nums = [int(x) for x in first.split(",")] if "," in first else [int(first) + i for i in range(len(arr) // 2)]
here = os.path.dirname(os.path.abspath(__file__))
for k, num in enumerate(nums):
    for j, side in enumerate("LR"):
        open(os.path.join(out, "p%d-%s.jpg" % (num, side)), "wb").write(base64.b64decode(arr[2 * k + j]))
    subprocess.check_call([sys.executable, os.path.join(here, "fs_sheet.py"), os.path.join(out, "p%d-L.jpg" % num),
                           os.path.join(out, "p%d-R.jpg" % num), os.path.join(out, "sheet-%d.jpg" % num), sc, n] + grid, stdout=subprocess.DEVNULL)
    print("image", num, "sheet-%d.jpg" % num)
