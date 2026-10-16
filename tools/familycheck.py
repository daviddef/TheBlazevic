#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse a family that has no page, and a page that cannot be found.

Written 17 October 2026 (the family-pages audit). This archive publishes a page per
family name, and until that day the direct line carried sixteen surnames with no page
at all: Hedviga's own great-great-grandmothers were a row on /connected/ and nothing
else. Nothing noticed, because nothing asked. This asks, twice.

  1. EVERY FAMILY IN families.json IS REACHABLE. It has a built page, it is in the
     sitemap (which the kit writes, and a noindex page is not in), it is in the
     "The families" menu in layouts/Base.astro, and /families/ links to it. The chips
     on defranceski.com are read from that menu, so a page missing from it is a page
     the landing site cannot see.
  2. EVERY SURNAME ON THE DIRECT LINE HAS A PAGE, OR SAYS WHY NOT. ancestors.json is
     grouped by the archive's own fold() (tools/ancestry.py); a group with no family
     page must be declared in sources/family-pages-pending.psv with the reason, and a
     declaration for a group that now has a page is stale and refused. A double
     surname whose every part has a page (Antić Papić) is covered by the parts.

It reads committed data and the build, never the GEDCOM, so it can run in CI.

  python3 tools/familycheck.py --dist site/dist
  python3 tools/familycheck.py --selftest      plants each fault and shows it is caught
"""
import argparse, json, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ancestry import fold, SURNAMES  # noqa: E402


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def page_keys():
    """slug -> fold keys, for the two lists the generator keeps (older four-plus-nine, and the direct-line twelve)."""
    keys = {sl: list(ks) for sl, ks in SURNAMES.items()}
    src = open(os.path.join(HERE, "build_site_data.py"), encoding="utf-8").read()
    # PAGE_FAMILIES = [ ("slug", "Label", "gloss", ["key", "key"]), ... ]
    block = src[src.index("PAGE_FAMILIES = ["):src.index("PAGE_KEYS =")]
    for m in re.finditer(r'\(\s*"([a-z]+)",\s*"[^"]+",\s*"[^"]*",\s*\[([^\]]*)\]\s*\)', block):
        keys[m.group(1)] = re.findall(r'"([^"]+)"', m.group(2))
    return keys


def pending(root):
    out = {}
    path = os.path.join(root, "sources", "family-pages-pending.psv")
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or line.count("|") < 1 or not line.strip():
            continue
        k, why = [x.strip() for x in line.split("|", 1)]
        out[k] = why
    return out


def check(root, dist, data=None, base=None, keys=None, pend=None):
    data = data or os.path.join(root, "site", "src", "data")
    base = base or os.path.join(root, "site", "src", "layouts", "Base.astro")
    keys = keys or page_keys()
    pend = pend if pend is not None else pending(root)
    problems = []
    fams = load_json(os.path.join(data, "families.json"))
    nav = open(base, encoding="utf-8").read()
    sitemap_path = os.path.join(dist, "sitemap.xml")
    sitemap = open(sitemap_path, encoding="utf-8").read() if os.path.exists(sitemap_path) else None
    fam_index_path = os.path.join(dist, "families", "index.html")
    fam_index = open(fam_index_path, encoding="utf-8").read() if os.path.exists(fam_index_path) else ""
    # the menu group "The families" only
    m = re.search(r'\["The families", \[(.*?)\]\],\n', nav, re.S)
    menu = m.group(1) if m else ""

    for f in fams:
        sl = f["slug"]
        if not os.path.exists(os.path.join(dist, sl, "index.html")):
            problems.append(f"{sl}: no built page at /{sl}/")
        if sitemap is None:
            problems.append("sitemap.xml missing from the build: run it before this check")
        elif not re.search(r"<loc>[^<]*/%s/</loc>" % re.escape(sl), sitemap):
            problems.append(f"{sl}: not in the sitemap")
        if not re.search(r'\["/%s/?", ' % re.escape(sl), menu):
            problems.append(f"{sl}: not in the 'The families' menu in layouts/Base.astro")
        if 'href="/%s/"' % sl not in fam_index:
            problems.append(f"{sl}: /families/ does not link to it")
        if sl not in keys:
            problems.append(f"{sl}: no fold keys known to the generator")

    has = {k for ks in keys.values() for k in ks}
    anc = load_json(os.path.join(data, "ancestors.json"))
    groups = {}
    for a in anc:
        sn = (a.get("surname") or "").strip()
        if not sn:
            continue
        groups.setdefault(fold(sn), []).append(a)
    uncovered = []
    for k, ps in sorted(groups.items()):
        covered = k in has or all(part in has for part in k.split())
        if covered:
            if k in pend:
                problems.append(f"family-pages-pending.psv: '{k}' is declared pending but has a page now: remove the line")
        elif k not in pend:
            problems.append(f"direct line: surname '{k}' ({len(ps)} ancestor(s), ahnentafel "
                            f"{', '.join(str(p['ahn']) for p in sorted(ps, key=lambda p: p['ahn']))}) has no family page "
                            f"and is not declared in sources/family-pages-pending.psv")
        else:
            uncovered.append(k)
    for k in pend:
        if k not in groups:
            problems.append(f"family-pages-pending.psv: '{k}' matches no surname on the direct line")
    return problems, len(fams), len(groups), uncovered


def selftest():
    """Copy the pieces to a scratch tree, break one thing at a time, and require a failure each time."""
    real_dist = os.environ.get("ARCHIVE_OUT") or "dist"
    real_dist = real_dist if os.path.isabs(real_dist) else os.path.join(ROOT, "site", real_dist)
    if not os.path.exists(os.path.join(real_dist, "families", "index.html")):
        print("selftest: no build to plant faults in (run astro build and the sitemap first)")
        return 2
    fails = 0

    def trial(name, mutate, expect):
        nonlocal fails
        t = tempfile.mkdtemp(prefix="familycheck-")
        try:
            data = os.path.join(t, "data"); os.makedirs(data)
            for fn in ("families.json", "ancestors.json"):
                shutil.copy(os.path.join(ROOT, "site", "src", "data", fn), data)
            dist = os.path.join(t, "dist"); os.makedirs(os.path.join(dist, "families"))
            shutil.copy(os.path.join(real_dist, "sitemap.xml"), dist)
            shutil.copy(os.path.join(real_dist, "families", "index.html"), os.path.join(dist, "families"))
            for f in load_json(os.path.join(data, "families.json")):
                os.makedirs(os.path.join(dist, f["slug"]))
                open(os.path.join(dist, f["slug"], "index.html"), "w").write("<html></html>")
            base = os.path.join(t, "Base.astro")
            shutil.copy(os.path.join(ROOT, "site", "src", "layouts", "Base.astro"), base)
            ctx = {"data": data, "dist": dist, "base": base, "pend": pending(ROOT)}
            mutate(ctx)
            probs, *_ = check(ROOT, ctx["dist"], data=ctx["data"], base=ctx["base"], pend=ctx["pend"])
            hit = any(expect in p for p in probs)
            ok = (not probs) if expect is None else hit
            print(f"  {'caught ' if ok else 'MISSED '} {name}" if expect else f"  {'clean  ' if ok else 'FALSE ALARM'} {name}"
                  + ("" if ok else f"  {probs[:2]}"))
            if not ok:
                fails += 1
        finally:
            shutil.rmtree(t, ignore_errors=True)

    def no_page(c): shutil.rmtree(os.path.join(c["dist"], "uroda"))
    def no_sitemap(c):
        p = os.path.join(c["dist"], "sitemap.xml"); s = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(re.sub(r"<url>(?:(?!</url>).)*?/uroda/</loc>.*?</url>", "", s, flags=re.S))
    def no_menu(c):
        s = open(c["base"], encoding="utf-8").read()
        open(c["base"], "w", encoding="utf-8").write(s.replace('["/uroda", "Uroda"], ', ""))
    def no_index_link(c):
        p = os.path.join(c["dist"], "families", "index.html"); s = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(s.replace('href="/uroda/"', 'href="/x/"'))
    def new_ancestor_surname(c):
        a = load_json(os.path.join(c["data"], "ancestors.json"))
        a.append({"id": "@PLANT@", "slug": "plant", "name": "A Plant", "surname": "Zzyzx", "ahn": 999})
        json.dump(a, open(os.path.join(c["data"], "ancestors.json"), "w", encoding="utf-8"))
    def stale_pending(c): c["pend"] = dict(c["pend"], uroda="planted: already has a page")
    def pending_nobody(c): c["pend"] = dict(c["pend"], zzyzx="planted: matches no one")
    def nothing(c): pass

    print("familycheck selftest:")
    trial("control: the real build", nothing, None)
    trial("a family page removed from the build", no_page, "no built page")
    trial("a family dropped from the sitemap", no_sitemap, "not in the sitemap")
    trial("a family dropped from the 'The families' menu", no_menu, "not in the 'The families' menu")
    trial("/families/ no longer linking a family", no_index_link, "does not link to it")
    trial("a new surname on the direct line with no page", new_ancestor_surname, "has no family page")
    trial("a pending line for a family that now has a page", stale_pending, "has a page now")
    trial("a pending line matching nobody", pending_nobody, "matches no surname")
    print("selftest " + ("PASSED: every planted fault was caught and the control was clean" if not fails else f"FAILED: {fails}"))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=os.environ.get("ARCHIVE_OUT") or "dist")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    dist = a.dist if os.path.isabs(a.dist) else os.path.join(ROOT, "site", a.dist)
    problems, nfam, ngroups, uncovered = check(ROOT, dist)
    for p in problems:
        print("  FAIL  familypages  " + p)
    if problems:
        return 1
    print(f"  ok    familypages  {nfam} families, each built, in the sitemap, in the menu and on /families/; "
          f"{ngroups} direct-line surnames, {ngroups - len(uncovered)} with a page, {len(uncovered)} declared pending "
          f"({', '.join(uncovered) or 'none'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
