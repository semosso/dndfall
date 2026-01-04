# todo: only working on spells for now
from curses import raw

import json  # for data intake from SRD
import re  # for info extraction

# PART 1, getting JSON data (selected number of spells from local json)
# todo: API calls to 5e SRD database, see https://5e-bits.github.io/docs/
with open(
    file="/home/vinicius/projects/dndfall/raw_spells.json", mode="r", encoding="utf-8"
) as raw_json:
    raw_spells: list[dict] = json.load(raw_json)

# PART 2, templating how data should look: raw (JSON above), normalized and finally curated
# normalized vs. curated: curated is barebones + tags extracted from normalized
# field information (e.g., school, duration), stays in normalized and should be queriable. TBD if this makes sense.
# P.s., multiple lambdas not only, but also to avoid aliasing between dicts
# (cont) I kept them in non mutables for consistency, but TBD
NORMALIZED_SCHEME: dict = {
    "index": lambda x: x,  # do I want this?
    "name": lambda x: x,
    "level": lambda x: x,
    "concentration": lambda x: x,
    "ritual": lambda x: x,
    "school": lambda x: x["name"],
    "range": lambda x: x,
    "components": lambda x: list(x),  # do I need this?
    "material": lambda x: x if "GP" in x else None,
    "duration": lambda x: x,
    "casting_time": lambda x: x,
    "classes": lambda x: [c["name"] for c in x],
    "higher_level": lambda x: (True, x) if x else False,
    # how could I change this to "description" and still get the data ("desc" in JSON)?
    "desc": lambda x: " ".join([s.strip() for s in x]),
}


# works on any structure to move it forward; raw to normalized, normalized to curated
def normalizing_JSON(
    raw_json: list = raw_spells, norm_format: dict = NORMALIZED_SCHEME
) -> list:
    normalized_spells: list[dict] = []
    for spell in raw_json:
        n_spell: dict = {}
        for key, fn in norm_format.items():
            if key in spell:
                n_spell[key] = fn(spell[key])
        normalized_spells.append(n_spell)
    return normalized_spells


# PART 3A, deciding which information should be extracted from description
# Fields vs. extration: level or school are fields; conditions, damage type etc. have to be extracted
# Anything extracted should be added as internal tags, queriable with specific syntax
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
    # TBD, will I have to add non-magical (bludgeoning, slashing, piercing)?
    # add "no_damage" as a tag, or do it via search syntax (e.g., != damage)
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

SAVING_THROW: set[str] = {
    "strength",
    "dexterity",
    "constitution",
    "wisdom",
    "intelligence",
    "charisma",
}  # on extract, better to look for "has to make a * saving throw",
# and then divide? or better to pull from here?

TAG_RULES: dict = {
    "conditions": [(r"\b{cond}").format(cond=cond) for cond in CONDITIONS],
    "damage_type": [
        (r"\b[0-9]+d[0-9]+(\+[0-9]+)? {dmg} damage").format(dmg=dmg)
        # melhor \d+?
        # just {dmg} damage should do it
        for dmg in DAMAGE_TYPE
    ],
    # "target": [],
    # "saving_throw": [],
    # "teleport": [],
    # "healing": [], "heal XX points", "regain" in cure
    # "buff": [], # bless-like, "adds the number"; receives immunity, resistance etc.
    # "debuff": [], # bane-like, "subtracts the number"
    # "restoration": [] # ends disease, condition etc.
    # "adv/disav": [] # gives one or the other
    # "average_damage": hardcode average
    #
}


# PART 3B: actual extraction mechanism: loops through NORMALIZED spell description, returns tags
# extract() works on normalized dict, tag() initializes and works on curated one -- seems OK
# I actually don't care about the return other than for the tag function. maybe nest it there?
def extract_tags(spell: dict, search_pattern: dict):
    tags: set = set()
    description: str = spell["desc"].lower()
    for key, rule in TAG_RULES.items():
        for pattern in rule:
            if match := re.search(pattern=pattern, string=description):
                tags.add((key, match.group()))  # TBD if I want the key
    return tags


# PART 3C: puts together the curated dict; what should it look like?
# TBH I don't care. NORMALIZED is the source of truth (actually not, but close)
# CURATED is opinion based; what matters are my opinions, the tags I think are relevant to index for query
# all the FACTUAL stuff is still accessible through the normalized (e.g., defined fields)
# this can "easily" be used with other categories, monsters etc. (create a pattern for each)
def curate_spells(normalized_spells: list[dict], patterns: dict):
    curated_spells: list[dict] = []
    for spell in normalized_spells:
        c_spell: dict = {
            "name": spell["name"],
            "level": spell["level"],
            "school": spell["school"],
            "tags": extract_tags(spell, patterns),
        }
        curated_spells.append(c_spell)
    return curated_spells


norm: list[dict] = normalizing_JSON()
print(curate_spells(normalized_spells=norm, patterns=TAG_RULES))

# PART 4, search engine, replicating scryfall's formal syntax idea
# e.g., l:/level: (<, <=, \==, >=, >, !=), c:/condition: (T/F, \==, fuzzy later, !=), etc.


# PART 5, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
