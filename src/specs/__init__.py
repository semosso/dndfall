from src.specs.schema import TagField
import src.specs.regex as regex
import src.specs.units as units
import src.specs.tag_fields as tag_fields


CONDITION: TagField = TagField(
    name="condition",
    values=units.CONDITIONS,
    source="description",
    patterns=regex.CONDITION_PATTERNS,
)

DAMAGE: tag_fields.DamageField = tag_fields.DamageField(
    name="damage",
    values=set(),
    source="description",
    patterns=regex.DAMAGE_PATTERNS,
)

MATERIAL_GP_COST: tag_fields.GpCostField = tag_fields.GpCostField(
    name="material_cost",
    values=set(),
    source="components",
    patterns=regex.GP_COST_PATTERNS,
)

RANGE: tag_fields.RangeField = tag_fields.RangeField(
    name="range",
    values=set(),
    source="range",
    patterns=regex.RANGE_PATTERNS,
)

DURATION: tag_fields.DurationField = tag_fields.DurationField(
    name="duration",
    values=set(),
    source="duration",
    patterns=regex.DURATION_PATTERNS,
)

CASTING_TIME: tag_fields.CastingTimeField = tag_fields.CastingTimeField(
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

AOE: tag_fields.AreaOfEffectField = tag_fields.AreaOfEffectField(
    name="aoe",
    values=set(),
    source="description",
    patterns=regex.AOE_PATTERNS,
)

TAG_FIELDS: list = [
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
