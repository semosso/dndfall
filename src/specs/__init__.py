from src.specs.schema import TagField
import src.specs.regex as regex
import src.specs.units as units
import src.specs.fields as fields


UPCAST: fields.UpcastableField = fields.UpcastableField(
    values=set(),
    source="higher_level",
    patterns=set(),
)

CONDITION: TagField = TagField(
    values=units.CONDITIONS,
    source="description",
    patterns=regex.CONDITION_PATTERNS,
)


DAMAGE: fields.DamageField = fields.DamageField(
    values=set(),
    source="description",
    patterns=regex.DAMAGE_PATTERNS,
)

MATERIAL_GP_COST: fields.GpCostField = fields.GpCostField(
    values=set(),
    source="components",
    patterns=set(),
)

RANGE: fields.RangeField = fields.RangeField(
    values=set(),
    source="range",
    patterns=set(),
)

DURATION: fields.DurationField = fields.DurationField(
    values=set(),
    source="duration",
    patterns=set(),
)

CASTING_TIME: fields.CastingTimeField = fields.CastingTimeField(
    values=set(),
    source="casting_time",
    patterns=regex.CASTING_TIME_PATTERNS,
)

SAVING_THROW: TagField = TagField(
    values=units.ABILITIES,
    source="description",
    patterns=regex.SAVING_THROW_PATTERNS,
)

CLASS_: TagField = TagField(
    values=units.CLASSES,
    source="classes",
    patterns=regex.CLASS_PATTERNS,
)

SCHOOL: TagField = TagField(
    values=units.SCHOOLS,
    source="school",
    patterns=regex.SCHOOL_PATTERNS,
)

AOE_SIZE: fields.AreaOfEffectField = fields.AreaOfEffectField(
    values=set(),
    source="description",
    patterns=set(),
)

AOE_SHAPE: fields.AreaOfEffectField = fields.AreaOfEffectField(
    values=set(),
    source="description",
    patterns=set(),
)

DERIVED_FIELDS: list = [
    CONDITION,
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

NOT_ANY_FIELDS: list = [CONDITION, SAVING_THROW]  # DAMAGE_TYPE
