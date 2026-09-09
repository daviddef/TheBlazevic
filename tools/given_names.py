#!/usr/bin/env python3
"""Cluster the given names in the register into one entry per person-name.

These registers were kept in Latin, then in Croatian, and the same child is
Joannes in one book and Ivan in the next. A reader searching "Ivan" should not
be shown half the Ivans. This builds the equivalence table from the names that
are actually in the data, and writes it where the site can use it.
"""
import json, re, os, collections, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

# Canonical Croatian form -> every spelling the registers use for it.
# Latin nominatives and accusatives both appear, because a priest writing
# "baptizavi Josephum" declines the name he is writing down.
GROUPS = {
    "ivan":      ["ivan","ivo","ive","joannes","joannis","joannem","ioannes","joann",
                  "john","juan","giovanni","jovan","ivica"],
    "marija":    ["marija","maria","mariam","mary","mare","mara","marica","mica"],
    "josip":     ["josip","joso","jozo","pepe","josephus","josephum","josephi","joseph",
                  "giuseppe","jospi"],
    "ante":      ["ante","anton","antun","antonius","antonium","antonio","tone","toni"],
    "antonija":  ["antonija","antonia","antoniam","tonka","tonica","antica","toncika"],
    "ana":       ["ana","anna","annam","anica","ankica","anka","hana"],
    "franjo":    ["franjo","frane","franciscus","franciscum","francesco","frank","fran"],
    "franciska": ["franciska","francisca","franciscam","franka","francika","fanika"],
    "mihovil":   ["mihovil","miho","mijo","michael","michaelis","michaelem"],
    "toma":      ["toma","tomo","thomas","thomam","tome","tomislav"],
    "matija":    ["matija","mate","mato","mathias","matthias","mathiam","matthaeus",
                  "matthaus","mattheam","matthea","matia","matthaeus","matej"],
    "juraj":     ["juraj","jure","jurko","georgius","georgium","georgii","georgio",
                  "gjuro","djuro","george","gjuka"],
    "nikola":    ["nikola","niko","miko","nicolaus","nicolaum","nicolai","nikula"],
    "katarina":  ["katarina","kata","katica","kate","catharina","catharinam","catta",
                  "catarina","katharina"],
    "stjepan":   ["stjepan","stipe","stephanus","stephanum","stevo","steve"],
    "luka":      ["luka","lucas","lucam","luce"],
    "lucija":    ["lucija","lucia","luciam","luca","luce?"],
    "magdalena": ["magdalena","manda","mande","magda"],
    "elizabeta": ["elizabeta","jelena","helena","helenam","jela","ela"],
    "petar":     ["petar","pere","pero","petrus","petrum","peter","pietro"],
    "vinko":     ["vinko","vicko","vincentius","vincentium","vicentius","vincent","vincenc"],
    "pavao":     ["pavao","pave","paulus","paulum","pauli","paul","pavle"],
    "ilija":     ["ilija","elias","eliam","ilia"],
    "terezija":  ["terezija","tereza","terezia","theresia","teresa"],
    "margarita": ["margarita","margaretha","margarethe","marta","martha","margareta"],
    "andrija":   ["andrija","andre","andreas","andream","andrea"],
    "martin":    ["martin","martinus","martinum"],
    "grgur":     ["grgur","grga","grgica","gregorius","gregorium"],
    "jakov":     ["jakov","jakob","jacobus","jacobum","jacob","jaco"],
}

SEX = {"ivan":"m","marija":"f","josip":"m","ante":"m","antonija":"f","ana":"f",
       "franjo":"m","franciska":"f","mihovil":"m","toma":"m","matija":"m","juraj":"m",
       "nikola":"m","katarina":"f","stjepan":"m","luka":"m","lucija":"f",
       "magdalena":"f","elizabeta":"f","petar":"m","vinko":"m","pavao":"m","ilija":"m",
       "terezija":"f","margarita":"f","andrija":"m","martin":"m","grgur":"m","jakov":"m"}

VAR = {v: k for k, vs in GROUPS.items() for v in vs}


def strip(s):
    return (s or "").lower().replace("ž","z").replace("ć","c").replace("č","c") \
                            .replace("š","s").replace("đ","d").replace("ë","e") \
                            .replace("æ","ae").strip(' "?.')


def canon(token):
    t = strip(token)
    return VAR.get(t, t)


def first_token(given):
    for t in re.split(r"[\s/]+", (given or "").strip()):
        t = t.strip('"')
        if t:
            return t
    return ""


if __name__ == "__main__":
    people = []
    for f in ("people.json", "ancestors.json"):
        people += json.load(open(os.path.join(DATA, f), encoding="utf-8"))
    byid = {p["id"]: p for p in people}

    seen = collections.defaultdict(collections.Counter)
    for p in byid.values():
        t = first_token(p.get("given"))
        if t:
            seen[canon(t)][t] += 1

    merged = {k: dict(v) for k, v in seen.items() if len(v) > 1}
    out = {"groups": {k: sorted(GROUPS[k]) for k in GROUPS},
           "sex": SEX,
           "observed": {k: dict(sorted(v.items(), key=lambda kv: -kv[1]))
                        for k, v in sorted(merged.items(),
                                           key=lambda kv: -sum(kv[1].values()))}}
    json.dump(out, open(os.path.join(DATA, "givennames.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"{len(byid)} people, {len(seen)} canonical given names")
    print(f"{len(merged)} of them appear under more than one spelling\n")
    for k, v in list(out["observed"].items())[:14]:
        tot = sum(v.values())
        print(f'  {tot:>4}  {k:<11} {", ".join(f"{n}×{c}" for n, c in v.items())}')
