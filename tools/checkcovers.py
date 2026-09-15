#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse when outstanding work exists on disk with no work-list row against it.

The work list has a gate that checks the rows it HAS. Nothing checked for rows
it was MISSING, and on 15 September 2026 that cost exactly what you would
expect: five letters had been sent to archives and parish offices, four of them
had rows, and the fifth — the reply that named the three further doors, and so
the reason three of the other rows existed at all — had none. Every row present
looked fine in isolation. The list was only wrong in what it did not say.

An absence cannot be spotted by looking at what is there. It needs a second list
to count against. This archive has two that are already exact:

  * **`sources/searched.json`** — a row with outcome `pending` means, in the
    register's own words, "known, wanted, and not yet got". That IS outstanding
    work, by definition, and every one of them should be answerable from the
    work list.
  * **`requests/sent/`** — a letter that has gone out is outstanding until it is
    answered. The folder is the truth; it holds the sent letters and nothing
    else.

So each work-list row may declare what it accounts for:

    { "n": 13, "what": "Waiting on the Državni arhiv u Gospiću",
      "covers": ["register:letters/gospic", "letter:EMAIL-gospic.txt"] }

and this refuses when

  * something outstanding is covered by no row — the missing-row case; or
  * a `covers` entry names a register key or a letter that does not exist — the
    rot case, which is what happens when a pending row is finally retired and
    the work-list row that pointed at it is left behind.

Both directions matter. The first catches a list that is too short; the second
catches one that has gone stale, which is how the register itself went wrong
earlier the same day.

**Why matching is explicit and not clever.** There is no fuzzy match on titles
here, deliberately. The register learned this lesson at a cost: "Senj marriages,
1734-1858" is genuinely unopened while "Senj marriages, 1859-1920" is read end to
end, and any gate matching on names would have called the first one stale. A
declared key is exact. A guess is not, and a gate that cries wolf gets switched
off.

    python3 tools/checkcovers.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKLIST = os.path.join(ROOT, "site", "src", "data", "worklist.json")
REGISTER = os.path.join(ROOT, "sources", "searched.json")
SENT = os.path.join(ROOT, "requests", "sent")

# There is deliberately no exemption list. The first draft of this gate excused
# keys beginning "plan/", on the grounds that a plan is not work. Running it
# showed that the one such row — ahnentafel 11, the emptiest person on the direct
# line — names two baptisms sitting inside a filmed book this archive has already
# opened. It was work, and the exemption was just noise-reduction dressed up as a
# rule. The register's own vocabulary settles it: "pending" means "known, wanted,
# and not yet got". If it is wanted, it is work, and it needs a row.


def main():
    bad = []

    work = json.load(open(WORKLIST, encoding="utf-8"))
    reg = json.load(open(REGISTER, encoding="utf-8"))

    # ---- what is outstanding, enumerated from the two exact lists ----------
    outstanding = {}
    for r in reg["rows"]:
        if r.get("outcome") != "pending":
            continue
        outstanding["register:" + r.get("key", "")] = r.get("src", "?")[:60]

    if os.path.isdir(SENT):
        for fn in sorted(os.listdir(SENT)):
            if fn.startswith("."):
                continue
            outstanding["letter:" + fn] = "a letter that has been sent"
    else:
        bad.append(f"no {os.path.relpath(SENT, ROOT)} folder — the letters cannot be counted")

    # ---- what the work list claims to account for --------------------------
    claimed = {}
    for row in work["rows"]:
        for c in row.get("covers", []):
            claimed.setdefault(c, []).append(row.get("n"))

    # ---- 1. outstanding work with no row ----------------------------------
    for token, what in sorted(outstanding.items()):
        if token not in claimed:
            bad.append(f"nothing on the work list covers {token!r} — {what}")

    # ---- 2. a row pointing at something that no longer exists --------------
    known_keys = {"register:" + r.get("key", "") for r in reg["rows"]}
    known_letters = set()
    if os.path.isdir(SENT):
        known_letters = {"letter:" + f for f in os.listdir(SENT)}
    for token, rows in sorted(claimed.items()):
        where = ", ".join(f"row {n}" for n in rows)
        if token.startswith("register:"):
            if token not in known_keys:
                bad.append(f"{where}: covers {token!r}, but no register row has that key")
        elif token.startswith("letter:"):
            if token not in known_letters:
                bad.append(f"{where}: covers {token!r}, but there is no such letter in requests/sent/")
        else:
            bad.append(f"{where}: covers {token!r} — must start with 'register:' or 'letter:'")

    if bad:
        for b in bad:
            print("  " + b)
        print(f"\n{len(bad)} problem(s): the work list does not account for what is outstanding")
        return 1

    print(f"  ok    work list accounts for {len(outstanding)} outstanding item(s) "
          f"— {sum(1 for k in outstanding if k.startswith('register:'))} pending register rows, "
          f"{sum(1 for k in outstanding if k.startswith('letter:'))} sent letters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
