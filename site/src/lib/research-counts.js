/* One sentence for each Research page: what it asks, and a number the archive can state from its own data. Counted at build time, so
   it cannot go stale. Numbers only; no name of anybody. 12 November 2026 (the research-menu trial, wave 3). A page with no count
   here has none that its own page does not already print in its heading. */
import questions from "../data/questions.json";
import errands from "../data/errands.json";
import worklist from "../data/worklist.json";
import searched from "../data/searched.json";
import corrections from "../data/corrections.json";
import recent from "../data/recent.json";
import targets from "../data/targets.json";
import readings from "../data/readings.json";
import snapshots from "../data/snapshots.json";
import indexed from "../data/indexed.json";
import graves from "../data/graves.json";
import found from "../data/found.json";
import { RESEARCH } from "./research-menu.js";

const rows = (x) => (Array.isArray(x) ? x : x.rows || []);
const nf = (n) => n.toLocaleString("en-GB");
const wl = rows(worklist);
const open = wl.filter((r) => r.state === "next" || r.state === "running").length;
const COUNT = {
  "/open-questions/": `${nf(rows(questions).length)} questions`,
  "/errands/": `${nf(rows(errands).length)} errands`,
  "/worklist/": `${nf(open)} still open, ${nf(wl.filter((r) => r.state === "done").length)} done`,
  "/harvest/": `${nf(targets.totalReachable)} events inside a film this archive can reach`,
  "/searched/": `${nf(rows(searched).length)} searches`,
  "/corrections/": `${nf(rows(corrections).length)} claims taken back`,
  "/changes/": `${nf((recent.entries || []).length)} entries`,
  "/readings/": `${nf(readings.counts.rows)} documents read`,
  "/snapshots/": `${nf(snapshots.count)} pages kept`,
  "/indexed/": `${nf(indexed.counts.indexed)} of ${nf(indexed.counts.parishes)} parishes searchable as text`,
  "/stones/": `${nf(graves.stones.n)} names read off stones`,
  "/found/": `${nf(found.count)} people kept beside the tree`,
};
const ASKS = Object.fromEntries(RESEARCH.flatMap((g) => g.items.flatMap((x) => x.sub ? x.items : [x])).filter((x) => x.asks).map((x) => [x.href, x.asks]));

export const blurbOf = (x) => {
  const asks = ASKS[x.href] || "";
  const n = COUNT[x.href];
  return [asks, n ? `<em>${n}.</em>` : ""].filter(Boolean).join(" ");
};
