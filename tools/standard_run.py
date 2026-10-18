#!/usr/bin/env python3
"""Run the kit's linking-standard gate (checkstandard.py) over the built site. This is the archive's one place that knows
where the config, the names index, the living list and the floor are.

    python3 ../tools/standard_run.py                 the gate, with the committed ratchet (.standardfloor.json): last in the build
    python3 ../tools/standard_run.py --table         the same, printing every page's five counts
    python3 ../tools/standard_run.py --write-floor   after an improvement, lock the gain in (refuses while anything rose)

The built site is site/<ARCHIVE_OUT or dist>, as for every kit tool. Run it AFTER `autolink_run.py` (it reads the links that
step wrote) and after every other step that reads or changes the built HTML.

WHAT IT CHECKS (docs: kit/docs/linking-standard.md). For the 12 narrative pages named in site/standard.json, per page:
  L1 names with an entry that are still not linked          L2 people read from records that have no entry
  L3 passages citing a record with no link to it            L4 held scans not beside the passage (none: link-only, below)
  L5 bare given names and forms nobody has written in full  EX exemptions
and a ratchet: a page's count may only go down. Counts only are printed, never a person's name.

LINK-ONLY, by David's ruling of 18 October 2026: FamilySearch frames and Matricula pages are never shown beside a
passage; the passage links to the record instead (scans.link_only in standard.json). So L4 is 0 by rule, not by luck.

IN CI (no GEDCOM, so no sources/*.ged): the gate runs on committed data only. The names index is the committed file (proved
no looser than the committed data by names_index.py --check, which autolink_run.py runs first); the living list is built
from the committed living.json alone (names_index.py --living, CI mode) and the gate refuses (exit 2) if the index or an
`allow` entry equals a living name; the config and the floor are committed; the records table is checked against the
committed data by build_records.py --check. Nothing in the gate reads a file that CI does not have. Counts do not depend
on the GEDCOM: the same build gives the same counts locally and in CI (checked on 18 October 2026).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
KIT = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
INDEX = os.path.join("src", "data", "names-index.json")
CONFIG = "standard.json"
FLOOR = ".standardfloor.json"
LIVING = os.path.join(os.path.dirname(ROOT), "private", "blazevic", "autolink-living.json")


def main(argv):
    py = sys.executable
    if not os.path.exists(LIVING):
        # the living list is written outside the repository by tools/names_index.py --living (autolink_run.py does it first)
        if subprocess.call([py, os.path.join(HERE, "names_index.py"), "--living"], cwd=SITE):
            return 2
    dist = os.environ.get("ARCHIVE_OUT") or "dist"
    cmd = [py, os.path.join(KIT, "checkstandard.py"), "--dist", dist, "--index", INDEX, "--config", CONFIG,
           "--living", LIVING, "--floor", FLOOR, "--strict-config"]
    if "--table" in argv:
        cmd.append("--table")
    if "--write-floor" in argv:
        cmd.append("--write-floor")
    return subprocess.call(cmd, cwd=SITE)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
