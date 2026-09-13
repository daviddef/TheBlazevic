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
