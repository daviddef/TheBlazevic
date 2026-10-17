#!/usr/bin/env python3
"""Make one reading sheet per register page from its two stitched columns (needs ffmpeg).

  python3 tools/fs_sheet.py LEFT.jpg RIGHT.jpg OUT.jpg [SCALE=0.55] [SPLIT=2]

Each column is cut into SPLIT strips that overlap by 170 px (so no row is lost on a cut; before 17 Oct 2026 late they did not) and the strips of both columns are laid side by
side: L1 L2 R1 R2 for SPLIT=2. A full register page then reads in one view at about half
source size, with the page's own rows in order and nothing cut off.
"""
import subprocess, sys, json
L, R, OUT = sys.argv[1:4]
OV = 170
sc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.55
n = int(sys.argv[5]) if len(sys.argv) > 5 else 2
def size(p):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "json", p])
    s = json.loads(o)["streams"][0]; return s["width"], s["height"]
parts = []
for i, p in enumerate((L, R)):
    w, h = size(p); sh = h // n
    for k in range(n):
        y0 = max(0, k * sh - (OV if k else 0))      # overlap: a row on the cut shows whole in one strip
        parts.append((i, k, w, min(h - y0, sh + (OV if k else 0) + OV), y0))
cmd = ["ffmpeg", "-y", "-v", "error", "-i", L, "-i", R]
fc, labels = [], []
for j, (i, k, w, sh, y) in enumerate(parts):
    fc.append("[%d:v]crop=%d:%d:0:%d,scale=iw*%.3f:ih*%.3f[p%d]" % (i, w, sh, y, sc, sc, j)); labels.append("[p%d]" % j)
fc.append("".join(labels) + "hstack=inputs=%d[o]" % len(parts))
subprocess.check_call(cmd + ["-filter_complex", ";".join(fc), "-map", "[o]", "-q:v", "3", OUT])
print(OUT, size(OUT))
