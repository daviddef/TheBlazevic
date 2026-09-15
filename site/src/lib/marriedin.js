/* The nineteen families, grouped by the generation at which each enters the
   descent — the same ahnentafel reading /marriages/ uses. */
import fams from "../data/marriedin.json";
const gen = (ahn) => Math.floor(Math.log2(Math.max(1, ahn))) + 1;
const LABEL = { 2:"Hedviga's parents", 3:"Her grandparents", 4:"Her great-grandparents",
  5:"Her great-great-grandparents", 6:"Five generations back", 7:"Six generations back",
  8:"Seven generations back" };
const entered = (f) => Math.min(...f.ancestors.map((a) => gen(a.ahn)));
const gens = [...new Set(fams.map(entered))].sort((a, b) => a - b);
export const chartGroups = gens.map((g) => ({
  key: "g" + g, label: LABEL[g] || `${g - 1} generations back`,
  families: fams.filter((f) => entered(f) === g)
    .map((f) => ({ surname: f.label, n: f.ancestors.length })),
}));
