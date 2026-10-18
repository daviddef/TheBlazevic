#!/usr/bin/env python3
"""The gate for citations that can be followed (components/Rec.astro, the kit's <Rec>).

    python3 tools/check_rec.py                    from the repo root or site/; ARCHIVE_OUT (as for every gate) names the build
    python3 tools/check_rec.py --sample 100       also check a random 100 record links against the SOURCE data, not the table

WHAT IT HOLDS (counts only; stdlib only, so it runs in CI as it does here)
  1  every <a data-rec> in the built site goes exactly where records.json says its id goes (no id the table lacks, no address
     the table does not give that id), and carries words;
  2  every row of records.json is an address the committed source data holds (tools/build_records.py --check proves the
     table is what the data derives; this checks the pages against the table);
  3  LINK-ONLY: no <img> in the build is a FamilySearch or Matricula address, and no record link draws a figure (class
     rec-fig): the table has no plates;
  4  a build with no <a data-rec> at all has examined nothing and fails.
--sample N takes N record links from the build (a fixed seed, so a run is repeatable), and for each one looks the ADDRESS up in
the source files the table is built from (snapshots.json, trove.json, searched.json, found.json, readings.json) and checks the
id's meaning against the page's words where the id carries one (a Matricula "sig. NNNNN" in the link text is the sig in the
address; a "folio N"/"page N"/"image N" in the text of a snapshot link is the number in that snapshot's own `where`). A
mismatch is a failure. Prints counts only.
"""
import json
import os
import random
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "src", "data")


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.recs, self.imgs, self.figs, self.trove = [], [], 0, []
        self._cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "nla.gov.au/nla.news-article" in (a.get("href") or ""):
            self.trove.append(a.get("href"))
        if tag == "a" and "data-rec" in a:
            self._cur = {"id": a.get("data-rec"), "href": a.get("href") or "", "text": []}
        if tag == "img":
            self.imgs.append(a.get("src") or "")
        if "rec-fig" in (a.get("class") or "").split():
            self.figs += 1

    def handle_data(self, d):
        if self._cur is not None:
            self._cur["text"].append(d)

    def handle_endtag(self, tag):
        if tag == "a" and self._cur is not None:
            self._cur["text"] = re.sub(r"\s+", " ", "".join(self._cur["text"])).strip()
            self.recs.append(self._cur)
            self._cur = None


def main(argv):
    dist = os.environ.get("ARCHIVE_OUT") or "dist"
    root = os.path.join(SITE, dist)
    n = None
    if "--sample" in argv:
        n = int(argv[argv.index("--sample") + 1])
    table = {r["id"]: r for r in json.load(open(os.path.join(DATA, "records.json"), encoding="utf-8"))["records"]}
    links, bad, imgs_bad, figs, trove = [], 0, 0, 0, []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".html"):
                continue
            path = os.path.join(dp, f)
            p = P()
            p.feed(open(path, encoding="utf-8", errors="replace").read())
            page = "/" + os.path.relpath(dp, root).replace(os.sep, "/") + "/"
            for r in p.recs:
                links.append((page, r))
            trove += [(page, h) for h in p.trove]
            imgs_bad += sum(1 for s in p.imgs if re.search(r"familysearch\.org|matricula-online\.eu", s))
            figs += p.figs
    if not links:
        print("rec  FAIL  no <a data-rec> in the build: a check that examined nothing has not passed")
        return 1
    pages = {}
    for page, r in links:
        pages[page] = pages.get(page, 0) + 1
        t = table.get(r["id"])
        if t is None or t["url"] != r["href"] or not r["text"] or t.get("hold") or t.get("living"):
            bad += 1
    print("rec  %d record links on %d pages; %d not exactly what records.json says; %d FamilySearch/Matricula images; %d figures"
          % (len(links), len(pages), bad, imgs_bad, figs))
    fail = bad or imgs_bad or figs
    if n:
        src = {}
        for name in ("snapshots", "trove", "searched", "found", "readings"):
            src[name] = open(os.path.join(DATA, name + ".json"), encoding="utf-8").read()
        snaps = {r["id"]: r for r in json.load(open(os.path.join(DATA, "snapshots.json"), encoding="utf-8"))["rows"]}
        rnd = random.Random(20261018)
        pool = sorted({(pg, r["id"], r["href"], r["text"]) for pg, r in links})
        # the Trove articles this archive already linked by hand (a table of 74 on /port-pirie/) are record links too
        tids = {r["url"]: r["id"] for r in table.values() if r["kind"] == "trove"}
        pool += sorted({(pg, tids.get(h, "?"), h, "") for pg, h in trove})
        pick = rnd.sample(pool, min(n, len(pool)))
        mism = 0
        for pg, i, href, text in pick:
            kind = table[i]["kind"] if i in table else "?"
            ok = False
            if kind == "ark":
                ark = href.rsplit("/ark:/61903/", 1)[-1]
                ok = any(ark in src[k] for k in ("found", "readings")) and (not re.search(r"\bark\b", text) or ark in text)
            elif kind in ("snapshot",):
                ok = href in src["snapshots"]
                s = snaps.get(i)
                for grp in re.findall(r"(?:folio|page|image|p\.)\s*(\d+(?:/\d+)*)", text, re.I):
                    # "folio 36/37" is a spread: either number is the snapshot's own
                    if s and not any(re.search(r"(?:folio|page|image|pg=|viewer pg=)\s*%s\b" % num, s["where"]) for num in grp.split("/")):
                        ok = False
            elif kind == "trove":
                ok = href in src["trove"]
            elif kind == "film":
                m = re.search(r"/film/(\d+)", href)
                ok = bool(m) and m.group(1) in src["searched"]
                for num in re.findall(r"\b(\d{6,9})\b", text):
                    ok = ok and int(num) == int(m.group(1))
            elif kind == "matricula":
                ok = href in src["searched"] or href in src["snapshots"] or href.replace("/?", "?") in src["searched"]
                sig = re.search(r"/(\d{5})/", href)
                for num in re.findall(r"sig\.?\s*(\d{5})", text):
                    ok = ok and bool(sig) and sig.group(1) == num
                pgm = re.search(r"pg=(\d+)", href)
                for num in re.findall(r"image\s+(\d+)", text, re.I):
                    ok = ok and bool(pgm) and pgm.group(1) == num
            if not ok:
                mism += 1
                if "-v" in argv:
                    print("  mismatch: %s  %s  %r" % (pg, i, text))
        print("rec  sample of %d record links checked against the source data: %d mismatches" % (len(pick), mism))
        fail = fail or mism
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
