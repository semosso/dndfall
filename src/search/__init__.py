import operator
from src.specs.schema import SearchField
import src.specs.units as units

NAME: SearchField = SearchField(
    name="spell_name", aliases={"name", "n"}, operator=units.TextOp, scalar=True
)

LEVEL: SearchField = SearchField(
    name="level",
    aliases={"level", "l"},
    operator=units.NumericOp,
    values={n for n in range(0, 10)},
    scalar=True,
)

CONCENTRATION: SearchField = SearchField(
    name="concentration",
    aliases={"concentration", "conc"},
    operator=units.BooleanOp,
    values={True, False},
    scalar=True,
)

RITUAL: SearchField = SearchField(
    name="ritual",
    aliases={"ritual", "r"},
    operator=units.BooleanOp,
    values={True, False},
    scalar=True,
)

DESCRIPTION: SearchField = SearchField(
    name="description",
    aliases={"description", "desc"},
    operator=units.TextOp,
    scalar=True,
)

UPCAST: SearchField = SearchField(
    name="upcast",
    aliases={"upcast", "up"},
    operator=units.BooleanOp,
    values={True, False},
    scalar=True,
)

CONDITION: SearchField = SearchField(
    name="condition",
    aliases={"condition", "cond"},
    operator=units.TextOp,
    values=units.CONDITIONS,
)

DAMAGE_TYPE: SearchField = SearchField(
    name="damage_type",
    aliases={"damage_type", "dt"},
    operator=units.TextOp,
    values=units.DAMAGE_TYPES,
)

DAMAGE_AVERAGE: SearchField = SearchField(
    name="damage_average",
    aliases={"damage_average", "da"},
    operator=units.NumericOp,
)

DAMAGE_MAXIMUM: SearchField = SearchField(
    name="damage_maximum",
    aliases={"damage_maximum", "dmax"},
    operator=units.NumericOp,
)
# needs a lot to work; JSON is not normalized for this yet, and I'm not sure
# this field makes sense yet, how it should look etc.

# DAMAGE_AT_SLOT: SearchField = SearchField(
#     name="damage_at_slot",
#     aliases={"damage_at_slot", "dslot"},
#     operator=units.NumericOp,
#     values={n for n in range(0, 10)},
# )

# DAMAGE_AT_LEVEL: SearchField = SearchField(
#     name="damage_at_level",
#     aliases={"damage_at_level", "dlvl"},
#     operator=units.NumericOp,
#     values={n for n in range(0, 21)},
# )

MATERIAL_GP_COST: SearchField = SearchField(
    name="gp_cost",
    aliases={"gp_cost", "gp"},
    operator=units.NumericOp,
)

RANGE: SearchField = SearchField(
    name="range",
    aliases={"range", "rg"},
    operator=units.NumericOp,
)

DURATION: SearchField = SearchField(
    name="duration",
    aliases={"duration", "dur"},
    operator=units.NumericOp,
)

CASTING_TIME: SearchField = SearchField(
    name="casting_time",
    aliases={"casting_time", "cast"},
    operator=units.NumericOp,
)

SAVING_THROW: SearchField = SearchField(
    name="saving_throw",
    aliases={"saving_throw", "st"},
    operator=units.TextOp,
    values=units.ABILITIES,
)

CLASSES: SearchField = SearchField(
    name="class",
    aliases={"class", "cls"},
    operator=units.TextOp,
    values=units.CLASSES,
)

SCHOOL: SearchField = SearchField(
    name="school",
    aliases={"school", "sch"},
    operator=units.TextOp,
    values=units.SCHOOLS,
)

AOE_SIZE: SearchField = SearchField(
    name="aoe_size",
    aliases={"aoe_size", "asz"},
    operator=units.NumericOp,
)

AOE_SHAPE: SearchField = SearchField(
    name="aoe_shape",
    aliases={"aoe_shape", "ash"},
    operator=units.TextOp,
    values=units.SHAPE_UNIT["aliases"],
)


SEARCH_FIELDS: list = [f_ for f_ in globals().values() if isinstance(f_, SearchField)]

SCALAR_FIELDS: list = ["name", "level", "concentration", "ritual", "school", "classes"]

NOT_ANY_FIELDS: list = [CONDITION, SAVING_THROW, DAMAGE_TYPE]


def build_field_by_alias():
    """Generates lookup dict for searching functions."""
    return {alias: field for field in SEARCH_FIELDS for alias in field.aliases}


FIELD_BY_ALIAS: dict = build_field_by_alias()
