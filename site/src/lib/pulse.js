/* What is new here, and the archive in numbers: the kit computes it at build time from this archive's own logs (kit/docs/whats-new.md).
   This file is the only Blažević-specific part: which JSON is which, and the one count no log holds.
   corrections.json carries no date, so the corrections give a count but no cards; searched.json is {rows:[...]} with `when`/`outcome`,
   which the kit reads as it stands. */
import { buildPulse } from "@daviddef/archive-kit/lib/pulse.js";
import { loadReceipts } from "@daviddef/archive-kit/lib/receipts.js";
import searched from "../data/searched.json";
import corrections from "../data/corrections.json";
import worklist from "../data/worklist.json";
import people from "../data/people.json";

export const pulse = buildPulse({
  searched, corrections, worklist,
  counts: { people: people.length },
  /* the Atlas state of each search row (kit/docs/whats-new-receipts.md): null when the Atlas cannot be reached, never an error */
  receipts: await loadReceipts("blazevic"),
});
