/* Stitch a window of a FamilySearch Deep Zoom image at full resolution.
 *
 * Paste into the console of a signed-in FamilySearch image-viewer page.
 * The crucial detail is the HOST: the viewer's own tiles come from
 * sg30p0.familysearch.org, which is cross-origin — CORS fails and the canvas
 * taints. The SAME tiles are served from www.familysearch.org, which is
 * same-origin with the viewer, so neither happens.
 *
 *   const r = await fetchWindow("3:1:3QSQ-G99X-1QBW", 13, 300, 600, 800, 820);
 *   document.body.innerHTML = ""; document.body.appendChild(r.canvas);
 *
 * Level 13 is full size for a 5768-pixel image: level = ceil(log2(max(W,H))).
 * Get W and H from image.xml first.
 */
async function dziSize(ark) {
  const r = await fetch(
    `/service/records/storage/deepzoomcloud/dz/v1/${ark}/image.xml`,
    { credentials: "include" });
  const x = await r.text();
  const m = x.match(/Width="(\d+)"\s+Height="(\d+)"/);
  const t = x.match(/TileSize="(\d+)"/);
  return { w: +m[1], h: +m[2], tile: +t[1],
           level: Math.ceil(Math.log2(Math.max(+m[1], +m[2]))) };
}

async function fetchWindow(ark, level, x0, y0, w, h) {
  const T = 256, OV = 1;
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  const c0 = Math.floor(x0 / T), c1 = Math.floor((x0 + w - 1) / T);
  const r0 = Math.floor(y0 / T), r1 = Math.floor((y0 + h - 1) / T);
  const jobs = [];
  for (let col = c0; col <= c1; col++)
    for (let row = r0; row <= r1; row++)
      jobs.push(new Promise((res) => {
        const im = new Image();
        im.onload = () => {
          // overlap means every tile after the first starts one pixel early
          g.drawImage(im, col * T - (col > 0 ? OV : 0) - x0,
                          row * T - (row > 0 ? OV : 0) - y0);
          res(1);
        };
        im.onerror = () => res(0);
        im.src = `/service/records/storage/deepzoomcloud/dz/v1/${ark}` +
                 `/image_files/${level}/${col}_${row}.jpg`;
      }));
  const loaded = (await Promise.all(jobs)).reduce((a, b) => a + b, 0);
  return { canvas: c, tiles: jobs.length, loaded };
}
