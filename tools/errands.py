#!/usr/bin/env python3
"""The errands page's data: every letter this archive has written, in full.

WHY. A letter that lives only in requests/ is a draft nobody will find; a draft
nobody finds is a question nobody asks. The errands page is where a draft is
published as a draft, in full, so that whoever is going to send it can do so
without re-reading the whole site, and so that the state of every letter -
drafted, sent, answered - is one glance and not a reading exercise.

The TEXT is read from requests/ and never retyped here, so the page cannot drift
from the file. The STATE is written below because it is a fact about the world
(was it sent? did anyone answer?) that no file header reliably carries: three
files in requests/sent/ say DRAFT - NOT SENT in their own first line, and that
header is what is believed here, not the folder they sit in.

A letter file in requests/ that is not listed below is REPORTED, so a new draft
cannot be written and left off the page.

Nothing here sends anything. Sending a letter is David's decision, always.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = os.path.join(ROOT, "requests")
OUT = os.path.join(ROOT, "site", "src", "data", "errands.json")

STATES = {
    "draft":    ["Drafted, not sent", "#B04A16", "written and kept here; nothing has gone out"],
    "sent":     ["Sent, waiting", "#7A5C00", "sent; no answer yet, or only an acknowledgement"],
    "answered": ["Answered", "#12703F", "sent and answered - kept because the answer is the finding"],
}

# file, state, who, what it asks, what it would settle, link
ROWS = [
    ("EMAIL-zupa-otocac.txt", "draft",
     "Župni ured Otočac (address to confirm from the diocese's directory)",
     "Ana Marić's baptism (about 1830-1836) and her marriage to Nikola Žubrinić (about 1850-1852)",
     "Ahnentafel 11 is the emptiest person on the direct line: a name, two tree links and nothing else. Her baptism would name ahnentafel 22 and 23 and the house; the marriage would name both sets of parents. The filmed baptisms begin in September 1834 and the filmed marriages in 1859, so neither is on any film this archive can read.",
     "/worklist/"),
    ("EMAIL-zupa-karlobag.txt", "draft",
     "Župni ured Karlobag (address to confirm from the diocese's directory)",
     "Catherina «Catta» Luckinić's baptism (the tree says 30 March 1727), and a Luckinić household of the 1720s",
     "Ahnentafel 105 has a death entry and no birth. The baptism book for 1727 was read and carries no Luckinić on the tree's date, and the book's own index lists none. A parish can say whether leaves are missing or another volume holds her.",
     "/worklist/"),
    ("EMAIL-nadbiskupija.txt", "draft",
     "Ured Riječke nadbiskupije (address to confirm)",
     "Where the registers of Sv. Jakov Krmpote went when the parish priest handed them over",
     "The Krmpote priest said the registers and archive of the parishes he administers were handed to the Rijeka archdiocese. The film of the baptisms begins in 1879 and no marriage register is filmed, so Juraj Blažević's baptism and marriage can only be there.",
     "/worklist/"),
    ("EMAIL-kustodija-zadar.txt", "draft",
     "Franjevačka kustodija sv. Jeronima, Zadar",
     "Oskar Kosina's burial, Buenos Aires, 15 January 1954",
     "The Zadar Franciscans ran the Croatian pastoral care in Argentina from 1929, so the 1954 funeral is in their custody's own papers and not in the later centre's books.",
     "/kosina/"),
    ("EMAIL-hkm-ludwigshafen.txt", "draft",
     "Hrvatska katolička misija bl. Alojzija Stepinca, Ludwigshafen",
     "A photograph of vlč. Anton Kosina (1921-2003) the family may publish, and what the mission holds of him",
     "He founded the mission; its own papers are the best record of him, and the published press gives only 1958-1985.",
     "/kosina/"),
    ("EMAIL-cemla-philippa.txt", "draft",
     "CEMLA, Buenos Aires",
     "The whole page of the landing book for the steamer PHILIPPA, 9 October 1947",
     "Oskar Kosina landed married and no Kosina woman is in the free index under either spelling. The bound page lists everyone who sailed with him; it settles whether she is on it under a maiden name.",
     "/kosina/"),
    ("EMAIL-gospic.txt", "sent",
     "Državni arhiv u Gospiću - zahtjevi@arhiv-gospic.hr",
     "The Kalanj × Perković marriage at Brinje; Otočac baptisms for Prozor 1875-1895; whether one man or two",
     "Sent 13 September 2026; acknowledged 14 September by Marija Fajdić and queued. Nothing since.",
     "/worklist/"),
    ("EMAIL-zupa-senj.txt", "sent",
     "Župni ured Senj",
     "Three Senj deaths (Milka Papić 1971, Zvonimir Vukelić 1915, Tereza Žubrinić 1931) and the two Papić baptisms of January and February 1895",
     "The filmed Senj baptisms stop at 1894 and the deaths at 1907, so all of these fall after the films. Sent 15 September 2026 on the Senj archive's instruction. Nothing back yet.",
     "/worklist/"),
    ("EMAIL-senj.txt", "answered",
     "Državni arhiv u Rijeci, Ispostava u Senju - senj@riarhiv.hr",
     "Juraj Blažević's baptism or marriage; Zvonimir Vukelić's 1915 death; the Butorac household",
     "Sent 13 September; answered 14 September by Denis Rukavina: the Senj collection centre does not hold this material, and he named three other doors (Rijeka, Gospić and the parish offices).",
     "/worklist/"),
    ("EMAIL-rijeka.txt", "answered",
     "Državni arhiv u Rijeci",
     "Ljubomir Blažević's 1892 Rijeka baptism, three Senj deaths after 1907, Krmpote before the film begins in 1879",
     "Sent 15 September; answered the same day by Boris Zakošek, and the answer is a refusal. Kept because a refusal is a result.",
     "/worklist/"),
    ("EMAIL-zupa-krmpote.txt", "answered",
     "Župni ured Sv. Jakov Krmpote (administered from Ledenice)",
     "Juraj Blažević's baptism, marriage and death; the Butorac household; a status animarum",
     "Sent 15 September; answered: the registers left the parish (handed to the Rijeka archdiocese), which is what the draft to the archdiocese follows up.",
     "/worklist/"),
]


def esc(s):
    return html.escape(s, quote=False).replace("\n", "<br>\n")


def body(path):
    t = open(path, encoding="utf-8").read().rstrip()
    # a leading banner of *** lines is a state note; the state is carried above
    return re.sub(r"\A(?:\*\*\*.*\n)+\n?", "", t)


def main():
    rows = []
    for i, (fn, state, who, what, settles, href) in enumerate(ROWS, 1):
        sent_path = os.path.join(REQ, "sent", fn)
        in_sent = os.path.exists(sent_path)
        path = sent_path if in_sent else os.path.join(REQ, fn)
        rows.append({
            "n": i, "state": state, "where": who, "what": what, "settles": settles,
            "file": "requests/" + ("sent/" if in_sent else "") + fn,
            "draft": esc(body(path)), "href": href,
        })
    known = set(os.listdir(REQ)) | set(os.listdir(os.path.join(REQ, "sent")))
    listed = {r[0] for r in ROWS}
    unlisted = sorted(f for f in known if f.startswith("EMAIL-") and f not in listed)
    out = {
        "title": "Errands",
        "dek": "Every letter this archive has written, in full - drafted, sent and answered - so that a draft is a page somebody can act from and not a file nobody opens.",
        "lead": "A reading that cannot be done from the films ends at a person: a parish priest, an archivist, a custodian. These are the letters to them. Each says who is being asked, what for, and what the answer would settle, and carries the text. Nothing on this page has been sent by the site; sending is a person's decision, and the state shown is the state of the letter.",
        "states": STATES,
        "tallyNote": "A negative or a refused request is kept as a result, here and on [the search register](/searched/).",
        "close": "Where a letter has been answered, the answer is on the work list and the search register. A draft's address is marked to be confirmed where this archive has not verified it; nothing here invents a street or an inbox.",
        "unlisted": unlisted,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"errands: {len(rows)} letters ({sum(r['state'] == 'draft' for r in rows)} drafted, "
          f"{sum(r['state'] == 'sent' for r in rows)} sent, {sum(r['state'] == 'answered' for r in rows)} answered)"
          + (f"; NOT LISTED: {', '.join(unlisted)}" if unlisted else ""))
    return 1 if unlisted else 0


if __name__ == "__main__":
    raise SystemExit(main())
