#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuse when the git object store is damaged, however green everything else is.

Written 27 September 2026, after a week in which this estate lost and rebuilt
several repositories and every test we circulated missed the same thing.

WHAT HAPPENED. iCloud reverted working trees after a macOS upgrade. Sessions
compared file mtimes, then mtimes AND sizes, then the index — all FILE-level
tests, and all of them useful. The Defranceski session ran the full set, got a
clean worktree, an empty `git diff HEAD`, an empty `git diff --cached` and
twelve green gates across 2,940 pages, and reported itself the one undamaged
repo of nine. It had **32 objects missing and 30 links broken**. Nothing that
looks at files can see that, because the files were fine; the object store
underneath them was not.

This archive's own version was narrower and just as invisible: `.git/objects`
and `.git/refs` vanished, came back partially, and left `refs/heads/main`
pointing at a commit whose object had not been restored. Every site gate would
have passed on the working tree right up until git was asked to do anything.

SO THE TEST HAS TO ASK GIT, NOT THE FILESYSTEM. Two probes, both effectively
free — 0.03s and 0.00s on a 55 MB repo, which is why this can sit in the build
chain rather than in a note nobody runs:

    git fsck --connectivity-only     every object a ref needs is present
    git write-tree                   the index itself is readable

`git commit --dry-run` is NOT a probe. It exits non-zero whenever nothing is
staged, which reads as damage on a clean tree — one session misdiagnosed its
own repo that way before testing properly.

WHAT THIS DOES NOT DO. It does not repair. The additive repair that worked
across this estate, and that permission classifiers allowed where `git reset
--hard` was refused, is:

    git -c gc.auto=0 -c maintenance.auto=0 fetch --refetch origin main

It deletes nothing and keeps uncommitted work, but it requires HEAD to equal
origin/main — check `git rev-list --count origin/main..HEAD` first, because a
repo with unpushed commits needs a person, not a command.

Usage:  python3 tools/repocheck.py
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT,
                          capture_output=True, text=True)


def main():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("  --    repo       no .git here; nothing to check")
        return 0

    # 1. Can git name HEAD at all? This is the failure this archive actually
    #    hit: the ref file survived and the commit it named did not.
    r = git("rev-parse", "--verify", "HEAD")
    if r.returncode != 0:
        print("  FAIL  repo       git cannot resolve HEAD — " +
              (r.stderr.strip().splitlines() or ["unknown error"])[0])
        print("\nThe ref exists and the object it names may not. Repair with:\n"
              "  git fetch origin main && git update-ref refs/heads/main <origin tip>")
        return 1

    # 2. Is every object the refs depend on actually present? DANGLING objects
    #    are normal debris from rebases and amends and are not a fault; MISSING
    #    and BROKEN are.
    r = git("fsck", "--connectivity-only")
    bad = [l for l in (r.stdout + r.stderr).splitlines()
           if l.strip() and not re.match(r"^(dangling|notice|Checking)", l.strip())]
    if bad:
        for l in bad[:12]:
            print(f"  FAIL  repo       {l.strip()[:110]}")
        if len(bad) > 12:
            print(f"                   … and {len(bad) - 12} more")
        print("\nThe object store is damaged. See the docstring of this file for the\n"
              "additive repair; do NOT run it if this repo has unpushed commits.")
        return 1

    # 3. Is the index readable? A corrupted index passes every file-level test.
    if git("write-tree").returncode != 0:
        print("  FAIL  repo       the git index is unreadable (write-tree failed)")
        print("\n`git reset` rebuilds the index from HEAD without touching a working file.")
        return 1

    # A stray tmp_pack is an interrupted repack. Harmless, but it means
    # something killed git mid-write — worth saying once, not worth refusing.
    pack = os.path.join(ROOT, ".git", "objects", "pack")
    stray = [f for f in os.listdir(pack)] if os.path.isdir(pack) else []
    stray = [f for f in stray if f.startswith("tmp_pack")]
    note = f", {len(stray)} interrupted repack(s) left behind" if stray else ""
    ahead = git("rev-list", "--count", "origin/main..HEAD").stdout.strip() or "?"
    print(f"  ok    repo       objects connected, index readable, {ahead} commit(s) "
          f"unpushed{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
