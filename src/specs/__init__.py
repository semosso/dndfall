from src.specs.schema import TagField
import src.specs.regex as regex
import src.specs.units as units
import src.specs.fields as fields


CONDITION: TagField = TagField(
    name="conditions",
    values=units.CONDITIONS,
    source="description",
    patterns=regex.CONDITION_PATTERNS,
)

DAMAGE: fields.DamageField = fields.DamageField(
    name="damage",
    values=set(),
    source="description",
    patterns=regex.DAMAGE_PATTERNS,
)

MATERIAL_GP_COST: fields.GpCostField = fields.GpCostField(
    name="material_cost",
    values=set(),
    source="components",
    patterns=regex.GP_COST_PATTERNS,
)

RANGE: fields.RangeField = fields.RangeField(
    name="range",
    values=set(),
    source="range",
    patterns=regex.RANGE_PATTERNS,
)

DURATION: fields.DurationField = fields.DurationField(
    name="duration",
    values=set(),
    source="duration",
    patterns=regex.DURATION_PATTERNS,
)

CASTING_TIME: fields.CastingTimeField = fields.CastingTimeField(
    name="casting_time",
    values=set(),
    source="casting_time",
    patterns=regex.CASTING_TIME_PATTERNS,
)

SAVING_THROW: TagField = TagField(
    name="saving_throw",
    values=units.ABILITIES,
    source="description",
    patterns=regex.SAVING_THROW_PATTERNS,
)

AOE: fields.AreaOfEffectField = fields.AreaOfEffectField(
    name="aoe",
    values=set(),
    source="description",
    patterns=regex.AOE_PATTERNS,
)

DERIVED_FIELDS: list = [
    CONDITION,
    DAMAGE,
    SAVING_THROW,
    MATERIAL_GP_COST,
    AOE,
    RANGE,
    DURATION,
    CASTING_TIME,
]

SCALAR_FIELDS: list = ["name", "level", "concentration", "ritual", "school", "classes"]

NOT_ANY_FIELDS: list = [CONDITION, SAVING_THROW]  # DAMAGE_TYPE
