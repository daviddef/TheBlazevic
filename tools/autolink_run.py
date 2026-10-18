#!/usr/bin/env python3
"""Run the kit's build-time name linker over the built site, and its gate. This is the archive's one place that knows
where the index, the living list and the floor are.

    python3 ../tools/autolink_run.py           link the names (after `astro build`, before anything that reads the HTML)
    python3 ../tools/autolink_run.py --check   change nothing; exit 1 if a run would add a link
    python3 ../tools/autolink_run.py --gate    checklinks.py with the committed ratchet (.linkfloor.json), last in the build
    python3 ../tools/autolink_run.py --write-floor   after an improvement, lock the gain in (refuses while anything rose)

The built site is site/<ARCHIVE_OUT or dist>, as for every kit tool.

WHAT RUNS WHERE
  1. tools/names_index.py --check   the committed index agrees with the COMMITTED data (works in CI, which has no GEDCOM);
  2. tools/names_index.py --living  the living list, written OUTSIDE the repository (../private/blazevic/): from the
                                    GEDCOM and the kit's living rule on a machine that has it, from the committed
                                    living.json alone in CI;
  3. kit autolink.py / checklinks.py with that list. The kit refuses to run (exit 2) if an index entry equals a living
     name or address.
Counts only are printed, never a person's name.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
KIT = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
INDEX = os.path.join("src", "data", "names-index.json")
FLOOR = ".linkfloor.json"
LIVING = os.path.join(os.path.dirname(ROOT), "private", "blazevic", "autolink-living.json")
PREFIXES = ["/people/", "/who/", "/found/"]


def run(cmd, **kw):
    return subprocess.call(cmd, cwd=SITE, **kw)


def main(argv):
    py = sys.executable
    if run([py, os.path.join(HERE, "names_index.py"), "--check"]):
        return 1
    if run([py, os.path.join(HERE, "names_index.py"), "--living"]):
        return 2
    dist = os.environ.get("ARCHIVE_OUT") or "dist"
    common = ["--dist", dist, "--index", INDEX, "--living", LIVING]
    if "--gate" in argv or "--write-floor" in argv:
        cmd = [py, os.path.join(KIT, "checklinks.py")] + common + ["--floor", FLOOR]
        for p in PREFIXES:
            cmd += ["--allow-prefix", p]
        if "--write-floor" in argv:
            cmd.append("--write-floor")
        return run(cmd)
    cmd = [py, os.path.join(KIT, "autolink.py")] + common
    for p in PREFIXES:
        cmd += ["--allow-prefix", p]
    if "--check" in argv:
        cmd.append("--check")
    return run(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
