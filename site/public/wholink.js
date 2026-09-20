/* Turn a known person's name in the page text into a link to their page.
   Runs after render, touches text nodes only, never re-links inside an anchor,
   and prefers the longest match so "Josip Anton Papić" beats "Josip Papić".

   ACCENTS ARE FOLDED ON BOTH SIDES, and until 21 September 2026 they were not.
   The index is built from the TREE's spelling and the prose uses the ARCHIVE's:
   the tree holds ahnentafel 4 as "Blazevic" and every page writes "Blazevic"
   with the carons. The matcher was case-insensitive and not accent-insensitive,
   so z and z-with-caron were two letters and the commonest name in this archive
   never linked once. A reader noticed it on a page full of names and no links.

   The fold is LENGTH-PRESERVING, one character in and one character out, so a
   match found in the folded text can be sliced straight out of the original —
   which is how the link keeps its accents while the matching ignores them.
   It is the same rule namefold.py applies to the register search, where folding
   an accent "needs nobody's permission" because it is one word two keyboards
   wrote differently.

   Only names held by EXACTLY ONE published person are in the index. This
   archive has eighteen men called Ivan Blažević; linking one of them would be
   the merge-on-a-name error the rest of the site exists to document. Ambiguous
   names stay plain text and /people does the disambiguation. See
   tools/whoindex.py. */
(function () {
  var BASE = (document.documentElement.getAttribute("data-base") || "").replace(/\/+$/, "");

  /* Letters that do not decompose under NFD and so survive the strip below:
     the Croatian d-bar above all, which is why Dordic and Dordic were two
     names to this matcher. */
  var HARD = { "\u0111": "d", "\u0110": "D", "\u00f0": "d", "\u00d0": "D",
               "\u0142": "l", "\u0141": "L", "\u00f8": "o", "\u00d8": "O",
               "\u00df": "s", "\u00e6": "a", "\u00c6": "A" };

  /* ONE CHARACTER IN, ONE CHARACTER OUT. String.normalize("NFD") turns one
     accented letter into a base plus a combining mark, so stripping the marks
     SHORTENS the string and every index after the first accent would be wrong.
     Folding per character keeps the offsets, which is the whole point: the
     match is found in folded text and sliced out of the original. */
  function fold(s) {
    var out = "";
    for (var i = 0; i < s.length; i++) {
      var ch = s[i];
      if (HARD[ch]) { out += HARD[ch]; continue; }
      var d = ch.normalize ? ch.normalize("NFD").replace(/[\u0300-\u036f]/g, "") : ch;
      out += d.length ? d[0] : ch;
    }
    return out;
  }
  fetch(BASE + "/whoindex.json").then(function (r) { return r.json(); }).then(function (idx) {
    if (!idx || !idx.length) return;
    var here = location.pathname.replace(/\/$/, "");
    var map = Object.create(null);
    var parts = [];
    for (var i = 0; i < idx.length; i++) {
      var n = idx[i][0];
      if (here.endsWith("/people/" + idx[i][1])) continue;   // don't self-link
      var f = fold(n);
      map[f.toLowerCase()] = idx[i];
      parts.push(f.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    }
    if (!parts.length) return;
    var L = "A-Za-z\\u00C0-\\u024F";     // letters incl. accents = mid-word
    var re;
    try {
      re = new RegExp("(?<![" + L + "])(" + parts.join("|") + ")(?![" + L + "])", "gi");
    } catch (e) { return; }             // no lookbehind on this browser: do nothing

    var main = document.querySelector("main") || document.body;
    var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || node.nodeValue.length < 7) return NodeFilter.FILTER_REJECT;
        var p = node.parentElement;
        while (p && p !== main) {
          var t = p.tagName;
          /* Never touch anything inside an SVG: an HTML <a> injected into an
             SVG <text> is not laid out by the SVG renderer, so the label
             measures zero and silently disappears from the chart. SVG tag
             names are lower-case, so the checks below never catch it. */
          if (p.ownerSVGElement || t === "svg" || t === "SVG") return NodeFilter.FILTER_REJECT;
          if (t === "A" || t === "CODE" || t === "PRE" || t === "SCRIPT" || t === "STYLE" ||
              t === "H1" || t === "TITLE" ||
              p.classList.contains("noauto") ||
              p.classList.contains("ptree")) return NodeFilter.FILTER_REJECT;
          p = p.parentElement;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);

    var seen = Object.create(null);
    for (var j = 0; j < nodes.length; j++) {
      var node = nodes[j], text = node.nodeValue, linked = 0;
      /* Match on the folded copy, slice from the original. Same length, so the
         offsets are interchangeable and the link text keeps its accents. */
      var hay = fold(text);
      re.lastIndex = 0;
      if (!re.test(hay)) continue;
      re.lastIndex = 0;
      var frag = document.createDocumentFragment(), last = 0, m;
      while ((m = re.exec(hay))) {
        var row = map[m[1].toLowerCase()];
        if (!row) continue;
        seen[row[1]] = (seen[row[1]] || 0) + 1;
        if (seen[row[1]] > 3) continue;          // first three mentions per page
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var a = document.createElement("a");
        a.href = BASE + "/people/" + row[1] + "/";
        a.className = "wholink";
        a.title = row[0] + " — their page in this archive";
        a.textContent = text.slice(m.index, m.index + m[1].length);
        frag.appendChild(a);
        last = m.index + m[1].length;
        linked++;
      }
      if (!linked) continue;
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
      if (frag.childNodes.length) node.parentNode.replaceChild(frag, node);
    }
  }).catch(function () {});
})();
