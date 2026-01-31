import re
from enum import StrEnum
from dataclasses import dataclass, field
import rich

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

DICE_UNIT: dict = {}  # type, amount? average rolls with high enough sample size?


class NumericOp(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    GT_E = ">="
    GT = ">"
    LT_E = "<="
    LT = "<"
    value_error_msg = "be numeric (e.g., 3, not three)"

    def operation(self, user_value):
        num_operations: dict = {
            NumericOp.EQ: lambda x: x == int(user_value),
            NumericOp.N_EQ: lambda x: x != int(user_value),
            NumericOp.GT_E: lambda x: x >= int(user_value),
            NumericOp.GT: lambda x: x > int(user_value),
            NumericOp.LT_E: lambda x: x <= int(user_value),
            NumericOp.LT: lambda x: x < int(user_value),
        }
        return num_operations[self]


class TextOp(StrEnum):
    IS = ":"
    N_IS = "!="
    value_error_msg = "follow formal syntax (e.g., 'fire' for damage_type)"

    def operation(self, user_value):
        txt_operations: dict = {
            TextOp.IS: lambda x: x.lower() == user_value,
            TextOp.N_IS: lambda x: x.lower() != user_value,
        }
        return txt_operations[self]


class BooleanOp(StrEnum):
    IS = ":"
    N_IS = "!="
    pass

    def operation(self, user_value):
        bool_operations: dict = {
            BooleanOp.IS: lambda x: x is user_value,
            BooleanOp.N_IS: lambda x: x is not user_value,
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
class ScalarField(SpellField):
    aliases: set[str]
    values: set[str | str | range | type[bool]]
    operator: type[StrEnum]


LEVEL: ScalarField = ScalarField(
    name="level",
    aliases={"level", "l"},
    operator=NumericOp,  # this was a list when I had multiple op per value
    values={range(0, 10)},  # list? does this have to be ordered? why not set?
)


CONCENTRATION: ScalarField = ScalarField(
    name="concentration",
    aliases={"concentration", "conc"},
    operator=BooleanOp,
    values={bool},
)


# not all spells have this, query/validator must account for this
RITUAL: ScalarField = ScalarField(
    name="ritual", aliases={"ritual", "r"}, operator=BooleanOp, values={bool}
)


SCHOOL: ScalarField = ScalarField(
    name="school",
    aliases={"school", "sch"},
    operator=TextOp,
    values={
        "Abjuration",
        "Conjuration",
        "Divination",
        "Enchantment",
        "Evocation",
        "Illusion",
        "Necromancy",
        "Transmutation",
    },
)


@dataclass
class DerivedField(SpellField):
    values: list[DerivedValue]


@dataclass
class DerivedValue:
    name: str
    aliases: set[str]
    source: str
    operator: type[StrEnum]
    subvalues: set[str] = field(default_factory=set)
    patterns: set[str] = field(default_factory=set)

    def derive_patterns(self):
        """Compiles regex patterns based on the DerivedValue instance's subvalues
        and search patterns.
        Returns a list of (subvalue, regex object) tuples."""
        regexes: list = [
            (
                subvalue,
                re.compile(
                    pattern=template.format(value=re.escape(pattern=subvalue)),
                    flags=re.IGNORECASE,
                ),
            )
            for subvalue in self.subvalues
            for template in self.patterns
        ]
        return regexes

    def derive_tags(self, spell: NormalizedSpell):
        """Given a spell (NormalizedSpell instance), extracts tags based on the
        DerivedValue instance.
        Returns a list of tags."""
        matches: list[str] = []
        source_text: str | bool = getattr(spell, self.source)
        if not isinstance(source_text, str):
            return []

        for subvalue, regex in self.derive_patterns():
            if regex.search(string=source_text):
                matches.append(subvalue)

        return matches


CONDITION_VALUE: DerivedValue = DerivedValue(
    name="condition",
    aliases={"condition", "cond"},
    source="description",
    operator=TextOp,
    subvalues={
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
    patterns={r"\b{value}\b"},
)

CONDITION: DerivedField = DerivedField(
    name="condition",
    values=[CONDITION_VALUE],
)


DAMAGE_TYPE: DerivedValue = DerivedValue(
    name="damage_type",
    aliases={"damage_type", "dmg_type", "dt"},
    source="description",
    operator=TextOp,
    subvalues={
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
    patterns={
        r"\b[0-9]+\s?d\s?[0-9]+\s?(\+\s?[0-9]+)?\s?{value} damage\b",
        r"\btake(s)? {value} damage\b",
    },
)


DAMAGE_AMOUNT: DerivedValue = DerivedValue(
    name="damage_amount",
    aliases={"damage_amount", "dmg_amt", "da"},
    source="description",
    operator=NumericOp,
    subvalues={"8d6"},
    patterns={r"\b8d6\b"},  # is this where I call on the building blocks?
)


DAMAGE: DerivedField = DerivedField(
    name="damage",
    values=[DAMAGE_TYPE, DAMAGE_AMOUNT],
)


# should allow a search for any ST (i.e., catch any attributes)
SAVING_THROW_VALUE: DerivedValue = DerivedValue(
    name="saving_throw",
    aliases={"saving_throw", "st"},
    source="description",
    operator=TextOp,
    subvalues={
        "strength",
        "dexterity",
        "constitution",
        "wisdom",
        "intelligence",
        "charisma",
    },
    patterns={
        # r"\b(make(s)?|succeed(s)? on|fail(s)?)\s?(a|an|another)?\s?(DC [0-9]+\s?)?(new|successful)?\s*{value} saving throw(s)?"
        # r"make\s+a\s+DC\s+15\s+{value}\s+saving\s+throw",
        r"\b(make(s)?|succeed(s)? on|fail(s)?)\s?.*{value} saving throw(s)?",
        r"\bsaving throw of {value}\b",
    },
)


SAVING_THROW: DerivedField = DerivedField(
    name="saving_throw",
    values=[SAVING_THROW_VALUE],
)


MATERIAL_GP_COST: DerivedValue = DerivedValue(
    name="GP_cost",
    aliases={"material", "gp_cost", "gp"},
    source="material",
    operator=NumericOp,
    subvalues={"GP_cost"},
    patterns={r"\b[0-9]+\s?[Gg][Pp]\b"},
)


MATERIAL: DerivedField = DerivedField(name="material", values=[MATERIAL_GP_COST])


CLASS_VALUE: DerivedValue = DerivedValue(
    name="class",
    aliases={"classes", "cls"},
    source="classes",
    operator=TextOp,
    subvalues={
        "Wizard",
        "Sorcerer",
        "Cleric",
        "Paladin",
        "Ranger",
        "Bard",
        "Druid",
        "Warlock",
    },
    patterns={r"\b{value}\b"},
)


CLASS_: DerivedField = DerivedField(name="class", values=[CLASS_VALUE])

# AREA_OF_EFFECT: DerivedField = DerivedField(
# feet comes in different places in desc; I can work on them, or just display
# e.g., a spell says 10ft and 50ft, for different things and effects
#     name="area_of_effect",
#     values={
#         "shape": {
#             "aliases": {"area_of_effct", "aoe"},
#             "subvalues": {},  # reference the shape_units,
#             "patterns": [],  # is this different than the shape_units pattern?
#             "source": [],
#             "operator": TextOp,
#         }
#     },
# )

# RANGE_: DerivedField = DerivedField()
# DURATION: DerivedField = DerivedField()
# CASTING_TIME: ScalarField = ScalarField()
# HIGHER_LEVEL: ScalarField = ScalarField()


# automate this at some point, either with an _init_ hook or something else
DERIVED_FIELDS: list = [CONDITION, DAMAGE, SAVING_THROW, MATERIAL, CLASS_]
SCALAR_FIELDS: list = [LEVEL, CONCENTRATION, RITUAL, SCHOOL]


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {
        alias: value
        for field in DERIVED_FIELDS
        for value in field.values
        for alias in value.aliases
    } | {alias: field for field in SCALAR_FIELDS for alias in field.aliases}


FIELD_BY_ALIAS: dict = build_field_by_alias()

# DERIVATION_TAGS: dict = {
#     "no_damage": DAMAGE_TYPE.name,
#     "no_saving_throw": SAVING_THROW.name,
# }
