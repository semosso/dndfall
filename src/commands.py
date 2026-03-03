import re
from enum import StrEnum
from dataclasses import dataclass, field


NAME: ScalarField = ScalarField(
    command="spell_name",
    aliases={"name", "n"},
    operator=TextOp,
)

LEVEL: ScalarField = ScalarField(
    command="level",
    aliases={"level", "l"},
    operator=NumericOp,
)


CONCENTRATION: ScalarField = ScalarField(
    command="concentration",
    aliases={"concentration", "conc"},
    operator=BooleanOp,
)


RITUAL: ScalarField = ScalarField(
    command="ritual",
    aliases={"ritual", "r"},
    operator=BooleanOp,
)


DESCRIPTION: ScalarField = ScalarField(
    command="description", aliases={"description", "desc"}, operator=TextOp
)


UPCAST: UpcastField = UpcastField(
    command="upcast",
    aliases={"upcast", "up"},
    operator=BooleanOp,
)


CONDITION: DerivedField = DerivedField(
    command="condition",
    aliases={"condition", "cond"},
    operator=TextOp,
)


DAMAGE_TYPE: DerivedField = DerivedField(
    command="damage_type",
    aliases={"damage_type", "dt"},
    operator=TextOp,
)

DAMAGE_AVERAGE: DiceAmountField = DiceAmountField(
    command="damage_amount",
    aliases={"damage_amount", "da"},
    operator=NumericOp,

)


DAMAGE_MAXIMUM: DiceAmountField = DiceAmountField(
    command="damage_maximum",
    aliases={"damage_maximum", "dmax"},
    operator=NumericOp,
    values=set(),

)


MATERIAL_GP_COST: GpCostField = GpCostField(
    command="gp_cost",
    aliases={"gp_cost", "gp"},
    operator=NumericOp,

)


RANGE: RangeField = RangeField(
    command="range",
    aliases={"range", "rg"},
    operator=NumericOp,

)


DURATION: DurationField = DurationField(
    command="duration",
    aliases={"duration", "dur"},
    operator=NumericOp,

)


CASTING_TIME: CastingTimeField = CastingTimeField(
    command="casting_time",
    aliases={"casting_time", "cast"},
    operator=NumericOp,

)


SAVING_THROW: DerivedField = DerivedField(
    command="saving_throw",
    aliases={"saving_throw", "st"},
    operator=TextOp,

)


CLASS_: DerivedField = DerivedField(
    command="class",
    aliases={"class", "cls"},
    operator=TextOp,

)


SCHOOL: DerivedField = DerivedField(
    command="school",
    aliases={"school", "sch"},
    operator=TextOp,



AOE_SIZE: AreaOfEffectField = AreaOfEffectField(
    command="aoe_size",
    aliases={"aoe_size", "asz"},
    operator=NumericOp,

)


AOE_SHAPE: AreaOfEffectField = AreaOfEffectField(
    command="aoe_shape",
    aliases={"aoe_shape", "ash"},
    operator=TextOp,

)

# REFERENCES for other modules, automate this at some point
DERIVED_FIELDS: list = [
    CONDITION,
    DAMAGE_AVERAGE,
    DAMAGE_MAXIMUM,
    DAMAGE_TYPE,
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

NOT_ANY_FIELDS: list = [CONDITION, DAMAGE_TYPE, SAVING_THROW]


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {
        alias: field
        for field in DERIVED_FIELDS + SCALAR_FIELDS
        for alias in field.aliases
    }


FIELD_BY_ALIAS: dict = build_field_by_alias()
