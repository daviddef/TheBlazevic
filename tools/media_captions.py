"""Match MyHeritage photo captions against published people.

The site media library holds 4,500 items; only 89 are attached to this archive.
The library's own person tags are not reachable (see tools/fetch_media.md), but
every item carries a caption, and the captions are overwhelmingly names.

So: fold the caption, fold each published person's name, and report where they
meet. A caption is MyHeritage's claim about the image, not evidence — this
produces a *shortlist to look at*, never an attachment.

    python3 tools/media_captions.py sources/media/captions.psv
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ancestry import fold  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "site" / "src" / "data"

# Caption words that describe the record, not the person.
RECORD = {
    "birth", "born", "death", "died", "marriage", "married", "baptism",
    "baptised", "baptized", "burial", "buried", "record", "records",
    "certificate", "index", "register", "page", "scan", "copy", "photo",
    "img", "image", "doc", "document", "file", "card", "list", "passenger",
    "manifest", "census", "grave", "headstone", "tombstone", "obituary",
}
NOISE = re.compile(r"^(?:\d+|[a-z]?\d[\w]*|_.*)$")


def words(caption):
    """Caption -> the tokens that could be name parts."""
    c = caption.split("|")[0]                    # strip the comment count
    c = re.sub(r"\b(1[6-9]\d\d|20[0-2]\d)\b", " ", c)   # strip years
    c = re.sub(r"[^\wÀ-ɏ]+", " ", c)
    out = []
    for t in c.split():
        t = t.strip()
        if len(t) < 3:
            continue
        low = t.lower()
        if low in RECORD or NOISE.match(low):
            continue
        out.append(t)
    return out


def load_captions(path):
    items = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        mid, _, caption = line.partition("|")
        items.append((mid.strip(), caption.strip()))
    return items


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "sources/media/captions.psv"
    items = load_captions(ROOT / src)

    people = json.loads((DATA / "people.json").read_text(encoding="utf-8"))
    have = {p["id"] for m in json.loads((DATA / "media.json").read_text(encoding="utf-8"))
            for p in m.get("people", [])}

    # surname key -> people; given key -> people
    by_sur, by_giv = {}, {}
    for p in people:
        for k, d in ((fold(p.get("surname") or ""), by_sur),
                     (fold(p.get("given") or ""), by_giv)):
            for part in (k or "").split():
                if len(part) >= 3:
                    d.setdefault(part, []).append(p)

    hits, seen_mid = [], set()
    for mid, caption in items:
        ws = [fold(w) for w in words(caption)]
        ws = [w for w in ws if w]
        if not ws:
            continue
        # a person matches when the caption carries BOTH a name of theirs
        # and their surname — one alone is far too loose
        score = {}
        for w in ws:
            for part in w.split():
                for p in by_sur.get(part, []):
                    score.setdefault(p["slug"], [p, set()])[1].add("surname")
                for p in by_giv.get(part, []):
                    score.setdefault(p["slug"], [p, set()])[1].add("given")
        for slug, (p, kinds) in score.items():
            if len(kinds) < 2:
                continue
            hits.append({
                "mid": mid, "caption": caption.split("|")[0].strip(),
                "slug": slug, "name": p["name"],
                "years": f"{p.get('byear') or '?'}–{p.get('dyear') or '?'}",
                "known": p["id"] in have,
            })
            seen_mid.add(mid)

    fresh = [h for h in hits if not h["known"]]
    out = DATA / "mediacandidates.json"
    fresh.sort(key=lambda h: (h["name"], h["mid"]))
    out.write_text(json.dumps(fresh, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"captions read      {len(items)}")
    print(f"captions that hit  {len(seen_mid)}")
    print(f"candidate pairs    {len(hits)}  ({len(fresh)} for people with no media yet)")
    print(f"people reached     {len({h['slug'] for h in fresh})}")
    print(f"wrote              {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
