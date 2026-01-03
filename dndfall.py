import json  # for data intake from SRD
import re  # for info extraction

# get JSON data, currently a selected number of spells from a local json
# todo: API calls to 5e SRD database, see https://5e-bits.github.io/docs/
with open(file="raw_spells.json", mode="r", encoding="utf-8") as raw_json:
    RAW_SPELLS: list[dict] = json.load(raw_json)


# normalize JSON intake into a list of dicts, with my schema
# todo: 1, implement schemas for monsters etc.
# 2, typeddict in the future, to typehint each field
# 3, lambdas not only but also to avoid aliasing raw <> normalized data
# (cont) I kept them in non mutables for consistency, but TBD
def normalize_json(db: list) -> list:
    FIELDS_TO_KEEP: dict = {
        "index": lambda x: x,  #
        "name": lambda x: x,
        "level": lambda x: x,
        "concentration": lambda x: x,
        "ritual": lambda x: x,
        "school": lambda x: x["name"],
        "range": lambda x: x,
        "components": lambda x: list(x),  # do I need this to avoid aliasing?
        "material": lambda x: x if "GP" in x else None,
        "duration": lambda x: x,
        "casting_time": lambda x: x,
        "classes": lambda x: [c["name"] for c in x],
        "higher_level": lambda x: (True, x) if x else False,
        # how could I change this to "description" and still get the data?
        # printed as \n sometimes, why?
        "desc": lambda x: "\n".join([s.strip() for s in x]),
    }

    normalized_db: list[dict] = []
    for spell in RAW_SPELLS:
        normalized_spell: dict = {}
        for key, fn in FIELDS_TO_KEEP.items():
            if key in spell:
                normalized_spell[key] = fn(spell[key])
        normalized_db.append(normalized_spell)

    return normalized_db


norm_spells: list[dict] = normalize_json(RAW_SPELLS)

# extracting relevant information (i.e., not in fields)
CONDITIONS: set[str] = {
    "blinded",
    "charmed",
    "deafened",
    "frightened",
    "grappled",
    "incapacitated",
    "invisible",
    "paralyzed",  # some of these call on other of these; e.g., incapacitated
    # maybe get the actual definitions of the status conditions?
    "petrified",
}

DAMAGE_TYPE: set[str] = {
    ## TBD if I'll have to add non-magical (bludgeoning, slashing, piercing)
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

TARGET: set[str] = {
    "area_of_effect",
    "self",
    "single_creature",
    "any_number_of_creatures",
}

SAVING_THROW: set[str] = {"str", "dex", "con", "wis", "int", "cha"}

REGEX_PATTERNS: dict = {
    "conditions": [(r"\b{cond}").format(cond=cond) for cond in CONDITIONS],
    "damage_type": [
        (r"\b[0-9]+d[0-9]+(\+[0-9]+)? {dmg} damage").format(dmg=dmg)  # melhor \d+ ?
        for dmg in DAMAGE_TYPE
    ],
    "target": [],
    "saving_throw": [],
}


# loops through spell description, finds info, and creates dict of tags
def extract_info(spells: list, regex_pattern: dict):
    matches: dict = {}
    for spell in spells:
        spell_keywords: list = []
        for cond in REGEX_PATTERNS["conditions"]:  # next, expand for all patterns
            match = re.search(cond, spell["desc"])
            if match:
                spell_keywords.append(match.group())
                matches[spell["name"]] = spell_keywords
    return matches


print(extract_info(norm_spells, REGEX_PATTERNS))
# print(extract_info(norm_spells, CONDITIONS))

# # def tagging(spells: list, trackables: set):
# #     for spell in spells:


# # for con in CONDITIONS:
# #     print(extract_info(norm_spells, con))

TAG_RULES: dict = {
    "conditions": (),
    "damage_type": (),
    "average_dmg": (),
    "aoe": (),
    "saving_throw": (),
}

# print(TAG_RULES)

# # # for spell in spells:
# # #     tags:dict = {}
# # #     for tag, rule in TAG_RULES.items():
# # #         if rule in spell["desc"]:
# # #             spell[tag] =
