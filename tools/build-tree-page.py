#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roots & Routes: the tree page for this archive, built from this archive's own committed data.

    python3 tools/build-tree-page.py            # rebuild data/tree-page/ (tree.json, atlas-data.json, roots.html, roots.embed.html) and site/public/roots-links.json
    python3 tools/build-tree-page.py --check    # exit 1 if the page is older than the data it was built from

WHERE THE PEOPLE COME FROM. There is no committed GEDCOM (the tree export carries living dates and stays outside the repo). The people are the ones
site/src/data/people.json holds, which is written from the tree by tools/build_site_data.py WITHOUT any living person (living people are in living.json,
as a name and a relationship). That file is turned into a small GEDCOM (data/tree-page/people.ged, not committed) and handed to the family-tree-page skill's
converter, vendored in tools/tree-page/ so CI and other sessions do not depend on ~/.claude. The converter then adds its own floor: nobody with no death
recorded and a birth year in the last 110 years is drawn.

COLOUR is the archive's own family (the `family` of a person in people.json, the labels of families.json), not a surname spelling: which spellings are one
name is the Record Atlas catalogue's to say (surname-variants skill), and this archive keeps no list of them.

PLACES are resolved through data/tree-page/place_map.json, never guessed: a place string the Record Atlas names uniquely in the country the string names is
accepted; the archive's own era-towns.tsv points are used for the rest it holds; anything else is listed in tree.report.json (unresolved_places) and the person is
placed at a relative's birth place or left off, and said so.

A ROUTE (three or more places) is carried whole for a person whose tree says where they came from: an `immigration` event with the detail «From Zimbabwe»
puts Zimbabwe between the birth place and the place of arrival (Hedviga: Senj, Zimbabwe, Johannesburg). A stop with no year is an undated arrival.
"""
import argparse, collections, datetime, hashlib, io, json, os, re, subprocess, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(ROOT, "data", "tree-page")
TP = os.path.join(ROOT, "tools", "tree-page")
EXT = os.path.join(TP, "painted-lines.ext.html")
HOST = "blazevic.defranceski.com"
ATLAS_CANDIDATES = [os.environ.get("RECORD_ATLAS", ""), os.path.expanduser("~/Projects/Family Projects/Record Atlas"),
                    os.path.join(os.path.dirname(ROOT), "Record Atlas")]
INPUTS = ["people.json", "families.json", "living.json"]

def jl(path): return json.load(io.open(path, encoding="utf-8"))
def run(args):
    print("$", " ".join(os.path.relpath(a, ROOT) if os.path.isabs(a) and a.startswith(ROOT) else a for a in args)); r = subprocess.run(args)
    if r.returncode: sys.exit(r.returncode)
def inputs_hash():
    h = hashlib.sha1()
    for n in INPUTS: h.update(io.open(os.path.join(DATA, n), "rb").read())
    for n in ("tree-views.template.html", "painted-lines.ext.html", "gedcom_to_tree.py"): h.update(io.open(os.path.join(TP, n), "rb").read())
    h.update(io.open(os.path.abspath(__file__), "rb").read())
    pm = os.path.join(OUT, "place_map.json")
    if os.path.exists(pm): h.update(io.open(pm, "rb").read())
    return h.hexdigest()[:16]
def atlas_path():
    for c in ATLAS_CANDIDATES:
        if c and os.path.exists(os.path.join(c, "data", "places.json")): return c
    sys.exit("Record Atlas checkout not found (set RECORD_ATLAS)")

# ---------------------------------------------------------------- people.json -> a small GEDCOM
def gdate(v):
    v = "" if v is None else str(v).strip()
    return v
def write_ged(people, path):
    ids = {p["id"] for p in people}
    out = ["0 HEAD", "1 CHAR UTF-8"]
    fams, fam_of_child, fam_of_spouse = {}, {}, collections.defaultdict(list)
    def fam(h, w):
        k = (h or "", w or "")
        if k not in fams: fams[k] = "@F%d@" % (len(fams) + 1)
        return fams[k]
    for p in people:
        par = [r for r in (p.get("rel") or {}).get("parents", []) if r.get("id") in ids]
        sex = {r["id"]: next((q["sex"] for q in people_by_id.get(r["id"], [])), "") for r in par}
        f = next((r["id"] for r in par if sex.get(r["id"]) == "M"), None)
        m = next((r["id"] for r in par if sex.get(r["id"]) == "F"), None)
        if not (f or m) and par:  # a parent of unrecorded sex: first is the father, second the mother, as the tree lists them
            f = par[0]["id"]; m = par[1]["id"] if len(par) > 1 else None
        if f or m: fam_of_child[p["id"]] = fam(f, m)
        for s in (p.get("rel") or {}).get("spouses", []):
            if s.get("id") in ids:
                a, b = (p["id"], s["id"]) if p.get("sex") == "M" else (s["id"], p["id"])
                k = fam(a, b)
                if k not in fam_of_spouse[p["id"]]: fam_of_spouse[p["id"]].append(k)
    for p in people:
        out += ["0 %s INDI" % p["id"], "1 NAME %s /%s/" % (p.get("given") or "", p.get("surname") or ""), "1 SEX %s" % (p.get("sex") or "M")]
        if p.get("born") or p.get("bornPlace") or p.get("byear"):
            out.append("1 BIRT"); out.append("2 DATE %s" % gdate(p.get("born") or p.get("byear")))
            if p.get("bornPlace"): out.append("2 PLAC %s" % p["bornPlace"])
        if p.get("died") or p.get("diedPlace") or p.get("dyear") or p.get("burial"):
            out.append("1 DEAT"); out.append("2 DATE %s" % gdate(p.get("died") or p.get("dyear")))
            if p.get("diedPlace"): out.append("2 PLAC %s" % p["diedPlace"])
        for e in p.get("events") or []:
            if e.get("kind") in ("residence", "immigration", "emigration", "census") and e.get("place"):
                out += ["1 RESI", "2 DATE %s" % gdate(e.get("date")), "2 PLAC %s" % e["place"]]
        for o in p.get("occupations") or []:
            if o.get("what"): out.append("1 OCCU %s" % o["what"]); break
        if p["id"] in fam_of_child: out.append("1 FAMC %s" % fam_of_child[p["id"]])
        for fx in fam_of_spouse.get(p["id"], []): out.append("1 FAMS %s" % fx)
    for (h, w), fx in fams.items():
        out.append("0 %s FAM" % fx)
        if h: out.append("1 HUSB %s" % h)
        if w: out.append("1 WIFE %s" % w)
        for cid, f in fam_of_child.items():
            if f == fx: out.append("1 CHIL %s" % cid)
    out.append("0 TRLR")
    io.open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---------------------------------------------------------------- places the archive has already placed
TOWN = re.compile(r"^(.*?) \((-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?)\)$")
def fold(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()).strip()
def km(a, b, c, d):
    import math
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))

def seed_place_map(atlas):
    """Place strings this archive has already put on the ground. data/era-ground.tsv decided, for every place string AS PRINTED in people.json, the town it
    belongs to and that town's point (data/era-towns.tsv: the archive's own gazetteer, the kit's cache, the Atlas's GeoNames), and REFUSED a string whose
    names disagree, a bare name that is several places, or a country-only string: those rows have no town and stay unresolved here. The country is the Atlas's
    own `geo.country_of` on the point, never a guess from the string; a Record Atlas place is linked only where it has the same name within 15 km."""
    sys.path.insert(0, os.path.join(atlas, "scripts")); import geo
    cj = jl(os.path.join(atlas, "data", "countries.json"))["countries"]
    pj = jl(os.path.join(atlas, "data", "places.json"))["places"]
    byname = collections.defaultdict(list)
    for x in pj:
        for nm in [x["name"]] + [n["n"].split(",")[0] for n in x.get("names", [])]: byname[fold(nm)].append(x)
    pm_path = os.path.join(OUT, "place_map.json")
    pm = jl(pm_path) if os.path.exists(pm_path) else {}
    seeded = 0
    for line in io.open(os.path.join(ROOT, "data", "era-ground.tsv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip(): continue
        c = line.rstrip("\n").split("\t")
        if len(c) < 4 or c[0] == "place": continue
        raw, town = c[0], TOWN.match(c[3].strip())
        if not town or (pm.get(raw) or {}).get("lat") is not None: continue
        name = town.group(1).strip(); name = name.title() if name.isupper() else name
        lat, lon = float(town.group(2)), float(town.group(3))
        iso = geo.country_of(lat, lon)
        if not iso: continue
        hit = next((x for x in byname.get(fold(name), []) if x.get("country") == iso and km(lat, lon, x["lat"], x["lon"]) <= 15), None)
        pm[raw] = {"name": name, "lat": lat, "lon": lon, "country": cj.get(iso, {}).get("name", iso), "iso": iso, "atlas_id": hit["id"] if hit else None,
                   "how": "data/era-ground.tsv town and point; country by the Atlas's geo.country_of"}
        seeded += 1
    ap_ = os.path.join(OUT, "place-additions.json")
    if os.path.exists(ap_):
        for k, v in jl(ap_)["places"].items():
            if (pm.get(k) or {}).get("lat") is None: pm[k] = v; seeded += 1
    io.open(pm_path, "w", encoding="utf-8").write(json.dumps(pm, indent=1, ensure_ascii=False))
    print("place_map: %d place strings seeded (era-ground.tsv and place-additions.json)" % seeded)

def build(a):
    os.makedirs(OUT, exist_ok=True)
    people = [p for p in jl(os.path.join(DATA, "people.json")) if not p.get("living")]
    global people_by_id
    people_by_id = collections.defaultdict(list)
    for p in people: people_by_id[p["id"]].append(p)
    ged = os.path.join(OUT, "people.ged"); write_ged(people, ged)
    slugs = {p["id"].strip("@"): p["slug"] for p in people}
    io.open(os.path.join(OUT, "slugs.json"), "w", encoding="utf-8").write(json.dumps(slugs, ensure_ascii=False))
    fams = jl(os.path.join(DATA, "families.json"))
    top = sorted(fams, key=lambda f: -f["count"])[:7]
    atlas = atlas_path(); seed_place_map(atlas)
    tree, pm = os.path.join(OUT, "tree.json"), os.path.join(OUT, "place_map.json")
    cmd = [sys.executable, os.path.join(TP, "gedcom_to_tree.py"), ged, "--out", tree, "--place-map", pm, "--atlas", atlas, "--living", "omit",
           "--lines", "8", "--slugs", os.path.join(OUT, "slugs.json"), "--title", "Roots & Routes",
           "--subtitle", "Explore the family tree ten ways: by generation, place, era and relationship. Click anyone and every view follows."]
    if a.accept_unique: cmd.append("--accept-unique")
    run(cmd)
    t = jl(tree)
    fam_of = {p["id"].strip("@"): p.get("family") for p in people}
    key_i = {f["slug"]: i for i, f in enumerate(top)}
    for p in t["people"]:
        p["line"] = key_i.get(fam_of.get(p["id"]), 7)
        p["page"] = "/people/%s/" % slugs[p["id"]] if p["id"] in slugs else None
        if p["page"] is None: p.pop("page")
    t["lines"] = [{"sur": f["label"], "host": HOST} for f in top] + [{"sur": "Other", "host": HOST}]
    t["meta"].update({"rowLabel": "Family line", "lineLabel": "Family line"})
    mark_relative_places(t, people)
    drop_conflicts(t, tree)
    keep_death_place(t, people)
    add_routes(t, people)
    io.open(tree, "w", encoding="utf-8").write(json.dumps(t, ensure_ascii=False, separators=(",", ":")))

def mark_relative_places(t, people):
    """The converter puts a person whose own birth place it cannot resolve (none recorded, or a string the place map does not place) at a relative's birth place, and
    says so only in its report (placed_from_relative). The page can say it on the card (`bpe`: «place taken from a relative, not recorded», and an asterisk), so it does:
    every person whose drawn birth place is not the place their own record names gets it."""
    pm = jl(os.path.join(OUT, "place_map.json"))
    own = {p["id"].strip("@"): (pm.get(p["bornPlace"]) or {}).get("name") if p.get("bornPlace") else None for p in people}
    n = 0
    for p in t["people"]:
        if own.get(p["id"]) != p["bp"]: p["bpe"] = True; n += 1
    print("relative's place: %d people are drawn at a relative's birth place and marked so on the page" % n)

def drop_conflicts(t, tree):
    """A person whose recorded death comes before their birth, or more than 110 years after it, is not one life. They are not drawn, they are named in tree.report.json (conflicts) for the
    research to settle, and every relation to them is removed so the page stays symmetric."""
    bad = {p["id"] for p in t["people"] if p.get("dy") is not None and not 0 <= p["dy"] - p["by"] <= 110}
    if not bad: return
    rep_path = os.path.splitext(tree)[0] + ".report.json"; rep = jl(rep_path)
    rep["conflicts"] = [{"id": p["id"], "slug": p.get("slug"), "born": p["by"], "died": p["dy"]} for p in t["people"] if p["id"] in bad]
    t["people"] = [p for p in t["people"] if p["id"] not in bad]
    for p in t["people"]:
        for k in ("father", "mother"):
            if p.get(k) in bad: p[k] = None
        p["spouse"] = [x for x in p["spouse"] if x not in bad]; p["kids"] = [x for x in p["kids"] if x not in bad]
    if t.get("focus") in bad: t["focus"] = t["people"][0]["id"]
    io.open(rep_path, "w", encoding="utf-8").write(json.dumps(rep, indent=1, ensure_ascii=False))
    print("conflicts: %d people whose death is before their birth are not one life (died before born, or over 110 years) and are not drawn" % len(bad))

def keep_death_place(t, people):
    """The converter takes a later residence as the place of death (a move). A death place the record states and the place map resolves is the place of
    death: Hedviga died at Johannesburg, and «South Africa» is where she arrived in 1975."""
    by = {p["id"].strip("@"): p for p in people}
    pm = jl(os.path.join(OUT, "place_map.json"))
    n = 0
    for p in t["people"]:
        src = by.get(p["id"]); r = pm.get((src or {}).get("diedPlace") or "")
        if r and r.get("lat") is not None and r.get("name") and r["name"] != p["dp"]: p["dp"] = r["name"]; n += 1
    print("death places: %d put back to the recorded place of death" % n)

def add_routes(t, people):
    """A person whose tree says «From <place>» on an immigration gets the whole route, not birth place to death place."""
    by = {p["id"].strip("@"): p for p in people}
    pm = jl(os.path.join(OUT, "place_map.json"))
    ok = lambda k: pm.get(k) and pm[k].get("lat") is not None and pm[k].get("name")
    n = 0
    for p in t["people"]:
        src = by.get(p["id"])
        if not src: continue
        for e in src.get("events") or []:
            m = re.match(r"^\s*from\s+(.+?)\s*$", e.get("detail") or "", re.I)
            if e.get("kind") != "immigration" or not m: continue
            frm = m.group(1)
            if not ok(frm): continue
            y = re.search(r"(1[5-9]\d\d|20[0-2]\d)\s*$", e.get("date") or "")
            dest = pm[e["place"]]["name"] if ok(e.get("place") or "") else None
            end = p["dp"] if p["dp"] != pm[frm]["name"] else dest
            if not end or end == p["bp"] or pm[frm]["name"] in (p["bp"], end): continue
            p["route"] = [[p["bp"], None, 0], [pm[frm]["name"], None, 0], [end, int(y.group(1)) if y else None, 1 if y else 0]]
            n += 1
            break
    print("routes: %d people carry a whole route" % n)

def write_roots_links(tree):
    """site/public/roots-links.json: the people Roots & Routes DRAWS (one id each). The person page offers 'Where they lived' only for those."""
    ids = sorted(p["id"] for p in jl(tree)["people"])
    out = {"note": "The people Roots & Routes draws, by person id. Made by tools/build-tree-page.py; do not edit by hand.", "people": ids}
    io.open(os.path.join(ROOT, "site", "public", "roots-links.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print("roots-links: %d people" % len(ids))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true"); ap.add_argument("--accept-unique", action="store_true")
    a = ap.parse_args()
    if a.check:
        try: have = jl(os.path.join(OUT, "tree.json"))["meta"]["inputs"]
        except Exception: print("tree page: not built yet. python3 tools/build-tree-page.py"); sys.exit(1)
        if have != inputs_hash(): print("tree page is STALE: the people, families, living list, place map or builder changed since it was built.\n  python3 tools/build-tree-page.py"); sys.exit(1)
        print("tree page is current"); return
    build(a)
    tree = os.path.join(OUT, "tree.json"); pm = os.path.join(OUT, "place_map.json"); ad = os.path.join(OUT, "atlas-data.json"); page = os.path.join(OUT, "roots.html")
    run([sys.executable, os.path.join(TP, "build_atlas_data.py"), "--atlas", atlas_path(), "--tree", tree, "--place-map", pm, "--out", ad])
    t = jl(tree); t["meta"]["inputs"] = inputs_hash()
    io.open(tree, "w", encoding="utf-8").write(json.dumps(t, ensure_ascii=False, separators=(",", ":")))
    write_roots_links(tree)
    tpl = os.path.join(TP, "tree-views.template.html")
    run([sys.executable, os.path.join(TP, "build_page.py"), "--template", tpl, "--tree", tree, "--atlas-data", ad, "--out", page, "--ext", EXT])
    embed = os.path.join(OUT, "roots.embed.html")
    run([sys.executable, os.path.join(TP, "build_page.py"), "--template", tpl, "--tree", tree, "--atlas-data", ad, "--out", embed, "--embed", "--ext", EXT])
    run([sys.executable, os.path.join(TP, "check_tree_page.py"), "--tree", tree, "--atlas-data", ad, "--page", page])
    run([sys.executable, os.path.join(TP, "check_tree_page.py"), "--tree", tree, "--atlas-data", ad, "--page", embed])

if __name__ == "__main__": main()
