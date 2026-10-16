#!/usr/bin/env python3
"""The names of living people, as phrases a page could contain.

Used by the living gate (tools/livingcheck.py) to ask whether a living person is
named where the archive does not name them: as a Person row of the search index
(INDEX-NAME), and, on a local build with the GEDCOM, in the text the archive
wrote about people it gives no page (GED-NAME, advisory).

The rule since 16 October 2026 is that a living person MAY be named, with their
town and country and nothing more; this module exists to find the names, not to
forbid them.

TWO SUBTRACTIONS, both learned in the kit's own gate (checkliving.py), whose
semantics these copy so the estate has one idea of the problem:

  * EXACT NAMESAKES. A living person whose name is common here shares the phrase
    with eighteen dead men of that name; the phrase cannot tell them apart, so it
    is neither searched for nor failed. They are COUNTED, and the gate prints the
    count.
  * LONGER PUBLISHED NAMES that contain the phrase: "Ana Kalanj" sits inside
    "Ana Kalanj Example".
"""
import re
import sys
import os
import collections

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
import searchkit  # noqa: E402

fold = searchkit.fold
MIN_PHRASE = 7
TOKEN = re.compile(r"[a-z0-9]+")


def norm(name):
    name = re.sub(r"\s*\(.*?\)", " ", name or "")
    name = re.sub(r"[\"“”]", " ", name)
    return " ".join(name.split())


def phrases_of(full):
    """The forms a page might use: the whole recorded name, and first + last."""
    parts = norm(full).split()
    if len(parts) < 2:
        return set()
    return {" ".join(parts), parts[0] + " " + parts[-1]}


def folded_phrases(name):
    return {fold(x) for x in phrases_of(name)}


class Names:
    """living_names: iterable of display names; dead_names: every published
    person who has died."""

    def __init__(self, living_names, dead_names):
        self.living = sorted({n for n in living_names if n})
        self.dead = sorted({n for n in dead_names if n})
        dead_phr = set()
        for n in self.dead:
            dead_phr |= folded_phrases(n)
        self.dead_folded = {fold(norm(n)) for n in self.dead if len(norm(n).split()) >= 2}
        self.forbidden = collections.defaultdict(set)   # folded phrase -> names
        self.namesakes = set()                           # living names fully namesaked
        for full in self.living:
            ph = {p for p in folded_phrases(full) if len(p) >= MIN_PHRASE}
            if not ph:
                continue
            live = {p for p in ph if p not in dead_phr}
            if not live:
                self.namesakes.add(full)
            for p in live:
                self.forbidden[p].add(full)
        self.covers = {
            p: sorted((n for n in self.dead_folded if p in n and len(n) > len(p)),
                      key=len, reverse=True)
            for p in self.forbidden}
        # phrases indexed by their first token: a scan over the text asks, at each
        # token, only about the phrases that could start there. (A regex of all
        # the phrases was tried first and takes minutes over a built site.)
        self.first = collections.defaultdict(list)
        for ph in self.forbidden:
            toks = TOKEN.findall(ph)
            if toks:
                self.first[toks[0]].append((ph, len(toks)))

    # ---- find / remove -----------------------------------------------------
    @staticmethod
    def _fold_map(text):
        """The folded text, and for each folded character the index in `text`
        it came from, so a match can be cut out of the original. Most text folds
        one character to one character, and then the map is the identity."""
        f = fold(text)
        if len(f) == len(text):
            return f, range(len(text))
        out, idx = [], []
        for i, ch in enumerate(text):
            for c in fold(ch):
                out.append(c)
                idx.append(i)
        return "".join(out), idx

    def hits(self, text):
        """[(start, end, folded phrase)] in `text`, covered matches excluded."""
        if not self.first or not text:
            return []
        ftext, idx = self._fold_map(text)
        toks = [(m.start(), m.end()) for m in TOKEN.finditer(ftext)]
        out = []
        for i, (a0, b0) in enumerate(toks):
            cands = self.first.get(ftext[a0:b0])
            if not cands:
                continue
            for ph, n in cands:
                if i + n > len(toks):
                    continue
                e = toks[i + n - 1][1]
                if ftext[a0:e] != ph:
                    continue
                win = ftext[max(0, a0 - 40):e + 40]
                if any(longer in win for longer in self.covers.get(ph, ())):
                    continue
                out.append((idx[a0], idx[e - 1] + 1, ph))
        return out

    def count_hits(self, text):
        return len(self.hits(text))

