/* LINKS TO THE REPOSITORY ARE NOT DRAWN (23 November 2026, David: "github links, no"). The data files keep the address of the working note that
   went with a reading, a snapshot or a finding (notes/….md in the repository, drawn as github.com/…/blob/main/…); that history is not edited.
   A component that draws such an address asks `isRepoUrl` and, when it is one, prints the words without the link. */
export const isRepoUrl = (h) => /^https?:\/\/(www\.)?(github\.com|raw\.githubusercontent\.com)\//i.test(h || "");
/* the address to link, or null when there is none or it is the repository's */
export const publicHref = (h) => (h && !isRepoUrl(h) ? h : null);
