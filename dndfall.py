# todo: only working on spells for now
import json  # for data intake from SRD
import re  # for info extraction
import rich  # better visualization of data structures
from collections import defaultdict  # defaultdicts for indices (and more?)

# PART 1, getting JSON data (selected number of spells from local json)
# todo: API calls to 5e SRD database, see https://5e-bits.github.io/docs/
with open(file="data/cop.json", mode="r") as raw_json:
    raw_spells: list[dict] = json.load(raw_json)

# PART 2, templating how data should look: raw (JSON above), normalized, and curated
# normalized vs. curated: curated is normalized + tags extracted from normalized
# get rid of multiple lambdas
NORMALIZED_SCHEME: dict = {
    "index": lambda x: x,
    "name": lambda x: x,
    "level": lambda x: x,
    "concentration": lambda x: x,
    "ritual": lambda x: x,
    "school": lambda x: x["name"],
    "range": lambda x: x,
    "components": lambda x: list(x),  # do I need this?
    "material": lambda x: x if re.search(r"\b[0-9]+( )?gp\b", x.lower()) else None,
    "duration": lambda x: x,
    "casting_time": lambda x: x,
    "classes": lambda x: [c["name"] for c in x],
    "higher_level": lambda x: x or None,
    # how can I change this to "description" and still get the data ("desc" in JSON)?
    "desc": lambda x: " ".join(
        " ".join(x).split()
    ),  # joins all str in list, splits on any whitespace, joins on single
}


# normalizes data based on the predefined scheme above
def normalizing_JSON(
    raw_json: list = raw_spells, norm_format: dict = NORMALIZED_SCHEME
) -> list[dict]:
    normalized_spells: list[dict] = []
    for spell in raw_json:
        n_spell: dict = {}
        for key, fn in norm_format.items():
            if key in spell:
                n_spell[key] = fn(spell[key])
        normalized_spells.append(n_spell)
    return normalized_spells


# PART 3A, conditions, damage type etc. have to be extracted and added as internal tags
CONDITIONS: set[str] = {
    "blinded",
    "charmed",
    "deafened",
    "frightened",
    "grappled",
    "incapacitated",
    "invisible",
    "paralyzed",  # some of these call on other of these; e.g., incapacitated
    # maybe get the actual definitions of the conditions? they have their own .json
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
    "necrotic",
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

TAG_RULES: dict = {
    # K are tag_values, V are tag_patterns
    "condition": {value: re.compile(pattern=rf"\b{value}\b") for value in CONDITIONS},
    "damage_type": {
        value: re.compile(pattern=rf"\b[0-9]+ ?d ?[0-9]+ ?(\+[0-9]+)? {value} damage")
        for value in DAMAGE_TYPE
        # eventually, separate dice and type into groups, for average damage calculation
    },
    "damage_no_dice": {
        f"{value} no dice": re.compile(pattern=rf"[^0-9] {value} damage")
        for value in DAMAGE_TYPE
        ## "{dmg} damage" by itself matches several things it shouldn't (e.g., resistance to)
        ## SPIRITUAL WEAPON, "takes force damage equal to 1d8 + your spellcasting ability modifier"
        ## FORBIDDANCE, "5d10 radiant or necrotic damage" (search for similar patterns)
        ## ETHEREALNESS, "take force damage equal to twice the number of feet you moved"
        ## DELAYED FIREBALL, "a creature takes fire damage equal to", "the spell's base damage is 12d6"
    },
    # half damage? sort of intersection between DMG and ST
    "saving_throw": {
        value: re.compile(
            pattern=rf"(make(s)?|succeed on)\s+(a|another)\s+(DC [0-9]+\s+)?(new|successful)?\s*{value} saving throw"
        )
        for value in SAVING_THROW
        ## ignores certain spells on purpose, focus is on forcing a ST (add as note on platform)
        ## (e.g., Resurrection (-4 penalty to ST), Bless (+ 1d4 to ST), Heroes' Feast (adv. on ST)
    },
    "fuck you SRD": {
        value: re.compile(
            pattern=rf"saving throw of {value}"
            ## SRD description is diff, "make a saving throw of Wisdom" (HOLD MONSTER, CONFUSION)
            ## add to notes on platform
        )
        for value in SAVING_THROW
    },
    "Contact Other Plane": {
        "intelligence": re.compile(
            pattern=r"make a DC 15 intelligence saving throw"
            ## Contact Other Plane, "when you cast this spell, make a DC intelligence 15 saving throw"
            ## I cannot get this to work at all
        )
    },
}


# PART 3B: actual extraction mechanism: loops through NORMALIZED spell description, returns type and tags
def extract_tags(spell_dict: dict, tag_rules: dict = TAG_RULES) -> dict:
    tags_dict: defaultdict[str, list] = defaultdict(list)
    description: str = spell_dict["desc"].lower()

    # if I call the function once for each type (e.g., conditions, damage type),
    # I can get rid of this first loop
    for tag_values, tag_patterns in tag_rules.items():
        for tag_value, tag_pattern in tag_patterns.items():
            if tag_pattern.search(string=description):
                tags_dict[tag_values].append(tag_value)

    return dict(tags_dict)


# PART 3C: puts together the curated dict; TBD, maybe I add all fields from normalized + tags
def curate_spells(normalized_spells: list[dict], patterns: dict) -> dict:
    curated_spells: dict[str, dict] = {}
    for spell in normalized_spells:
        c_spell: dict = {
            "spell_id": spell["index"],
            "name": spell["name"],
            "level": spell["level"],
            "tags": extract_tags(spell_dict=spell, tag_rules=patterns),
            "description": spell["desc"],
        }  # can leave this empty, call extract, add to those that have it
        key: str = c_spell["name"]
        curated_spells[key] = (
            c_spell  # why does this work, w/o flagging that the key is missing?
        )
    return curated_spells


# initializing data set
norm: list[dict] = normalizing_JSON()
spells: dict[str, dict] = curate_spells(normalized_spells=norm, patterns=TAG_RULES)
rich.print(spells)  # testing

# with open(file="data/cop2.json", mode="w") as cop_test:
#     cop_test.write(spells["Contact Other Plane"]["description"])
# cop_test.close()


# PART 4, search engine, replicating scryfall's formal syntax idea
# e.g., l:/level: (<, <=, \==, >=, >, !=), c:/condit ion: (T/F, \==, fuzzy later, !=), etc.
def has_tag():
    pass


def numeric_search():
    pass


def text_search():
    pass


def set_search():
    pass


def match_spell():
    # will call on the helper ones depending on type
    # figure out how to create a good syntax
    # (i.e., how to match user's input to my operatores and helpers)
    pass


# PART 5, test suite, see notes on Obsidian
# e.g., expand spells and try language not captured by regex
# e.g., "heals" vs. "regains" HP, "{dmg}" vs. "of {dmg}", "takes damage"

# PART 6, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
