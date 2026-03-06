import rich
import json
from collections import defaultdict

from src.specs.schema import NormalizedSpell
from src.search import SEARCH_FIELDS


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
def create_indices(spells: dict):
    """Creates reverse indices from JSON fields, including tags.
    Input: indices schema, plus a NormalizedSpell object which mirrors a JSON.
    Return: reverse lookup indices dictionary"""
    indices: dict = {field.name: defaultdict(set) for field in SEARCH_FIELDS}
    for spell in spells:
        index_tags = spells[spell].flatten_tags()
        for k, v in index_tags.items():
            for value in v:
                indices[k][value].add(spell)
    #     if isinstance(v, dict):
    #         for nested_k, nested_v in v.items():
    #             if isinstance(nested_v, list) and nested_v is not None:
    #                 for instance in nested_v:
    #                     if isinstance(instance, dict):
    #                         for ik, iv in instance.items():
    #                             if iv is not None:
    #                                 indices[ik][iv].add(spell.name)
    #             elif nested_v is not None:
    #                 indices[nested_k][nested_v].add(spell.name)
    #     elif isinstance(v, list):
    #         for value in v:
    #             if isinstance(value, dict):
    #                 for key, val in value.items():
    #                     if val is not None:
    #                         indices[key][val].add(spell.name)
    #             elif value is not None:
    #                 indices[k][value].add(spell.name)
    #     elif v is not None:
    #         indices[k][v].add(spell.name)
    return indices


SPELLS = spell_objects_from_JSON()
# temporary for testing


# | {"spell_name": set()}


# # testing
# print(SPELLS["Fireball"])
rich.print(create_indices(SPELLS))
