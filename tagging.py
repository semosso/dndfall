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
    "condition": {
        "source": "description",
        "patterns": {cond: re.compile(pattern=rf"\b{cond}\b") for cond in CONDITION},
    },
    "damage_type": {
        # eventually, separate dice and type into groups, for average damage
        "source": "description",
        "patterns": {
            dmg_type: [
                re.compile(
                    pattern=rf"\b[0-9]+\s?d\s?[0-9]+\s?(\+[0-9]+)? {dmg_type} damage",
                    flags=re.IGNORECASE,
                ),
                re.compile(
                    pattern=rf"\btake(s)? {dmg_type} damage", flags=re.IGNORECASE
                ),
            ]
            + (
                [  # specific to FORBIDDANCE, which has this weird language
                    re.compile(pattern=r"5d10 radiant or necrotic", flags=re.IGNORECASE)
                ]
                if dmg_type in ["radiant", "necrotic"]
                else []
            )
            for dmg_type in DAMAGE_TYPE
        },
    },
    "saving_throw": {
        "source": "description",
        "patterns": {
            ability: [
                # ignores certain spells on purpose, focus is on things that force ST
                # e.g., Resurrection (-4 penalty), Bless (+ 1d4), Heroes' Feast (advantage)
                re.compile(
                    pattern=rf"\b(make(s)?|succeed on)\s+(a|another)\s+(DC [0-9]+\s+)?(new|successful)?\s*{ability} saving throw",
                    flags=re.IGNORECASE,
                ),
                # HOLD MONSTER and CONFUSION in SRD: "make a saving throw of Wisdom"
                ## add to notes on platform
                re.compile(
                    pattern=rf"\bsaving throw of {ability}", flags=re.IGNORECASE
                ),
                # Contact Other Plane, "make a DC 15 intelligence saving throw"
                re.compile(
                    pattern=rf"make\s+a\s+DC\s+15\s+{ability}\s+saving\s+throw",
                    flags=re.IGNORECASE,
                ),
            ]
            for ability in SAVING_THROW
        },
    },
    # not in description, so had to change extract_tags(), add source to each category etc.
    "material": {
        "source": "material",
        "patterns": {
            "GP_cost": re.compile(pattern=r"\b[0-9]+\s?[Gg][Pp]\b", flags=re.IGNORECASE)
        },
    },
}


def extract_tags(spell, rules: dict = TAG_RULES) -> dict[str, list[str] | bool]:
    tags: dict[str, list[str] | bool] = {}
    # for condition (category), values (source or patterns) in tag_rules
    for category, values in rules.items():
        found_tag: list[str] = []
        source_value: str | None = getattr(spell, values["source"], None)

        if not isinstance(source_value, str):
            continue  # some spells don't have material

        # for pattern in key patterns
        for tag, regexes in values["patterns"].items():
            # if regexes is a list, proceed; if not, make and use a list
            regex_list: list = regexes if isinstance(regexes, list) else [regexes]

            if any(regex.search(string=source_value) for regex in regex_list):
                # found_tag = ["blinded"]
                found_tag.append(tag)

        if found_tag:
            # tags = {"condition": "blinded"}
            tags[category] = found_tag
        # specific T/F cases from tags
        tags["no_damage"] = "damage_type" not in tags
        tags["no_saving_throw"] = "saving_throw" not in tags
    return tags
