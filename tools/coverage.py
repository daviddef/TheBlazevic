#!/usr/bin/env python3
"""How much of the direct line actually rests on a document.

Every page here says what its evidence is, person by person. Nobody had ever
added it up. After a day in which three joins on the spine were disputed -
Oreskovic, Bacchi, Pecanic - the honest total matters more than any single page.

Four states, in descending order of what they are worth:

    read      a register or certificate for this person has been read here
    scanned   an image is attached but has not been read out
    named     no record of their own, but they are named in somebody else's
    tree      the tree asserts them and nothing else does

`named` is where the Latin genitives live: a man who appears only as
"filius Pauli" has no record, only records that mention him.
"""
import json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")


def load(n):
    return json.load(open(os.path.join(DATA, n), encoding="utf-8"))


anc = load("ancestors.json")
media = load("media.json")
corr = load("corrections.json")
con = load("consistency.json")
latin = {l["slug"] for l in load("latincases.json")} if os.path.exists(
    os.path.join(DATA, "latincases.json")) else set()

# people with an image attached, and people a correction actually discusses
with_media = collections.Counter()
for m in media:
    for p in (m.get("people") or []):
        if p.get("slug"):
            with_media[p["slug"]] += 1

read_ids, disputed = set(), set()
for c in corr:
    (disputed if c["kind"] == "disputed" else read_ids).add(c["id"])
for i in con:
    if i.get("slug") and i["sev"] == 1:
        disputed.add(i["id"])

rows = []
for a in anc:
    ahn = a.get("ahnentafel") or a.get("ahn")
    if not ahn:
        continue
    gen = ahn.bit_length()          # 1 -> gen 1, 2-3 -> 2, 4-7 -> 3 ...
    n_media = with_media.get(a["slug"], 0)
    if a["id"] in read_ids:
        state = "read"
    elif n_media:
        state = "scanned"
    elif a["id"] in disputed:
        state = "named"
    elif a.get("born") or a.get("died"):
        state = "named"
    else:
        state = "tree"
    rows.append({
        "ahn": ahn, "gen": gen, "name": a["name"], "slug": a["slug"],
        "born": a.get("born") or "", "state": state, "media": n_media,
        "disputed": a["id"] in disputed,
        "latin": a["slug"] in latin,
    })

rows.sort(key=lambda r: r["ahn"])
out = os.path.join(DATA, "coverage.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# The same judgement for everyone, not only the direct line, so a person page
# can mark each relative in its chart by what is actually known of them.
everyone = load("people.json") + anc
ev = {}
for q in everyone:
    if q["slug"] in ev:
        continue
    a2 = next((r["ahn"] for r in rows if r["slug"] == q["slug"]), None)
    n = with_media.get(q["slug"], 0)
    if q["id"] in disputed:
        st = "disputed"
    elif q["id"] in read_ids:
        st = "read"
    elif n:
        st = "scanned"
    elif a2:
        st = "line"
    else:
        st = "tree"
    ev[q["slug"]] = {"state": st, "ahn": a2, "media": n}
json.dump(ev, open(os.path.join(DATA, "evidence.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"evidence.json: {len(ev)} people  "
      + str(dict(collections.Counter(v['state'] for v in ev.values()))))

by_gen = collections.defaultdict(collections.Counter)
for r in rows:
    by_gen[r["gen"]][r["state"]] += 1
print(f"{len(rows)} direct ancestors\n")
print(f"{'gen':<5}{'known':>7}{'possible':>10}{'read':>7}{'scanned':>9}{'named':>7}{'tree':>6}{'disputed':>10}")
for g in sorted(by_gen):
    c = by_gen[g]
    known = sum(c.values())
    d = sum(1 for r in rows if r["gen"] == g and r["disputed"])
    print(f"{g:<5}{known:>7}{2 ** (g - 1):>10}{c['read']:>7}{c['scanned']:>9}"
          f"{c['named']:>7}{c['tree']:>6}{d:>10}")
tot = collections.Counter(r["state"] for r in rows)
print(f"\ntotal: {dict(tot)}  disputed: {sum(1 for r in rows if r['disputed'])}")
print(f"wrote {os.path.relpath(out, ROOT)}")
