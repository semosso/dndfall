import json
import re  # for regex, still unused

## converts json from external file into list of dicts
with open(file="raw_spells.json", mode="r", encoding="utf-8") as raw_json:
    RAW_SPELLS: list[dict] = json.load(raw_json)

## defines information to track, as separate sets
## TBD "charmed", tricky
CONDITIONS: set[str] = {
    "blinded",
    "charmed",
    "deafened",
    "frightened",
    "grappled",
    "incapacitated",
    "invisible",
    "paralyzed",
    "petrified",
}

## TBD if I'll have to add non-magical (bludgeoning, slashing, piercing)
DMG_TYPE: set[str] = {
    "acid",
    "cold",
    "fire",
    "force",
    "lightning",
    "necroctic",
    "poison",
    "psychic",
    "radiant",
    "thunder",
}

## TBD if I care about position in list (e.g., a-z)?
## tried with sets, but unordered upset me
FIELDS: tuple = ("name", "level", "casting_time", "concentration")


## helper 1: initial intake of spells, spells=[[spell]=[(key, value)]]
## now it's fine, for learning purposes, but change it later
## this shows the point of raw > normalized > curated (currenly mixing 2 and 3)
def init_spells(data: list = RAW_SPELLS) -> list:
    # to do:
    # 1, mutate is fine for initial intake, but beware
    # 2, adapt for additional spells/conditions only (maybe at JSON level)
    # 3, make it agnostic for monsters etc.
    spells: list[list[tuple]] = []
    for raw_spell in RAW_SPELLS:
        spell: list[tuple] = []
        # comprehension got rid of 4 lines; consolidates description into string
        rev_desc: str = " ".join([e.strip() for e in raw_spell["desc"]])
        for key in FIELDS:
            spell.append((f"{key}", raw_spell[key]))
        for key in CONDITIONS:  # for str in set
            if key in rev_desc:
                spell.append(("conditions", key))
        for key in DMG_TYPE:
            # to do:
            # 1, regex for XdX damage, will avoid descriptive language
            # 2, match regex before going through each dmg_type
            # (cont): maybe the condition search can do it, and then call this one
            if key in rev_desc:
                spell.append(("damage_type", key))
        spell.append(("description", rev_desc))  # description as last element
        spells.append(spell)

    return spells


## helper 2: adding additional key,value pairs and/or spells
def add_value():
    # should add only if the spell requires it
    pass


def add_spell():
    pass


spells = init_spells(RAW_SPELLS)
for e in spells:
    print(e, "\n")
