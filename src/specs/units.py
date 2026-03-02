from enum import StrEnum


# valid operators, facilitates search query validation
class NumericOp(StrEnum):
    EQ = ":"
    N_EQ = "-"
    GT_E = ">="
    GT = ">"
    LT_E = "<="
    LT = "<"


class TextOp(StrEnum):
    EQ = ":"
    N_EQ = "-"


class BooleanOp(StrEnum):
    IS = ":"


# helper schema: distance, shape and time blocks, dice types, operators etc.
LENGTH_UNIT: dict = {
    "foot": {
        "aliases": ["foot", "feet", "ft", "ft."],
        "ratio": 1.0,
    },
    "mile": {
        "aliases": ["mile", "miles", "mi", "mi."],
        "ratio": 5280.0,
    },
    "touch": {"aliases": ["touch"], "ratio": 5.0},
    "self": {"aliases": ["self"], "ratio": 1.0},
    "rad": {
        "aliases": ["radius"],
        "ratio": 2.0,
    },
    "diam": {
        "aliases": ["diameter"],
        "ratio": 1.0,
    },
}

TIME_UNIT: dict = {
    "second": {
        "aliases": ["second", "seconds"],
        "ratio": 1.0,
    },
    "instantaneous": {"aliases": ["instantaneous", "instant", "inst"], "ratio": 1.0},
    "minute": {
        "aliases": ["minute", "minutes"],
        "ratio": 60.0,
    },
    "hour": {
        "aliases": ["hour", "hours"],
        "ratio": 3600.0,
    },
    "day": {
        "aliases": ["day", "days"],
        "ratio": 86400.0,
    },
    "year": {
        "aliases": ["year", "years", "yr", "yrs"],
        "ratio": 31536000.0,
    },
    "dnd_economy": {
        "aliases": ["action", "bonus", "reaction"],
        "ratio": 6.0,
    },
}

SHAPE_UNIT: dict = {
    "aliases": ["cone", "cube", "cylinder", "line", "sphere"],
}

SIZE_UNIT: dict = {
    # tiny, small, large, huge, gargantuan and how they interact (i.e., < or >)
}

CURRENCY_UNIT: dict = {
    "gold": {
        "aliases": ["gold", "gp", "gps"],
        "ratio": 1.0,
    },
    "electrum": {
        "aliases": ["electrum", "ep", "eps"],
        "ratio": 0.5,
    },
    "silver": {
        "aliases": ["silver", "sp", "sps"],
        "ratio": 0.1,
    },
    "copper": {
        "aliases": ["copper", "cp", "cps"],
        "ratio": 0.01,
    },
    "platinum": {
        "aliases": ["platinum", "pp", "pps"],
        "ratio": 10,
    },
}


class DiceRoll:
    DICE_UNITS: dict = {
        "d4": {"average": 2.5, "max": 4},
        "d6": {"average": 3.5, "max": 6},
        "d8": {"average": 4.5, "max": 8},
        "d10": {"average": 5.5, "max": 10},
        "d12": {"average": 6.5, "max": 12},
        "d20": {"average": 10.5, "max": 20},
    }

    @staticmethod
    def avg_roll(cls, number, die):
        return cls.DICE_UNITS[die]["average"] * int(number)

    @staticmethod
    def max_roll(cls, number, die):
        return cls.DICE_UNITS[die]["max"] * int(number)


def find_ratio(value, categories):
    if "foot" in categories or "rad" in categories:
        for category in categories:
            if value.lower() in LENGTH_UNIT[category]["aliases"]:
                return LENGTH_UNIT[category]["ratio"]
        return 1.0
    elif "second" in categories:
        for category in categories:
            if value.lower() in TIME_UNIT[category]["aliases"]:
                return TIME_UNIT[category]["ratio"]
        return 1.0
    elif "gold" in categories:
        for category in categories:
            if value.lower() in CURRENCY_UNIT[category]["aliases"]:
                return CURRENCY_UNIT[category]["ratio"]
        return 1.0
    else:
        return False


# field values
CONDITIONS = {
    "blinded",
    "charmed",
    "deafened",
    "frightened",
    "grappled",
    "incapacitated",
    "invisible",
    "paralyzed",
    "petrified",
    "poisoned",
    "prone",
    "restrained",
    "stunned",
    "unconscious",
}

DAMAGE_TYPES = {
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
    "piercing",
    "bludgeoning",
    "slashing",
}

ABILITIES = {
    "strength",
    "dexterity",
    "constitution",
    "wisdom",
    "intelligence",
    "charisma",
}

CLASSES = {
    "wizard",
    "sorcerer",
    "cleric",
    "paladin",
    "ranger",
    "bard",
    "druid",
    "warlock",
    "artificer",
}

SCHOOLS = {
    "abjuration",
    "conjuration",
    "divination",
    "enchantment",
    "evocation",
    "illusion",
    "necromancy",
    "transmutation",
}
