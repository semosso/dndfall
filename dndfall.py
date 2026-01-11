# todo: only working on spells for now
import json  # for data intake from SRD
import re  # for info extraction
import rich  # better visualization of data structures
from collections import defaultdict  # defaultdicts for indices (and more?)
from typing import TypedDict, NotRequired  # spell scheme validation


# PART 1, getting JSON data (selected number of spells from local json)
# todo: API calls to 5e SRD database, see https://5e-bits.github.io/docs/
with open(file="data/spells.json", mode="r") as raw_json:
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
    # how can I add this second case of values to the same dict above?
    # remove the "alternative" eventually, just for testing now
    "alternative_damage_type": {
        f"{value} (alternative)": re.compile(pattern=rf"\btake(s)? {value} damage")
        for value in DAMAGE_TYPE
        # captureed everything; only missing FORBIDDANCE, "5d10 radiant or necrotic damage"
        ## could itertools, but taking 3000 checks (10*10 dmg types * 300 spells) is absurd
    },
    # half damage? sort of intersection between DMG and ST
    "saving_throw": {
        value: re.compile(
            pattern=rf"\b(make(s)?|succeed on)\s+(a|another)\s+(DC [0-9]+\s+)?(new|successful)?\s*{value} saving throw"
        )
        for value in SAVING_THROW
        # ignores certain spells on purpose, focus is on things that force ST (add as note)
        # (e.g., Resurrection (-4 penalty), Bless (+ 1d4), Heroes' Feast (advantage)
    },
    "fuck you SRD": {
        value: re.compile(pattern=rf"\bsaving throw of {value}")
        for value in SAVING_THROW
        # SRD description for HOLD MONSTER, CONFUSION: "make a saving throw of Wisdom"
        ## CONFUSION still has regular language on top of it; HOLD MONSTER doesn't
        ## add to notes on platform
    },
    "Contact Other Plane": {
        "intelligence": re.compile(
            pattern=r"\bmake a DC 15 intelligence saving throw"
            # Contact Other Plane, "when you cast this spell, make a DC intelligence 15 saving throw"
            # I cannot get this to work at all
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


# PART 3C: puts together the curated dict
# I might make it all fields from normalized + tags


# trying out TypedDict, I already have some structure
class CuratedSpell(TypedDict):
    spell_id: int
    name: str
    level: int
    description: str
    tags: NotRequired[dict[str, dict[str, list[str]]]]


def curate_spells(
    normalized_spells: list[dict], patterns: dict
) -> dict[str, CuratedSpell]:
    curated_spells: dict[str, CuratedSpell] = {}
    for spell in normalized_spells:
        c_spell: CuratedSpell = {
            "spell_id": spell["index"],
            "name": spell["name"],
            "level": spell["level"],
            "description": spell["desc"],
            "tags": extract_tags(spell_dict=spell, tag_rules=patterns),
        }  # can leave this empty, call extract, add to those that have it
        curated_spells[c_spell["name"]] = c_spell
    return curated_spells


# initializing data set, move this to main guard at some point
norm: list[dict] = normalizing_JSON()
spells: dict[str, CuratedSpell] = curate_spells(
    normalized_spells=norm, patterns=TAG_RULES
)
# for v in spells.values():  # testing
#     rich.print(v["name"])
#     rich.print(v["tags"])
## key "False Life" prints as type False, figure it out
## same for "True" in Polymorph etc.


# PART 4, indexing, query and search engine
# replicate scryfall's formal syntax (e.g., l:/level: (<, <=, \==, >=, >, !=),
# c:/condit ion: (T/F, \==, fuzzy later, !=))
def create_indices(spells: dict[str, CuratedSpell]) -> dict:
    # it should look someting like this
    indices: defaultdict = defaultdict(list)

    # it should look something like this:
    {
        "level": {
            0: [spell, spell],
            1: [spell, spell],
        },
        "condition": {
            "blinded": [spell, spell],
        },
        "damage_type": {
            "fire": [spell, spell],
            "cold": [spell, spell],
        },
        "saving_throw": {
            "strength": [spell, spell],
            "dexterity": [spell, spell],
        },
    }
    pass


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
