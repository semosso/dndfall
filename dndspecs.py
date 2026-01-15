import re
from dataclasses import dataclass


@dataclass
class TagRule:
    ## edge cases as specific TagRules that have to be handled in addition to regex
    # FORBIDDANCE: damage_type, r"\b5d10 radiant or necrotic
    pass


@dataclass(frozen=True)
class TagCategory:
    name: str
    values: set[str]  # I need a data structure and an iterable, right?
    source: str
    patterns: str | list[str]
    edge_rules: list[TagRule] | None = None

    def derive_patterns(self):
        regexes: list = [
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
        return regexes


# creates the CATEGORIES that I want to extract from Spell["description"]
# CATEGORIES have Types, e.g., DAMAGE_TYPE has Fire, CONDITION has Blinded
CONDITION: TagCategory = TagCategory(
    name="condition",
    values={
        "blinded",
        "charmed",  # Hallow has "nor can such creatures charm, frighten or possess"
        "deafened",
        "frightened",
        "grappled",  # "attempts to grapple" in Arcane Hand
        "incapacitated",
        "invisible",
        "paralyzed",  # some of these call on other of these; e.g., incapacitated
        "petrified",
    },
    source="description",
    patterns=[r"\b{value}\b"],
)  # should it be Spell.description? what comes first?


DAMAGE_TYPE: TagCategory = TagCategory(
    name="damage_type",
    values={
        # TBD, do I care about non-magical (bludgeoning, slashing, piercing)?
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
    patterns=[
        r"\b[0-9]+\s?d\s?[0-9]+\s?(\+[0-9]+)? {value} damage\b",
        r"\btake(s)? {value} damage\b",
    ],
)


SAVING_THROW: TagCategory = TagCategory(
    name="saving_throw",
    values={
        "strength",
        "dexterity",
        "constitution",
        "wisdom",
        "intelligence",
        "charisma",
    },
    source="description",
    patterns=[
        r"\b(make(s)?|succeed on)\s+(a|another)\s+(DC [0-9]+\s+)?(new|successful)?\s*{value} saving throw",
        r"\bsaving throw of {value}\b",
        r"make\s+a\s+DC\s+15\s+{value}\s+saving\s+throw",
    ],
)


MATERIAL: TagCategory = TagCategory(
    name="material",
    values={"GP_cost"},
    source="material",
    patterns=[r"\b[0-9]+\s?[Gg][Pp]\b"],
)

TAG_CATEGORIES: list[TagCategory] = [CONDITION, DAMAGE_TYPE, SAVING_THROW]
# removed MATERIAL to make it work

DERIVATION_TAGS: dict = {
    "no_damage": DAMAGE_TYPE.name,
    "no_saving_throw": SAVING_THROW.name,
}
