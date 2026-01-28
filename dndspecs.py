import re
from enum import StrEnum
from dataclasses import dataclass, field

## helper schema: distance, shape and time blocks, dice types, operators etc.

LENGTH_UNIT: dict = {
    "foot": {
        "aliases": ["foot", "feet", "ft", "ft."],
        "pattern": [r"\b{value}\b"],
        "ratio": 1.0,
    },
    "mile": {
        "aliases": ["mile", "miles", "mi", "mi."],
        "pattern": [r"\b{value}\b"],
        "ratio": 5280.0,
    },
}

TIME_UNIT: dict = {
    "second": {
        "aliases": ["second", "seconds"],
        "pattern": [r"\b{value}\b"],
        "ratio": 1.0,
    },
    "minute": {
        "aliases": ["minute", "minutes"],
        "pattern": [r"\b{value}\b"],
        "ratio": 60.0,
    },
    "hour": {
        "aliases": ["hour", "hours"],
        "pattern": [r"\b{value}\b"],
        "ratio": 3600.0,
    },
    "day": {
        "aliases": ["day", "days"],
        "pattern": [r"\b{value}\b"],
        "ratio": 86400.0,
    },
    "year": {
        "aliases": ["year", "years", "yr", "yrs"],
        "pattern": [r"\b{value}\b"],
        "ratio": 31536000.0,
    },
    "dnd_economy": {
        "aliases": ["action", "bonus action", "bonus", "reaction"],  # plurals?
        "pattern": [r"\b{value}\b"],  # int + alias, "spend a" etc.
        "ratio": 6.0,
    },
}

SHAPE_UNIT: dict = {  # diff than units is gonna bite me in the ass, TBAdjusted
    "shapes": {
        "values": ["cone", "cube", "cylinder", "line", "sphere"],
        "pattern": [r"\b{value}\b"],
        # diameter vs radius?
        "ratios": "",  # TBD
    },
}

SIZE_UNIT: dict = {
    # tiny, small, large, huge, gargantuan and how they interact (i.e., < or >)
}

DIE_UNIT: dict = {}  # type, amount? average rolls with high enough sample size?


class NumericOp(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    def operation(self, user_value):
        num_operations: dict = {
            NumericOp.EQ: lambda x: x == int(user_value),
            NumericOp.N_EQ: lambda x: x != int(user_value),
            NumericOp.HT_o_E: lambda x: x >= int(user_value),
            NumericOp.HT: lambda x: x > int(user_value),
            NumericOp.LT_o_E: lambda x: x <= int(user_value),
            NumericOp.LT: lambda x: x < int(user_value),
        }
        return num_operations[self]


class TextOp(StrEnum):
    IS = ":"
    IS_N = "!="

    def operation(self, user_value):
        txt_operations: dict = {
            TextOp.IS: lambda x: x.lower() == user_value,
            TextOp.IS_N: lambda x: x.lower() != user_value,
        }
        return txt_operations[self]


class BooleanOp(StrEnum):
    IS = "=="
    IS_N = "!="

    def operation(self, user_value):
        bool_operations: dict = {
            BooleanOp.IS: lambda x: x.lower() is user_value,
            BooleanOp.IS_N: lambda x: x.lower() is not user_value,
        }
        return bool_operations[self]


## spell and field classes


@dataclass
class NormalizedSpell:
    name: str
    level: int
    concentration: bool
    ritual: bool
    school: str
    range_: str
    components: list[str]  # I only care for material with GP cost, but sure
    material: str | None
    duration: str
    casting_time: str
    classes: list[str]
    higher_level: bool | tuple[bool, str]  # could be just bool | str, TBH
    description: str
    url: str
    tags: dict[str, list[str] | bool] = field(init=False)


@dataclass
class TagRule:
    ## edge cases as specific TagRules that have to be handled in addition to regex
    # FORBIDDANCE: damage_type, r"\b5d10 radiant or necrotic
    # edge_rules: list[TagRule] | None = None
    pass


@dataclass
# this class is for validation purposes by the query/validate functions
class SpellField:
    name: str


@dataclass
class DirectField(SpellField):
    aliases: set[str]
    values: list  # TBD
    operator: type[StrEnum]


LEVEL: DirectField = DirectField(
    name="level",
    aliases={"level", "l"},
    values=[range(0, 10)],  # list? does this have to be ordered? why not set?
    operator=NumericOp,  # this was a list when I had multiple op per value
)


CONCENTRATION: DirectField = DirectField(
    name="concentration",
    aliases={"concentration", "conc"},
    values=[bool],
    operator=BooleanOp,
)


# not all spells have this, query/validator must account for this
RITUAL: DirectField = DirectField(
    name="ritual", aliases={"ritual", "r"}, values=[bool], operator=BooleanOp
)


SCHOOL: DirectField = DirectField(
    name="school",
    aliases={"school", "sch"},
    values=[
        "Abjuration",
        "Conjuration",
        "Divination",
        "Enchantment",
        "Evocation",
        "Illusion",
        "Necromancy",
        "Transmutation",
    ],
    operator=TextOp,
)


CLASSES: DirectField = DirectField(
    name="classes",
    aliases={"classes", "cls"},
    values=[
        "Wizard",
        "Sorcerer",
        "Cleric",
        "Paladin",
        "Ranger",
        "Bard",
        "Druid",
        "Warlock",
    ],
    operator=TextOp,
)


@dataclass
class DerivedField(SpellField):
    values: dict[str, dict]  # add additional structure validation?

    @classmethod  # TBD
    def derive_patterns(cls, value: dict):
        regexes: list = [
            (
                subvalue,
                re.compile(
                    pattern=template.format(value=re.escape(pattern=subvalue)),
                    flags=re.IGNORECASE,
                ),
            )
            for subvalue in value["subvalues"]
            for template in value["patterns"]
        ]
        return regexes


CONDITION: DerivedField = DerivedField(
    name="condition",
    values={
        "condition": {
            "aliases": {"condition", "cond", "c"},
            # set or list? do I need to enforce order here or in caller function?
            "subvalues": {
                "blinded",
                "charmed",
                "deafened",
                "frightened",
                "grappled",
                "incapacitated",
                "invisible",
                "paralyzed",
                "petrified",
            },
            "patterns": [r"\b{value}\b"],
            "source": "description",
            "operator": TextOp,
        }
    },
)

DAMAGE: DerivedField = DerivedField(
    name="damage",
    values={
        "damage_type": {
            "aliases": {"damage_type", "dt"},
            "subvalues": {
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
            },
            "patterns": [
                r"\b[0-9]+\s?d\s?[0-9]+\s?(\+\s?[0-9]+)?\s?{value} damage\b",
                r"\btake(s)? {value} damage\b",
            ],
            "source": "description",
            "operator": TextOp,
        },
        "damage_amount": {
            "aliases": {"damage_amount", "da"},
            "subvalues": {"8d6"},
            "patterns": [r"\b8d6\b"],  # is this where I call on the building blocks?
            "source": "description",
            "operator": NumericOp,
        },
    },
)

# should allow a search for any ST (i.e., catch any attributes)
SAVING_THROW: DerivedField = DerivedField(
    name="saving_throw",
    values={
        "saving_throw": {
            "aliases": {"saving_throw", "st"},
            "subvalues": {
                "strength",
                "dexterity",
                "constitution",
                "wisdom",
                "intelligence",
                "charisma",
            },
            "patterns": [
                # r"\b(make(s)?|succeed(s)? on|fail(s)?)\s?(a|an|another)?\s?(DC [0-9]+\s?)?(new|successful)?\s*{value} saving throw(s)?"
                r"\b(make(s)?|succeed(s)? on|fail(s)?)\s?.*{value} saving throw(s)?",
                r"\bsaving throw of {value}\b",
                # r"make\s+a\s+DC\s+15\s+{value}\s+saving\s+throw",
            ],
            "source": "description",
            "operator": TextOp,
        }
    },
)

# feet comes in different places in desc; I can work on them, or just display
# e.g., a spell says 10ft and 50ft, for different things and effects
AREA_OF_EFFECT: DerivedField = DerivedField(
    name="area_of_effect",
    values={
        "shape": {
            "aliases": {"area_of_effct", "aoe"},
            "subvalues": {},  # reference the shape_units,
            "patterns": [],  # is this different than the shape_units pattern?
            "source": [],
            "operator": TextOp,
        }
    },
)


# need to group the GP_cost; want to add the tag + do comparisons
# this is not it yet, just an idea
MATERIAL: DerivedField = DerivedField(
    name="material",
    values={
        "GP_cost_text": {
            "aliases": {"gp_cost", "gp"},
            "subvalues": {},
            "patterns": [r"\b[0-9]+\s?[Gg][Pp]\b"],
            "source": [],
            "operator": TextOp,
        },
        "GP_cost_num": {
            "aliases": {"gp_cost", "gp"},
            "subvalues": {},
            "patterns": [r"\b[0-9]+\s?[Gg][Pp]\b"],
            "source": [],
            "operator": NumericOp,
        },
    },
)

# # additional derived fields, with mixed txt/op/bool values
# RANGE_: DerivedField = DerivedField()
# DURATION: DerivedField = DerivedField()
# CASTING_TIME: DirectField = DirectField()
# HIGHER_LEVEL: DirectField = DirectField()


# automate this at some point, either with an _init_ hook or something else
DERIVED_FIELDS: list = [CONDITION, DAMAGE, SAVING_THROW]
DIRECT_FIELDS: list = [LEVEL]  # , CONCENTRATION, RITUAL, SCHOOL, CLASSES

# DERIVATION_TAGS: dict = {
#     "no_damage": DAMAGE_TYPE.name,
#     "no_saving_throw": SAVING_THROW.name,
# }


# reference only
# derived_field_schema: dict = {
#     "<subtype1>": {"subvalue": "", "pattern": "", "source": "", "operator": ""},
#     "<subtype2>": {"subvalue": "", "pattern": "", "source": "", "operator": ""},
# }
