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

## But the film-number URL runs into a different parish

**A first reading of this got it wrong, and the correction is the finding.** The
film-number URL was walked across its whole length and every sampled image was a
baptism:

    image 250   baptism, "baptizata die 5ta 9bris 1852"
    image 330   baptism, village names in the margin
    image 410   baptism, "Levante Maria Filipovich"
    image 465   baptism, "Lucas filius legitimus Georgii Dupsic"
    image 483   END OF ROLL

The conclusion drawn was that the film number walks Item 1 only and the deaths
are not on it. **That was wrong.** Those images are not Otočac at all. The
waypoint changes partway through, and the breadcrumb on the later ones reads:

> Croatia, Church Books › Roman Catholic (Rimokatolička crkva) › **Pakrac** ›
> Births (Rođeni) 1781-1823

**The Otočac book is 218 images, not 483.** Its own waypoint is
`9RK1-Y4C:391644801,391674001`, and its breadcrumb reads «Otočac › **Births
(Rođeni) 1846-1858 Deaths (Umrli) 1834-1858**» — both items, exactly as the
catalogue says. The deaths are there: image 100 is April **1835**, image 165 is
page 149 of **1849**, image 200 is page 221 of **1855**.

**So the film number concatenates parishes.** `…/search/film/005482657?i=N`
stays inside Otočac for N ≤ 218 and silently crosses into Pakrac after that. Four
hundred and eighty-three images under one film number are two different parishes'
books, and nothing in the viewer says so except the breadcrumb, which the film
number's own URL does not show.

## How to land in the right book

    /search/image/index?owc=<WAYPOINT>%3Fcc%3D2040054&cc=2040054

lands in the book itself and prints its breadcrumb and its true image count.
From there the film-number URL can be used to step, but only within the count
the breadcrumb gives. Adding `&i=` to an ARK URL does **not** move the viewer;
the *Previous Image* / *Next Image* buttons do.

## What this means in practice

**A DGS number names a reel, and a reel may hold more than one parish.** Three
failures this week have the same root:

* **005481648** — catalogued as the Karlobag 1691–1804 baptisms; opened by film
  number it has 596 images and image 216 is headed *«Godine 1845»*.
* **005497948** — 802 images, at least three books, waypoint changing between
  images.
* **005482657** — 483 images under the film number, of which **218 are Otočac
  and the rest are Pakrac**.

**So: use the catalogue to learn what exists, the waypoint to land in the right
book, the record index for an ARK where the parish is indexed — and record the
ARK.** An ARK resolves to exactly one image, permanently. A film number resolves
to a walk that may leave the parish without telling you.
