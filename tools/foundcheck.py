#!/usr/bin/env python3
"""Is anybody in sources/found.psv actually in the tree after all?

found.psv means one thing: «read out of a register, and NOT in the family
tree». That claim has been made wrongly twice.

  · 15 September 2026, the Karlobag wives. A check concluded none of six was
    in the tree. All six were there — as PARENT REFERENCES on their children,
    with no page of their own. Searching the published people is not searching
    the tree.

  · the same day, IVAN DEFRANČESKI. His gravestone was photographed at Senj
    and recorded here as «the surname does not occur once in this tree». It
    occurs on Hedviga Blažević's own marriage: he is her husband, born 1925,
    died 1995, and his slug is null because he is not published. The archive
    had just failed to recognise the grave of the man at the centre of it.

So this looks everywhere a name can hide — published people AND every name in
every rel.parents, rel.spouses, rel.siblings and rel.children list — and tests
each found person two ways:

    name + year      the given name matches and the years are within one
    name + parents   the given name matches and BOTH parents named in the
                     relation text match that candidate's parents

A hit is not proof. It is a person this archive said was not in the tree who
looks very much like somebody in it, and the row needs a human decision. The
check prints them and exits non-zero so a build cannot carry the claim
silently.

Run: python3 tools/foundcheck.py [--quiet]
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
FOUND = os.path.join(ROOT, "sources", "found.psv")

# Rows that have been looked at by a person and settled. A found.psv row is
# listed here with the reason it is NOT the tree person it resembles.
SETTLED = {
    # A SETTLE CAN GO STALE, and one did on 21 September 2026. «Maria Rosaria
    # Antic» was settled on the grounds that «ahnentafel 24 has no children
    # published at all, so there is nothing to match her against» — which was
    # true when it was written and stopped being true the moment this archive
    # began publishing blood rather than surnames. She IS his published
    # daughter. The entry is gone and she is a reading. A settle that names the
    # STATE OF THE ARCHIVE rather than a fact about the people has a shelf life.
    # The four below arrived on 21 September with the Kosina research. Every one
    # resembles somebody only in a GIVEN NAME and a year; not one shares a
    # surname or a parent, which is the test this file applies everywhere else.
    # 22 September 2026, AND THIS ONE IS THE FILE'S OWN WARNING COMING TRUE.
    # Petrus Uroda had no candidate at all until publication gained a parents
    # closure that afternoon and 443 people arrived at once, one of them a
    # Petrus born a year from his. A settle that depends on WHO IS PUBLISHED has
    # a shelf life; this one depends on the men, so it does not.
    "Petrus Jacobus Uroda":
        "baptised at Karlobag on 2 July 1767 and BURIED THERE ON 7 NOVEMBER of "
        "the same year, an infant of four months — the death index says so. "
        "Petrus Defranceschi of 1768 is a different surname, a different family "
        "and a man who lived. A shared given name and a year apart is the whole "
        "resemblance",

    # 22 September 2026, and the same shape again: a Slovene woman in Carniola
    # against a Croatian woman of the same given name and year, where the year
    # on the found row is a REGISTER ENTRY and not a birth.
    # 22 September 2026, and the third time this exact shape has come up: a
    # Carniolan woman against a Croatian one on a given name and a year that
    # mean different things. This one is the plainest of the three, because
    # the found row's year IS a birth and the two lives do not overlap.
    # 22 September 2026. Both of these are the same shape a third and fourth time:
    # a Carniolan woman against a Croatian one on a given name and a year, where
    # the year on the found row is not even a birth.
    "Maria Kosinar the second":
        "baptised at Kranj-Šmartin on 6 December 1818 to Franz Kosinar and Maria "
        "Dortschen. Maria Papić (Papa) of 1818 is at Selce, four hundred "
        "kilometres away, with a different surname and different parents. A "
        "shared given name and a shared year is the whole resemblance",

    "Maria Kozina of 1859":
        "born AND baptised at Kranj-Šmartin on 7 August 1859, at Oberfeichting "
        "(Zgornje Bitnje) house 9, to Johann Kozina, Hüblar, and Ursula Sedej — "
        "the register gives the day twice, the sex column and both parents. The "
        "candidates are Croatian children of 1858-59 four hundred kilometres "
        "away, with different surnames and different parents; the resemblance is "
        "a given name and a year",

    "Franciška Kozina, married Kert":
        "THE DATE ON HER ROW IS HER MARRIAGE, not her birth: she married "
        "Ignacij Kert at Kranj–Šmartin in 1897 on her father's consent as an "
        "under-age bride, so she was born after about 1873. The candidate is a "
        "Croatian child born in 1896, four hundred kilometres away, who would "
        "have been one year old",

    "Marija Kozina, married Žiherl":
        "THE DATE ON HER ROW IS HER MARRIAGE, not her birth: she married Anton "
        "Žiherl at Kranj–Šmartin in 1898, daughter of Urban Kozina, kmet. The "
        "candidates are Croatian children born in 1897–98, four hundred "
        "kilometres away, who would have been infants at her wedding",

    "Marija \"Mina\" Kozina":
        "married Kancijan Česen at Stražišče in 1883, and her marriage entry "
        "gives her birthplace as Zgornje Bitnje no. 9 and her parents as Janez "
        "Kozina and Urša Sedej — so she is Johann Kozina's youngest daughter, "
        "baptised there 7 August 1859. THE DATE ON HER ROW IS HER MARRIAGE. The "
        "candidates are Croatian girls born in 1892-93, four hundred kilometres "
        "away, sharing nothing but a given name",

    "Maria Kosinar":
        "baptised at Kranj-Šmartin on 8 August 1815 and BURIED THERE ON 31 "
        "MARCH 1816, aged three quarters of a year — the register gives both "
        "days. Maria Žubrinić of 1814 is a Croatian child four hundred "
        "kilometres away who lived, with a different surname and different "
        "parents. This one's parents are Franz Kosinar and Maria Dortschen",

    "Maria \"Mina\" Dortschen":
        "named as a mother at Kranj-Šmartin in 1814, so born around 1790 — the "
        "1814 on her row is her daughter's baptism. Maria Žubrinić of 1814 is a "
        "newborn in Croatia, four hundred kilometres away, with a different "
        "surname and different parents",

    # 21 September 2026, from the Carniolan registers. A Slovene cottager's wife
    # at Kranj in 1836 against four Croatian women of the same given name and
    # year, three of them Žubrinić. Nothing but «Lucia» and «1836» is shared,
    # and the 1836 on her row is the year she is NAMED AS A MOTHER, not her birth.
    "Lucia Labornik":
        "a Slovene Häusler's wife at Kranj-Šmartin, named as a mother in 1836 — "
        "the year on the row is the register entry, not her birth, so she will "
        "have been born around 1810. The candidates are Lucia Mlinarich and three "
        "Lucia Žubrinić of 1835-36 in Croatia: a shared given name, a shared year "
        "that means different things, and no shared surname, parent or parish",
    "Marija Kosina":
        "resembles Marija Anka Kalanj 1897 and Marija Papić 1896 on a given name "
        "and a year. Different surname and different parents — hers are Martin "
        "Kosina and Angelika Boras, and she was buried in the year she was born",
    "Josip Kosina":
        "three Josip Pavelići and a Josip Perpić of 1895-96 share the given name "
        "and nothing else. His parents are Martin Kosina and Angelika Boras, and "
        "like his sister Marija he was buried in the year he was born",
    "Petar Kasuniž":
        "the 1891 on this row is the year of the MARRIAGE at which he is named as "
        "the bride's father, not his own birth — he will have been born around "
        "1860. Petar Kalanj 1890 is a different surname and an infant at the time",
    "Marija Turina":
        "the same: 1891 is the marriage she is named at, not her birth. The "
        "candidates are four women born about 1890 with a different surname, and "
        "one of them is her own daughter's generation",
    "Maria Magdalena Theresia Žubrinić":
        "resembles Maria Magdalena Žubrinić 1845 and Maria Žubrinić 1847, but "
        "neither has Maria Marković as a mother — the parents are the test and "
        "they fail it",
    "Maria Žubrinić":
        "1858 is a common year for this name; no candidate has Magdalena "
        "Glavinić as a mother",
    "Joanna Perpić":
        "resembles Joanna Kalanj 1875, and the resemblance is a given name and "
        "one year apart. Different surname, and a different father — Joannes "
        "Perpić of Krivi Put against Ivan Kalanj. The parents are the test and "
        "they fail it",
    "Matilda Papić":
        "she IS probably in the tree, as Franka or Sulka Papić, both born 1895 "
        "with no death recorded. That is the open question the row exists to "
        "state, not an error",
    "Ivan Defrančeski":
        "IN THE TREE — Hedviga Blažević's husband, born 1925, died 1995, "
        "unpublished. Kept here only until his grave is recorded against him",

    # 29 September 2026, the Brinje marriage register. Eight candidates, not
    # one of them a Borić, none of them at Brinje.
    "Marija Borić":
        "resembles Marija Kalanj (1893, two of them), Marija Boras (1892) and "
        "five more, none surnamed Borić and none placed at Brinje. Her own "
        "register entry names her father as Niko Borić of Brinje house 142, "
        "which is the test this file applies everywhere else and none of the "
        "eight candidates pass it — a given name and a year is the whole "
        "resemblance",
    "Ive Borić":
        "resembles Ivan 'Ive' John Pavelich (born Pavelić) 1893 — a different "
        "surname on the coast, not Brinje, sharing only a nickname and the "
        "year this row's marriage happened to fall in. Ive Borić's own row "
        "names his father as Jozo Borić of Križ Kamenica, which the candidate "
        "does not touch at any point",
    "Marko Perković":
        "resembles Marko Ridjan 1895, married to Ana Papić — a different "
        "surname, and the resemblance is the year of his own marriage matching "
        "another man's. Marko Perković's row names his father as Pere Perković "
        "of Novi Kut, Brinje parish, which the candidate has no connection to",
    "Marija Borić, wife of Vičić Jure":
        "resembles four Marija/Marije born around 1890-91, none surnamed "
        "Borić and none placed at Brinje - a Papić, two Pavelić and one "
        "unsourced 'published' entry. This row is not even her own baptism; "
        "it is her son Tomo Vičić's, which names her only as his mother's "
        "maiden surname. A given name and a birth year four hundred "
        "kilometres from anywhere is the whole resemblance",
    "Petar Borić":
        "resembles Petar Kalanj (1890), a different surname and a different "
        "family - Petar Borić's own row names his parents as Tome Borić and "
        "Jela Borić of Brinje house 141, which the candidate has no "
        "connection to. A given name and a birth year is the whole "
        "resemblance",
    "Ivan Borić, witness at Brinje house 138":
        "resembles three men named Ivan, none surnamed Borić and none "
        "placed at Brinje - a Krmpotić in-law, a Kalanj child of Josip "
        "Kalanj born two years later, and an unrelated Perpić. This row "
        "names him only as a witness to a Radotić baptism at Brinje house "
        "138; the resemblance is a given name and a year",
    "Marija Borić, wife of Frane Jurajić":
        "resembles the same handful of Marija/Marije born 1890-92 this file "
        "has already settled twice for other Borić women - a Papić, a "
        "Boras, two Pavelić, and an unsourced 'published' entry, none "
        "surnamed Borić and none at Brinje. This row is her son Ivo "
        "Jurajić's baptism, not her own; the resemblance is a given name "
        "and a birth year",
    "Jure Borić, witness at Brinje house 288":
        "resembles Jure Pavelić 1893, a different surname entirely - this "
        "row names him only as a witness at a Sertić baptism, no house "
        "number of his own given. The resemblance is a given name and a "
        "year",
    "Ana Borić, witness at Brinje house 289":
        "resembles Ana Kalanj 1894, a different surname and a year off by "
        "one - this row names her only as a witness at a Sertić baptism. "
        "The resemblance is a given name and roughly a year",
    "Franjo Kalanj":
        "resembles two Franjo born 1893 in the tree, one a Kalanj - but "
        "that Franjo Kalanj's mother is Margareta Butorac, and this row's "
        "own register entry names the mother as Kate Zoričić, the same "
        "woman already in this file as Viol Kalanj's wife since 1890. "
        "Same given name and birth year, different parents entirely",
    "Marija Borić, wife of Jure Vičić":
        "resembles the same handful of Marija/Marije born 1890-92 this file "
        "has now settled three times for Borić women married out - a "
        "Papić, a Boras, two Pavelić, and an unsourced 'published' entry, "
        "none surnamed Borić and none at Brinje. This row is a second son "
        "Tomo Vičić's baptism, not her own; the resemblance is a given "
        "name and a birth year",
    "Marija Borić, wife of Jure Krnarić":
        "resembles four Marija Kalanj born 1893-94 - a different surname "
        "entirely, not even Borić, and the resemblance is a given name plus "
        "her daughter's own 1894 birth year coincidentally matching theirs. "
        "This row is her daughter Manda Krnarić's baptism, not her own; none "
        "of the four candidates is surnamed Borić or tied to a Krnarić",
    "Marija Borić, witness at Kamenica house 3":
        "resembles the same four Marija Kalanj born 1893-94 already settled "
        "for the Krnarić entry above - a different surname entirely, and the "
        "resemblance is a given name plus a birth year that belongs to the "
        "child she witnessed, not to her. None of the four is surnamed Borić "
        "or placed at Kamenica",
    "Marija Kalanj, daughter of Viol Kalanj":
        "resembles Marija Blažević 1898 - a different surname, born the year "
        "before and on the coast, sharing only a given name. This row's own "
        "register entry names her parents as Viol Kalanj and Zoričić Kate of "
        "Brinje house 188, which the candidate has no connection to",
    "Matija Borić, wife of Stipo Mesić (Kamenica 20, 1899)":
        "resembles Marija Blažević 1898 - a different surname, born a year "
        "earlier on the coast, sharing only a given name and a decade. This "
        "row's own register entry names her husband as Mesić Stipo of "
        "Kamenica house 20, which the candidate has no connection to",
    "Marija Borić, witness at Kamenica house 20":
        "resembles the same Marija Blažević 1898 settled for the Mesić "
        "entry above - a different surname on the coast, sharing only a "
        "given name. This row names her only as a witness to a Mesić "
        "baptism at Kamenica",
    "Marija Borić, wife of Frane Vranić (1888)":
        "resembles four Marijas born 1887-88 in the tree (Šestan, Babić, "
        "Blažević and a Marija Milka Kalanj, a coastal child of Luka Kalanj) "
        "- all infants on the coast, sharing only a given name and a decade. "
        "This row's own register entry names her as the Borić wife of Frane "
        "Vranić, of Brinje house 266, mother of a girl born in April 1888, "
        "which none of them touches; not merged",
    "Marija Kalanj, wife of Ivan Mesić (1896)":
        "resembles Marija Anka Kalanj 1897 and Marija Papić 1896 in the tree "
        "- two Marijas born the same decade on the coast, one a Kalanj, but "
        "neither a married woman of Brinje. This row's own register entry "
        "names her as the wife of Mesić Ivan, of Brinje house 176, mother of "
        "a child born in October 1896, which neither candidate touches; the "
        "shared surname Kalanj is the open question this archive has carried "
        "since the first Brinje Kalanj was found, and the row is not merged",
    "Marija Kalanj, witness at Brinje house 228":
        "resembles Marija Blažević 1898 - a different surname, born a year "
        "earlier on the coast, sharing only a given name. This row names her "
        "only as a witness to a Murat baptism at Brinje house 228, which the "
        "candidate has no connection to",
    "Marija Kalanj, daughter of Jure Kalanj and Vučetić Manole (house 231, 1891)":
        "resembles Marija 1890 and three other Marijas born 1890-92 in the "
        "tree - none of them a Kalanj of Brinje. This row's own register "
        "entry names her parents as Jure Kalanj and Vučetić Manole of Brinje "
        "house 231, which none of the candidates touches",
    "Petar Kalanj, son of Tome Kalanj and Nesić Marija":
        "resembles Petar Kalanj 1890, a child of Joso (Josephus) Kalanj on "
        "the coast - same surname, a year apart, different place. This row's "
        "own register entry names his parents as Tome Kalanj and Nesić Marija "
        "of Brinje house 188, which that child's family does not touch; not "
        "merged, though the shared surname is the open question this archive "
        "has carried since the first Brinje Kalanj was found",
    "Kata Borić, informant at Kamenica house 8 (1888)":
        "resembles Kata Blažević 1889 - a different surname, a year "
        "later, on the coast, sharing only a given name. This row "
        "names her only as an informant at a Mesić baptism at Kamenica "
        "house 8, which the candidate has no connection to",
    "Mile Kalanj, son of Tome Kalanj and Marija Kalanj (house 188, 1888)":
        "resembles Mile Špalj 1888, a child of Matija Prpić on the "
        "coast - a different surname sharing only the given name and "
        "the year. This row own register entry names his parents as "
        "Kalanj Tome and Kalanj Marija of Brinje house 188, which that "
        "child family does not touch; not merged",
    "Marija Kalanj, wife of Jure Fröhlich (1889)":
        "resembles several Marijas born 1888-90 in the tree (Papić, "
        "Šestan and a Marija Milka Kalanj, all infants on the coast) - "
        "none a married woman of Brinje. This row own register entry "
        "names her as the Kalanj wife of Fröhlich Jure, of Brinje "
        "house 68, mother of a girl born in January 1889, which none "
        "of the candidates touches; not merged",
    "Marija Borić, daughter of Lojze Borić and Marija Mesić (Kamenica 23, 1889)":
        "resembles several Marijas born 1888-90 in the tree (Papić, "
        "Šestan and a Marija Milka Kalanj) - coastal infants sharing "
        "only a given name and a decade. This row own register entry "
        "names her as the daughter of Borić Lojze and Mesić Marija, of "
        "Kamenica house 23, which none of the candidates touches; not "
        "merged",
    "Stjepan Borić, informant at Kamenica house 23 (1889)":
        "resembles Stjepan Žubrinić 1888, a coastal child of Kata "
        "Oršanić - a different surname sharing only a given name. This "
        "row names a Borić man only as an informant at a Kamenica "
        "birth in 1889, which the candidate has no connection to; not "
        "merged",
    "Stjepan Borić, informant at Lučane house 36 and Brinje house 60 (1889)":
        "resembles Stjepan Žubrinić 1888, a coastal child of Kata "
        "Oršanić - a different surname sharing only a given name. This "
        "row names a Borić man only as an informant at two "
        "Brinje-parish births in May 1889, which the candidate has no "
        "connection to; not merged",
    "Kate Perković, wife of Ivan Javor (1889)":
        "resembles Kate Prpić 1890, a coastal child of Lucija - a "
        "different surname, a year later, sharing only a given name. "
        "This row own register entry names her as the Perković wife of "
        "Javor Ivan, of Brinje house 70, mother of a boy born in "
        "August 1889, which the candidate does not touch; not merged",
    "Marija Borić, wife of Franjo Jurajić (house 286, 1889)":
        "resembles several Marijas born 1888-90 in the tree (Papić, "
        "Šestan, a Marija Milka Kalanj and one published Marija) - "
        "coastal infants sharing only a given name and a decade. This "
        "row own register entry names her as the Borić wife of Jurajić "
        "Franjo, of Brinje house 286, mother of a girl born in "
        "September 1889, which none of the candidates touches; not "
        "merged",
    "Marija Borić, wife of Jure Krnarić (house 208, 1889)":
        "resembles several Marijas born 1888-90 in the tree (Papić, "
        "Šestan, a Marija Milka Kalanj and a published Marija) - "
        "coastal infants sharing only a given name and a decade. This "
        "row own register entry names her as the Borić wife of Krnarić "
        "Jure, of Brinje house 208, mother of a girl born in November "
        "1889, which none of the candidates touches; not merged",
    "Marija Perković, wife of Marko Komadina (1889)":
        "resembles several Marijas born 1888-90 in the tree (Papić, "
        "Šestan, a Marija Milka Kalanj and a published Marija) - "
        "coastal infants sharing only a given name and a decade. This "
        "row own register entry names her as the Perković wife of "
        "Komadina Marko, of Brinje house 100, mother of a girl born in "
        "November 1889, which none of the candidates touches; not "
        "merged",
    "Mate Kalanj, son of Jure Kalanj and Ane Vičić (house 249, 1890)":
        "resembles three Mates born 1889-90 in the tree (Žunski, "
        "Blažević and Pavelić) - coastal children and a spouse, none a "
        "Kalanj of Brinje. This row own register entry names him as "
        "the son of Kalanj Jure and Vičić Ane of Brinje house 249, "
        "born in January 1890, which none of the candidates touches; "
        "not merged",
    "Marija Kalanj, daughter of Jure Kalanj and Franjica Bionović (house 188, 1890)":
        "resembles four Marijas born 1890-91 in the tree (a published "
        "Marija, Papić and two Pavelić) - coastal infants sharing only "
        "a given name and a year. This row own register entry names "
        "her as the daughter of Kalanj Jure and Bionović Franjica of "
        "Brinje house 188, born on 3 June 1890, which none of the "
        "candidates touches; not merged",
    "Ivan Kalanj, son of Niko Kalanj and Marija Vučetić (house 231, 1891)":
        "resembles Ivan Kalanj 1892, a child of Joso (Josephus) Kalanj "
        "on the coast - same surname and first name, a year apart, "
        "different place - and two other Ivans of 1890-91 with other "
        "surnames. This row own register entry names his parents as "
        "Niko Kalanj and Vučetić Marija of Brinje house 231, which "
        "that coastal child family does not touch; not merged, though "
        "the shared surname is the open question this archive has "
        "carried since the first Brinje Kalanj was found",
    "Marija Borić, daughter of Tome Borić and Marica Radotić (Kamenica 24, 1891)":
        "resembles several Marijas born 1890-92 in the tree (a "
        "published Marija, Papić, Boras and Pavelić) - coastal infants "
        "sharing only a given name and a few years. This row own "
        "register entry names her as the daughter of Borić Tome and "
        "Radotić Marica of Kamenica house 24, which none of the "
        "candidates touches; not merged",
    "Ivan Borić and Marija Sertić, informants at Brinje house 139 (1891)":
        "resembles Ivan Kalanj 1892, Ivan Krmpotić 1890 and Ivan "
        "Perpić 1891 - infants and a spouse in the tree sharing only a "
        "first name. This row names a Borić man only as an informant "
        "at a Brinje birth in 1891, which none of them touches; not "
        "merged",
    "Marija Kalanj, daughter of Ferdo Kalanj and Ruže Krnarić (house 188, 1891)":
        "resembles several Marijas born 1890-92 in the tree (a "
        "published Marija, Papić, Boras and Pavelić) - coastal infants "
        "sharing only a given name and a few years. This row own "
        "register entry names her as the daughter of Kalanj Ferde and "
        "Krnarić Ruže of Brinje house 188, which none of the "
        "candidates touches; not merged",
    "Josip Borić, son of Petar Borić and Ruže Zoričić (Kamenica 24, 1891)":
        "resembles three Josips of 1890-92 in the tree (Blažević, "
        "Papić and Glavičić) - coastal infants and a spouse sharing "
        "only a given name and a year. This row own register entry "
        "names him as the son of Borić Petar and Zoričić Ruže of "
        "Kamenica house 24, which none of the candidates touches; not "
        "merged",
    "Ivan Borić and Ane, informants at Kamenica house 16 (1891)":
        "resembles Ivan Kalanj 1892, Ivan Krmpotić 1890 and Ivan "
        "Perpić 1891 - infants and a spouse in the tree sharing only a "
        "first name. This row names a Borić man only as an informant "
        "at a Kamenica birth in 1891, which none of them touches; not "
        "merged",
    "Marija Kalanj, wife of Jure Fröhlich (house 68, 1891)":
        "resembles several Marijas born 1890-92 in the tree (a "
        "published Marija, Papić, Boras and Pavelić) - coastal infants "
        "sharing only a given name and a few years. This row own "
        "register entry names her as the Kalanj wife of Fröhlich Jure, "
        "of Brinje house 68, mother of a boy born in November 1891, "
        "which none of the candidates touches; not merged",
    "Kate Perković, wife of Pave Zoričić (house 70, 1891)":
        "resembles Kate Prpić 1890, a coastal child of Lucija - a "
        "different surname, a year earlier, sharing only a given name. "
        "This row own register entry names her as the Perković wife of "
        "Zoričić Pave, of Brinje house 70, mother of a boy born in "
        "November 1891, which the candidate does not touch; not merged",
    "Marija Borić, wife of Jure Vičić (house 117, 1891)":
        "resembles several Marijas born 1890-92 in the tree (a "
        "published Marija, Papić, Boras and Pavelić) - coastal infants "
        "sharing only a given name and a few years. This row own "
        "register entry names her as the Borić wife of Vičić Jure, of "
        "Brinje house 117, mother of a boy born in December 1891, "
        "which none of the candidates touches; not merged",
    "Marija Borić, wife of Jure Krnarić (house 208, 1892)":
        "resembles several Marijas born 1891-93 in the tree (two "
        "coastal Marija Kalanj infants of 1893, Boras and Pavelić) - "
        "infants sharing only a given name and a few years, and two of "
        "them Kalanj girls on the coast. This row own register entry "
        "names her as the Borić wife of Krnarić Jure, of Brinje house "
        "208, mother of a boy born in May 1892, which none of the "
        "candidates touches; not merged",
    "Marija Kalanj, daughter of Ferdo Kalanj and Ruže Krnarić (house 188, 1892)":
        "resembles several Marijas born 1891-93 in the tree, among "
        "them two coastal Marija Kalanj infants of 1893, a Boras and a "
        "Pavelić - coastal infants sharing only a given name and a few "
        "years, and two of them Kalanj girls on the coast. This row "
        "own register entry names her as the daughter of Kalanj Ferole "
        "and Krnarić Ruže of Brinje house 188, born in December 1892, "
        "which none of the candidates touches; not merged",
    "Ivan Borić, son of Lojze Borić and Manole Mesić (Kamenica 23, 1892)":
        "resembles Ivan Kalanj 1892 (a coastal child of Joso Kalanj), "
        "Ivan Pavelić 1893 and Ivan Perpić 1891 - infants in the tree "
        "sharing only a first name and a year. This row own register "
        "entry names him as the son of Borić Lojze and Mesić Manole of "
        "Kamenica house 23, which none of the candidates touches; not "
        "merged",
    "Marija Borić, wife of Franjo Jurajić (house 296, 1893)":
        "resembles several Marijas born 1892-93 in the tree (two "
        "coastal Marija Kalanj infants, a Boras, a Pavelić) - coastal "
        "infants sharing only a given name and a year. This row is a "
        "married Borić woman, mother of Jurajić Bare of Brinje house "
        "296, named in her own register entry, which none of the "
        "candidates touches; not merged",
    "Marija Kalanj, wife of Ive Mesić (house 178, 1893)":
        "resembles several Marija Kalanj infants of 1893 in the tree "
        "(coastal children of Kalanj families) - infants sharing only "
        "a given name and a surname, while this row is a married "
        "Kalanj woman of Brinje, mother of Mesić Luce, named in her "
        "own register entry; not merged",
    "Mate Kalanj and Luce, informants at Brinje house 176 (1893)":
        "resembles infants named Mate born 1892-94 in the tree (a "
        "Blažević, a Miletić, a Pavelić) - coastal children sharing "
        "only a first name and a year. This row is an adult couple "
        "named as informants in a Brinje register entry, which none of "
        "the candidates touches; not merged",
    "Marija Kalanj, wife of Jure Fröhlich (house 68, 1894)":
        "resembles Marija Kalanj infants of 1893-94 in the tree "
        "(coastal children of Kalanj families) - infants sharing only "
        "a name and a few years, while this row is a married Kalanj "
        "woman of Brinje, mother of Fröhlich Jure, named in her own "
        "register entry; not merged",
    "Mate Kalanj and Kate Šebalj, informants at Brinje house 157 (1894)":
        "resembles infants named Mate born 1892-94 in the tree "
        "(coastal children sharing only a first name and a year). This "
        "row is an adult informant named in a Brinje register entry, "
        "which none of the candidates touches; not merged",
    "Marko Borić, son of Niko Borić and Marija (house 148, 1894)":
        "resembles Marko Ridjan 1895 in the tree (a spouse in the Papić "
        "line, sharing only a first name and a year). This row is a Brinje "
        "baptism entry that names its parents (Borić Niko x Marija, "
        "house 148), which the candidate does not touch; not merged",
    "Ivan Borić, informant at Kamenica house 13 (1894)":
        "resembles Ivan infants of 1892-94 in the tree (coastal "
        "children sharing only a first name and a few years). This row "
        "is an adult informant named in a Brinje register entry, which "
        "none of the candidates touches; not merged",
    "Marija Kalanj, wife of Ivan Marinčić (Lučane, 1894)":
        "resembles Marija Kalanj infants of 1893-94 in the tree "
        "(coastal children of Kalanj families) - infants sharing only "
        "a given name and a surname, while this row is a married "
        "Kalanj woman of Lučane, mother of Marinčić Manole, named in "
        "her own register entry; not merged",
    "Marija Borić, daughter of Vijo Borić and Ane Sertić (house 186, 1895)":
        "resembles Marija infants of 1895 in the tree (coastal "
        "children sharing only a given name and a year). This row is a "
        "Brinje baptism entry naming its parents (Borić Vijo x Sertić "
        "Ane, house 186), which none of the candidates touches; not "
        "merged",
    "Marija Mesić, wife of Tome Kalanj (house 188, 1895)":
        "resembles Marija or Manole Kalanj infants of 1895 in the tree "
        "(coastal children sharing a given name and a surname). This "
        "row is a married Mesić woman of Brinje, mother of Kalanj "
        "Manole, named in her own register entry (Kalanj Tome x Mesić "
        "Marija, house 188), which none of the candidates touches; not "
        "merged",
    "Joso Borić and Marica Vranić, informants at Brinje house 124 (1895)":
        "resembles a Joso born in the tree around 1895 (a coastal "
        "child sharing only a first name and a year). This row is an "
        "adult informant named in a Brinje register entry, which the "
        "candidate does not touch; not merged",
    "Marija Borić, informant at Kamenica house 5 (1895)":
        "resembles Marija infants of 1895-96 in the tree (children "
        "sharing only a given name and a year). This row is an adult "
        "informant named in a Brinje register entry, which none of the "
        "candidates touches; not merged",
    "Marko Borić, informant at Brinje house 60 (1896)":
        "resembles Marko Ridjan 1895 (a spouse in the Papić line) or "
        "another Marko of 1895-96 in the tree, sharing only a first "
        "name and a year. This row is an adult informant named in a "
        "Brinje register entry, which none of the candidates touches; "
        "not merged",
    "Marko Kalanj, son of Jure Kalanj and Franjica Bionović (house 188, 1896)":
        "resembles a Marko infant of 1895-96 in the tree (a spouse or "
        "child sharing only a first name and a year). This row is a "
        "Brinje baptism naming its parents (Kalanj Jure x Bionović "
        "Franjica, house 188), which the candidate does not touch; not "
        "merged",
    "Mate Kalanj and Manole, informants at Brinje house 176 (1896)":
        "resembles an infant Mate of the 1890s in the tree (a coastal "
        "child sharing only a first name and a few years). This row is "
        "an adult informant named in a Brinje register entry, which "
        "the candidate does not touch; not merged",
    "Marija Kalanj, wife of Ivan Marinčić (Lučane 24, 1896)":
        "resembles Marija Kalanj infants of the 1890s in the tree "
        "(coastal children sharing a given name and surname). This row "
        "is a married Kalanj woman of Lučane, mother of Marinčić "
        "Marija, named in her own register entry; not merged",
    "Marija Kalanj, informant at Brinje house 158 (1896)":
        "resembles Marija Kalanj infants of the 1890s in the tree "
        "(coastal children sharing a given name and surname). This row "
        "is an adult informant named in a Brinje register entry; not "
        "merged",
    "Marija Borić, wife of Vid Hofjevac (house 160, 1896)":
        "resembles Marija infants of 1896 in the tree (children "
        "sharing only a given name and a year). This row is a married "
        "Borić woman of Brinje, mother of Hofjevac Mile, named in her "
        "own register entry; not merged",
    "Marija Kalanj, wife of Jure Fröhlich (house 68, 1897)":
        "resembles Marija Kalanj infants of the 1890s in the tree "
        "(coastal children sharing a given name and surname). This row "
        "is a married Kalanj woman of Brinje, mother of Fröhlich "
        "Rosika, named in her own register entry; not merged",
    "Marija Borić and Ferdo Milaković, informants at Kamenica house 27 (1897)":
        "resembles Marija or Ferdo infants of the 1890s in the tree "
        "(coastal children sharing only a given name and a few years). "
        "This row is an adult informant pair named in a Brinje "
        "register entry, which none of the candidates touches; not "
        "merged",
    "Rosa Borić and Marko Sertić, informants at Brinje house 138 (1897)":
        "resembles an infant Rosa or Marko of the 1890s in the tree "
        "(children sharing only a given name and a few years). This "
        "row is an adult informant pair named in a Brinje register "
        "entry, which the candidate does not touch; not merged",
    "Marija Borić and Marko Hofjevac, informants at Brinje house 146 (1897)":
        "resembles Marija or Marko infants of the 1890s in the tree "
        "(coastal children sharing only a given name and a few years). "
        "This row is an adult informant pair named in a Brinje "
        "register entry, which none of the candidates touches; not "
        "merged",
    "Marija Borić, wife of Niko Hofjevac (house 253, 1897)":
        "resembles Marija infants of 1897 in the tree (children "
        "sharing only a given name and a year). This row is a married "
        "Borić woman of Brinje, mother of Hofjevac Marija, named in "
        "her own register entry; not merged",
    "Marija Kalanj and Viol Bartolović, informants at Brinje house 224 (1898)":
        "resembles Marija Kalanj or Viol infants of the 1890s in the "
        "tree (coastal children sharing a given name and a surname). "
        "This row is an adult informant pair named in a Brinje "
        "register entry; not merged",
    "Marija Mesić, wife of Tome Kalanj (house 188, 1898)":
        "resembles Marija or Franciska Kalanj infants of the 1890s in "
        "the tree (coastal children sharing a given name and a "
        "surname). This row is a married Mesić woman of Brinje, mother "
        "of Kalanj Franciska, named in her own register entry; not "
        "merged",
    "Marija Borić, wife of Ivan Borić (house 141, 1898)":
        "resembles Marija infants of the 1890s in the tree (children "
        "sharing only a given name and a few years). This row is a "
        "married Borić woman of Brinje, mother of Borić Ane, named in "
        "her own register entry; not merged",
    "Marija Boležić, wife of Niko Borić (house 142, 1898)":
        "resembles Marija or Marica infants of 1898 in the tree "
        "(children sharing only a given name and a year). This row is "
        "a married woman of Brinje, mother of Borić Marica, named in "
        "her own register entry (Borić Niko x Boležić Marija); not "
        "merged",
    "Marija Vuković, wife of Ive Borić (house 126, 1898)":
        "resembles Marija or Niko infants of 1898 in the tree "
        "(children sharing only a given name and a year). This row is "
        "a baptism naming its parents (Borić Ive x Vuković Marija, "
        "house 126), which none of the candidates touches; not merged",
    "Marija Perkić, wife of Jure Vranić (house 265, 1898)":
        "resembles Marija or Bare infants of 1898 in the tree "
        "(children sharing only a given name and a year). This row is "
        "a married woman of Brinje, mother of Vranić Bare, named in "
        "her own register entry; not merged",
    "Ivan Javor and Kate, informants at Brinje house 257 (1899)":
        "resembles Ivan Kalanj 1900 in the tree - a different surname, "
        "sharing only the given name Ivan. This row is an informants "
        "line naming a Javor man at a Lohmer birth in Brinje, which "
        "that child of the tree does not touch; not merged",
    "Ivan Javor, widower bridegroom of 18 November 1888 (house 83)":
        "resembles Ivan children of 1887-1888 in the tree - different "
        "surnames, sharing only the given name Ivan and a year. This "
        "row is a 70-year-old Javor widower of Brinje house 83 in his "
        "own marriage entry, which none of those children touches; not "
        "merged",
    "Marija Javor, bride of 9 February 1890 (house 90)":
        "resembles Marija children of 1890-1891 in the tree - "
        "different surnames and, here, a bride of 22 in her own "
        "marriage entry, sharing only a given name and a decade; not "
        "merged",
    "Marija Borić, widow Bišanić, bride of 23 November 1890":
        "resembles Marija children of 1890-1891 in the tree - "
        "different surnames and, here, a widow of 33 in her own "
        "marriage entry, sharing only a given name and a decade; not "
        "merged",
    "Marija Kalanj, bride of 24 January 1892 (house 231)":
        "resembles Marija Kalanj infants of 1893 in the tree (coastal "
        "Klenovica children) and other Marija of 1892 - the surname "
        "match is real but this row is a woman of 21 in her own 1892 "
        "marriage entry at Brinje house 231, born about 1871 to Kalanj "
        "Joso and Ruže, a different generation from any infant of "
        "1893, and no document links her to the tree; not merged",
    "Marija Javor, bride of 23 October 1892 (house 118)":
        "resembles Marija infants of 1892-1893 in the tree - different "
        "surnames, and this is a bride of 22 in her own marriage entry "
        "at Brinje house 118, sharing only a given name and a year; "
        "not merged",
    "Marija Perlić, bride of 13 February 1893 (house 101)":
        "resembles Marija infants of 1892-1893 in the tree - different "
        "surnames, and this is a maiden of 35 in her own marriage "
        "entry at Brinje house 101, sharing only a given name and a "
        "decade; not merged",
    "Ivan Javor, bridegroom of 29 January 1894 (house 82)":
        "resembles Ivan infants of 1893-1894 in the tree - different "
        "surnames, and this is a man of 29 in his own marriage entry, "
        "sharing only the given name Ivan and a decade; not merged",
    "Luka Javor, bridegroom of 29 January 1894 (house 76)":
        "resembles Luka Martin Kalanj 1893 in the tree - a different "
        "surname, sharing only the given name Luka and a decade; this "
        "row is a bridegroom of 28 in his own marriage entry; not "
        "merged",
    "Ivan Borić, bridegroom of 8 April 1894 (house 126)":
        "resembles Ivan infants of 1893-1894 in the tree - different "
        "surnames, and this is a man of 23 in his own marriage entry, "
        "sharing only the given name Ivan and a decade; not merged",
    "Jure Perković, witness at the marriage of Dražanović Ivan and Šebalj Ruže (1894)":
        "resembles Jure Pavelić 1893 in the tree - a different "
        "surname, sharing only the given name Jure and a decade; this "
        "row is a witness line in an 1894 Brinje marriage entry; not "
        "merged",
    "Marija Javor, widow, daughter of Perković Duka (marriage of 1895)":
        "resembles Marija infants of 1894-1896 in the tree - different "
        "surnames and, here, a widow in her own 1895 marriage entry, "
        "sharing only a given name and a decade; not merged",
    "Bare Perlić, bride of 26 January 1896 (house 101)":
        "resembles Bare infants of 1890s in the tree - a different "
        "surname, sharing only the given name; this row is a bride of "
        "26 in her own marriage entry at Brinje house 101, born about "
        "1870; not merged",
    "Kate Perković, witness at the marriage of Bolešić Grgo and Vučetić Jela (1896)":
        "resembles Kate children of the 1890s in the tree - different "
        "surnames and generations; this row is an adult woman named in "
        "a witness line of an 1896 Brinje marriage entry, sharing only "
        "a given name; not merged",
    "Bare Borić, bride of 15 January 1899 (Kamenica 23)":
        "resembles Bare infants of the 1890s in the tree - a different "
        "surname and a woman of 24 in her own marriage entry at "
        "Kamenica 23, sharing only a given name; not merged",
    "Matija Borić, widow Smoljić, bride of 3 July 1898 (Križpolje-Plašćica 168)":
        "resembles Matija infants of the 1890s in the tree - different "
        "surnames and, here, a widow of 48 in her own marriage entry, "
        "sharing only a given name; not merged",
    "Milka Borić, child of Ivan Borić and Matija, died aged 10 (house 141, 1889)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marija Borić, daughter of Tome Borić and Marica, died aged 4 (Kamenica 24, 1891)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Mate Kalanj, son of Jure Kalanj and Ane, died aged 12 months (house 249, 1891)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marija Borić, widow of 83 (Kamenica 28, 1891)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Jure Kalanj, son of Mijo Kalanj and Ane, died aged 5 (house 249, 1892)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Joso Borić, son of Niko Borić and Mare, died aged 6 (house 142, 1893)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marko Borić, son of Lojze Borić and Ruže, died aged 15 (Kamenica 23, 1894)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marko Kalanj, son of Jure Kalanj and Franjica, died aged 9 (house 188, 1894)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marija Borić, daughter of Vujo Borić and Ane, died aged 3 (house 126, 1897)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marija Borić, daughter of Ivan Borić and Matija, died aged 3 (house 141, 1897)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Marija Borić, daughter of Tomo Borić and Marica, died aged 8 (Kamenica 24, 1899)":
        "a Brinje death entry that names its own Borić or Kalanj "
        "parents or spouse and house; the tree candidates are children "
        "of other families (Pavelić, Blažević, Papić, Ridjan, Boras) "
        "in other parishes, matching only on a given name and a year",
    "Petar Kalanj, son of Tome Kalanj and Marija, died aged 3 (house 181 as read, 1894)":
        "a Brinje death entry that names its own Kalanj parents and "
        "house; the one tree candidate, Viktor Petar, was BORN in 1894 "
        "(a sibling of Roza Zorica Kalanj), while this Petar was "
        "already three years old when he died in October 1894, so they "
        "cannot be the same child; the match is on the given name "
        "Petar and the year only.",
    "Marko Borić":
        "resembles Marko Ridjan 1895, married to Ana Papić - a different "
        "surname on the coast, not Brinje, sharing only a given name and a "
        "year one apart. This row's own register entry names his parents as "
        "Niko Borić and Boletić Marija of Brinje house 148, which the "
        "candidate has no connection to",
    "Ana Borić, daughter of Grgo Borić":
        "resembles two Ana Kalanj born 1894-95 - a different surname "
        "entirely, and neither candidate's parents match. This row's own "
        "register entry names her parents as Grgo Borić and Marija "
        "Milaković of Brinje house 126, which neither candidate touches",
    "Ivan Borić, witness at Lučane":
        "resembles four men named Ivan/Ive, none surnamed Borić - a "
        "Pavelić, a de Franceschi, a Prpić and a Belobarbić. This row "
        "names him only as a witness to a Lovinčić baptism at Lučane; the "
        "resemblance is a given name and a year",
    "Marija Borić, wife of Vid Hofjevac":
        "resembles a Papić and a Kalanj, neither surnamed Borić. This "
        "row's own register entry names her husband as Vid Hofjevac of "
        "Brinje house 160, which neither candidate touches",
    "Marija Borić, witness at Kamenica (1895)":
        "resembles the same Papić and Kalanj already settled for the "
        "Hofjevac entry above - neither surnamed Borić, neither placed at "
        "Kamenica. This row names her only as a witness to a Sertić "
        "baptism there",
    "Antonius Uroda of Šibenik":
        "resembles Antonius Defranceschi of 1742, a sibling of "
        "leonardus-defranceschi - a different surname entirely, and a "
        "different place. This row is a Magister Antonius Vroda of the Dolac "
        "suburb of Šibenik (married 30 Oct 1718 to Antonia, daughters buried "
        "Jan and Jul 1742); the resemblance is a given name and a year",
    "Vincentia Blažević widow bride of 1812":
        "resembles Vincentia 1811, a spouse of jacobi-kraljich - a Kraljić, "
        "not a Blažević. This row is a Blažević widow who married the "
        "widower Petrus Bozijan at Senj on 18 August 1812; the resemblance "
        "is a given name and a year",
    "Maria Kalanj bride of Babić 1842":
        "resembles Maria Lucia Komadina 1841 / Maria Sestan 1843 / Maria "
        "Žubrinić 1841 - different surnames, different parents. This row is "
        "a Kalanj bride of 1842, daughter of Jacobus and Magdalena; the "
        "resemblance is a given name and a year",
    "Antonius Babić of Senj groom of 1842":
        "resembles Antonius Žubrinić / Antonius Oreskovic of 1842 - other "
        "surnames, other parents. This row is a Babić, son of the late "
        "Georgius Babić and Maria née Babić; the resemblance is a given name "
        "and a year",
    "Maria Bajsich bride of Babić 1847":
        "resembles Maria Rosaria Antić / Maria Žubrinić of 1847-48 - other "
        "surnames, other parents. This row is a Bajsich bride, daughter of "
        "Martinus and Maria; the resemblance is a given name and a year",
    "Franciscus Babić of Senj groom of 1847":
        "resembles Franciscus Xubrinich 1847 - a Žubrinić, other parents. "
        "This row is a Babić, son of Franciscus Babić and Dorothea née "
        "Babić; the resemblance is a given name and a year",
    "Catharina Ostoman bride of Babić 1848":
        "resembles Catharina Perpic / Catharina Žubrinić of 1847 - other "
        "surnames, other parents. This row is an Ostoman bride, daughter of "
        "Matthias and Maria; the resemblance is a given name and a year",
    "Antonia Babić of Novigrad bride of 1831":
        "resembles Antonia Tomljanović 1831 [spouses of dujo-pavelic-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Gerbacz bride of Vincentius Uroda 1849":
        "resembles Maria 1848 [published]; Maria Blažević 1850 [siblings of slavka]; Maria Žubrinić 1848 [children of kate-babic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina widow of Stephanus Babić bride of 1857":
        "resembles Catharina Papić (Papa) 1858 [children of margareta-loncaric] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonius Gerbac widower of Starigrad groom of 1857":
        "resembles Antonius Blažević 1858 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Tomljenović of Karlobag bride of 1858":
        "resembles Maria Mariam 1858 [siblings of christophorus]; Maria Žubrinić Xubrinic 1857 [children of matia-banic]; Maria Blažević 1858 [children of anton-kljapo-blazevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucas Glavicsich of Senj groom of 1858":
        "resembles Luka Lucas Kalanj 1859 [children of maria-jovanovic-jovanovic-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Martha Lončarić widow of Linić bride of 1858":
        "resembles Martha Žubrinić 1857 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Vincentius Gerzic of Senj groom of 1858":
        "resembles Franciscus Sestan 1857 [children of sancta-alexandra-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Lončarić bride of 1845":
        "resembles Francisca Žubrinić 1846 [children of joanna]; Francisca Sestan 1846 [children of sancta-alexandra-defranceschi]; Francisca Žubrinić 1844 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Martinus Lenack groom of 1832 at Senj":
        "resembles Martinus Žubrinić Xubrinich 1833 [children of anna-3]; Martinus Šojat 1831 [children of ivka-krmpotic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonia widow bride of Krmpotić 1830":
        "resembles Antonia Tomljanović 1831 [spouses of dujo-pavelic-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Michael Krmpotić widower of Senj groom of 1830":
        "resembles Michaellum Michael Kalanj 1831 [children of margarita-barichevic]; Michael Vukelic 1830 [spouses of stanislava-blazevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonius Babić witness at Senj marriage of 1858":
        "resembles Antonius Blažević 1858 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Ana Dragičević bride of Valerian Lukatella 1849":
        "resembles Ana Anna Miletic 1848 [spouses of josip-josephus-joso-kalanj] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Butković bride of Lenac 1853":
        "resembles Maria Žubrinić Xubrinich 1853 [children of juliana]; Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Kalanj 1853 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Jacobus Lenac groom of 1853 at Senj":
        "resembles Jacobus Orešković Oreskovic 1852 [children of marcus-oreskovic-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Špalj bride of Malik 1820":
        "resembles Francisca Kraljich 1820 [children of anna-5]; Francisca 1819 [published]; Francisca Žubrinić Xubrinich 1820 [children of martha-franczetich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Malik soldier groom of 1820 at Senj":
        "resembles Joannes Juan Ivan Ive Žubrinić Zubrinic 1821 [children of margarita-3]; Joannes Žubrinić Xubrinich 1821 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Toma Pasquan groom of 1850 at Senj with a Žubrinić bride of Baška":
        "resembles Toma Žubrinić 1851 [children of matia-banic]; Toma Žubrinić 1850 [children of maria-klobacar]; Toma Žubrinić 1849 [children of luce-lucia-simetovic-simatovic-simatovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Lenac bride of Perpich 1845":
        "resembles Francisca Žubrinić 1846 [children of joanna]; Francisca Sestan 1846 [children of sancta-alexandra-defranceschi]; Francisca Žubrinić 1844 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Perpich groom of 1845 at Senj":
        "resembles Joannes Žubrinić Zubrinic Xubrinich 1844 [children of catharina-7]; Joannes Spudicevich-Tomich 1846 [spouses of anna-kalanj-6]; Joannes Žubrinić 1846 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Sbaich bride of Orichovich 1821":
        "resembles Maria Žubrinić Zubrinic 1822 [children of anna-4]; Maria Sekula 1820 [children of maria-11]; Maria Žubrinić Zubrinic Xubrinich 1821 [children of catharina-7] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Thomas Orichovich groom of 1821 at Senj":
        "resembles Thomas Žubrinić Xubrinich 1822 [children of magdalena-3]; Thomas Žubrinić 1822 [siblings of stephanus-zubrinic-6] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Anna Maria Theresia Brozinčević bride of Prpić 1853":
        "resembles Anna Papić (Papa) 1853 [children of franica-karsul] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Prpić groom of 1853 at Senj":
        "resembles Franciscus Sestan 1853 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucia Lončarić bride of Savretić 1823":
        "resembles Lucia Žubrinić Xubrinich 1823 [children of anna-3]; Lucia Žubrinić Xubrinich 1822 [children of margarita-2]; Luce Lucia Simetović Šimatović Simatović 1823 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Georgius Savretić groom of 1823 with Boras witnesses":
        "resembles Georgius Bellobalbic 1824 [siblings of paulina-bellobalbic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Boras witness at Senj marriage of 1823":
        "resembles Josephus Žubrinić Xubrinich 1824 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Miškulin widow bride of Gregorius Smojver 1838":
        "resembles Maria Žubrinić 1838 [children of lucia-jurjevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Smojver of Karlobag bride of Josephus Schwarz 1839":
        "resembles Maria Žubrinić 1838 [children of lucia-jurjevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Schwarz corporal groom of 1839 with a Smojver bride of Karlobag":
        "resembles Josephus Žubrinić Xubrinich 1840 [children of anna-smolcsich-smolcsich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Georgius Tomjanović groom of 1837 with a Smojver bride of Jablanac":
        "resembles Martinus Georgius Žubrinić 1838 [children of maria-8]; Georgius Juraj (Joannis) Papa 'Jure' Antić Papić 1838 [children of josephum-antic]; Jure Juraj Georgius Grandic 1836 [children of margareta-barbalic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Vukelić of Sveti Juraj bride of Franciscus Thian 1826":
        "resembles Maria Lisabetta Žubrinić Xubrinich 1827 [children of anna-3]; Maria 1827 [published]; Maria 1827 [spouses of martinus-georgius-zubrinic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Thian groom of 1826 with a Vukelić bride of Sveti Juraj":
        "resembles Franciscus Žubrinić Xubrinich 1825 [children of maria-baptised-margarita] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Petrus Tomaić soldier groom of 1833 with a Krmpotić bride of St Salvator":
        "resembles Petrus Kalanj 1833 [spouses of magdalena-butkovic-butkovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Orešković bride of Joannes Thian 1843":
        "resembles Maria Sestan 1843 [children of joanna-defranceschi]; Maria Žubrinić 1844 [children of ana-untersinger] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Thian groom of 1843 with an Orešković bride":
        "resembles Joannes Žubrinić Zubrinic Xubrinich 1844 [children of catharina-7]; Joannes Baptista Defranceschi 1842 [children of francisca-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Marija Orešković bride of Mathe Thian 1849":
        "resembles Marija Butkovic 1850 [spouses of mate-andjulico] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Magličić bride of Ignatius Turkalj 1853 whose mother was an Orešković":
        "resembles Maria Žubrinić Xubrinich 1853 [children of juliana]; Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Kalanj 1853 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria of Bescan bride of Casparus Paulus Babić 1856":
        "resembles Maria Žubrinić Xubrinic 1857 [children of matia-banic]; Maria Perpic 1857 [spouses of ivan-blazevic-4]; Maria Magdalena Žubrinić 1855 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Petrus Vukelić widower of Krasno groom of 1833 with a Krmpotić widow":
        "resembles Petrus Kalanj 1833 [spouses of magdalena-butkovic-butkovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonia Dvoić bride of Vitus Vukelić 1851":
        "resembles Antonia Blažević 1851 [published]; Antonia Blažević 1852 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucia Butković of Ledenice bride of 1851":
        "resembles Lucia Kalanj 1851 [children of magdalena-ferkovic]; Lucia Sekula 1851 [children of mande-mandalena-magdalena-kostelac] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Tomjanović bride of Joannes Vukelić 1851":
        "resembles Francisca Žubrinić 1852 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Vukelić of Gospić groom of 1851":
        "resembles Joannes Žubrinić 1852 [children of vincentia]; Joannes Sestan 1851 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Krmpotić bride of Franciscus Samarzia 1853":
        "resembles Maria Žubrinić Xubrinich 1853 [children of juliana]; Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Kalanj 1853 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Samarzia widower soldier groom of 1853 with a Krmpotić bride":
        "resembles Franciscus Sestan 1853 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Sučić widow bride of Josephus Boras 1851":
        "resembles Maria Blažević 1850 [siblings of slavka]; Maria Talić 1850 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Boras groom of 1851 at Senj":
        "resembles Josephus Josip Kalanj 1850 [children of antonius-kalanj]; Joso Josip Josephus Kalanj 1851 [children of antonius-kalanj]; Josephus Žubrinić Xubrinich 1852 [children of rosalia-marinic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina Stillin of Ledenice bride of Christophorus Babić 1851":
        "resembles Catharina Žubrinić 1852 [children of luce-lucia-simetovic-simatovic-simatovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Petrinović of Novi bride of Michael Belobarbić 1852":
        "resembles Francisca Žubrinić 1852 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Babić mariner groom of 1852 whose mother was née Jurčić":
        "resembles Joannes Žubrinić 1852 [children of vincentia]; Joannes Sestan 1851 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Boras died Senj 1839 aged 50":
        "resembles Josephus Žubrinić Xubrinich 1840 [children of anna-smolcsich-smolcsich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Anna Boras widow died Senj September 1841":
        "resembles Anna Agatha Žubrinić 1841 [children of magdalena-mande-drazenovic-drazenovic]; Anna Dujmović 1841 [spouses of nicolaus-zubrinic-xubrinich-4] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucia widow Kraljikas aged 106 died Senj September 1836":
        "resembles Lucia Žubrinić 1835 [children of maria-9]; Lucia Žubrinić Xubrinich Zubrinich 1835 [children of maria-begovich-begovic]; Lucia Mlinarich 1836 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina widow Kralj aged 84 died Senj November 1838":
        "resembles Catharina Žubrinić Xubrinich 1837 [children of helena-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Eva Lukatelli widow aged 54 died Senj January 1844":
        "resembles Eva Kostelacz 1844 [children of stephanus-kostelacz]; Eva Žubrinić 1845 [children of juliana-kostelacz] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joanna Krmpotić aged 60 died Senj December 1844":
        "resembles Natalis Joanna Žubrinić 1845 [children of lucia-jurjevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Georgius Orešković drowned at sea aged 20 died Senj June 1827":
        "resembles Georgius Žubrinić Xubrinich 1828 [children of maria-baptised-margarita] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Mathia Orešković aged 80 died Senj January 1848":
        "resembles Mathia Maria Papić (Papa) 1847 [children of helena-carich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Perpić widow aged 63 died Senj September 1836":
        "resembles Maria? 1835 [published]; Maria Marija Kalanj 1835 [children of antonius-kalanj]; Maria Žubrinić Xubrinich 1836 [children of magdalena-oreskovich-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Perpić aged 48 died Senj April 1841":
        "resembles Maria Lucia Komadina 1841 [spouses of martin-martinus-kalanj]; Maria Žubrinić 1841 [children of helena-oreskovic]; Maria Žubrinić 1841 [children of maria-catharina-oreskovic-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Perpić frontier soldier aged 61 died Senj July 1842":
        "resembles Josip Josephus Joso Kalanj 1841 [siblings of margareta-margaritum-kalanj]; Josephus Bogic 1842 [spouses of sabina-zubrinic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonia Perpić aged 35 died Senj February 1847":
        "resembles Antonia Sestan 1847 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Pilipić infant died Senj January 1847":
        "resembles Maria 1848 [published]; Maria Rosaria Antić 1847 [children of josephum-antic]; Maria Žubrinić 1848 [children of kate-babic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Perpić aged 25 died Senj 1848 faded":
        "resembles Franciscus Xubrinich 1847 [children of catharina-raslich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Špalj Spal aged 80 died Senj 1820":
        "resembles Joannes Juan Ivan Ive Žubrinić Zubrinic 1821 [children of margarita-3]; Joannes Žubrinić Xubrinich 1821 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonia Šojat aged 95 died Senj December 1830":
        "resembles Antonia Tomljanović 1831 [spouses of dujo-pavelic-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Hellena Špalj aged 79 died Senj November 1831":
        "resembles Hellena Žubrinić Xubrinich 1830 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina Špalj widow aged 78 died Senj August 1836":
        "resembles Catharina Monica Žubrinić Xubrinich 1836 [children of martha-franczetich]; Catharina Žubrinić Xubrinich 1837 [children of helena-oreskovic]; Maria Catharina Orešković Oreskovic 1835 [children of marcus-oreskovic-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Michael Šojat aged 51 died Senj June 1846":
        "resembles Miko Michael Sekula 1846 [children of mande-mandalena-magdalena-kostelac]; Michael Žubrinić 1847 [children of lucia-shimatovich]; Michael Žubrinić 1845 [children of luce-lucia-simetovic-simatovic-simatovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Tomljanović widow aged 60 died Senj April 1834":
        "resembles Maria? 1835 [published]; Maria Marija Kalanj 1835 [children of antonius-kalanj]; Maria Catharina Orešković Oreskovic 1835 [children of marcus-oreskovic-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucas Tomljanović infant died Senj February 1842":
        "resembles Lucas Žubrinić 1843 [children of maria-9] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Tomljanović aged 57 died Senj 1848":
        "resembles Maria 1848 [published]; Maria Rosaria Antić 1847 [children of josephum-antic]; Maria Žubrinić 1848 [children of kate-babic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Petrus Vukelić aged 70 died Senj June 1825":
        "resembles Petar Petrus Petrum Kalanj Kallayn 1825 [siblings of franjo-think-this-is-wrong-kalanj] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Lucas Vukelić died Senj January 1827":
        "resembles Lucas Žubrinić Zubrinic Xubrinich 1826 [children of anna-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Vukelić aged 77 died Senj January 1836":
        "resembles Joannes Juan Ivan Ive Žubrinić 1837 [spouses of kata-brajkovic]; Joannes Žubrinić Xubrinich 1836 [children of helena-czvetkovich]; Joannes Žubrinić Xubrinich 1837 [children of catharina-raslich-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Vukelić widow aged 70 died Senj January 1836":
        "resembles Maria? 1835 [published]; Maria Marija Kalanj 1835 [children of antonius-kalanj]; Maria Žubrinić Xubrinich 1836 [children of magdalena-oreskovich-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Vukelić infant died Senj August 1836":
        "resembles Joannes Juan Ivan Ive Žubrinić 1837 [spouses of kata-brajkovic]; Joannes Žubrinić Xubrinich 1836 [children of helena-czvetkovich]; Joannes Žubrinić Xubrinich 1837 [children of catharina-raslich-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Gasparus Vukelić infant died Senj January 1844":
        "resembles Josephus Sestan 1844 [children of sancta-alexandra-defranceschi]; Josephus Žubrinić 1845 [children of maria-markovic]; Josephus Žubrinić 1845 [children of maria-markovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Vukelić aged 67 died Senj June 1847":
        "resembles Joannes Žubrinić 1847 [siblings of theresia]; Joannes Spudicevich-Tomich 1846 [spouses of anna-kalanj-6]; Joannes Žubrinić 1846 [children of maria-kostelacz-jergovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joanna Župan infant died Senj May 1835":
        "resembles Joanna Žubrinić Kraljcich 1835 [children of maria-8] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina Župan widow aged 70 died Senj August 1836":
        "resembles Catharina Monica Žubrinić Xubrinich 1836 [children of martha-franczetich]; Catharina Žubrinić Xubrinich 1837 [children of helena-oreskovic]; Maria Catharina Orešković Oreskovic 1835 [children of marcus-oreskovic-oreskovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Ivan Pilipić aged 60 died Senj November 1849":
        "resembles Ivan Papić (Papa) 1850 [children of kate-loncaric]; Ivan Žubrinić 1850 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Vukelić aged 8 died Senj February 1850":
        "resembles Maria Blažević 1850 [siblings of slavka]; Maria Talić 1850 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Babić aged 7 died Senj July 1850":
        "resembles Maria Blažević 1850 [siblings of slavka]; Maria Talić 1850 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Catharina Orešković aged 26 died Senj August 1851":
        "resembles Catharina Žubrinić 1852 [children of luce-lucia-simetovic-simatovic-simatovic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Anna Vukelić infant died Senj October 1851":
        "resembles Ana Anna Kalanj 1851 [children of antonius-kalanj] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Belobarbić newborn died Senj May 1852":
        "resembles Maria Žubrinić Xubrinich 1853 [children of juliana]; Maria Magdalena Kalanj 1853 [published]; Maria Antonia Žubrinić Xubrinich 1853 [children of apolonia-raslic-raslic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Vukelić theology student aged 26 died Senj June 1852":
        "resembles Joannes Žubrinić 1852 [children of vincentia]; Joannes Sestan 1851 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Theresia Vukelić widow aged 72 died Senj January 1854":
        "resembles Theresia Žubrinić 1854 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Belobarbić newborn died Senj February 1854":
        "resembles Joannes Ivan Boras 1855 [spouses of vladimira-baricevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Boras aged 22 died Senj February 1854":
        "resembles Franciscus Sestan 1853 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Ana Belobarbić infant died Senj March 1854":
        "resembles Ana Nezak 'Anica' Boras 1854 [children of josip-josephus-boras] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Theresia Perpić infant died Senj June 1854":
        "resembles Theresia Žubrinić 1854 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Anna Smojver aged 16 died Senj July 1854":
        "resembles Anna Papić (Papa) 1853 [children of franica-karsul] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Vukelić aged 19 died Senj September 1854":
        "resembles Franciscus Sestan 1853 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josephus Belobarbić infant died Senj December 1854":
        "resembles Josephus Josip Rivosechi 1853 [children of maria-fabianic-fabiani] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Babić porter died Senj July 1855":
        "resembles Joannes Ivan Boras 1855 [spouses of vladimira-baricevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Karić aged 22 died Senj April 1855":
        "resembles Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Žubrinić 1855 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonius Babić aged 2 died Senj August 1855":
        "resembles Antonius Defranceschi 1855 [children of francisca-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Antonius Belobarbić aged 14 died Senj August 1855":
        "resembles Antonius Defranceschi 1855 [children of francisca-2] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Babić aged 6 died Senj August 1855":
        "resembles Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Žubrinić 1855 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Romana Babić aged 4 died Senj August 1855":
        "resembles Francisca Sestan 1856 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Babić aged 2 died Senj August 1855":
        "resembles Maria Sestan 1854 [children of sancta-alexandra-defranceschi]; Maria Magdalena Žubrinić 1855 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Tomljanović aged 2 died Senj November 1855":
        "resembles Joannes Ivan Boras 1855 [spouses of vladimira-baricevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Babić servant died Senj June 1856":
        "resembles Francisca Sestan 1856 [children of joanna-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Babić aged 2 died Senj August 1856":
        "resembles Maria Žubrinić Xubrinic 1857 [children of matia-banic]; Maria Perpic 1857 [spouses of ivan-blazevic-4]; Maria Magdalena Žubrinić 1855 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joanna Smojver aged 57 died Senj October 1856":
        "resembles Joanna Žubrinić 1856 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joanna Vukelić aged 2 died Senj January 1857":
        "resembles Joanna Žubrinić 1856 [children of maria-matasic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Babić aged 5 died Senj March 1857":
        "resembles Maria Mariam 1858 [siblings of christophorus]; Maria Žubrinić Xubrinic 1857 [children of matia-banic]; Maria Blažević 1858 [children of anton-kljapo-blazevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Vukelić aged 2 died Senj April 1857":
        "resembles Franciscus Sestan 1857 [children of sancta-alexandra-defranceschi] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Butković aged 5 died Senj August 1857":
        "resembles Maria Mariam 1858 [siblings of christophorus]; Maria Žubrinić Xubrinic 1857 [children of matia-banic]; Maria Blažević 1858 [children of anton-kljapo-blazevic] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Jacobus Borić finance watchman aged 19 died Senj November 1857":
        "resembles Jacobus Perpic 1858 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Anna Smojver widow aged 90 died Senj November 1858":
        "resembles Maria Anna Antonia Boras 1859 [children of josip-josephus-boras]; Anna Kalanj 1859 [children of ivan-joannes-kalanj-2]; Anna Žubrinić 1857 [children of lucia-luce-pesun-posun] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Maria Špalj bride 1814":
        "resembles Maria Žubrinić 1814 [children of barbara] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Franciscus Babić of Novigrad groom 1815":
        "resembles Franciscus Francisci Žubrinić Xubrinich Zubrinic 1815 [spouses of magdalena-5] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Ivan Belobarbić groom 1849":
        "resembles Ivan Papić (Papa) 1850 [children of kate-loncaric]; Ivan Žubrinić 1850 [published] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Josip Pavetić groom 1849":
        "resembles Josephus Josip Kalanj 1850 [children of antonius-kalanj] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Francisca Pilipić daughter of Franciscus died Senj June 1827":
        "resembles Francisca Žubrinić Xubrinich 1827 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Gregorius Tomljanović son of Antonius died Senj February 1831":
        "resembles Gregorius Josephus Žubrinić 1832 [children of maria-9] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
    "Joannes Perpić newborn died Senj February 1820":
        "resembles Joannes Juan Ivan Ive Žubrinić Zubrinic 1821 [children of margarita-3]; Joannes Žubrinić Xubrinich 1821 [children of lucia-gercsevich] - a different surname and different parents in the tree; the resemblance is a given name and a year. This row is a Senj-volume walk reading (13-14 Oct 2026), see notes/senj-marriage-volume-walk.md",
}


def flat(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(s):
    return {t for t in re.findall(r"[a-z]+", flat(s)) if len(t) > 2}


def year(s):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", str(s or ""))
    return int(m.group(1)) if m else None


def main():
    quiet = "--quiet" in sys.argv
    people = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))
    if isinstance(people, dict):
        people = people.get("rows", [])
    by = {p.get("slug"): p for p in people}

    # Every name in the tree, wherever it hides.
    cands = []
    for p in people:
        cands.append((p.get("name"), year(p.get("born")), "published", p.get("slug")))
        for kind, lst in (p.get("rel") or {}).items():
            for x in (lst or []):
                if not x.get("name"):
                    continue
                b = x.get("born")
                cands.append((x["name"], b if isinstance(b, int) else year(b),
                              f"{kind} of {p.get('slug')}", x.get("slug")))

    def parents_of(slug):
        p = by.get(slug)
        return [q.get("name") for q in ((p or {}).get("rel", {}) or {}).get("parents") or []]

    rows, malformed = [], []
    for n, line in enumerate(open(FOUND, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        if line.count("|") != 6:
            malformed.append(n)
            continue
        rows.append([x.strip() for x in line.split("|")])
    if malformed or not rows or not people:
        print(f"found.psv — REFUSED: {len(rows)} usable row(s), {len(people)} published "
              f"people, {len(malformed)} malformed line(s) {malformed[:10]}; a check that "
              f"examined nobody has not passed")
        return 1

    problems = []
    for name, ahn, relation, event, date, place, cite in rows:
        ft, fy = toks(name), year(date)
        given = (re.findall(r"[a-z]+", flat(name)) or [""])[0]
        rel_t = toks(relation)
        hits = []
        for cname, cy, src, cslug in cands:
            ct = toks(cname)
            if given not in ct or not (ft & ct):
                continue
            # A year that is known on both sides and far apart settles it on its
            # own. Without this a Stephanus of 1769 «matches» one of 1858 because
            # his father was also a Michael.
            if fy and cy and abs(cy - fy) > 3:
                continue
            by_year = fy and cy and abs(cy - fy) <= 1
            par = [p for p in parents_of(cslug) if p]
            # Both parents must match, and a parent matches only when BOTH its
            # given name and its surname are in the relation text. One shared
            # «Maria» is not a parent in common.
            def parent_matches(p):
                pt = [t for t in re.findall(r"[a-z]+", flat(p)) if len(t) > 2]
                need = 2 if len(pt) > 1 else 1
                return sum(1 for t in set(pt) if t in rel_t) >= need
            by_parents = bool(par) and all(parent_matches(p) for p in par)
            if by_year or by_parents:
                hits.append((cname, cy, src, cslug, by_parents))
        seen, uniq = set(), []
        for h in hits:
            k = (flat(h[0]), h[1], h[3])
            if k not in seen:
                seen.add(k)
                uniq.append(h)
        if uniq:
            problems.append((name, fy, uniq))

    unsettled = [p for p in problems if p[0] not in SETTLED]
    if not quiet:
        for name, fy, uniq in problems:
            mark = "settled" if name in SETTLED else "UNSETTLED"
            print(f"  {mark:9} {name} ({fy or 'no year'}) — {len(uniq)} candidate(s)")
            for cname, cy, src, cslug, bp in uniq[:4]:
                flagp = " ← PARENTS AGREE" if bp else ""
                print(f"            {cname} {cy or '?'} [{src}]{flagp}")
            if name in SETTLED:
                print(f"            settled: {SETTLED[name]}")
    print(f"found.psv — {len(rows)} people, {len(problems)} resemble somebody in the tree, "
          f"{len(unsettled)} of them unsettled")
    if unsettled:
        print("\nA found.psv row claims somebody is NOT in the tree and they look like "
              "somebody who is.\nDecide, then add the name to SETTLED in this file with "
              "the reason, or take the row out.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
