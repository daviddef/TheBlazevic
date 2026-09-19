#!/usr/bin/env python3
"""Cemetery memorials, matched against this archive's people.

TWO KINDS OF EVIDENCE, AND THEY ARE NEVER MIXED.

  sources/findagrave/*.psv  — an INDEX. Somebody else's transcription of a
      memorial, where a date may be the cemetery's record rather than the stone
      and a plot number is Find a Grave's reading of a register of burials.

  sources/graves/*.psv      — a STONE. Read off a photograph of the memorial
      itself, at full resolution, by this archive. Better evidence, and for the
      Croatian cemeteries it is the only evidence there is: Find a Grave has
      never covered them.

They are counted, matched and published apart. The top-level keys of
graves.json mean the INDEX and nothing else — pages already assert things like
«not one of them is in Croatia» against them, and that stays true. The
photographed surveys live under «stones».

What each is good for differs, and the shape follows.

  An index gives a PLOT, so the index half groups by plot: «CC, Lot 26, 1»
  holds John Zubrinich and two children who died at eight and at six months.
  That is a household, read off a lot number.

  A photograph gives a STONE, so the stone half groups by stone: a row whose
  description begins «same ...» belongs to the row above it. That is how both
  survey files are written, and where the convention is not followed the group
  splits rather than wrongly merging — conservative in the safe direction.

CONFIDENCE IS LOAD-BEARING. A stone row carries r / p / ?: read at full
resolution, read at contact-sheet scale with the digits unverified, or not to
be relied on. Only «r» rows may raise a date disagreement against the tree,
because a «p» digit is not evidence and has already been wrong four times.

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
SRCDIR = os.path.join(ROOT, "sources", "findagrave")
STONEDIR = os.path.join(ROOT, "sources", "graves")
DATA = os.path.join(ROOT, "site", "src", "data")

MONTH = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

# Every harvest file in sources/findagrave/ is read, not just the first one.
# A file may declare, in its header comments:
#     # surname: Zubrinich          what to call it
#     # match: zubrini              the stem to match this archive's people on
#     # stop: zubrinich, zubrinic   surname forms to drop from a given-name match
# and anything it does not declare is taken from the filename stem.


def flat(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(name, stop):
    return {t for t in re.findall(r"[a-z]+", flat(name)) if t not in stop and len(t) > 1}


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


def read_file(path):
    """One harvest file -> (meta, rows)."""
    meta, rows = {}, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            m = re.match(r"#\s*(surname|match|stop)\s*:\s*(.+)$", line, re.I)
            if m:
                meta[m.group(1).lower()] = m.group(2).strip()
            continue
        if not line.strip():
            continue
        name, b, d, cem, place, plot = (line.split("|") + [""] * 6)[:6]
        rows.append({"name": name, "born": b, "died": d, "cemetery": cem,
                     "place": place, "plot": plot})
    stem = re.split(r"[-_0-9]", os.path.basename(path))[0]
    meta.setdefault("surname", stem.title())
    meta.setdefault("match", flat(stem)[:7])
    stop = {flat(x) for x in meta.get("stop", meta["surname"]).split(",") if x.strip()}
    stop |= {flat(meta["surname"])}
    for r in rows:
        r["surname"] = meta["surname"]
    return meta, stop, rows


CONF = {"r": "read at full resolution",
        "p": "read at contact-sheet scale — digits unverified",
        "?": "uncertain, not to be relied on"}


def read_stone_file(path):
    """One photographed survey -> (meta, rows). Format:

        surname|given|born|died|stone|conf|photo

    The file may declare «# cemetery:» and «# photographed:» in its header;
    anything it does not declare is taken from the filename stem.
    """
    meta, rows = {}, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            m = re.match(r"#\s*(cemetery|photographed)\s*:\s*(.+)$", line, re.I)
            if m:
                meta[m.group(1).lower()] = m.group(2).strip()
            continue
        if line.count("|") != 6:
            continue
        surname, given, b, d, stone, conf, photo = line.split("|")
        rows.append({"surname": surname.strip(), "given": given.strip(),
                     "born": b.strip(), "died": d.strip(), "stone": stone.strip(),
                     "conf": conf.strip() or "?",
                     "photos": [x.strip() for x in photo.split(",") if x.strip()]})
    stem = os.path.basename(path)[:-4]
    meta.setdefault("cemetery", stem.split("-")[0].title())
    meta.setdefault("photographed", "")
    for r in rows:
        r["cemetery"] = meta["cemetery"]
        r["confNote"] = CONF.get(r["conf"], CONF["?"])
    return meta, rows


def given_index():
    """Canonical given names and their sex, from the archive's own vocabulary.

    givennames.json already knows that Joannes, Ivan, Ivica and John are one
    name and that Franjo is not Franciska. Reusing it is the difference between
    matching Stjepan to Stephannes and matching Franjo to Francisca.
    """
    try:
        gn = json.load(open(os.path.join(DATA, "givennames.json"), encoding="utf-8"))
    except OSError:
        return {}, {}
    canon, sex = {}, {}
    for key, variants in (gn.get("groups") or {}).items():
        k = flat(key)
        canon[k] = k
        for v in variants:
            canon[flat(v)] = k
    for key, s in (gn.get("sex") or {}).items():
        sex[flat(key)] = flat(s)[:1]
    return canon, sex


def canon_names(text, canon):
    out = set()
    for t in re.findall(r"[a-z]+", flat(text)):
        if len(t) < 3:
            continue
        out.add(canon.get(t, t))
    return out


def edit1(a, b):
    """True if a and b differ by at most one letter. Both must be ≥5 long.

    This is the spelling slack the vocabulary does not cover — Fabijana and
    Fabiana are one name and no list will ever hold every pair. It is
    deliberately tight: Franjo/Francisca and Slave/Miroslava are four and six
    edits apart and stay apart.
    """
    if abs(len(a) - len(b)) > 1 or min(len(a), len(b)) < 5:
        return False
    if a == b:
        return True
    if len(a) > len(b):
        a, b = b, a
    i = j = diff = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        diff += 1
        if diff > 1:
            return False
        if len(a) == len(b):
            i += 1
        j += 1
    return True


def match_stone(r, people, canon, sex):
    """Best published person for one stone row, or (None, 0).

    Conservative on purpose, and in this order:

      surname — the person's own, OR a spouse's, because a Croatian stone gives
                a married woman under her husband's name: «MILKA BLAŽEVIĆ rod.
                PAPIĆ» is the tree's Milka Papić.
      given   — canonical forms must intersect, and the sexes must not conflict.
      years   — at least one within two.

    A gravestone is a memorial. This is a report, not a merge.
    """
    sur = flat(r["surname"])
    gset = canon_names(r["given"], canon)
    by, dy = year(r["born"]), year(r["died"])
    if not sur or not gset:
        return None, 0
    gsex = {sex[g] for g in gset if g in sex}
    best, bestscore, married = None, 0, False
    for p in people:
        own = flat(p.get("surname")) or flat(p.get("name")).split()[-1:][0] if p.get("name") else ""
        hit_own = own and (sur[:6] in own or own[:6] in sur)
        hit_wed = False
        if not hit_own:
            for sp in (p.get("rel") or {}).get("spouses") or []:
                spn = flat(sp.get("name"))
                if sur[:6] and sur[:6] in spn:
                    hit_wed = True
                    break
        if not (hit_own or hit_wed):
            continue
        pset = canon_names(p.get("given") or p.get("name"), canon)
        if not (gset & pset) and not any(edit1(a, b) for a in gset for b in pset):
            continue
        psex = flat(p.get("sex"))[:1]
        if psex and gsex and psex not in gsex:
            continue
        pb, pd = p.get("byear"), p.get("dyear")
        near_b = by and pb and abs(pb - by) <= 2
        near_d = dy and pd and abs(pd - dy) <= 2
        # When all four years are known they must ALL agree. Without this a
        # child who died at one matches a woman who died at sixty-two on the
        # strength of a shared birth year.
        if by and dy and pb and pd:
            if abs(pb - by) > 3 or abs(pd - dy) > 3:
                continue
        elif not (near_b or near_d):
            continue
        score = (2 if by and pb == by else 1 if near_b else 0) \
            + (2 if dy and pd == dy else 1 if near_d else 0) \
            + (1 if hit_own else 0)
        if score > bestscore:
            best, bestscore, married = p, score, hit_wed
    if bestscore < 2:
        return None, 0
    best = dict(best)
    best["_married"] = married
    return best, bestscore


def stone_half(people):
    """Every photographed survey, matched and grouped by stone."""
    if not os.path.isdir(STONEDIR):
        return None
    files = sorted(f for f in os.listdir(STONEDIR) if f.endswith(".psv"))
    if not files:
        return None

    rows, surveys, conflicts, groups = [], [], [], []
    for f in files:
        meta, rs = read_stone_file(os.path.join(STONEDIR, f))
        # group by stone: «same ...» attaches to the row above
        gid = None
        for r in rs:
            if not r["stone"].lower().startswith("same"):
                gid = len(groups)
                groups.append({"cemetery": r["cemetery"], "stone": r["stone"],
                               "photos": list(r["photos"]), "people": []})
            if gid is None:                      # a file opening with «same»
                gid = len(groups)
                groups.append({"cemetery": r["cemetery"], "stone": r["stone"],
                               "photos": list(r["photos"]), "people": []})
            r["group"] = gid
            groups[gid]["people"].append(r)
        surveys.append({"file": f, "cemetery": meta["cemetery"],
                        "photographed": meta["photographed"], "n": len(rs)})
        rows += rs

    canon, sex = given_index()

    # Match everything first, then look at who got claimed twice.
    #
    # Two Senj stones read KATA ŠPALJ — 1884–1975 and 1886–1981 — and the tree
    # holds exactly ONE Kate Špalj, born 1886, with no death recorded. Both
    # stones matched her, because a match needs a year within two and there was
    # no death year to disagree with. One of those women is not in this tree,
    # and publishing her under somebody else's name would be the Ivan
    # Defrančeski mistake run backwards: not a person missed, a person invented.
    #
    # So the better score keeps the match, the rest are unmatched again, and the
    # contest is published either way. A tie drops all of them: if the archive
    # cannot tell which stone is hers, it does not get to choose.
    claims = {}
    for r in rows:
        best, score = match_stone(r, people, canon, sex)
        if best:
            claims.setdefault(best.get("id") or best.get("name"), []).append((score, r, best))

    contested = []
    for key, cl in claims.items():
        if len(cl) < 2:
            continue
        top = max(c[0] for c in cl)
        winners = [c for c in cl if c[0] == top]
        keep = winners[0] if len(winners) == 1 else None
        contested.append({
            "person": cl[0][2]["name"], "slug": cl[0][2].get("slug"),
            "kept": None if keep is None else
                    f"{keep[1]['given']} {keep[1]['surname']} "
                    f"{keep[1]['born'] or '?'}–{keep[1]['died'] or '?'}",
            "stones": [f"{c[1]['given']} {c[1]['surname']} "
                       f"{c[1]['born'] or '?'}–{c[1]['died'] or '?'} "
                       f"({c[1]['cemetery']})" for c in cl],
        })
        for c in cl:
            if c is not keep:
                c[1]["_dropped"] = True

    for score, r, best in [(c[0], c[1], c[2]) for cl in claims.values() for c in cl]:
        if r.get("_dropped"):
            continue
        r["slug"], r["archiveName"] = best["slug"], best["name"]
        r["archiveBorn"], r["archiveDied"] = best.get("born", ""), best.get("died", "")
        if best.get("_found"):
            # She stands BESIDE the tree, not in it. found.psv exists to keep
            # that distinction and the page must not quietly lose it here.
            r["foundNotInTree"] = True
            r["foundVia"] = best.get("_via", "")
        if best.get("_married"):
            r["viaMarriedName"] = True
        # only a full-resolution reading may contradict the tree
        if r["conf"] != "r":
            continue
        for field, tree in (("born", best.get("born")), ("died", best.get("died"))):
            sy, ty = year(r[field]), year(tree)
            if sy and ty and sy != ty:
                conflicts.append({"name": f"{r['given']} {r['surname']}".strip(),
                                  "slug": best["slug"], "field": field,
                                  "stone": r[field], "tree": tree, "years": sy - ty,
                                  "cemetery": r["cemetery"],
                                  "photo": (r["photos"] or [""])[0]})

    for g in groups:
        g["known"] = sum(1 for x in g["people"] if x.get("slug"))
        g["unknown"] = len(g["people"]) - g["known"]

    where, surnames, conf = {}, {}, {}
    for r in rows:
        where[r["cemetery"]] = where.get(r["cemetery"], 0) + 1
        surnames[r["surname"]] = surnames.get(r["surname"], 0) + 1
        conf[r["conf"]] = conf.get(r["conf"], 0) + 1

    return {
        "what": ("Read off photographs of the stones themselves, at full "
                 "resolution, by this archive. Find a Grave has never covered "
                 "these cemeteries."),
        "surveys": surveys,
        "n": len(rows),
        "matched": sum(1 for r in rows if r.get("archiveName")),
        "unmatched": sum(1 for r in rows if not r.get("archiveName")),
        "contested": contested,
        "confidence": [[k, conf.get(k, 0), CONF[k]] for k in ("r", "p", "?")],
        "cemeteries": sorted(where.items(), key=lambda kv: (-kv[1], kv[0])),
        "surnames": sorted(surnames.items(), key=lambda kv: (-kv[1], kv[0])),
        "stones": sorted([g for g in groups if len(g["people"]) > 1],
                         key=lambda g: (-g["known"], -len(g["people"]))),
        "conflicts": sorted(conflicts, key=lambda c: (c["cemetery"], c["name"])),
        "rows": rows,
    }


def tree_people():
    """Everyone a stone could be, and it is not the register file.

    This read people.json and nothing else, and people.json is not the tree.
    It is not even everyone with a page: 52 DIRECT ANCESTORS are in
    ancestors.json and not in it, so their graves could not match by
    construction. And beyond both sits every person who exists only as a name
    on somebody else's record — a parent, a spouse, a sibling, a child — with
    no page and no slug.

    That is the same blindness, for the fifth time in this archive and the
    second time on this very evidence. «IVAN DEFRANĆESKI 1925–1995» was
    photographed at Senj and filed as a surname that does not occur once in
    this tree. He is Hedviga Blažević's husband, carried on her own marriage,
    unpublished. Searching the published people is not searching the tree.

    Relations are returned in the same shape as a published person, so the
    matcher does not need to know which kind it is holding. They have no slug,
    which is how the page tells them apart.
    """
    pool, seen = [], set()
    for f in ("people.json", "ancestors.json"):
        for p in json.load(open(os.path.join(DATA, f), encoding="utf-8")):
            if p.get("id") in seen:
                continue
            seen.add(p.get("id"))
            pool.append(p)

    published = set(seen)
    for p in list(pool):
        for kind, lst in (p.get("rel") or {}).items():
            for x in (lst or []):
                if not x.get("name") or x.get("id") in seen:
                    continue
                seen.add(x.get("id"))
                # A relation gives a name and, sometimes, two integer years.
                # Split the name into given and surname the only way available:
                # last token is the surname. That is wrong for «de Franceschi»
                # and right for everything else, and the matcher compares on a
                # six-character prefix either way.
                parts = (x["name"] or "").split()
                pool.append({
                    "id": x.get("id"), "name": x["name"],
                    "given": " ".join(parts[:-1]) or x["name"],
                    "surname": parts[-1] if len(parts) > 1 else "",
                    "byear": x.get("born") if isinstance(x.get("born"), int) else None,
                    "dyear": x.get("died") if isinstance(x.get("died"), int) else None,
                    "sex": "", "slug": None, "rel": {},
                    "_via": f"{kind} of {p.get('name')}",
                })

    # AND THE PEOPLE THIS ARCHIVE READ OUT OF A REGISTER ITSELF.
    #
    # sources/found.psv exists for exactly one reason: a person who is in a
    # register and NOT in the tree had nowhere to be recorded. So it holds the
    # one population a stone is most likely to name and the tree least likely
    # to explain — and this matcher could not see it.
    #
    # The cost was one name and it is the one that proves the point. «MATILDA
    # PAPIĆ 1895–1921» stands on a Senj cross, third name on the stone. It was
    # photographed, read, found to be absent from the tree, and WRITTEN DOWN IN
    # found.psv as a person this archive had discovered. Then the matcher was
    # run and reported the stone as matching nobody — because the file written
    # to hold her was not in the pool she was matched against.
    #
    # That is the sixth time in this archive that a tool has searched a smaller
    # list than the question deserved, and the second time on this very
    # evidence. These people keep their null slug and carry «found»: they stand
    # BESIDE the tree, which is the whole reason the file exists, and the page
    # must never show them as though the tree held them.
    try:
        fj = json.load(open(os.path.join(DATA, "found.json"), encoding="utf-8"))
    except FileNotFoundError:
        fj = {"rows": []}
    for r in fj.get("rows", []):
        name = (r.get("name") or "").strip()
        if not name:
            continue
        text = str(r.get("date") or "")
        b = re.search(r"born\s+(\d{4})", text)
        d = re.search(r"died\s+(\d{4})", text)
        byear = int(b.group(1)) if b else None
        dyear = int(d.group(1)) if d else None
        if byear is None and dyear is None:
            y = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", text)
            ev = (r.get("event") or "").lower()
            if y:
                # «named as parent» dates the CHILD's entry, not this person's,
                # so it gives neither year and must not pretend to.
                if "bapt" in ev or "birth" in ev:
                    byear = int(y.group(1))
                elif "death" in ev or "buri" in ev or "memorial" in ev:
                    dyear = int(y.group(1))
        parts = name.split()
        pool.append({
            "id": None, "name": name,
            "given": " ".join(parts[:-1]) or name,
            "surname": parts[-1] if len(parts) > 1 else "",
            "byear": byear, "dyear": dyear,
            "born": str(byear or ""), "died": str(dyear or ""),
            "sex": "", "slug": None, "rel": {},
            "_found": True,
            "_via": f"read out of a register at {r.get('place') or 'an unnamed place'}, "
                    f"and not in the tree",
        })
    return pool, published


def main():
    people, _published = tree_people()

    files = sorted(f for f in os.listdir(SRCDIR) if f.endswith(".psv"))
    if not files:
        print("no harvest files in sources/findagrave/")
        return 1

    rows, stops, matched_pool = [], {}, {}
    for f in files:
        meta, stop, rs = read_file(os.path.join(SRCDIR, f))
        rows += rs
        stops[meta["surname"]] = stop
        matched_pool[meta["surname"]] = [
            p for p in people if meta["match"] in flat(p.get("name"))]

    # --- match each memorial to a published person -----------------------
    conflicts = []
    for r in rows:
        stop = stops[r["surname"]]
        zub = matched_pool[r["surname"]]
        g, by, dy = toks(r["name"], stop), year(r["born"]), year(r["died"])
        best, bestscore = None, 0
        for p in zub:
            pg = toks(p.get("name"), stop)
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
            if best.get("_found"):
                r["foundNotInTree"] = True
                r["foundVia"] = best.get("_via", "")
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

    surnames = {}
    for r in rows:
        surnames[r["surname"]] = surnames.get(r["surname"], 0) + 1

    stones = stone_half(people)

    out = {
        "source": "Find a Grave, searched 14 September 2026",
        "what": ("An INDEX: somebody else's transcription of a memorial. Every "
                 "top-level key here counts the Find a Grave harvest and nothing "
                 "else. The photographed surveys are under «stones»."),
        "files": files,
        "surnames": sorted(surnames.items(), key=lambda kv: -kv[1]),
        "n": len(rows),
        "matched": sum(1 for r in rows if r.get("slug")),
        "unmatched": sum(1 for r in rows if not r.get("slug")),
        "cemeteries": sorted(where.items(), key=lambda kv: (-kv[1], kv[0])),
        "shared": shared,
        "conflicts": sorted(conflicts, key=lambda c: -abs(c["days"])),
        "rows": rows,
        "stones": stones,
    }
    json.dump(out, open(os.path.join(DATA, "graves.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"graves.json — INDEX: {out['n']} memorials from {len(files)} file(s), "
          f"{out['matched']} matched to a person here, "
          f"{len(shared)} shared plots, {len(conflicts)} date disagreements")
    if stones:
        conf = " ".join(f"{k}={n}" for k, n, _ in stones["confidence"])
        print(f"           STONES: {stones['n']} names from {len(stones['surveys'])} "
              f"survey(s) ({conf}), {stones['matched']} matched, "
              f"{len(stones['stones'])} shared stones, "
              f"{len(stones['conflicts'])} date disagreements")


if __name__ == "__main__":
    main()
