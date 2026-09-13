/* FamilySearch film reader — paste whole into the viewer's console (or via a
   javascript_tool call) on any www.familysearch.org image page.

   Why this exists: the viewer will not give you a full-resolution image, and
   the archive lost a day to two wrong theories about why. It is all solvable:
   tiles are served SAME-ORIGIN from www.familysearch.org, so no CORS, no
   tainted canvas, cookies sent automatically.

   Usage, in order:
     __scan()                        after opening the thumbnail grid, then
                                     scroll the grid and call it again until
                                     Object.keys(__map).length === film length
     await __grid([10,20], 0,0,1,1, 430, 2, 3)   survey: whole frames, level-3 drop
     await __grid([196], 0.06,0.40,0.33,0.66, 790, 1)   read: one cell, full res
     __show()  /  __hide()           paint the canvas over the page, screenshot it

   Crops are FRACTIONS of width/height, never pixels: image sizes vary across a
   film (5812x4273 here, 5768x4198 there) and the paper sits differently in each
   frame, so a pixel box that works on one lands on the film border of the next.
*/

// number -> ARK, scraped from the thumbnail grid's alt attributes.
window.__map = window.__map || {};
window.__scan = () => {
  let n = 0;
  for (const e of document.querySelectorAll("img")) {
    const m = (e.src || "").match(/dz\/v1\/([^/]+)\//);
    const a = (e.alt || "").match(/Image (\d+)/);
    if (m && a && !window.__map[a[1]]) { window.__map[a[1]] = m[1]; n++; }
  }
  return n;
};

window.__dimCache = {};
window.__getDims = async (ark) => {
  if (window.__dimCache[ark]) return window.__dimCache[ark];
  const t = await (await fetch(
    `/service/records/storage/deepzoomcloud/dz/v1/${ark}/image.xml`)).text();
  const W = +t.match(/Width="(\d+)"/)[1], H = +t.match(/Height="(\d+)"/)[1];
  return (window.__dimCache[ark] = { W, H, level: Math.ceil(Math.log2(Math.max(W, H))) });
};

// drop: subtract N zoom levels. A full frame at level 13 is ~400 tiles and will
// time out; at level 10 it is 9. Survey with drop 3, read with drop 0.
window.__cell = async function (ark, fx0, fy0, fx1, fy1, drop) {
  drop = drop || 0;
  const d = await window.__getDims(ark);
  const level = d.level - drop, s = Math.pow(2, drop);
  const W = Math.ceil(d.W / s), H = Math.ceil(d.H / s);
  const x0 = Math.round(fx0 * W), y0 = Math.round(fy0 * H);
  const w = Math.round((fx1 - fx0) * W), h = Math.round((fy1 - fy0) * H);
  const T = 256, OV = 1;
  const t = document.createElement("canvas"); t.width = w; t.height = h;
  const g = t.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, w, h);
  const c0 = Math.floor(x0 / T), c1 = Math.floor((x0 + w) / T);
  const r0 = Math.floor(y0 / T), r1 = Math.floor((y0 + h) / T);
  const jobs = [];
  for (let col = c0; col <= c1; col++) for (let row = r0; row <= r1; row++) {
    jobs.push(new Promise((res) => {
      const im = new Image(); let done = false;
      const fin = () => { if (!done) { done = true; res(); } };
      // a hidden Browser pane throttles the tab; without this a stalled tile
      // hangs the whole call until the tool times out
      const tm = setTimeout(fin, 12000);
      im.onload = () => {
        try { g.drawImage(im, col * T - (col > 0 ? OV : 0) - x0,
                              row * T - (row > 0 ? OV : 0) - y0); } catch (e) {}
        clearTimeout(tm); fin();
      };
      im.onerror = () => { clearTimeout(tm); fin(); };
      im.src = `/service/records/storage/deepzoomcloud/dz/v1/${ark}/image_files/${level}/${col}_${row}.jpg`;
    }));
  }
  await Promise.all(jobs);
  return t;
};

// contact sheet: several images, same crop, tiled and labelled. A six-way
// search finds one page in a 376-image film in about three screenshots.
window.__grid = async function (nums, fx0, fy0, fx1, fy1, cellW, cols, drop) {
  const cells = [];
  for (const n of nums) {
    const ark = window.__map[n];
    cells.push(ark ? await window.__cell(ark, fx0, fy0, fx1, fy1, drop) : null);
  }
  const first = cells.find(Boolean);
  if (!first) return { err: "no cells — is __map populated?" };
  const cellH = Math.round(cellW * first.height / first.width);
  const rows = Math.ceil(nums.length / cols);
  const c = document.createElement("canvas");
  c.width = cellW * cols; c.height = cellH * rows;
  const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height);
  cells.forEach((t, i) => {
    const cx = (i % cols) * cellW, cy = Math.floor(i / cols) * cellH;
    if (t) g.drawImage(t, 0, 0, t.width, t.height, cx, cy, cellW, cellH);
    g.strokeStyle = "#c00"; g.strokeRect(cx, cy, cellW, cellH);
    g.fillStyle = "#c00"; g.font = "bold 20px monospace";
    g.fillText("#" + nums[i], cx + 5, cy + 22);
  });
  window.__canvas = c;
  return { w: c.width, h: c.height };
};

// a tall narrow margin strip rotated 90° — for village names written sideways
// down the gutter of a status animarum
window.__pagus = async function (nums, fx0, fy0, fx1, fy1, outW, drop) {
  const strips = [];
  for (const n of nums) {
    const ark = window.__map[n];
    strips.push(ark ? await window.__cell(ark, fx0, fy0, fx1, fy1, drop) : null);
  }
  const first = strips.find(Boolean); if (!first) return { err: "none" };
  const rw = first.height, rh = first.width;
  const sc = outW / rw, cellH = Math.round(rh * sc);
  const c = document.createElement("canvas");
  c.width = outW; c.height = cellH * nums.length;
  const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height);
  strips.forEach((t, i) => {
    if (t) {
      g.save(); g.translate(0, i * cellH); g.scale(sc, sc);
      g.translate(0, rh); g.rotate(-Math.PI / 2); g.drawImage(t, 0, 0); g.restore();
    }
    g.strokeStyle = "#c00"; g.strokeRect(0, i * cellH, outW, cellH);
    g.fillStyle = "#c00"; g.font = "bold 20px monospace";
    g.fillText("#" + nums[i], 6, i * cellH + 22);
  });
  window.__canvas = c; return { w: c.width, h: c.height };
};

window.__show = () => {
  const o = document.createElement("div"); o.id = "ovl";
  o.style.cssText = "position:fixed;inset:0;background:#fff;z-index:2147483647;overflow:hidden";
  o.appendChild(window.__canvas); document.body.appendChild(o); return "ok";
};
window.__hide = () => { const o = document.getElementById("ovl"); if (o) o.remove(); return "hidden"; };

"fs_reader loaded";
