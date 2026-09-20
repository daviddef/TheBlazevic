#!/usr/bin/env python3
"""Make every note this work list cites something a reader can actually open.

WHY. The work list is where this archive explains its own reasoning, and it
cites its working notes constantly — «written up in notes/ana-sumbul-maric.md»,
«notes/karlobag-is-indexed.md». Some of those citations are markdown links to
GitHub and some are bare code spans.

On 20 September 2026 the split was EIGHT linked and TWENTY-ONE not. A reader on
the site met `notes/karlobag-the-index-calls-them-piberich.md` as grey monospace
text, with no way to reach the argument it names. The archive was citing
evidence its readers could not follow -- which is the thing this whole project
exists not to do.

The notes are not built as pages: they are working papers, they change, and they
are kept in the repository on purpose. That is fine. What is not fine is naming
one and not saying where it is.

WHAT IT DOES. Rewrites `notes/x.md` -- a backtick code span -- into a markdown
link to the file on GitHub. Already-linked citations are left exactly as they
are, so it is idempotent and safe to run on every regeneration.

WHAT IT REFUSES. A citation naming a note that does not exist. A dead reference
is worse than a bare one: it sends a reader somewhere there is nothing.

Reads and rewrites site/src/data/worklist.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKLIST = os.path.join(ROOT, "site", "src", "data", "worklist.json")
REPO = "https://github.com/daviddef/TheBlazevic/blob/main"

# Only a backtick code span. An existing [text](url) is left alone, which is what
# makes this safe to run again and again.
SPAN = re.compile(r"`(notes/[a-z0-9][a-z0-9\-]*\.md)`")
ANY = re.compile(r"notes/[a-z0-9][a-z0-9\-]*\.md")


def main():
    doc = json.load(open(WORKLIST, encoding="utf-8"))
    rows = doc if isinstance(doc, list) else doc.get("rows") or doc.get("items") or []

    cited = set()
    for r in rows:
        cited.update(ANY.findall(r.get("note") or ""))
    dead = sorted(p for p in cited if not os.path.exists(os.path.join(ROOT, p)))
    if dead:
        print(f"FAIL  the work list cites {len(dead)} note(s) that do not exist:")
        for p in dead:
            print(f"        {p}")
        print("\n      A dead citation sends a reader somewhere there is nothing.")
        return 1

    changed = 0

    def link(m):
        nonlocal changed
        changed += 1
        return f"[{m.group(1)}]({REPO}/{m.group(1)})"

    for r in rows:
        note = r.get("note")
        if not note:
            continue
        new = SPAN.sub(link, note)
        if new != note:
            r["note"] = new

    if changed:
        with open(WORKLIST, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print(f"notelinks — {len(cited)} notes cited, all present; {changed} citation(s) made clickable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
