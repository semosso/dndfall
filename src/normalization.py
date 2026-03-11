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


def create_indices(spells: dict):
    """Creates reverse indices from JSON fields, including tags.
    Input: indices schema, plus a NormalizedSpell object which mirrors a JSON.
    Return: reverse lookup indices dictionary"""
    indices: dict = {
        field.name: defaultdict(set)
        for field in SEARCH_FIELDS
        if field.name != "spell_name"
    } | {"spell_name": set()}
    for spell_name, spell_obj in spells.items():
        indices["spell_name"].add(spell_name)
        info = spell_obj.extract_index_info()
        for k, v in info.items():
            for value in v:
                indices[k][value].add(spell_name)
    return indices


# testing
# SPELLS = spell_objects_from_JSON()
# INDICES = create_indices(SPELLS)
# with open(file="tests/INDICES.json", mode="w") as test_index:
#     json.dump(
#         INDICES,
#         test_index,
#         indent=2,
#         default=lambda o: list(o) if isinstance(o, set) else o,
#     )
