#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roots & Routes: the tree viewer for this archive, built from this archive's own committed data.

    RETIRED AS A PAGE (23 November 2026, David: "roots and routes, remove it"; the Tree Canvas on recordatlas.org replaced it estate-wide).
    /roots/ is now a redirect to /trees/. What is still built, and why: roots.html is served bare at /roots/view.html for the frames on a
    person's page (kit PersonRootsViews), and roots-links.json says which people have one. The fragment for the page (roots.embed.html) is gone.

    python3 tools/build-tree-page.py            # rebuild data/tree-page/ (tree.json, atlas-data.json, roots.html) and site/public/roots-links.json
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
INPUTS = ["people.json", "families.json", "living.json", "corrections.json"]
FULLDATE = re.compile(r"^\d{1,2} (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) \d{4}$")   # "20 APR 1779", "9 JUN 1628": this archive's own stored shape (GEDCOM, upper-case month); a day is present, no ABT / BEF / AFT / TO / FROM / BET / EST word, no long month, no note

def jl(path): return json.load(io.open(path, encoding="utf-8"))
def run(args):
    print("$", " ".join(os.path.relpath(a, ROOT) if os.path.isabs(a) and a.startswith(ROOT) else a for a in args)); r = subprocess.run(args)
    if r.returncode: sys.exit(r.returncode)
def inputs_hash():
    h = hashlib.sha1()
    for n in INPUTS: h.update(io.open(os.path.join(DATA, n), "rb").read())
    for n in ("tree-views.template.html", "painted-lines.ext.html", "gedcom_to_tree.py"): h.update(io.open(os.path.join(TP, n), "rb").read())
    h.update(io.open(os.path.abspath(__file__), "rb").read())
    h.update(io.open(CARDS_TSV, "rb").read())   # the people decided by hand (data/tree-cards.tsv)
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
def husband_wife(p, other_id):
    """The husband and wife slots of a family, the same whichever of the two is being read. A recorded M is the husband, a recorded F the wife; a couple where
    the record holds no sex for either (or neither is decisive) is ordered by id, so it is ONE family, not two. The slot says nothing about anybody's sex."""
    a, b = p["id"], other_id
    sa, sb = p.get("sex"), (people_by_id.get(other_id) or [{}])[0].get("sex")
    if sa == "M" and sb != "M": return a, b
    if sb == "M" and sa != "M": return b, a
    if sa == "F" and sb != "F": return b, a
    if sb == "F" and sa != "F": return a, b
    return (a, b) if a <= b else (b, a)

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
        unk = [r["id"] for r in par if sex.get(r["id"]) not in ("M", "F")]   # a parent whose sex the record does not hold fills the slot that is empty, in the order the tree lists them; the slot says nothing about sex
        if not f and unk: f = unk.pop(0)
        if not m and unk: m = unk.pop(0)
        if f or m: fam_of_child[p["id"]] = fam(f, m)
        for s in (p.get("rel") or {}).get("spouses", []):
            if s.get("id") in ids:
                a, b = husband_wife(p, s["id"])
                k = fam(a, b)
                if k not in fam_of_spouse[p["id"]]: fam_of_spouse[p["id"]].append(k)
    for p in people:
        out += ["0 %s INDI" % p["id"], "1 NAME %s /%s/" % (p.get("given") or "", p.get("surname") or ""), "1 SEX %s" % (p.get("sex") if p.get("sex") in ("M", "F") else "U")]   # never inferred from a name: no recorded sex is U
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
    src_by = {p["id"].strip("@"): p for p in people}
    fix_n = collections.Counter(c["id"] for c in jl(os.path.join(DATA, "corrections.json")))
    for p in t["people"]:
        p["line"] = key_i.get(fam_of.get(p["id"]), 7)
        # FULL DATES (bd, dd), for DEAD people only: `people` above holds no living person (living.json is a different list) and the converter's 110-year floor drops
        # anyone with no death recorded and a birth in the last 110 years. The string is people.json's own `born` / `died`, byte for byte, as people.json holds it
        # ("20 APR 1779", "9 JUN 1628"; the page shows them as "20 Apr 1779"); a year alone, a month and year, or an approximate date ("ABT 1875", "BEF 12 MAR 1900") is NOT a full date and gets no field.
        src = src_by.get(p["id"]) or {}
        # CORRECTIONS COUNT (cx): how many rows of site/src/data/corrections.json name this person (its `id`, the tree id). It is the SAME filter the person page
        # uses for "N corrections and notes have been recorded against this page" (corrections.filter(c => c.id === p.id)), so the two always agree: every kind
        # counts, as it does there. A count only, never what a row says; omitted when 0; only for people drawn here, who are all in people.json, which holds no living person.
        n = fix_n.get("@%s@" % p["id"].strip("@"), 0)
        if n: p["cx"] = n
        if FULLDATE.match(str(src.get("born") or "")): p["bd"] = src["born"]
        if FULLDATE.match(str(src.get("died") or "")): p["dd"] = src["died"]
        p["page"] = "/people/%s/" % slugs[p["id"]] if p["id"] in slugs else None
        if p["page"] is None: p.pop("page")
    t["lines"] = [{"sur": f["label"], "host": HOST} for f in top] + [{"sur": "Other", "host": HOST}]
    t["meta"].update({"rowLabel": "Family line", "lineLabel": "Family line"})
    mark_relative_places(t, people)
    drop_conflicts(t, tree)
    keep_death_place(t, people)
    add_routes(t, people)
    t["undrawn"] = undrawn_cards(t, people, key_i, tree)
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

CARDS_TSV = os.path.join(ROOT, "data", "tree-cards.tsv")
FLOOR_FROM = datetime.date.today().year - 110   # the converter's floor: no death recorded and born this year minus 110 or later

def circa(v):
    """A date the register gives as an estimate, a bound or a range (ABT, EST, CAL, BEF, AFT, BET, TO, FROM): the year on a card is then approximate (`bye` / `dye`)."""
    return bool(re.match(r"^(ABT|EST|CAL|BEF|AFT|BET|TO|FROM)\b", str(v or "").strip().upper()))

def read_cards():
    """data/tree-cards.tsv: id|kind|why. The people David decided to draw although the rules above do not (standin, slip). A bad row stops the build."""
    rows = {}
    for n, line in enumerate(io.open(CARDS_TSV, encoding="utf-8"), 1):
        if not line.strip() or line.startswith("#"): continue
        c = [x.strip() for x in line.rstrip("\n").split("|")]
        if len(c) < 3 or c[1] not in ("standin", "slip") or not c[0] or not c[2]: sys.exit("data/tree-cards.tsv line %d: need id|kind|why, kind standin or slip" % n)
        if c[0] in rows: sys.exit("data/tree-cards.tsv line %d: %s is listed twice" % (n, c[0]))
        rows[c[0]] = c[1]
    return rows

def undrawn_cards(t, people, key_i, tree):
    """EVERYONE THE REGISTER PUBLISHES IS IN tree.json (David, 17 November 2026): the people the ten views skip go into `undrawn`, which the views ignore and the Record Atlas Tree Canvas
    draws as an unplaced card. Every person of people.json (none is living) who is not drawn on the maps gets one, in three kinds:
      - NO DEATH recorded and born this year minus 110 or later (born 1916 to 1945 here): NAME AND FAMILY LINKS ONLY (no year, place, page link or count); not marked living,
        because nothing says they are;
      - a CONFLICT (died before born, or over 110 years: not one life): the DEATH only; the birth that cannot both be true is dropped; page, links and count as for the next kind;
      - everyone else: their details (the year the register holds, parent/spouse/child links, page, correction count).
    A `standin` in data/tree-cards.tsv is also flagged `placeholder: true`, whether drawn on the maps or a card. THE LIVING (site/src/data/living.json, the people the archive already
    names on its noindex pages) are cards too, `living: true`, NAME AND FAMILY LINKS ONLY (no year, place, page link or count), because /roots/ and /roots/view.html are noindex
    (David, 17 November 2026: everyone in the archive is on the canvas, always). NEVER here: the sorting buckets (tools/buckets.py, 42 records, the check_site gate "no sorting buckets
    published") and anybody the register does not name (the possible minors are published nowhere). Names are drawn as published, never hidden or corrected. Links go only to people
    in tree.json (drawn, a card or a living card) and follow people.json's and living.json's own."""
    by = {p["id"].strip("@"): p for p in people}
    conf = {c["id"].strip("@"): c for c in (jl(os.path.splitext(tree)[0] + ".report.json").get("conflicts") or [])}
    drawn = {p["id"] for p in t["people"]}
    listed = read_cards()
    for i in listed:
        if i not in by: sys.exit("data/tree-cards.tsv: %s is not in people.json" % i)
    def yr(v):
        m = re.search(r"(1\d\d\d|20\d\d)", str(v or "")); return int(m.group(1)) if m else None
    def no_death(s): return not (s.get("died") or s.get("burial") or s.get("dyear") or s.get("deathRecorded"))
    cand = {}
    for i, s in by.items():
        if i in drawn: continue
        b = yr(s.get("born")) or s.get("byear")
        if i in conf: cand[i] = "conflict"
        elif no_death(s) and b is not None and b >= FLOOR_FROM: cand[i] = "name"
        else: cand[i] = "details"
    for p in t["people"]:
        if listed.get(p["id"]) == "standin": p["placeholder"] = True
    fix_n = collections.Counter(c["id"] for c in jl(os.path.join(DATA, "corrections.json")))
    living = jl(os.path.join(DATA, "living.json"))
    lids = {x["slug"] for x in living}
    clash = lids & (drawn | set(cand))
    if clash: sys.exit("living.json: a living slug is also a tree id: %s" % sorted(clash)[:3])
    ids = drawn | set(cand) | lids
    def ref(e):
        """The id of a relative in tree.json: a living relative is their slug, a dead one their tree id."""
        if e.get("living") and e.get("slug") in lids: return e["slug"]
        if e.get("id") and e["id"].strip("@") in ids: return e["id"].strip("@")
        return None
    out = []; kinds = collections.Counter()
    for i in sorted(cand):
        s = by[i]; rel = s.get("rel") or {}
        link = lambda lst: [r for r in (ref(x) for x in (lst or [])) if r and r != i]
        f = m = None; free = []
        for x in link(rel.get("parents")):
            sx = (by[x].get("sex") if x in by else None)
            if sx == "M" and not f: f = x
            elif sx == "F" and not m: m = x
            else: free.append(x)
        for x in free:
            if not f: f = x
            elif not m: m = x
        c = {"id": i, "sex": {"M": "m", "F": "f"}.get(s.get("sex"), "u"), "given": s.get("given") or "", "sur": s.get("surname") or "",
             "line": key_i.get(s.get("family"), 7), "father": f, "mother": m, "spouse": sorted(set(link(rel.get("spouses")))), "kids": sorted(set(link(rel.get("children"))))}
        c["unplaced"] = True
        if cand[i] in ("details", "conflict"):
            b, d = yr(s.get("born")) or s.get("byear"), yr(s.get("died")) or s.get("dyear")
            if cand[i] == "conflict":
                # the recorded birth and death cannot both be true (died before born, or over 110 years): the card shows the DEATH only (David, 17 November 2026)
                b = None; d = d if d is not None else yr(conf[i].get("died"))
            if b is not None:
                c["by"] = b
                if circa(s.get("born")): c["bye"] = True
            if d is not None:
                c["dy"] = d
                if circa(s.get("died")): c["dye"] = True
            c["slug"] = s["slug"]; c["page"] = "/people/%s/" % s["slug"]
            if fix_n.get("@%s@" % i): c["cx"] = fix_n["@%s@" % i]
        if listed.get(i) == "standin": c["placeholder"] = True
        kinds[cand[i]] += 1
        out.append(c)
    # THE LIVING: name and family links only. The name is living.json's own; given and surname are split on the last word (a particle stays with the surname); a family colour only
    # where the surname is one of the archive's own families. No sex (living.json has none, and it stays out of public data), no year, no place, no page link, no count.
    fams = jl(os.path.join(DATA, "families.json"))
    fam_slug = {fold(f["label"]): f["slug"] for f in fams}
    PART = {"de", "del", "della", "van", "von", "da", "di", "le", "la", "du", "ten", "ter", "der", "den"}
    for x in sorted(living, key=lambda r: r["slug"]):
        s = x["slug"]; w = x["name"].split()
        k = len(w) - 1
        while k > 1 and w[k - 1].lower() in PART: k -= 1
        given, sur = (" ".join(w[:k]), " ".join(w[k:])) if len(w) > 1 else (x["name"], "")
        rel = x.get("rel") or {}
        link = lambda lst: [r for r in (ref(e) for e in (lst or [])) if r and r != s]
        f = m = None
        for r in link(rel.get("parents")):
            if r in by and by[r].get("sex") == "F" and not m: m = r
            elif r in by and by[r].get("sex") == "M" and not f: f = r
            elif not f: f = r
            elif not m: m = r
        out.append({"id": s, "sex": "u", "given": given, "sur": sur, "line": key_i.get(fam_slug.get(fold(sur.split()[-1] if sur else "")), 7),
                    "father": f, "mother": m, "spouse": sorted(set(link(rel.get("spouses")))), "kids": sorted(set(link(rel.get("children")))), "living": True, "unplaced": True})
        kinds["living"] += 1
    rep_path = os.path.splitext(tree)[0] + ".report.json"; rep = jl(rep_path)
    rep["undrawn"] = {"cards": len(out), "name_and_family_only": kinds["name"], "with_details": kinds["details"], "conflict_death_only": kinds["conflict"], "living_name_and_family_only": kinds["living"], "listed_in_tree_cards_tsv": len(listed),
                      "placeholder_flagged": sum(1 for v in listed.values() if v == "standin"), "in_tree_json_total": len(t["people"]) + len(out)}
    io.open(rep_path, "w", encoding="utf-8").write(json.dumps(rep, indent=1, ensure_ascii=False))
    print("undrawn: %d cards (%d name and family only, %d with details, %d conflicts shown by their death only, %d living: name and family only); %d people flagged as stand-ins" % (len(out), kinds["name"], kinds["details"], kinds["conflict"], kinds["living"], rep["undrawn"]["placeholder_flagged"]))
    return out

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
    run([sys.executable, os.path.join(TP, "check_tree_page.py"), "--tree", tree, "--atlas-data", ad, "--page", page])

if __name__ == "__main__": main()
