import re

# creates the CATEGORIES that I want to extract from Spell["description"]
# CATEGORIES have Types, e.g., DAMAGE_TYPE has Fire, CONDITION has Blinded
CONDITION: set[str] = {
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
    # TBD, do I care about non-magical (bludgeoning, slashing, piercing)?
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
}

# creates the tagging rules for each CATEGORY, Type
# each CATEGORY has PATTERNS for creating its or its Types' REGEX
TAG_RULES: dict = {
    # K are tag_values, V are tag_patterns
    "condition": {value: re.compile(pattern=rf"\b{value}\b") for value in CONDITION},
    "damage_type": {
        # eventually, separate dice and type into groups, for average damage
        value: [
            re.compile(
                pattern=rf"\b[0-9]+\s?d\s?[0-9]+\s?(\+[0-9]+)? {value} damage",
                flags=re.IGNORECASE,
            ),
            re.compile(pattern=rf"\btake(s)? {value} damage", flags=re.IGNORECASE),
        ]
        + (
            [  # specific to FORBIDDANCE, which has this weird language
                re.compile(pattern=r"5d10 radiant or necrotic", flags=re.IGNORECASE)
            ]
            if value in ["radiant", "necrotic"]
            else []
        )
        for value in DAMAGE_TYPE
        # match half damage? sort of intersection between DMG and ST
    },
    "saving_throw": {
        value: [
            # ignores certain spells on purpose, focus is on things that force ST
            # e.g., Resurrection (-4 penalty), Bless (+ 1d4), Heroes' Feast (advantage)
            re.compile(
                pattern=rf"\b(make(s)?|succeed on)\s+(a|another)\s+(DC [0-9]+\s+)?(new|successful)?\s*{value} saving throw",
                flags=re.IGNORECASE,
            ),
            # HOLD MONSTER and CONFUSION in SRD: "make a saving throw of Wisdom"
            ## add to notes on platform
            re.compile(pattern=rf"\bsaving throw of {value}", flags=re.IGNORECASE),
            # Contact Other Plane, "make a DC 15 intelligence saving throw"
            re.compile(
                pattern=rf"make\s+a\s+DC\s+15\s+{value}\s+saving\s+throw",
                flags=re.IGNORECASE,
            ),
        ]
        for value in SAVING_THROW
    },
}


# material:  if re.search(r"\b[0-9]+( )?gp\b", x.lower()) else None
# "higher_level": lambda x: x or None


# loops through NORMALIZED spell description, returns tags (category: type)
# 11/1, 5pm: expects to receive a dict of patterns, so it doesn't work with other rules
def extract_tags(spell_description: str, rules: dict = TAG_RULES) -> dict:
    tags: dict[str, list[str] | bool] = {}

    for category, patterns in rules.items():  # for condition, REGEX patterns dict
        found_tag: list[str] = []
        for tag, regexes in patterns.items():  # for "blinded", "\bblinded\b"
            # if regexes is a list, proceed; if not, make and use a list
            regex_list: list = regexes if isinstance(regexes, list) else [regexes]
            if any(regex.search(string=spell_description) for regex in regex_list):
                found_tag.append(tag)  # found_tag = ["blinded"]
        if found_tag:
            tags[category] = found_tag  # tags = {"condition": "blinded"}
        tags["no_damage"] = "damage_type" not in tags

    return tags
