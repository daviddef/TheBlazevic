# Reading a FamilySearch image at full resolution

**Solved 13 September 2026.** This archive said twice, in two different places,
that re-sourcing the 960-pixel documents needed "a person at the keyboard". Both
statements were wrong, and the second was wrong in a more interesting way than
the first.

## What the archive used to say, and why it was wrong

**Version 1.** *"The viewer will accept a page number but does not repaint its
canvas under automation."* — **False.** Typing an image number into the viewer's
own box and pressing Return repaints it and changes the image's ARK. The URL
parameter `?i=N` does *not* drive it; the input box does.

**Version 2** (written this morning). *"The tiles return 401 without the session
cookie; requesting them with CORS fails; loading them without CORS taints the
canvas. Reachable by a signed-in person pressing Download, and by nothing else."*
— **Also false**, and the error was mine: I tested the **wrong host**.

The viewer loads its tiles from `sg30p0.familysearch.org`, which is cross-origin
and does exactly what I described. **The same tiles are served from
`www.familysearch.org`**, which is same-origin with the viewer page — no CORS
preflight, no tainted canvas, cookies sent automatically.

## The method

```js
// 1. The Deep Zoom descriptor, same-origin. Gives Width, Height, TileSize.
await fetch(`/service/records/storage/deepzoomcloud/dz/v1/${ark}/image.xml`,
            {credentials: "include"});
//    -> <Image TileSize="256" Overlap="1" Format="jpg">
//         <Size Width="5768" Height="4198"/></Image>

// 2. Tiles, same path. Level 13 is full size for a 5768px image
//    (level = ceil(log2(max(W,H)))).
`/service/records/storage/deepzoomcloud/dz/v1/${ark}/image_files/13/${col}_${row}.jpg`

// 3. Draw them into a canvas at (col*256 - overlap, row*256 - overlap).
//    Same-origin, so the canvas is NOT tainted and toDataURL works.
```

`tools/familysearch_stitch.js` holds a working `fetchWindow(ark, level, x, y, w, h)`
that returns a canvas for any rectangle of any image.

**To read rather than archive**: stitch a window the size of the viewport, replace
`document.body` with the canvas, and screenshot. That renders the register at
**1:1 of 5,768 pixels** — about six times the resolution of the 960-pixel copies
this archive has been squinting at.

## Finding the ARK for an image

Each image in a film has its own ARK. Two ways to get one:

1. Drive the viewer's **image-number box** (not the URL) and read the ARK back out
   of the tile `src` of the displayed image.
2. The filmstrip puts **every ARK in the film** into the DOM at once — about 160
   of them for the Senj marriages — though unordered, so it does not tell you
   which image number each belongs to.

## What is still to do

The technique is proven; the remaining work is **navigation**. The three documents
this archive holds at 960 pixels are all in *Croatia, Church Books — Senj —
Marriages 1859-1920*, 376 images:

| Wanted | Where |
|---|---|
| Senj marriages **p.192 no.5**, 3 May 1885 | Josip Papić × Antonija Prpić |
| Senj marriages **p.294 no.30**, 4 Nov 1907 | **Zvonimir Vukelić × Milka Papić** — answers the 1915 question too |
| Senj marriages, **8 December 1920** | Ljubomir Blažević × Milka Papić |

Image **374** is page 350 and holds late 1918, which brackets the 1920 entry
within the last two or three images of the film.

---

## Navigation — added 13 September 2026, after using it on three entries

The method above gets **an** image. Finding the **right** one is a separate
problem, and the note above solves it badly: it says to type into the viewer's
image-number box. That works, but it is slow, it needs a screenshot per probe,
and it turns out to be unnecessary.

**The whole film is already in the DOM.** Every filmstrip thumbnail carries the
image number in its `alt` and the ARK in its `src`:

```html
<img alt="Image 221"
     src=".../deepzoomcloud/dz/v1/3:1:3QS7-899X-17ZY/thumb_p200.jpg">
```

So scrape a number→ARK map and then fetch tiles for any image directly, with no
viewer navigation at all:

```js
window.__map = window.__map || {};
window.__scan = () => {
  let n = 0;
  for (const e of document.querySelectorAll("img")) {
    const m = (e.src || "").match(/dz\/v1\/([^/]+)\//);
    const a = (e.alt || "").match(/Image (\d+)/);
    if (m && a && !__map[a[1]]) { __map[a[1]] = m[1]; n++; }
  }
  return n;
};
```

One load gives roughly 150 thumbnails around the current image. Typing a low and
a high image number into the box and re-scanning covers the rest — three scans
mapped 316 of 376 images, and the missing 60 were never needed.

### Do not trust a page-to-image guess

The Senj marriage film runs about **page = image − 5**, but that was *measured*,
not assumed, and an earlier guess in this archive ("image 374 is page 350") was
wrong by more than 150 pages. Fix it from real points before searching:

    image 196 = page 192      image 299 = page 294
    image 280 = page 275      image 371 = page 366
    image 372 = END OF ITEM

### Reading cheaply

Screenshots are the expensive part, not the tiles. Two things help a lot:

* **Probe several images in one picture.** Crop the same small region — the date
  column, or the top corner where the page number sits — from four or six images
  and tile them into one labelled canvas. A six-way search finds one page in a
  376-image film in about three screenshots.
* **Use fractional crops, not pixel crops.** Image sizes vary across a film
  (5,812 × 4,273 here, 5,768 × 4,198 elsewhere) and the paper sits differently in
  each frame, so a pixel box that worked on one image lands on the film border of
  the next. Fetch `image.xml` per ARK and crop by fraction of width and height.

### And then slow down

The archive's standing rule applies with full force at this point: **no date, no
surname and no house number gets recorded from a whole-page view.** Having a
5,812-pixel scan is not the same as having read it. On this very film I read a
groom's birth month as `1/VIII` from a page-scale view; enlarged 2.7× on the cell
alone it is `1/III` — three strokes under one overline. Crop the single cell,
enlarge, and only then write it down.
