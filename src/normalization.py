import rich
import json
from collections import defaultdict

from src.specs.schema import NormalizedSpell
from src.specs import DERIVED_FIELDS, SCALAR_FIELDS


with open(file="src/data/TAGGED_spells.json", mode="r") as spell_JSON:
    spell_source = json.load(spell_JSON)


def spell_objects_from_JSON(database: list = spell_source):
    """Casts spells from JSON into NormalizedSpell instances.
    Input: list of spells, each a dictionary.
    Return: dicionary of spell names and spells (as NormalizedSpell instances)."""
    spells: dict[str, NormalizedSpell] = {}

    for sp in database:
        spell: NormalizedSpell = NormalizedSpell(
            name=sp["name"],
            level=sp["level"],
            concentration=sp["concentration"],
            ritual=sp["ritual"],
            school=sp["school"],
            range=sp["range"],
            components=sp["components"],
            duration=sp["duration"],
            casting_time=sp["casting_time"],
            classes=sp["classes"],
            higher_level=sp["higher_level"],
            higher_description=sp["higher_description"],
            description=sp["description"],
            url=sp["url"],
            srd_flag=sp["srd_flag"],
            tags=sp["tags"],
        )
        spells[spell.name] = spell

    return spells


# def flatten_tags(tags: dict):
#     for k, v in tags.items():
#         if isinstance(v, dict):
#             if any(isinstance(val, (dict, list)) for val in v.values()):
#                 yield from flatten_tags(v)
#             else:
#                 yield k, v
#         elif isinstance(v, list):
#             for item in v:
#                 if isinstance(item, dict):
#                     yield from flatten_tags(item)
#                 elif item is not None:
#                     yield k, item
#         elif v is not None:
#             yield k, v


# very inefficient, I can change this later; fine for cached indices
def create_indices(indices: dict, spell: NormalizedSpell):
    """Creates reverse indices from spell attributes, including tags.
    Input: a NormalizedSpell object, lists of spell attributes (scalar and derived).
    Return: reverse lookup indices dictionary"""
    for k, v in spell.tags:
        if isinstance(v, dict):
            for nested_k, nested_v in v.items():
                if isinstance(nested_v, list) and nested_v is not None:
                    for instance in nested_v:
                        if isinstance(instance, dict):
                            for ik, iv in instance.items():
                                if iv is not None:
                                    indices[ik][iv].add(spell.name)
                elif nested_v is not None:
                    indices[nested_k][nested_v].add(spell.name)
        elif isinstance(v, list):
            for value in v:
                if isinstance(value, dict):
                    for key, val in value.items():
                        if val is not None:
                            indices[key][val].add(spell.name)
                elif value is not None:
                    indices[k][value].add(spell.name)
        elif v is not None:
            indices[k][v].add(spell.name)

    # return indices


SPELLS = spell_objects_from_JSON()
# temporary for testing
commands = [
    "damage_type",
    "damage_average",
    "damage_maximum",
    "damage_at_slot_level",
    "damage_at_character_level",
    "conditions",
    "saving_throw",
    "material_cost",
    "aoe_size",
    "aoe_shape",
    "range",
    "duration",
    "casting_time",
]
INDICES: dict = (
    {field: defaultdict(set) for field in SCALAR_FIELDS}
    | {
        field: defaultdict(set)
        for field in commands
        # if field.name != "spell_name"
    }
    # | {"spell_name": set()}
)
for spell in SPELLS:
    create_indices(INDICES, SPELLS[spell])


# # testing
# print(SPELLS["Fireball"])
# rich.print(INDICES)
