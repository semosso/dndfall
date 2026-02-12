import re
from collections.abc import Callable
from enum import StrEnum
from dataclasses import dataclass, field


## helper schema: distance, shape and time blocks, dice types, operators etc.

LENGTH_UNIT: dict = {
    "foot": {
        "aliases": ["foot", "feet", "ft", "ft."],
        "ratio": 1.0,
    },
    "mile": {
        "aliases": ["mile", "miles", "mi", "mi."],
        "ratio": 5280.0,
    },
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
    "shapes": ["cone", "cube", "cylinder", "line", "sphere"],
}

SIZE_UNIT: dict = {
    # tiny, small, large, huge, gargantuan and how they interact (i.e., < or >)
}

DICE_UNITS: dict = {
    "d4": 2.5,
    "d6": 3.5,
    "d8": 4.5,
    "d10": 5.5,
    "d12": 6.5,
    "d20": 10.5,
}


class NumericOp(StrEnum):
    EQ = ":"
    N_EQ = "!="
    GT_E = ">="
    GT = ">"
    LT_E = "<="
    LT = "<"


class TextOp(StrEnum):
    EQ = ":"
    N_EQ = "!="


class BooleanOp(StrEnum):
    IS = ":"


class DiceRoll:
    def __init__(self, match):
        self.match = match
        self.amount, self.die, self.modifier = "", "", ""
        pattern = next(iter(DAMAGE_AMOUNT.patterns))
        result = re.search(pattern, self.match)
        if result:
            self.amount = result.group(1)
            self.die = result.group(2)
            self.modifier = result.group(3) if result.group(3) else 0

    def avg_damage(self):
        return (DICE_UNITS[self.die] * int(self.amount)) + int(self.modifier)

    def max_damage(self):
        pass


class Range_:
    def generate_range_pattern():
        foot_aliases = "|".join(LENGTH_UNIT["foot"]["aliases"])
        mile_aliases = "|".join(LENGTH_UNIT["mile"]["aliases"])

        pattern = rf"""(?x)
        \b([0-9]+)\s*-?\s*
        ({foot_aliases}|{mile_aliases})*
        """

        return {pattern}

    def __init__(self, match):
        self.match = match
        self.number, self.unit = "", ""
        pattern = next(iter(RANGE_.patterns))
        result = re.search(pattern, self.match)
        if result:
            self.number = result.group(1)
            self.unit = result.group(2)

    def get_size(self):

        def find_ratio(value, categories):
            for category in categories:
                if value in LENGTH_UNIT[category]["aliases"]:
                    return LENGTH_UNIT[category]["ratio"]
            return 1.0  # base case

        unit_ratio = find_ratio(self.unit, ["foot", "mile"])

        return int(self.number) * unit_ratio


## spell classes


@dataclass
class NormalizedSpell:
    name: str
    level: int
    concentration: bool
    ritual: bool
    school: str
    range_: str
    components: str
    material: str | None
    duration: str
    casting_time: str
    classes: list[str]
    higher_level: bool | tuple[bool, str]
    description: list
    url: str
    tags: dict[str, list[str] | bool] = field(init=False)


@dataclass
class TagRule:
    # for edge cases that have to be handled in addition to regex
    # FORBIDDANCE's damage_type (r"\b5d10 radiant or necrotic)
    # edge_rules: list[TagRule] | None = None
    pass


## field classes


@dataclass(kw_only=True)
class SpellField:
    name: str
    aliases: set[str]
    operator: type[StrEnum]
    values: set[str | bool] | range


@dataclass
class ScalarField(SpellField):
    pass


LEVEL: ScalarField = ScalarField(
    name="level",
    aliases={"level", "l"},
    operator=NumericOp,
    values=range(0, 10),
)


CONCENTRATION: ScalarField = ScalarField(
    name="concentration",
    aliases={"concentration", "conc"},
    operator=BooleanOp,
    values={True, False},
)


RITUAL: ScalarField = ScalarField(
    name="ritual",
    aliases={"ritual", "r"},
    operator=BooleanOp,
    values={True, False},
)


UPCASTABLE: ScalarField = ScalarField(
    name="higher_level",
    aliases={"upcast", "up"},
    operator=BooleanOp,
    values={True, False},
)


@dataclass(kw_only=True)
class DerivedField(SpellField):
    source: str
    patterns: set[str] = field(default_factory=set)
    values: set[str | bool] | range = field(default_factory=set)
    use_capture: bool = False
    transform: Callable | None = None

    def derive_tags(self, spell: NormalizedSpell):
        """Compiles regex patterns based on the DerivedValue instance's subvalues
        and search patterns.
        Returns a list of (subvalue, regex object) tuples."""
        """Given a spell (NormalizedSpell instance), extracts tags based on the
        DerivedValue instance.
        Returns a list of tags."""
        source_text: list | bool | None = getattr(spell, self.source, None)
        # some spells don't have source (e.g., when source is "material")
        if source_text is None:
            return []
        source_str = (
            " ".join(" ".join(source_text).split())
            if isinstance(source_text, list)
            else source_text
        )
        matches: list[str] = []
        if not self.values:
            results: list = self.process_patterns(source_str)
            if results:
                matches.append(self.get_values())
        else:
            patterns: list = [
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
            for value, regex in patterns:
                if regex.search(string=source_str):
                    matches.append(value)
        return matches

    def generate_patterns(self, *args, **kwargs):
        pass

    def process_patterns(self, *args, **kwargs):
        pass

    def get_values(self, *args, **kwargs):
        pass


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
    aliases={"damage_type", "dt"},
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
        "piercing",
        "bludgeoning",
        "slashing",
    },
    source="description",
    patterns={
        r"\b[0-9]+\s?d\s?[0-9]+\s?(\+\s?[0-9]+)?\s?{value} damage\b",
        r"\btake(s)? {value} damage\b",
    },
)


DAMAGE_AMOUNT: DerivedField = DerivedField(
    name="damage_amount",
    aliases={"damage_amount", "da"},
    operator=NumericOp,
    values=set(),
    source="description",
    patterns={r"\b([0-9]+)(d[0-9]+)\s*(?:\+\s*([0-9]+))?\s*\w+\s*damage"},
    transform=lambda x: DiceRoll(x).avg_damage(),
)


@dataclass
class GpCostField(DerivedField):
    def process_patterns(self, source_text):
        self.pattern = re.compile(
            pattern=r"\b([0-9,]+)\s?[Gg][Pp]\b", flags=re.IGNORECASE
        )
        self.number = ""
        result = re.search(pattern=self.pattern, string=source_text)
        if result:
            self.number = result.group(1)
        return self.number

    def get_values(self):
        return self.number.replace(",", "")


MATERIAL_GP_COST: GpCostField = GpCostField(
    name="gp_cost",
    aliases={"gp_cost", "gp"},
    operator=NumericOp,
    values=set(),
    source="material",
    patterns={r"\b([0-9,]+)\s?[Gg][Pp]\b"},
)


# @dataclass
# class AreaOfEffectField(DerivedField):
#     @classmethod
#     def generate_aoe_patterns(cls):
#         foot_aliases = "|".join(LENGTH_UNIT["foot"]["aliases"])
#         mile_aliases = "|".join(LENGTH_UNIT["mile"]["aliases"])
#         rad_aliases = "|".join(LENGTH_UNIT["rad"]["aliases"])
#         diam_aliases = "|".join(LENGTH_UNIT["diam"]["aliases"])
#         shapes = "|".join(SHAPE_UNIT["shapes"])

#         pattern = {
#             # cone, sphere, cube (most)
#             rf"""(?x)
#         \b(?P<number>[0-9]+)\s*-?\s*
#         (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
#         (?P<rad_diam>{rad_aliases}|{diam_aliases})?\s*-?\s*
#         (?P<shape>{shapes})
#         """,
#             # cylinder after radius, I won't track height
#             # 10-foot-radius, 40-foot-high cylinder
#             rf"""(?x)
#         \b(?P<number>[0-9]+)\s*-?\s*
#         (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
#         (?P<modifier>{rad_aliases}|{diam_aliases})\s*-?\s*.*
#         (?P<shape>cylinder)
#         """,
#             # cylinder before radius, I won't track height
#             rf"""(?x)
#         \b(?P<shape>cylinder)\s+.*?
#         (?P<number>[0-9]+)\s*-?\s*
#         (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*.*
#         (?P<modifier>{rad_aliases}|{diam_aliases})
#         """,
#             # line after long
#             rf"""(?x)
#         \b(?P<number>[0-9]+)\s*-?\s*
#         (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
#         (?:\w+\s+)?
#         (?P<shape>line)
#         """,
#             # line before long
#             rf"""(?x)
#         \b(?P<shape>line)\s+.*
#         (?P<number>[0-9]+)\s+
#         (?P<unit>{foot_aliases}|{mile_aliases})
#         (?:\s+long)?
#         """,
#             # walls are also lines
#             rf"""(?x)
#         \b(?P<shape>wall)\s+.*
#         (?P<number>[0-9]+)\s+
#         (?P<unit>{foot_aliases}|{mile_aliases})
#         (?:\s+long)?
#             """,
#         }

#         return pattern

#     @classmethod
#     def process_patterns(cls, match):
#         cls.match = match
#         cls.number, cls.unit, cls.rad_diam, cls.shape = "", "", "", ""

#         for pattern in AreaOfEffectField.generate_aoe_patterns():
#             result = re.search(pattern, cls.match)
#             if result:
#                 groups = result.groupdict()

#                 cls.number = groups.get("number") or ""
#                 cls.unit = groups.get("unit") or ""
#                 cls.rad_diam = groups.get("rad_diam")
#                 cls.shape = groups.get("shape") or ""

#             if cls.number:
#                 break

#     @classmethod
#     def get_size(cls):
#         if not cls.number:
#             return None

#         def find_ratio(value, categories):
#             for category in categories:
#                 if value in LENGTH_UNIT[category]["aliases"]:
#                     return LENGTH_UNIT[category]["ratio"]
#             return 1.0  # base unit

#         unit_ratio = find_ratio(cls.unit, ["foot", "mile"])
#         rad_diam_ratio = (
#             find_ratio(cls.rad_diam, ["rad", "diam"]) if cls.rad_diam else 1.0
#         )

#         return int(cls.number) * unit_ratio * rad_diam_ratio

#     @classmethod
#     def get_shape(cls):
#         if cls.shape == "wall":
#             return "line"
#         return cls.shape


# AOE_SHAPE: AreaOfEffectField = AreaOfEffectField(
#     name="aoe_shape",
#     aliases={"aoe_shape", "ash"},
#     operator=TextOp,
#     values=set(),
#     source="description",
#     patterns=AreaOfEffectField.generate_aoe_patterns(),
#     use_capture=True,
#     transform=AreaOfEffectField.get_shape(),
# )


# AOE_SIZE: AreaOfEffectField = AreaOfEffectField(
#     name="aoe_size",
#     aliases={"aoe_size", "asz"},
#     operator=NumericOp,
#     values=set(),
#     source="description",
#     patterns=AreaOfEffectField.generate_aoe_patterns(),
#     use_capture=True,
#     transform=AreaOfEffectField.get_size(),
# )


RANGE_: DerivedField = DerivedField(
    name="range",
    aliases={"range", "rg"},
    operator=NumericOp,
    values=set(),
    source="range_",
    patterns=Range_.generate_range_pattern(),
    use_capture=True,
    transform=lambda x: Range_(x).get_size(),
)


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
        r"\b(make(s)?|succeed(s)? on|fail(s)?)\s+(?!all\s).*?\b{value} saving throw(s)?",
        r"\bsaving throw of {value}\b",
    },
)


CLASS_: DerivedField = DerivedField(
    name="class",
    aliases={"class", "cls"},
    operator=TextOp,
    values={
        "wizard",
        "sorcerer",
        "cleric",
        "paladin",
        "ranger",
        "bard",
        "druid",
        "warlock",
    },
    source="classes",
    patterns={r"\b{value}\b"},
)


SCHOOL: DerivedField = DerivedField(
    name="school",
    aliases={"school", "sch"},
    operator=TextOp,
    values={
        "abjuration",
        "conjuration",
        "divination",
        "enchantment",
        "evocation",
        "illusion",
        "necromancy",
        "transmutation",
    },
    source="school",
    patterns={r"\b{value}\b"},
)


# DURATION: DerivedField = DerivedField()
# CASTING_TIME: ScalarField = ScalarField()


# REFERENCES for other modules, automate this at some point
DERIVED_FIELDS: list = [
    CONDITION,
    DAMAGE_AMOUNT,
    DAMAGE_TYPE,
    SAVING_THROW,
    MATERIAL_GP_COST,
    CLASS_,
    SCHOOL,
    # AREA_OF_EFFECT_SIZE,
    # AREA_OF_EFFECT_SHAPE,
    RANGE_,
]
SCALAR_FIELDS: list = [
    LEVEL,
    CONCENTRATION,
    RITUAL,
    UPCASTABLE,
]


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {
        alias: field
        for field in DERIVED_FIELDS + SCALAR_FIELDS
        for alias in field.aliases
    }


FIELD_BY_ALIAS: dict = build_field_by_alias()
