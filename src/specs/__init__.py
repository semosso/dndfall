import src.specs.regex as regex
import src.specs.units as units
from src.specs.schema import ScalarField, DerivedField
from src.specs.fields import (
    DamageField,
    UpcastableField,
    GpCostField,
    RangeField,
    DurationField,
    CastingTimeField,
    AreaOfEffectField,
)

NAME: ScalarField = ScalarField(
    name="spell_name",
    aliases={"name", "n"},
    operator=units.TextOp,
    values=set(),
)

LEVEL: ScalarField = ScalarField(
    name="level",
    aliases={"level", "l"},
    operator=units.NumericOp,
    values=range(0, 10),
)


CONCENTRATION: ScalarField = ScalarField(
    name="concentration",
    aliases={"concentration", "conc"},
    operator=units.BooleanOp,
    values={True, False},
)


RITUAL: ScalarField = ScalarField(
    name="ritual",
    aliases={"ritual", "r"},
    operator=units.BooleanOp,
    values={True, False},
)


DESCRIPTION: ScalarField = ScalarField(
    name="description",
    aliases={"description", "desc"},
    operator=units.TextOp,
    values=set(),
)

UPCAST: UpcastableField = UpcastableField(
    name="upcastable",
    aliases={"upcast", "up"},
    operator=units.BooleanOp,
    values="set()",
    source="higher_level",
    patterns=set(),
)

CONDITION: DerivedField = DerivedField(
    name="condition",
    aliases={"condition", "cond"},
    operator=units.TextOp,
    values=units.CONDITIONS,
    source="description",
    patterns=regex.CONDITION_PATTERNS,
)


DAMAGE: DamageField = DamageField(
    name="damage",
    aliases={"damage_type", "dt"},
    operator=units.TextOp,
    values=set(),
    source="description",
    patterns=set(),
)

# DAMAGE_AVERAGE: DiceAmountField = DiceAmountField(
#     name="damage_amount",
#     aliases={"damage_amount", "da"},
#     operator=units.NumericOp,
#     values=set(),
#     source="description",
#     patterns=set(),
# )


# DAMAGE_MAXIMUM: DiceAmountField = DiceAmountField(
#     name="damage_maximum",
#     aliases={"damage_maximum", "dmax"},
#     operator=units.NumericOp,
#     values=set(),
#     source="description",
#     patterns=set(),
#     modifier=True,
# )


MATERIAL_GP_COST: GpCostField = GpCostField(
    name="gp_cost",
    aliases={"gp_cost", "gp"},
    operator=units.NumericOp,
    values=set(),
    source="components",
    patterns=set(),
)


RANGE: RangeField = RangeField(
    name="range",
    aliases={"range", "rg"},
    operator=units.NumericOp,
    values=set(),
    source="range",
    patterns=set(),
)


DURATION: DurationField = DurationField(
    name="duration",
    aliases={"duration", "dur"},
    operator=units.NumericOp,
    values=set(),
    source="duration",
    patterns=set(),
)

CASTING_TIME: CastingTimeField = CastingTimeField(
    name="casting_time",
    aliases={"casting_time", "cast"},
    operator=units.NumericOp,
    values=set(),
    source="casting_time",
    patterns=regex.CASTING_TIME_PATTERNS,
)


SAVING_THROW: DerivedField = DerivedField(
    name="saving_throw",
    aliases={"saving_throw", "st"},
    operator=units.TextOp,
    values=units.ABILITIES,
    source="description",
    patterns=regex.SAVING_THROW_PATTERNS,
)


CLASS_: DerivedField = DerivedField(
    name="class",
    aliases={"class", "cls"},
    operator=units.TextOp,
    values=units.CLASSES,
    source="classes",
    patterns=regex.CLASS_PATTERNS,
)


SCHOOL: DerivedField = DerivedField(
    name="school",
    aliases={"school", "sch"},
    operator=units.TextOp,
    values=units.SCHOOLS,
    source="school",
    patterns=regex.SCHOOL_PATTERNS,
)


AOE_SIZE: AreaOfEffectField = AreaOfEffectField(
    name="aoe_size",
    aliases={"aoe_size", "asz"},
    operator=units.NumericOp,
    values=set(),
    source="description",
    patterns=set(),
)


AOE_SHAPE: AreaOfEffectField = AreaOfEffectField(
    name="aoe_shape",
    aliases={"aoe_shape", "ash"},
    operator=units.TextOp,
    values=set(),
    source="description",
    patterns=set(),
    modifier=True,
)

DERIVED_FIELDS: list = [
    CONDITION,
    # DAMAGE_AVERAGE,
    # DAMAGE_MAXIMUM,
    DAMAGE,
    SAVING_THROW,
    MATERIAL_GP_COST,
    CLASS_,
    SCHOOL,
    AOE_SIZE,
    AOE_SHAPE,
    RANGE,
    DURATION,
    CASTING_TIME,
    UPCAST,
]

SCALAR_FIELDS: list = [
    NAME,
    LEVEL,
    CONCENTRATION,
    RITUAL,
]

NOT_ANY_FIELDS: list = [CONDITION, SAVING_THROW]  # DAMAGE_TYPE


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {
        alias: field
        for field in DERIVED_FIELDS + SCALAR_FIELDS
        for alias in field.aliases
    }


FIELD_BY_ALIAS: dict = build_field_by_alias()
