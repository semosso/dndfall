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

DICE_UNIT: dict = {}  # type, amount? average rolls with high enough sample size?


class NumericOp(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    GT_E = ">="
    GT = ">"
    LT_E = "<="
    LT = "<"


class TextOp(StrEnum):
    EQ = ":"
    N_EQ = "!="


class BooleanOp(StrEnum):
    IS = ":"
    N_IS = "!="


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
    # for edge cases that have to be handled in addition to regex
    # FORBIDDANCE's damage_type (r"\b5d10 radiant or necrotic)
    # edge_rules: list[TagRule] | None = None
    pass


@dataclass(kw_only=True)
# this class is for validation purposes by the query/validate functions
class SpellField:
    name: str
    aliases: set[str]
    operator: type[StrEnum]
    values: set[str | type[bool]] | range


@dataclass
class ScalarField(SpellField):
    pass


LEVEL: ScalarField = ScalarField(
    name="level",
    aliases={"level", "l"},
    operator=NumericOp,  # this was a list when I had multiple op per value
    values=range(0, 10),  # list? does this have to be ordered? why not set?
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


@dataclass(kw_only=True)
class DerivedField(SpellField):
    source: str
    patterns: set[str] = field(default_factory=set)
    values: set[str] | range = field(default_factory=set)
    use_capture: bool = False

    def derive_patterns(self):
        """Compiles regex patterns based on the DerivedValue instance's subvalues
        and search patterns.
        Returns a list of (subvalue, regex object) tuples."""
        if self.use_capture:
            return [
                (None, re.compile(pattern=pattern, flags=re.IGNORECASE))
                for pattern in self.patterns
            ]
        else:
            return [
                (
                    value,
                    re.compile(
                        pattern=template.format(value=re.escape(pattern=value)),
                        flags=re.IGNORECASE,
                    ),
                )
                for value in self.values
                for template in self.patterns
            ]

    def derive_tags(self, spell: NormalizedSpell):
        """Given a spell (NormalizedSpell instance), extracts tags based on the
        DerivedValue instance.
        Returns a list of tags."""
        matches: list[str] = []
        source_text: str | bool = getattr(spell, self.source)
        if not isinstance(source_text, str):
            return []

        for value, regex in self.derive_patterns():
            if self.use_capture:
                for match in regex.finditer(string=source_text):
                    if match.groups():
                        matches.append(match.group(1).replace(",", ""))
            else:
                if regex.search(string=source_text):
                    matches.append(value)

        return matches


CONDITION: DerivedField = DerivedField(
    name="condition",
    aliases={"condition", "cond"},
    operator=TextOp,
    values={
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
    source="description",
    patterns={r"\b{value}\b"},
)


DAMAGE_TYPE: DerivedField = DerivedField(
    name="damage_type",
    aliases={"damage_type", "dmg_type", "dt"},
    operator=TextOp,
    values={
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
    source="description",
    patterns={
        r"\b[0-9]+\s?d\s?[0-9]+\s?(\+\s?[0-9]+)?\s?{value} damage\b",
        r"\btake(s)? {value} damage\b",
    },
)


DAMAGE_AMOUNT: DerivedField = DerivedField(
    name="damage_amount",
    aliases={"damage_amount", "dmg_amt", "da"},
    operator=NumericOp,
    values={"8d6"},
    source="description",
    patterns={r"\b8d6\b"},  # is this where I call on the building blocks?
)


# should allow a search for any ST (i.e., catch any attributes)
SAVING_THROW: DerivedField = DerivedField(
    name="saving_throw",
    aliases={"saving_throw", "st"},
    operator=TextOp,
    values={
        "strength",
        "dexterity",
        "constitution",
        "wisdom",
        "intelligence",
        "charisma",
    },
    source="description",
    patterns={
        # r"\b(make(s)?|succeed(s)? on|fail(s)?)\s+(?:a|an|another)?\s*(?:DC [0-9]+\s*)?(?:new|successful)?\s*{value} saving throw(s)?"
        # r"make\s+a\s+DC\s+15\s+{value}\s+saving\s+throw",
        r"\b(make(s)?|succeed(s)? on|fail(s)?)\s+(?!all\s).*?\b{value} saving throw(s)?",
        r"\bsaving throw of {value}\b",
    },
)


MATERIAL_GP_COST: DerivedField = DerivedField(
    name="gp_cost",
    aliases={"material", "gp_cost", "gp"},
    operator=NumericOp,
    values=range(0, 100000000),
    source="material",
    patterns={r"\b([0-9]+(,[0-9]+)?)\s?[Gg][Pp]\b"},
    use_capture=True,
)


CLASS_: DerivedField = DerivedField(
    name="class",
    aliases={"classes", "cls"},
    operator=TextOp,
    values={
        "Wizard",
        "Sorcerer",
        "Cleric",
        "Paladin",
        "Ranger",
        "Bard",
        "Druid",
        "Warlock",
    },
    source="classes",
    patterns={r"\b{value}\b"},
)


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


# REFERENCES for other modules
# automate this at some point, either with an _init_ hook or something else
DERIVED_FIELDS: list = [
    CONDITION,
    DAMAGE_AMOUNT,
    DAMAGE_TYPE,
    SAVING_THROW,
    MATERIAL_GP_COST,
    CLASS_,
]
SCALAR_FIELDS: list = [LEVEL, CONCENTRATION, RITUAL, SCHOOL]


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {
        alias: field
        for field in DERIVED_FIELDS + SCALAR_FIELDS
        for alias in field.aliases
    }


FIELD_BY_ALIAS: dict = build_field_by_alias()

# DERIVATION_TAGS: dict = {
#     "no_damage": DAMAGE_TYPE.name,
#     "no_saving_throw": SAVING_THROW.name,
# }
