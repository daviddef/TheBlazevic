# A film number does not reach everything the film holds

15 September 2026. Written after work-list row 28 spent a sitting looking for a
death register that the catalogue says is on the film, on a film whose every
image is a baptism.

## The catalogue will tell you what a film holds, exactly

This is the call, and it is the thing this archive should have had a week ago:

    /service/search/catalog/item/koha:<NNNNNN>

The reply carries **`source.film_note[]`**, one entry per digital film, each with
`digital_film_no`, `items`, `text` and `fs_indexed`. For Otočac, `koha:837578`:

| DGS | items | text | indexed |
|---|---|---|---|
| 5498269 | Items 1–4 | Status animarum 1710-1846 · Vjenčani 1859-1872 · Umrli 1780-1836, 1859-1872 | |
| 5482656 | Item 6 | Rođeni 1834-1846 | **Y** |
| 5482657 | Items 1–2 | **Rođeni 1846-1858 · Umrli 1834-1858** | **Y** |

That is authoritative, it is one HTTP call, and it is how `holdings.psv` should
be audited rather than by opening films and guessing (work-list row 42).

## But the film-number URL walks only part of it

`https://www.familysearch.org/en/search/film/005482657?i=<N>` was walked across
its whole length:

    image 250   baptism, "baptizata die 5ta 9bris 1852"
    image 330   baptism, village names in the margin
    image 410   baptism, "Levante Maria Filipovich"
    image 465   baptism, "Lucas filius legitimus Georgii Dupsic"
    image 483   END OF ROLL

**483 images, and every sampled one is Item 1 — *Rođeni 1846-1858*.** The
catalogue's Item 2, ***Umrli 1834-1858***, is not on this traversal at all. The
waypoint in the URL also **changes between images** — `9RK1-Y4C…` at image 1,
`9RK1-Y44…` from image 250 on — so the film number is walking a sequence of
waypoints and simply does not include the one holding the deaths.

## What this means in practice

**A DGS number names a reel. It does not name a route to everything on the
reel.** Three separate failures this week have the same shape:

* **005481648** — catalogued as the Karlobag 1691–1804 baptisms; opened by film
  number it has 596 images and image 216 is headed *«Godine 1845»*. The 1771–1804
  baptisms are under another waypoint, reached in the end through the **record
  index**.
* **005497948** — 802 images and at least three books, the waypoint changing
  between images.
* **005482657** — the deaths the catalogue promises are not on the film-number
  traversal.

**So: use the catalogue to learn what exists, the record index to get an ARK
where the parish is indexed, and record the ARK.** An ARK resolves to exactly
one image, permanently. A film number resolves to a walk that may not pass the
book you want.

## What row 28 needs next

The Otočac *Umrli 1834-1858* must be reached by its **own waypoint**, not by the
film number. Otočac deaths are **not in the record index** — 165 indexed
baptisms in the sample and not one death — so the index cannot supply an ARK
either. The remaining route is the waypoint browser: the parish's own image
index, `/search/image/index?owc=…`, which lists each book separately.
