#!/usr/bin/env python3
"""Find a Grave's Zubrinich memorials, matched against this archive's people.

A cemetery index is not a register and this tool says so in its output: a date
here may be the burial rather than the death, and a plot number is Find a
Grave's transcription of a cemetery's own record. What it is very good for is
the thing a parish register cannot do — it puts people in the SAME GROUND.

Shared plot is the whole point. «CC, Lot 26, 1» holds John Zubrinich and two
children who died at eight and at six months. «PRF, Lot 5, 10» holds Thomas Leo
and a woman this archive has never heard of. That is a household, read off a
lot number.

Nothing here is merged into the tree. The output marks each memorial as matched
to a published person or not, and where a matched date disagrees it prints the
disagreement rather than choosing.

Writes site/src/data/graves.json.
"""
import json
import os
import re
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "findagrave", "zubrinich-2026-09-14.psv")
DATA = os.path.join(ROOT, "site", "src", "data")

MONTH = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
STOP = {"zubrinich", "zubrinic", "zubrinić"}


def flat(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(name):
    return {t for t in re.findall(r"[a-z]+", flat(name)) if t not in STOP and len(t) > 1}


def parse(s):
    """'6 Mar 1860' -> date; '1860' -> (1860, None); '' -> None."""
    s = str(s or "").strip()
    if not s:
        return None
    m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})$", s)
    if m:
        return date(int(m.group(3)), MONTH[m.group(2).lower()], int(m.group(1)))
    m = re.search(r"\b(1[789]\d\d|20\d\d)\b", s)
    return date(int(m.group(1)), 1, 1) if m else None


def year(s):
    d = parse(s)
    return d.year if d else None


def exact(s):
    return bool(re.match(r"\d{1,2}\s+[A-Za-z]{3}", str(s or "").strip()))


def main():
    people = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))
    zub = [p for p in people if "zubrini" in flat(p.get("name"))]

    rows = []
    for line in open(SRC, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        name, b, d, cem, place, plot = (line.split("|") + [""] * 6)[:6]
        rows.append({"name": name, "born": b, "died": d, "cemetery": cem,
                     "place": place, "plot": plot})

    # --- match each memorial to a published person -----------------------
    conflicts = []
    for r in rows:
        g, by, dy = toks(r["name"]), year(r["born"]), year(r["died"])
        best, bestscore = None, 0
        for p in zub:
            pg = toks(p.get("name"))
            if not (g & pg):
                continue
            pb, pd = p.get("byear"), p.get("dyear")
            # a two-year gap on BOTH dates is a different person
            if by and pb and abs(pb - by) > 2 and dy and pd and abs(pd - dy) > 2:
                continue
            score = len(g & pg) + (2 if by and pb == by else 0) + (2 if dy and pd == dy else 0)
            if score > bestscore:
                best, bestscore = p, score
        if best and bestscore >= 3:
            r["slug"], r["archiveName"] = best["slug"], best["name"]
            r["archiveBorn"], r["archiveDied"] = best.get("born", ""), best.get("died", "")
            gd, ad = parse(r["died"]), parse(best.get("died"))
            if gd and ad and exact(r["died"]) and exact(best.get("died")) and gd != ad:
                conflicts.append({"name": r["name"], "slug": best["slug"],
                                  "grave": r["died"], "tree": best.get("died"),
                                  "days": (gd - ad).days})

    # --- who lies in the same ground -------------------------------------
    plots = {}
    for r in rows:
        if not r["plot"] or not r["cemetery"]:
            continue
        key = f"{r['cemetery']} · {r['plot']}"
        plots.setdefault(key, []).append(r)
    shared = [{"plot": k, "cemetery": v[0]["cemetery"], "place": v[0]["place"],
               "people": sorted(v, key=lambda x: year(x["born"]) or year(x["died"]) or 9999),
               "known": sum(1 for x in v if x.get("slug")),
               "unknown": sum(1 for x in v if not x.get("slug"))}
              for k, v in plots.items() if len(v) > 1]
    shared.sort(key=lambda s: (-s["unknown"], s["plot"]))

    where = {}
    for r in rows:
        c = r["cemetery"] or "unrecorded"
        where[c] = where.get(c, 0) + 1

    out = {
        "source": "Find a Grave, searched 14 September 2026",
        "n": len(rows),
        "matched": sum(1 for r in rows if r.get("slug")),
        "unmatched": sum(1 for r in rows if not r.get("slug")),
        "cemeteries": sorted(where.items(), key=lambda kv: (-kv[1], kv[0])),
        "shared": shared,
        "conflicts": sorted(conflicts, key=lambda c: -abs(c["days"])),
        "rows": rows,
    }
    json.dump(out, open(os.path.join(DATA, "graves.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"graves.json — {out['n']} memorials, {out['matched']} matched to a person here, "
          f"{len(shared)} shared plots, {len(conflicts)} date disagreements")


if __name__ == "__main__":
    main()
