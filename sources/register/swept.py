#!/usr/bin/env python3
"""Every named individual met while reading a register, whether or not they are kin.

A baptism names the priest and two godparents; a marriage names four parents,
two witnesses and the officiant; a death names the informant. Almost none of
them are in the family tree, and until now they existed only as prose in
notes/. This is that catch, act by act, with the page it came from.

`detail` is what the source says about the person, in the source's own words
where possible. `kind`:
    swept   met while reading a register act by act
    tree    from the MyHeritage tree (added by tools/register.py, not here)

Rule followed throughout: if the register gives a trade, a rank or a house, it
is recorded; if it does not, nothing is invented.
"""

# (name, surname, detail, source)
SENJ_MARRIAGES = [
 # ---- p.303, 1909 -------------------------------------------------------
 ("Franjo Boras", "Boras", "groom, 3 Oct 1909 · brijač — barber · b. 1 Oct 1888 · only his mother is named", "Senj marriages p.303 no.21"),
 ("Ana Boras", "Boras", "mother of the groom · no father named in the entry", "Senj marriages p.303 no.21"),
 ("Ivan Boras", "Boras", "witness", "Senj marriages p.303 no.21"),
 ("Anton Papić", "Papić", "witness · nadničar — day-labourer", "Senj marriages p.303 no.21"),
 ("Petar Turina", "Turina", "officiating · kapelan", "Senj marriages p.303 no.21"),
 ("Ivan Tadić", "Tadić", "groom · kočijaš — coachman", "Senj marriages p.303 no.22"),
 ("Ivanja Marković", "Marković", "bride · radnica u tvornici duhana", "Senj marriages p.303 no.22"),
 ("Mate Tadić", "Tadić", "witness · radnik u tvornici duhana", "Senj marriages p.303 no.22"),
 ("Marija Čop", "Čop", "bride · radnica u tvornici duhana u Senju", "Senj marriages p.303 no.23"),
 # ---- p.307, 1910 -------------------------------------------------------
 ("Olga Štimac", "Štimac", "bride, 3 Jul 1910 · radnica u tvornici duhana · b. 25 Jan 1887", "Senj marriages p.307 no.12"),
 ("Šimo Štimac", "Štimac", "father of the bride · kr. nadcestar u miru — retired royal road-master", "Senj marriages p.307 no.12"),
 ("Kata Rauker", "Rauker", "mother of the bride", "Senj marriages p.307 no.12"),
 ("Božo pl. Vukelić", "Vukelić", "witness · gradski ovrhovoditelj — city bailiff · pl. = plemeniti, noble", "Senj marriages p.307 no.12"),
 ("Rudolf Vančina", "Vančina", "witness · trgovac — merchant", "Senj marriages p.307 no.12"),
 ("Ante Lončarić", "Lončarić", "officiating · dr., profesor bogoslovlja — professor of theology", "Senj marriages p.307 no.12"),
 ("Dane Pećarić", "Pećarić", "groom · mestar u tvornici duhana — master in the tobacco factory", "Senj marriages p.307 no.14"),
 ("Tereza Šanta Mandić", "Mandić", "bride · švelja — seamstress", "Senj marriages p.307 no.14"),
 ("Franjka Rukavina", "Rukavina", "bride · radnica u tvornici duhana", "Senj marriages p.307 no.13"),
 ("Vinko Javorović", "Javorović", "witness · radnik u tvornici duhana", "Senj marriages p.307 no.11"),
 # ---- p.315, 1911 -------------------------------------------------------
 ("Franjo Fabijanić", "Fabijanić", "groom, 24 Jul 1911 · nadničar · b. 4 Aug 1888", "Senj marriages p.315 no.25"),
 ("Katica Gomerčić", "Gomerčić", "bride · radnica u tvornici duhana · of Poljice kbr. 38, župa Otočac · b. 6 Nov 1891", "Senj marriages p.315 no.25"),
 ("Nikola Gomerčić", "Gomerčić", "father of the bride · poljodjelac of Poljice 38", "Senj marriages p.315 no.25"),
 ("Marija Gomerčić r. Žubrinić", "Žubrinić", "mother of the bride · †deceased · poljodjelka of Poljice kbr. 38, župa Otočac — a Žubrinić address held nowhere else in this archive", "Senj marriages p.315 no.25"),
 ("Marijan Fabijanić", "Fabijanić", "witness · cipelar — shoemaker", "Senj marriages p.315 no.25"),
 ("Nikola Malinarić", "Malinarić", "officiating · kapelan", "Senj marriages p.315 no.25"),
 ("Franciska Butković", "Butković", "bride · radnica u tvornici duhana · of Alan kbr. 29, župa Krivi Put", "Senj marriages p.315 no.23"),
 ("Josipa Vrčević", "Vrčević", "bride · radnica u tvornici duhana", "Senj marriages p.315 no.24"),
 ("Marija Lončarić", "Lončarić", "bride · radnica u tvornici duhana", "Senj marriages p.315 no.26"),
 ("Ivan Lončarić", "Lončarić", "witness · radnik u tvornici duhana", "Senj marriages p.315 no.26"),
 ("Fridrik Rambošek", "Rambošek", "groom · strojovođa in the financial guard · of Kroměříž, Moravia", "Senj marriages p.315 no.27"),
 ("Ambroz Rivosecchi", "Rivosecchi", "witness · trgovački poslovođa — trade manager", "Senj marriages p.315 no.27"),
 # ---- p.322, 1912 -------------------------------------------------------
 ("Ginro Babić", "Babić", "groom, 1 Dec 1912 · nadglednik u tvornici duhana na Rieci — supervisor at the Rijeka tobacco factory · b. 16 Apr 1890", "Senj marriages p.322 no.25"),
 ("Ivan Babić", "Babić", "father of the groom · †deceased", "Senj marriages p.322 no.25"),
 ("Karlina Škofa", "Škofa", "mother of the groom", "Senj marriages p.322 no.25"),
 ("Andrija Babić", "Babić", "witness · nadglednik u tvornici duhana na Rieci", "Senj marriages p.322 no.25"),
 ("Ambroz Rivosecchi", "Rivosecchi", "witness · trgovac s vinom — wine merchant", "Senj marriages p.322 no.25"),
 ("Josip Müller", "Müller", "officiating · kapelan", "Senj marriages p.322 no.25"),
 ("Kata Kolaković", "Kolaković", "bride · radnica u tvornici duhana u Senju · of Prozor kod Otočca", "Senj marriages p.322 no.2 (1913)"),
 ("Pera Marija Hrkalović", "Hrkalović", "bride · radnica u tvornici duhana u Senju · of Vrhovine · received from grčko-istočna into the Roman Catholic church 23 Dec 1912", "Senj marriages p.322 no.3 (1913)"),
 # ---- p.324, 1913 -------------------------------------------------------
 ("Josip Glavičić", "Glavičić", "groom, 18 May 1913 · nadničar · b. 19 Feb 1891", "Senj marriages p.324 no.11"),
 ("Lucija Prpić", "Prpić", "bride · radnica u tvornici duhana · of Mrzli Dol kbr. 53, župa Krivi Put · b. 5 Jun 1890 · sister of Mile Prpić who married Franjka Papić the following year", "Senj marriages p.324 no.11"),
 ("Petar Prpić", "Prpić", "father of the bride · poljodjelac iz Mrzlog Dola", "Senj marriages p.324 no.11"),
 ("Tonka Prpić r. Pavelić", "Pavelić", "mother of the bride · poljodjelka iz Mrzlog Dola", "Senj marriages p.324 no.11"),
 ("Zvonimir Prpić", "Prpić", "groom · pekarski pomoćnik — baker's assistant · living Rijeka", "Senj marriages p.324 no.12"),
 ("Marija Katalinić", "Katalinić", "bride · radnica u tvornici duhana · of Melnice kbr. 147, župa Vratnik", "Senj marriages p.324 no.12"),
 ("Ivan Trjan", "Trjan", "groom · radnik u tvornici duhana", "Senj marriages p.324 no.13"),
 ("Roza Jergović", "Jergović", "bride · radnica u tvornici duhana · of Vrelo, župa sv. Križ Lešće, Otočac", "Senj marriages p.324 no.13"),
 ("Franjo Rivosecchi", "Rivosecchi", "witness · pisar kod kr. suda — clerk at the royal court", "Senj marriages p.324 no.13"),
 ("Katica Štimac", "Štimac", "bride · radnica u tvornici duhana u Senju · daughter of Šime Štimac cestar and Kata Rauker — sister of Olga who married Nikola Žubrinić", "Senj marriages p.324 no.9"),
 # ---- p.326, 1913 -------------------------------------------------------
 ("Josip Nagoda", "Nagoda", "groom, 5 Oct 1913 · opančarski obrtnik · of Ogulin · b. 25 Jan 1888", "Senj marriages p.326 no.23"),
 ("Toma Nagoda", "Nagoda", "father of the groom · †deceased · klobučar — hatter", "Senj marriages p.326 no.23"),
 ("Ana Nagoda r. Skuzzi", "Skuzzi", "mother of the groom", "Senj marriages p.326 no.23"),
 ("Franjo Rivosecchi", "Rivosecchi", "groom · pisar kod kot. suda u Senju — district court clerk · udovac", "Senj marriages p.326 no.19"),
 ("Josip Rivosecchi", "Rivosecchi", "father of the groom · †deceased", "Senj marriages p.326 no.19"),
 ("Matilda Rivosecchi r. Biljan", "Biljan", "mother of the groom · udova, gostioničarka — widow, innkeeper", "Senj marriages p.326 no.19"),
 ("Viktor Rivosecchi", "Rivosecchi", "witness · gimnazijski profesor", "Senj marriages p.326 no.19"),
 ("Lucija Furlan", "Furlan", "bride · radnica u tvornici duhana", "Senj marriages p.326 no.19"),
 ("Manda Rukavina", "Rukavina", "bride · radnica u tvornici duhana", "Senj marriages p.326 no.20"),
 ("Ana Žarković", "Žarković", "bride · radnica u tvornici duhana", "Senj marriages p.326 no.21"),
 # ---- p.333, 1914 -------------------------------------------------------
 ("Mile Prpić", "Prpić", "groom, 16 Aug 1914 · lugar i nadvornik općine ogulinske — forester and overseer for Ogulin municipality · born Krivi Put · b. 9 Mar 1892", "Senj marriages p.333 no.25"),
 ("Petar Prpić", "Prpić", "father of the groom", "Senj marriages p.333 no.25"),
 ("Antonija Prpić r. Pavelić", "Pavelić", "mother of the groom", "Senj marriages p.333 no.25"),
 ("Mile Prpić", "Prpić", "witness · gostioničar — innkeeper", "Senj marriages p.333 no.25"),
 ("Zvonko M. Vukelić", "Vukelić", "witness · pivar — brewer · the middle initial matches Zvonimir Matei Vukelić, Milka's first husband; the only document found so far placing him in this family other than his own marriage", "Senj marriages p.333 no.25"),
 # ---- p.348, 1918 -------------------------------------------------------
 ("Vinko Potočnjak", "Potočnjak", "groom, 1 Apr 1918 · glasbenik u c. i kr. mornarici u Poli — musician in the Imperial and Royal Navy at Pola · udovac at 29 · b. 4 Apr 1888", "Senj marriages p.348 no.5"),
 ("Šimun Potočnjak", "Potočnjak", "father of the groom · †deceased · mornar — sailor", "Senj marriages p.348 no.5"),
 ("Marija Potočnjak r. Srdoč", "Srdoč", "mother of the groom", "Senj marriages p.348 no.5"),
 ("Josip Nagoda", "Nagoda", "witness · opančar", "Senj marriages p.348 no.5"),
 ("Franjo Blažević", "Blažević", "witness · zidar — mason", "Senj marriages p.348 no.5"),
 ("Josip Benac", "Benac", "officiating · kapelan", "Senj marriages p.348 no.5"),
 ("Anton Antić", "Antić", "groom · podčasnik — non-commissioned officer", "Senj marriages p.348 no.2"),
 ("Marija Petronio", "Petronio", "bride · radnica u tvornici duhana", "Senj marriages p.348 no.2"),
 ("Ludmila Kremenić", "Kremenić", "bride · radnica u tvornici duhana", "Senj marriages p.348 no.3"),
 # ---- p.350, 1918 -------------------------------------------------------
 ("Marko Riđan", "Riđan", "groom, 18 Aug 1918 · vojni obveznik, rezervist · of Podvrške, Slavonia · b. 2 Aug 1895", "Senj marriages p.350 no.16"),
 ("Josip Riđan", "Riđan", "father of the groom · radnik", "Senj marriages p.350 no.16"),
 ("Ivka Riđan r. Ivetić", "Ivetić", "mother of the groom", "Senj marriages p.350 no.16"),
 ("Miško Prpić", "Prpić", "witness · lugar — forester · the second Prpić of Krivi Put recorded in that office", "Senj marriages p.350 no.16"),
 ("Ambroz Rivosecchi", "Rivosecchi", "witness · trgovac vinom — wine merchant · his third appearance as a witness in this family", "Senj marriages p.350 no.16"),
 ("Luka Malinarić", "Malinarić", "officiating · kapelan", "Senj marriages p.350 no.16"),
 ("Katarina Vukelić", "Vukelić", "bride · radnica u tvornici duhana · of Krivi Put · b. 16 Jan 1895", "Senj marriages p.350 no.13"),
 ("Katarina Atalić", "Atalić", "bride · radnica u tvornici duhana · her mother entered Manda r. Žubrinić", "Senj marriages p.350 no.11"),
 # ---- p.355, 1919 -------------------------------------------------------
 ("Viktor Matijević", "Matijević", "groom, 12 May 1919 · limar — tinsmith · b. 27 Aug 1886", "Senj marriages p.355 no.18"),
 ("Mate Matijević", "Matijević", "father of the groom · †deceased", "Senj marriages p.355 no.18"),
 ("Lucija Matijević r. Tomljanović", "Tomljanović", "mother of the groom", "Senj marriages p.355 no.18"),
 ("Ivan Grünhut", "Grünhut", "witness · dimnjačar — chimney sweep", "Senj marriages p.355 no.18"),
 ("Franjo Borovinčić", "Borovinčić", "witness · profesor sv. bogoslovja — professor of sacred theology", "Senj marriages p.355 no.18"),
 ("Matija Packer", "Packer", "officiating", "Senj marriages p.355 no.18"),
 ("Marija Papić", "Papić", "bride · radnica u tvornici duhana · b. 16 Aug 1890 · daughter of †Stjepan Papić and Anica r. Fajdetić — the other Papić household in Senj", "Senj marriages p.355 no.17"),
 ("Anton Papić", "Papić", "witness · posjednik — landowner", "Senj marriages p.355 no.17"),
 ("Antun Polić", "Polić", "witness · nadčinovnik u tvornici duhana — senior clerk in the tobacco factory", "Senj marriages p.355 no.16"),
 ("Franjka Delač", "Delač", "bride · radnica u tvornici duhana", "Senj marriages p.355 no.16"),
 ("Dragica Tomljanović", "Tomljanović", "bride · radnica u tvornici duhana", "Senj marriages p.355 no.19"),
 ("Lucija Biondić", "Biondić", "bride · radnica u tvornici duhana", "Senj marriages p.355 no.20"),
 ("Anka Vukelić", "Vukelić", "bride · radnica u tvornici duhana · of Krasno", "Senj marriages p.355 no.21"),
 ("Marija Kršanić", "Kršanić", "bride · radnica u tvornici duhana", "Senj marriages p.355 no.22"),
 ("Margarita Srdoč", "Srdoč", "bride · kućanica — the only bride on the page not in the tobacco factory", "Senj marriages p.355 no.15"),
 ("Nikola Sudar", "Sudar", "groom · trgovac — merchant", "Senj marriages p.355 no.15"),
 # ---- p.359, 1919 -------------------------------------------------------
 ("Pavao Kosina", "Kosina", "groom, 20 Nov 1919 · trgovac · b. 15 Mar 1894 · killed in the air raid on Senj, 8 Oct 1943", "Senj marriages p.359 no.44"),
 ("Martin Kosina", "Kosina", "father of the groom · †deceased", "Senj marriages p.359 no.44"),
 ("Anđelika Kosina r. Boras", "Boras", "mother of the groom", "Senj marriages p.359 no.44"),
 ("Nikola Sudar", "Sudar", "witness · trgovac", "Senj marriages p.359 no.44"),
 ("Julije Prvan", "Prvan", "witness · trgovac", "Senj marriages p.359 no.44"),
 ("Antun Kosina", "Kosina", "groom, 24 Nov 1919 · trgovac · brother of Pavao — the two married four days apart", "Senj marriages p.359 no.46"),
 ("Anka Krasunić", "Krasunić", "bride · švelja — seamstress", "Senj marriages p.359 no.46"),
 ("Milan Br(i)lović", "Br(i)lović", "groom, 21 Dec 1919 · sedlar — saddler · b. 30 Oct 1899", "Senj marriages p.359 no.50"),
 ("Mile Br(i)lović", "Br(i)lović", "father of the groom", "Senj marriages p.359 no.50"),
 ("Pepica Br(i)lović r. Srdoč", "Srdoč", "mother of the groom", "Senj marriages p.359 no.50"),
 ("Josip Turčić", "Turčić", "witness · zidar — mason", "Senj marriages p.359 no.50"),
 ("Mate Tomljanović", "Tomljanović", "witness · radnik", "Senj marriages p.359 no.50"),
 ("Antun Golik", "Golik", "officiating · biskupski tajnik — episcopal secretary", "Senj marriages p.359 no.50"),
 ("Marija Ilić", "Ilić", "bride · radnica u tvornici duhana", "Senj marriages p.359 no.45"),
 ("Ivan Antić", "Antić", "witness · mašinista u tvornici duhana — machinist in the tobacco factory", "Senj marriages p.359 no.45"),
 ("Ivka Babić", "Babić", "bride · radnica u tvornici duhana", "Senj marriages p.359 no.47"),
 ("Marija Babić", "Babić", "bride · radnica u tvornici duhana", "Senj marriages p.359 no.48"),
 ("Božica Zrinski", "Zrinski", "bride · radnica u tvornici duhana", "Senj marriages p.359 no.49"),
]

SENJ_DEATHS = [
 ("Marija Nabrčnik", "Nabrčnik", "died 23 Jul 1907, aged 30 · radnica u tvornici duhana · tuberculosis — five days before Toma Blažević, of the same disease, on the same page", "Senj deaths p.225 no.59"),
 ("Dane Vukelić", "Vukelić", "died 17 Jul 1907, aged 24 · kočijaš — coachman · ustrieljen — shot · ne-providjen, without the sacraments", "Senj deaths p.225 no.57"),
 ("Marija Crnković", "Crnković", "died 10 Jul 1907, aged 24½ · anaemia acuta", "Senj deaths p.225 no.56"),
 ("Vinko Kinkela", "Kinkela", "died 23 Jul 1907, aged 1½ · catarrh. pulmon.", "Senj deaths p.225 no.58"),
 ("Šimun Srdoč", "Srdoč", "died 30 Jul 1907, aged 73 · župnik u miru, izsluženi dekan — retired parish priest and dean · marasmus", "Senj deaths p.225 no.61"),
 ("Matija Golik", "Golik", "officiating at burials · kapelan", "Senj deaths p.225"),
]

KARLOBAG = [
 ("Josephus Furich", "Furich", "officiating, 11 Mar 1768 · A.R. Dominus, parochus", "Karlobag baptisms 1768, p.296"),
 ("Franciscus de Justiniani", "Justiniani", "godfather, 1768 · Dominus · a Venetian patrician name at Karlobag", "Karlobag baptisms 1768, p.296"),
 ("Ursula", "Justiniani", "godmother, 1768 · Domina · widow of Dominus Joannes Krixich", "Karlobag baptisms 1768, p.296"),
 ("Joannes Krixich", "Krixich", "named as deceased husband of the godmother, 1768 · Dominus · Krixich is Križić — the Venetian X standing for Ž, in a second family and town", "Karlobag baptisms 1768, p.296"),
 ("Joannes Antonius Ivankovich", "Ivankovich", "officiating, 1777 and 1781 · parochus loci · writes Nomen in the genitive in 1777 and the nominative in 1781 — the same formula, the same book, four years apart", "Karlobag baptisms 1777 and 1781"),
 ("Joannes Hallinich de Zirfeld", "Hallinich", "godfather, Apr 1777 · Pro-Colonellus · read in an earlier session as Ballinich; a Feb 1779 entry carries the same surname beside the words Joës Bapta, whose two-bowled capital B settles that it is not that letter", "Karlobag baptisms 1777"),
 ("Daniel de Hofenegg", "Hofenegg", "his wife Maria stood godmother, Apr 1777 · Centurio — captain", "Karlobag baptisms 1777"),
 ("Michael Martinaz", "Martinaz", "officiating, 12 Jan 1779 · presbyter curatus loci", "Karlobag baptisms 1779, p.50"),
 ("Joannes Jankovich", "Jankovich", "godfather, 1779 · Dominus Capitaneus — captain", "Karlobag baptisms 1779, p.50"),
 ("Georgius Uroda", "Uroda", "his wife Maria stood godmother, 1779 · entered Dominus — the honorific is recorded for the Uroda family here and nowhere else", "Karlobag baptisms 1779, p.50"),
 ("Antonio Bar. de Holstein", "Holstein", "father of a child baptised Feb 1779 · Baron von Holstein, at Karlobag", "Karlobag baptisms 1779, p.51"),
 ("Joannes Baptista Hallinich de Zirfeld", "Hallinich", "godfather, Feb 1779 · Illustrissimus Dominus", "Karlobag baptisms 1779, p.51"),
 ("Margarita", "Ruskich", "godmother, Feb 1779 · Domina · widow of Wolff Georg de Ruskich", "Karlobag baptisms 1779, p.51"),
 ("Franciscus de Vukassovich", "Vukassovich", "officiating, Feb 1779 · capellanus loci", "Karlobag baptisms 1779, p.51"),
 ("Philippus Rupčich", "Rupčić", "godfather, Mar 1781", "Karlobag baptisms 1781, p.65"),
 ("Jurich", "Jurich", "officiating, 18 Jan 1754 · administrator · keeps this register in Croatian, not Latin — Letta 1754, kerstih, kumi", "Karlobag baptisms 1754, p.215"),
 ("Matija Kriškovich", "Kriškovich", "father of a second Vicenac Fabijan baptised the same day, 18 Jan 1754", "Karlobag baptisms 1754, p.215"),
 ("Ive Markova", "Markov", "godparent, 18 Jan 1754", "Karlobag baptisms 1754, p.215"),
 ("Oliva Pilipić", "Pilipić", "godmother, 18 Sep 1838 · daughter of the late Josephus Pilipić, negotiator — merchant", "Karlobag baptisms 1838, p.88"),
 ("Antonius Kukuljan", "Kukuljan", "godfather, 18 Sep 1838", "Karlobag baptisms 1838, p.88"),
]

OTOCAC = [
 ("Petrus Xubrinich", "Žubrinić", "godfather, 24 Jan 1834 · son of Franciscus Xubrinich · Vigiliarum Magister pensionatus — retired master of the watch", "Otočac baptisms 1834"),
 ("Joannes Xubrinich", "Žubrinić", "his wife Maria stood godmother, 24 Jan 1834 · Sylvarum Custos in Shumechicza — forest guard at Šumećica", "Otočac baptisms 1834"),
 ("Thomas Prsimovich", "Prsimovich", "officiating, 1834 · abbas et archipresbyter", "Otočac baptisms 1834"),
 ("Vitus Kranjčević", "Kranjčević", "godfather, 16 Mar 1845 · murarius — mason", "Otočac baptisms 1845, no.18"),
 ("Maria Žubrinić", "Žubrinić", "godmother, 16 Mar 1845 · mulier Custodis Carcerum — wife of the keeper of the gaol · a fifth Frontier office held by a Žubrinić", "Otočac baptisms 1845, no.18"),
 ("Ambrosius Brozovich", "Brozović", "officiating, 1845 · cooperator", "Otočac baptisms 1845, no.18"),
 ("Michaël Marković", "Marković", "father of a child baptised 11 Mar 1845 · his wife Magdalena née Kostelac · read at first as a second Michaël Žubrinić, which the register's word order disproves", "Otočac baptisms 1845, no.17"),
]

VRBNIK = [
 ("Michaël Kombol", "Kombol", "officiating, 14 Mar 1806 · C.L. · writes nomine followed by the accusative for every child on the page", "Vrbnik baptisms 1806, house 244"),
 ("Mathias Jellichich", "Jelličić", "godfather, 14 Mar 1806 · Judex — the village judge · with his wife Margarita", "Vrbnik baptisms 1806, house 244"),
 ("Lončarić Franich", "Lončarić", "a household on the same page · Franich underlined by the scribe as a nadimak, a house by-name", "Vrbnik baptisms 1806"),
 ("Antić Dudin", "Antić", "a household on the same page · Dudin underlined as a nadimak", "Vrbnik baptisms 1806"),
 ("Pobor Rataj", "Pobor", "a household on the same page · Rataj underlined as a nadimak", "Vrbnik baptisms 1806"),
]

ALL = (SENJ_MARRIAGES + SENJ_DEATHS + KARLOBAG + OTOCAC + VRBNIK)

# ---- added 13 September 2026 ---------------------------------------------
# The register was built before these five pages were read, and carried none of
# them. The Krivi Put page is the reason to do this properly: it holds SEVEN
# Perpic children where only one had been recorded, and four house numbers the
# gazetteer had never seen.

KRIVI_PUT_1859 = [
 ("Marcus Perpić", "Prpić", "baptised 15 May 1859, born the 13th · son of Antonius and Maria Perpić, *Confiniarii* · **Mrzli Dol N° 4** · a house this archive had not seen", "Krivi Put baptisms 1859, HDA 407 p.110 no.48"),
 ("Dojmus Pavelić", "Pavelić", "godfather, 15 May 1859, with Anna Bezjić", "Krivi Put baptisms 1859, HDA 407 p.110 no.48"),
 ("Marcus Rončević", "Rončević", "baptised 15 May 1859 · son of Rocus and Catharina Rončević, *Confiniarii* · **Krivi Put N° 46**", "Krivi Put baptisms 1859, HDA 407 p.110 no.49"),
 ("Nicolaus Perpić", "Prpić", "godfather, 15 May 1859, with Anna Krmpotić, wife of Joannes", "Krivi Put baptisms 1859, HDA 407 p.110 no.49"),
 ("Michael Perpić", "Prpić", "baptised 15 May 1859, born the 14th · son of Stephanus and Rosalia Perpić, *Confiniarii* · **Mrzli Dol N° 2**", "Krivi Put baptisms 1859, HDA 407 p.110 no.50"),
 ("Josephus Blažević", "Blažević", "godfather, 15 May 1859, to a Perpić child at Mrzli Dol — with *puella* Maria Sojat, daughter of Michael", "Krivi Put baptisms 1859, HDA 407 p.110 no.50"),
 ("Maria Sojat", "Sojat", "godmother, 15 May 1859 · entered *puella*, unmarried · Sojat is a Krivi Put family in its own right - fifteen people, and nine marriages into the Blazevici and Prpici", "Krivi Put baptisms 1859, HDA 407 p.110 no.50"),
 ("Lucas Tomljanović", "Tomljanović", "godfather at Antonija Perpić's baptism, 15 May 1859, with Anna Tomljanović, daughter of Andreas", "Krivi Put baptisms 1859, HDA 407 p.110 no.51"),
 ("Mathias Vukelić", "Vukelić", "baptised 19 May 1859 · son of Josephus and Mathia Vukelić · **Alan N° 54** · a later hand adds **† 10.I.1946**", "Krivi Put baptisms 1859, HDA 407 p.110 no.52"),
 ("Clara Tomljanović", "Tomljanović", "godmother, 19 May 1859 · entered *vidua*, widow of Stephanus", "Krivi Put baptisms 1859, HDA 407 p.110 no.52"),
 ("Ana Perpić", "Prpić", "baptised 21 May 1859, born the 20th · daughter of Antonius and Catharina Perpić · **Krivi Put N° 51**", "Krivi Put baptisms 1859, HDA 407 p.110 no.53"),
 ("Marcus Sojat", "Sojat", "godfather, 21 May 1859, with his wife Margaritha", "Krivi Put baptisms 1859, HDA 407 p.110 no.53"),
 ("Lucia Vukelić", "Vukelić", "baptised 26 May 1859, born the 25th · entered ***Posthuma*** — born after her father died · daughter of *Dominus* Antonius and Catharina Vukelić, *Confiniarii* · **Alan N° 51**", "Krivi Put baptisms 1859, HDA 407 p.110 no.54"),
 ("Georgius Šolić", "Šolić", "godfather, 26 May 1859, with Francisca Vukelić, wife of Georgius", "Krivi Put baptisms 1859, HDA 407 p.110 no.54"),
 ("Thomas Tomljanović", "Tomljanović", "baptised 2 June 1859 · son of Joannes Tomljanović and Maria · **Krivi Put N° 23**", "Krivi Put baptisms 1859, HDA 407 p.110 no.55"),
 ("Žanić", "Žanić", "officiating at every baptism on this page · *Administrator*", "Krivi Put baptisms 1859, HDA 407 p.110"),
]

KRMPOTE = [
 ("Ivo Blažević", "Blažević", "godfather, 25 October 1888, at Smokvica kbr. 114 · entered ***sin Matin*** — son of Mate · a different man from the Ive *sin Tomin* who stood in 1895", "Sv. Jakov Krmpote baptisms 1888, HDA 111 p.104 no.60"),
 ("Anica Tomljanović", "Tomljanović", "godmother, 25 October 1888, at Smokvica kbr. 114 · *seljaci*", "Sv. Jakov Krmpote baptisms 1888, HDA 111 p.104 no.60"),
 ("Fran Dominčel", "Dominčel", "officiating, October 1888 · *upravitelj župe*", "Sv. Jakov Krmpote baptisms 1888, HDA 111 p.104"),
 ("Ivo Blažević", "Blažević", "godfather, 16 April 1895, at Smokvica kbr. 114 · entered ***sin Tomin*** — son of Toma · the patronymic is a distinction the priest chose to draw", "Sv. Jakov Krmpote baptisms 1895, HDA 176 p.168 no.26"),
 ("Marija Blažević", "Blažević", "godmother, 16 April 1895, at Smokvica kbr. 114 · entered ***ćer Tomina*** — daughter of Toma", "Sv. Jakov Krmpote baptisms 1895, HDA 176 p.168 no.26"),
 ("L. Malinarić", "Malinarić", "officiating, April 1895 · *upravitelj župe*", "Sv. Jakov Krmpote baptisms 1895, HDA 176 p.168"),
 ("Vale Blažević", "Blažević", "father of a child baptised November 1888 · *seljak* at **Staro-selo 89**, with Ivka r. Pećanić — a second Blažević household in the same book", "Sv. Jakov Krmpote baptisms 1888, HDA 111 p.104 no.62"),
 ("Jakov Blažević", "Blažević", "godfather, November 1888, with Tonka Blažević", "Sv. Jakov Krmpote baptisms 1888, HDA 111 p.104 no.62"),
]

SENJ_MORE = [
 ("Josip Glavičić", "Glavičić", "godfather at Milka's baptism, 17 October 1886 · ***trhonoša***, the same trade as her father", "Senj baptisms 1886, str.122 no.96"),
 ("Ivka Filipović", "Filipović", "godmother at Milka's baptism, 17 October 1886", "Senj baptisms 1886, str.122 no.96"),
 ("Stjepan Dominez", "Dominez", "officiating at Milka's baptism, 17 October 1886 · *kapelan*", "Senj baptisms 1886, str.122 no.96"),
 ("Tereza Papić", "Papić", "died 2 June 1903, aged 4 years 7 months · *Scarlatina* · daughter of **Franjo Papić, *nadničar***, and Kate — the father the tree does not record", "Senj deaths 1903, p.162 no.51"),
 ("Bara Borić", "Borić", "died 6 June 1903, aged 17 · ***radnica u tvornici duhana u Senju*** · *Scarlatina c. m. Septichoemia*", "Senj deaths 1903, p.162 no.53"),
 ("Blaž Jelovica", "Jelovica", "died 9 June 1903, aged 20 months · *Scarlatina* · the fourth of four scarlet-fever deaths on this page in eight days", "Senj deaths 1903, p.162 no.54"),
 ("Matija Glažar", "Glažar", "officiating at these burials, June 1903 · *kapelan*", "Senj deaths 1903, p.162"),
]

ALL = ALL + KRIVI_PUT_1859 + KRMPOTE + SENJ_MORE
