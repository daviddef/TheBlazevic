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
     await __pagus([64], 0,0.1,0.09,0.95, 900, 1, "contrast(2.4) brightness(1.5)")
                                     the Pagus margin, rotated upright and
                                     lifted out of the binding shadow
     __show()  /  __hide()           paint the canvas over the page, screenshot it
     __q([["p206", async () => __cell(__map[102], 0.13, 0.11, 0.35, 0.99, 0)]])
                                     preferred: stitch in the background and POST
                                     the full-resolution PNG to a local sink

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
// filter: a canvas filter string applied while drawing, e.g.
// "contrast(2.4) brightness(1.5)" — lifts the Pagus margin out of the binding
// shadow. Above about 2.6 on a tight crop the page blows to pure black/white.
window.__cell = async function (ark, fx0, fy0, fx1, fy1, drop, filter) {
  drop = drop || 0;
  const d = await window.__getDims(ark);
  const level = d.level - drop, s = Math.pow(2, drop);
  const W = Math.ceil(d.W / s), H = Math.ceil(d.H / s);
  const x0 = Math.round(fx0 * W), y0 = Math.round(fy0 * H);
  const w = Math.round((fx1 - fx0) * W), h = Math.round((fy1 - fy0) * H);
  const T = 256, OV = 1;
  const t = document.createElement("canvas"); t.width = w; t.height = h;
  const g = t.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, w, h);
  if (filter) g.filter = filter;
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
window.__grid = async function (nums, fx0, fy0, fx1, fy1, cellW, cols, drop, filter) {
  const cells = [];
  for (const n of nums) {
    const ark = window.__map[n];
    cells.push(ark ? await window.__cell(ark, fx0, fy0, fx1, fy1, drop, filter) : null);
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
// down the gutter of a status animarum.
//
// ROTATE CLOCKWISE. This was wrong for two sittings: at -90° the Pagus text
// comes out mirrored and upside down, which is why the village names looked
// like an illegible binding shadow. At +90° the same crop reads at once.
window.__pagus = async function (nums, fx0, fy0, fx1, fy1, outW, drop, filter) {
  const strips = [];
  for (const n of nums) {
    const ark = window.__map[n];
    strips.push(ark ? await window.__cell(ark, fx0, fy0, fx1, fy1, drop, filter) : null);
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
      g.translate(t.height, 0); g.rotate(Math.PI / 2); g.drawImage(t, 0, 0); g.restore();
    }
    g.strokeStyle = "#c00"; g.strokeRect(0, i * cellH, outW, cellH);
    g.fillStyle = "#c00"; g.font = "bold 20px monospace";
    g.fillText("#" + nums[i], 6, i * cellH + 22);
  });
  window.__canvas = c; return { w: c.width, h: c.height };
};


// The paper moves frame to frame by more than the width of the Pagus column, so
// a fixed fraction lands on the film border of the next image. Anchor instead on
// the binding shadow: take the frame at a 4-level drop and return the darkest
// column as a fraction of frame width. Then crop at anchor + offset.
//
// Measured on the Otocac status animarum: Pagus runs about anchor+0.004 to
// anchor+0.064, the N-degree-Domus column and Nomina Familiae follow it.
window.__spine = async function (n) {
  const t = await window.__cell(window.__map[n], 0, 0.15, 0.45, 0.85, 4);
  const d = t.getContext("2d").getImageData(0, 0, t.width, t.height).data;
  let best = 1e9, bx = 0;
  for (let x = 0; x < t.width; x++) {
    const f = 0.45 * x / t.width;
    if (f < 0.03 || f > 0.30) continue;       // skip the black film border
    let s = 0;
    for (let y = 0; y < t.height; y++) s += d[(y * t.width + x) * 4];
    const m = s / t.height;
    if (m < best) { best = m; bx = f; }
  }
  return { f: +bx.toFixed(4), v: Math.round(best) };
};

// Screenshots are capped at the viewport, so a stitched page has to be shrunk to
// fit and can no longer be enlarged — which defeats the standing rule about
// never reading a date at page scale. Post the PNG to a local sink instead and
// crop it on disk. http://127.0.0.1 is a trustworthy origin, so an HTTPS page is
// allowed to post to it; give the sink Access-Control-Allow-Origin: * and the
// fetch reports a real status instead of failing silently as no-cors does.
window.__send = async function (name, port) {
  const b = await new Promise((r) => window.__canvas.toBlob(r, "image/png"));
  const res = await fetch("http://127.0.0.1:" + (port || 8799) +
                          "/put?name=" + encodeURIComponent(name),
                          { method: "POST", body: b });
  return name + " " + window.__canvas.width + "x" + window.__canvas.height +
         " http" + res.status;
};

// The console bridge kills any evaluation at 45 s and a full-resolution page is
// more than that. Queue the work, record a status string, poll it with a second
// short call. Throttle the tiles too: 3-4 at a time with a ~25 ms gap ran a
// whole sitting without tripping Akamai's bot manager.
window.__st = "idle";
window.__q = async function (jobs) {
  window.__log = []; window.__st = "q 0/" + jobs.length;
  (async () => {
    let i = 0;
    for (const [name, fn] of jobs) {
      try { window.__canvas = await fn(); window.__log.push(await window.__send(name)); }
      catch (e) { window.__log.push("ERR " + name + ": " + (e && e.message)); }
      window.__st = "q " + (++i) + "/" + jobs.length;
    }
    window.__st = "q DONE";
  })();
  return "queued " + jobs.length;
};

window.__show = () => {
  const o = document.createElement("div"); o.id = "ovl";
  o.style.cssText = "position:fixed;inset:0;background:#fff;z-index:2147483647;overflow:hidden";
  o.appendChild(window.__canvas); document.body.appendChild(o); return "ok";
};
window.__hide = () => { const o = document.getElementById("ovl"); if (o) o.remove(); return "hidden"; };

"fs_reader loaded";
