#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""«Where we have looked»: the input to the kit's #looked section on a person page (kit PERSON-PAGE-SPEC.md 2a).

    python3 tools/build_looked.py            # rebuild site/src/data/looked.json (needs the Record Atlas checkout, read-only)
    python3 tools/build_looked.py --check    # offline (CI): looked.json was built from the inputs that are committed now

WHAT IT DOES. The search register (site/src/data/searched.json: 274 rows, each tagged) is joined to people by TAG only, never by person: a row belongs
to a person when it names the person's SURNAME FAMILY and one of the person's PLACES. Nothing is guessed:

  SURNAME. A tag is a surname when its folded form (case, accents, spaces, hyphens removed) is a family slug in families.json or the folded surname of at
  least one person in people.json. Which spellings are one name is the Record Atlas catalogue's to say (surname-variants skill): a surname the catalogue
  holds takes the catalogue's family id as its key (Perpić and Prpić are one key, so a row about one reaches the other's people); one it does not hold keeps
  its own folded form as the key. This archive keeps no list of spellings; this file stores only keys, and the headline name to print.
  PLACE. A tag is a place when its folded form is a place name a person's record holds (any comma-separated part of a born/baptised/died/burial/event place,
  a house number removed). Country-level tags (Croatia, Australia, ...) are not used: they would match a whole country. A row also reaches the place of any
  Atlas volume whose FamilySearch waypoint it quotes (9RK1-3Y9): that is an identifier, not a guess.
  NOTHING. A row whose outcome is «nothing» is drawn as «looked, nothing found» only where Record Atlas `surname_variants.py cover` would exit 0 for the
  spellings the ROW ITSELF NAMES (its source line and its «what was searched» line; the narrative of what came back is not read, because it names
  spellings that were seen, not typed). If a spelling the catalogue holds as same / attested / rule is not named there, the row's verdict is «missed» with
  that spelling; if the row names no form of the surname at all, «unknown». Neither is ever drawn as an absence.
  VOLUMES. The volumes the Record Atlas lists for a place come from data/tree-page/atlas-data.json, the same Atlas place data the Roots & Routes «Where to
  look» reads, by place name; titles are the Atlas's full titles when the checkout is present. A place that file has no Atlas id for but the Atlas has under
  its own id (Senj: id `senj`, within a kilometre of this archive's point) is read from the Atlas directly, and says so in `places[].how`.
  HOLDINGS. searched.json `holdings` (the books held per parish, with the year ranges and what was checked) are attached to the parish's place.

WHAT IT LEAVES OUT, AND COUNTS. A row with the tag `internal` (the archive's own data audits, not a source), a row with no surname tag, a row with no place
tag: not shown on any person page. The counts are in `stats` and printed. The text of a row is cut at 240 characters and its markdown removed; a row whose
text names a living person (living.json) is refused.

THE ATLAS IS NEVER WRITTEN TO. site/src/data/looked.json is stamped with the sha256 of every input, so `--check` (run in the build) fails when searched.json,
people.json, atlas-data.json or families.json changes without this tool being run. looked.json is declared hand-kept in regen.py for the same reason
era-snapshot.json and given-names.json are: it embeds Atlas data the GEDCOM-free CI cannot re-derive.
"""
import collections, datetime, hashlib, io, json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(DATA, "looked.json")
TP = os.path.join(ROOT, "data", "tree-page")
ATLAS_CANDIDATES = [os.environ.get("RECORD_ATLAS", ""), os.path.expanduser("~/Projects/Family Projects/Record Atlas"),
                    os.path.join(os.path.dirname(ROOT), "Record Atlas"),
                    "/Volumes/DJ - Crucial - 4TB-SSD/Claude Projects/Family Projects/Record Atlas"]
INPUTS = [os.path.join(DATA, "searched.json"), os.path.join(DATA, "people.json"), os.path.join(DATA, "families.json"),
          os.path.join(DATA, "living.json"), os.path.join(TP, "atlas-data.json"), os.path.join(TP, "place_map.json")]
# A place the archive's holdings call by its parish name and the Atlas lists under the village: Krmpote-Vodice is the Krmpote film (searched.json rows tag it
# `krmpote` and quote the same waypoint as the Atlas's Krmpote-Vodice volume).
PLACE_ALIAS = {"krmpotevodice": "krmpote"}
CAP_TEXT = 240


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def jl(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def place_tokens(s):
    """The parts of a place string a tag can name: each comma part, a trailing house number removed, folded."""
    out = set()
    for seg in str(s or "").split(","):
        seg = re.sub(r"\s+\d+[a-z]?$", "", seg.strip())
        f = fold(seg)
        if f:
            out.add(f)
    return out


def clean(t, cap=CAP_TEXT):
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t or "")
    t = re.sub(r"[*`_]{1,3}", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > cap:
        t = t[:cap].rsplit(" ", 1)[0].rstrip(",;:—-– ") + "…"
    return t


WP = re.compile(r"\b([0-9][A-Z0-9]{3}-[A-Z0-9]{2,4})\b")
WC = re.compile(r"[?&]wc=([0-9A-Z]{4}-[0-9A-Z]{2,4})")
ARK = re.compile(r"ark:/61903/([0-9]:[0-9]:[A-Z0-9\-]+)")
RANGE = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\s*[–—-]\s*(1[5-9]\d\d|20[0-2]\d)\b")
MON = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def vol_id(url):
    m = WC.search(url or "")
    if m:
        return m.group(1)
    m = ARK.search(url or "")
    return m.group(1) if m else None


def ordkey(when):
    m = re.search(r"(\d{1,2})?\D*([A-Za-z]{3})[a-z]*\.?\s*(\d{4})", when or "")
    return int(m.group(3)) * 10000 + MON.get(m.group(2).lower(), 0) * 100 + int(m.group(1) or 0) if m else 0


def atlas_dir():
    for c in ATLAS_CANDIDATES:
        if c and os.path.exists(os.path.join(c, "scripts", "surname_variants.py")):
            return c
    return None


def inputs_stamp():
    return {os.path.relpath(p, ROOT): sha(p) for p in INPUTS}


def check():
    if not os.path.exists(OUT):
        print("looked.json is missing: run python3 tools/build_looked.py")
        return 1
    have = jl(OUT).get("inputs", {})
    want = inputs_stamp()
    bad = [k for k in sorted(set(have) | set(want)) if have.get(k) != want.get(k)]
    for k in bad:
        print(f"  STALE  {k}: looked.json was built from {have.get(k, 'nothing')}, the file is now {want.get(k, 'missing')}")
    if bad:
        print("\nlooked.json was built from different inputs. Run `python3 tools/build_looked.py` (it needs the Record Atlas checkout) and commit the result.")
        return 1
    d = jl(OUT)
    n_nil_bad = [r["id"] for r in d["rows"] if r["outcome"] == "nothing" and not all(v and v[0] in ("covered", "missed", "unknown") for v in r.get("nil", {}).values())]
    if n_nil_bad:
        print("  a nil row without a verdict for every surname: " + ", ".join(map(str, n_nil_bad)))
        return 1
    print(f"ok    looked.json matches its {len(want)} inputs ({len(d['rows'])} rows, {len(d['places'])} places)")
    return 0


def main():
    if "--check" in sys.argv:
        return check()
    atlas = atlas_dir()
    if not atlas:
        sys.exit("Record Atlas checkout not found (set RECORD_ATLAS); it is only read")
    sys.path.insert(0, os.path.join(atlas, "scripts"))
    import surname_variants as SV  # the Atlas's own code: read-only use of terms/cover logic
    cat = SV.load()

    S = jl(os.path.join(DATA, "searched.json"))
    P = jl(os.path.join(DATA, "people.json"))
    F = jl(os.path.join(DATA, "families.json"))
    LV = jl(os.path.join(DATA, "living.json"))
    AD = jl(os.path.join(TP, "atlas-data.json"))
    PM = jl(os.path.join(TP, "place_map.json"))
    APL = {p["id"]: p for p in jl(os.path.join(atlas, "data", "places.json"))["places"]}

    # ------------------------------------------------------------------ surnames
    typed = collections.defaultdict(collections.Counter)
    for p in P:
        if p.get("surname"):
            typed[fold(p["surname"])][p["surname"]] += 1
    fam_label = {f["slug"]: f["label"] for f in F}
    sur_folds = set(typed) | {fold(s) for s in fam_label}
    key_of, label_of = {}, {}

    def catalogue_family(name):
        t = SV.tiers(cat, name)
        return t["family"]["id"] if t["family"] and t["role"] == "member" else None

    for fo in sur_folds:
        names = [n for n, _ in typed[fo].most_common()] if fo in typed else []
        names += [fam_label[s] for s in fam_label if fold(s) == fo]
        fid = next((catalogue_family(n) for n in names if catalogue_family(n)), None)
        key_of[fo] = fid or fo
        if fid:
            label_of.setdefault(fid, next(f["name"] for f in cat["families"] if f["id"] == fid))
        else:
            label_of.setdefault(fo, (fam_label.get(next((s for s in fam_label if fold(s) == fo), ""), None)) or (names[0] if names else fo))

    # ------------------------------------------------------------------ places
    countries = {fold(v.get("country", "")) for v in PM.values() if isinstance(v, dict)} - {""}
    all_tokens = set()
    head_spelling = collections.defaultdict(collections.Counter)
    for p in P:
        strings = [p.get(k) for k in ("bornPlace", "baptisedPlace", "diedPlace", "burial")] + [e.get("place") for e in p.get("events", [])] \
                  + [r.get("marriedPlace") for r in (p.get("rel") or {}).get("spouses", [])]
        for s in strings:
            for seg in str(s or "").split(","):
                seg = re.sub(r"\s+\d+[a-z]?$", "", seg.strip())
                if fold(seg):
                    all_tokens.add(fold(seg))
                    head_spelling[fold(seg)][seg] += 1

    # ------------------------------------------------------------------ Atlas volumes per place key
    adp = collections.defaultdict(list)
    for pl in AD["places"]:
        adp[PLACE_ALIAS.get(fold(pl["n"]), fold(pl["n"]))].append(pl)
    full_title = {}
    for ap in APL.values():
        for c in ap.get("collections", []):
            if c.get("url"):
                full_title[c["url"]] = c.get("title", "")

    def volumes_for(key):
        vols, seen, cat_n, how, atlas_id = [], set(), 0, None, None
        for pl in adp.get(key, []):
            atlas_id = atlas_id or pl.get("id")
            for t, u, f, to, prov in pl["cols"]:
                vid = vol_id(u)
                if vid and vid not in seen:
                    seen.add(vid)
                    vols.append({"id": vid, "t": clean(full_title.get(u) or t, 160), "u": u, "f": f, "to": to})
            cat_n += len(pl.get("cat", []))
        if not vols:
            # the Atlas has the place under its own id although this archive's place map has none: take it only on name and position
            pmv = next((v for k, v in PM.items() if isinstance(v, dict) and fold(k) == key), None)
            ap = APL.get(key)
            if pmv and ap and pmv.get("lat") is not None and ap.get("lat") is not None and abs(ap["lat"] - pmv["lat"]) < 0.02 and abs(ap["lon"] - pmv["lon"]) < 0.02:
                for c in ap.get("collections", []):
                    if c.get("url") and vol_id(c["url"]) not in seen:
                        seen.add(vol_id(c["url"]))
                        vols.append({"id": vol_id(c["url"]), "t": clean(c.get("title", ""), 160), "u": c["url"], "f": c.get("from"), "to": c.get("to")})
                    elif not c.get("url"):
                        cat_n += 1
                if vols:
                    how = f"the Atlas place {ap['id']} ({ap['name']}), found by name and position: this archive's place map has no Atlas id for it"
                    atlas_id = ap["id"]
        vols.sort(key=lambda v: (v["f"] if v["f"] is not None else 9999, v["to"] if v["to"] is not None else 9999, v["t"]))
        return vols, cat_n, how, atlas_id

    # ------------------------------------------------------------------ the rows
    stats = collections.Counter()
    living_names = [fold(x["name"]) for x in LV if x.get("name")]
    rows, used_places = [], set()
    hold_keys = {PLACE_ALIAS.get(fold(h["parish"]), fold(h["parish"])) for h in S["holdings"]}
    wp_place = {}
    place_keys_with_vols = {}
    # volumes of every place a tag may name
    tag_folds = {fold(t) for r in S["rows"] for t in r["tags"]}
    place_candidates = {t for t in tag_folds if t in all_tokens and key_of.get(t) is None and t not in countries}
    for k in sorted(place_candidates | set(adp)):
        vols, cat_n, how, aid = volumes_for(k)
        place_keys_with_vols[k] = (vols, cat_n, how, aid)
        for v in vols:
            wp_place.setdefault(v["id"], k)

    def tried_text(r):
        return " ".join([clean(r["src"], 4000), clean(r["what"], 4000)])

    def toks(text):
        w = re.findall(r"[^\W\d_][\w'’\-]*", text)
        return set(w) | {a + b for a, b in zip(w, w[1:])} | {a + " " + b for a, b in zip(w, w[1:])}

    def verdict(r, key):
        label = label_of[key]
        t = SV.tiers(cat, label)
        if t["family"] and t["role"] == "member":
            need = [m["form"] for s in ("same", "attested", "rule") for m in t["tiers"][s]]
        else:
            need = [label]
        have = {SV.fold_key(x) for x in toks(tried_text(r))}
        miss = [f for f in need if SV.fold_key(f) not in have]
        if len(miss) == len(need):
            return ["unknown"]
        return ["covered"] if not miss else ["missed"] + miss

    for i, r in enumerate(S["rows"]):
        tags = [fold(t) for t in r["tags"]]
        if "internal" in r["tags"]:
            stats["internal (the archive's own data audits, not a source)"] += 1
            continue
        keys = sorted({key_of[t] for t in tags if t in sur_folds})
        text = " ".join([r["src"], r["what"]])
        quoted = " ".join(str(r.get(k, "")) for k in ("src", "what", "url", "waypoint", "key"))
        vols_hit = sorted({m for m in WP.findall(quoted) if m in wp_place} | ({vol_id(r.get("url"))} & set(wp_place)))
        places = sorted({t for t in tags if t in place_candidates} | {wp_place[v] for v in vols_hit})
        places_with_books = [k for k in places if k in hold_keys or place_keys_with_vols.get(k, ([],))[0]]
        if not keys and r["outcome"] in ("pending", "blocked") and places_with_books and not any(t.startswith("ahn") for t in tags):
            # wanted at a place, not a search for a name: shown to anyone at the place, in the «not looked yet» box (kit placeOnly)
            quoted_href = r.get("url") or ""
            head, _, tail = r["src"].partition(" \u2014 ")
            rows.append({"id": i, "placeOnly": True, "src": clean(head if tail else r["src"], 120), "volume": clean(tail, 200) if tail else "", "years": "", "span": None,
                         "what": "", "when": r["when"], "ord": ordkey(r["when"]), "outcome": r["outcome"], "surnames": [], "places": places_with_books, "href": quoted_href, "volumes": []})
            used_places.update(places_with_books)
            stats["wanted at a place (pending or blocked, no surname): shown to anyone at the place"] += 1
            continue
        if not keys:
            stats["no surname tag"] += 1
            continue
        if not places:
            stats["a surname but no place the people records name"] += 1
            continue
        if any(n and n in fold(text) for n in living_names):
            stats["refused: the text names a living person"] += 1
            continue
        yrs = [int(x) for a in RANGE.findall(r["src"]) for x in a]
        head, _, tail = r["src"].partition(" — ")
        row = {"id": i, "src": clean(head if tail else r["src"], 120), "volume": clean(tail, 200) if tail else "",
               "years": f"{min(yrs)}–{max(yrs)}" if yrs else "", "span": [min(yrs), max(yrs)] if yrs else None,
               "what": clean(r["what"]), "when": r["when"], "ord": ordkey(r["when"]), "outcome": r["outcome"],
               "surnames": keys, "places": places, "href": r.get("url") or "", "volumes": vols_hit}
        if r["outcome"] == "nothing":
            row["nil"] = {k: verdict(r, k) for k in keys}
        rows.append(row)
        used_places.update(places)
        stats["shown on person pages (by tag)"] += 1
    rows.sort(key=lambda x: (-x["ord"], x["id"]))

    # ------------------------------------------------------------------ places and holdings
    hold = {}
    for h in S["holdings"]:
        k = PLACE_ALIAS.get(fold(h["parish"]), fold(h["parish"]))
        hold[k] = {"parish": h["parish"], "books": h["books"], "checked": clean(h.get("checked", ""), 200), "bad": bool(h.get("bad"))}
    places = {}
    for k in sorted(used_places | set(hold)):
        vols, cat_n, how, aid = place_keys_with_vols.get(k) or volumes_for(k)
        spellings = [pl["n"] for pl in adp.get(k, []) if pl.get("id")] + [n for n, _ in head_spelling[k].most_common()]
        name = next((n for n in spellings if re.sub(r"[ -~]", "", n)), None) or (spellings[0] if spellings else k)   # the spelling with its accents
        if k in hold and not adp.get(k):
            name = hold[k]["parish"]
        places[k] = {"name": name, "atlas": aid, "volumes": vols, "catalogued": cat_n}
        if how:
            places[k]["how"] = how
        if k in hold:
            places[k]["held"] = hold[k]
    needed = {k for r in rows for k in r["surnames"]}
    surname_key = {fo: key_of[fo] for fo in sorted(key_of) if key_of[fo] in needed}
    out = {"_note": "Built by tools/build_looked.py from the search register, the people records, the Roots & Routes Atlas place data and the Record Atlas surname catalogue; "
                    "do not edit by hand. Read by site/src/lib/looked.js for the kit's #looked section.",
           "built": datetime.date.today().isoformat(), "catalogueBuilt": cat.get("built"), "inputs": inputs_stamp(),
           "surnameKey": surname_key, "labels": {k: label_of[k] for k in sorted(needed)},
           "placeAlias": PLACE_ALIAS, "rows": rows, "places": places, "stats": dict(stats),
           "totals": {"register": len(S["rows"]), "shown": len(rows)}}
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0, sort_keys=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(rows)} of {len(S['rows'])} register rows can reach a person page; {len(places)} places, {len(needed)} surname keys")
    for k, v in stats.items():
        print(f"  {v:4}  {k}")
    nil = collections.Counter(v[0] for r in rows for v in r.get("nil", {}).values())
    print("  nil verdicts (per row and surname):", dict(nil))
    return 0


if __name__ == "__main__":
    sys.exit(main())
