#!/usr/bin/env python3
"""Trove, the National Library of Australia — enumerate, then read.

Written 27 September 2026, the day the account holder was given an API key
valid to December 2026. It is the first keyed API this archive has had, and
it matters because of ONE BRANCH: Ivan Žubrinić reached Port Pirie about
1884 and his family is registered ZUBRINICH through Broken Hill, Whyalla
and Quorn to this day. Everything this archive knows about them comes from
indexes. Trove is the newspapers themselves.

THE KEY IS NEVER IN THIS FILE OR IN ANY TRACKED FILE. This repository is
public and publishes to GitHub Pages, so a key in a committed file is a key
on the open web inside two minutes. It lives in sources/keys/trove.env,
which .gitignore excludes entire, and this tool refuses to run without it
rather than falling back to anything.

WHAT THE API GIVES AND WHAT IT DOES NOT. With this key the search endpoint
returns metadata — date, newspaper, page, heading, a relevance score and a
direct link — and it returns NO ARTICLE TEXT. `include=articletext` and
`reclevel=full` were both tried against /v3/result and /v3/newspaper/<id>
and both return an empty articleText. So the OCR has to come from the
public article page, which is free and needs no login:

    https://nla.gov.au/nla.news-article<id>

That split is the method. The API ENUMERATES a surname across a continent
and a century in one request; the public page READS the one article the
enumeration pointed at. Neither half does the other's job.

AND THE SEARCH IS FUZZY, WHICH IS THE THING TO WATCH. A query for
"Zubrinich" returns 9,263 newspaper hits, and the early ones are pony races
and advertising: Trove is matching OCR garble, not the name. Quoting does
not restrict it. THE COUNT IS NOT A FINDING. Only an article whose fetched
text contains the string is a hit, which is what --verify does, and this
tool prints the two numbers separately so they can never be confused.

    python3 tools/trove.py "Zubrinich" --state "South Australia" --verify
    python3 tools/trove.py "Zubrinich" --paper 348 --verify --max 60
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYFILE = os.path.join(ROOT, "sources", "keys", "trove.env")
API = "https://api.trove.nla.gov.au/v3/result"
PAGE = "https://nla.gov.au/nla.news-article%s"


def key():
    """The key, from the ignored env file and nowhere else."""
    env = os.environ.get("TROVE_API_KEY")
    if env:
        return env
    if not os.path.exists(KEYFILE):
        sys.exit(
            "No Trove key. Put it in sources/keys/trove.env as\n"
            "    TROVE_API_KEY=...\n"
            "which .gitignore excludes. Never in a tracked file: this repo is public."
        )
    for line in open(KEYFILE, encoding="utf-8"):
        if line.startswith("TROVE_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("sources/keys/trove.env has no TROVE_API_KEY= line.")


def get(url, hdrs=None):
    req = urllib.request.Request(url, headers=hdrs or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def search(term, k, state=None, paper=None, n=100, sort="dateasc"):
    q = {"q": term, "category": "newspaper", "n": str(min(n, 100)),
         "encoding": "json", "sortby": sort}
    if state:
        q["l-state"] = state
    if paper:
        q["l-title"] = str(paper)
    d = json.loads(get(API + "?" + urllib.parse.urlencode(q),
                       {"X-API-KEY": k}))
    cat = d["category"][0]["records"]
    return cat.get("total"), cat.get("article", [])


def text_of(article_id):
    """The OCR, off the public page. Returns '' when it cannot be read."""
    try:
        h = get(PAGE % article_id)
    except Exception:
        return ""
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("term")
    ap.add_argument("--state")
    ap.add_argument("--paper", help="Trove newspaper id, e.g. 348 = Port Pirie Recorder")
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--verify", action="store_true",
                    help="fetch each article's OCR and keep only literal matches")
    ap.add_argument("--needle", help="what must appear in the text (default: the term)")
    a = ap.parse_args()

    k = key()
    total, arts = search(a.term, k, a.state, a.paper, a.max)
    print("Trove says %s newspaper hit(s) for %r%s — AND THE SEARCH IS FUZZY, "
          "so that number is not a finding." % (
              total, a.term, " in " + a.state if a.state else ""))
    if not a.verify:
        for x in arts[:a.max]:
            print("%s | %-38s | p%-3s | %s" % (
                x.get("date"), x["title"]["title"][:38], x.get("page"),
                (x.get("heading") or "")[:54]))
        return

    needle = (a.needle or a.term).lower()
    kept = 0
    for x in arts[:a.max]:
        t = text_of(x["id"])
        i = t.lower().find(needle)
        if i < 0:
            continue
        kept += 1
        frag = re.sub(r"\s+", " ", t[max(0, i - 120):i + 200])
        print("\n%s | %s | p%s" % (x.get("date"), x["title"]["title"], x.get("page")))
        print("   %s" % (x.get("heading") or "").strip()[:90])
        print("   %s" % frag)
        print("   %s" % (x.get("troveUrl") or PAGE % x["id"]))
        time.sleep(0.4)
    print("\n%d of %d fetched article(s) actually contain %r." %
          (kept, min(len(arts), a.max), a.needle or a.term))


if __name__ == "__main__":
    main()
