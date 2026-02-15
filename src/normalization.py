from collections import defaultdict

from src import dndspecs


def normalizing_spells(database: list):
    """Casts spells from JSON into NormalizedSpell instances.
    Input: list of spells, each a dictionary.
    Return: dicionary of spell names and spells (as NormalizedSpell instances)."""
    spells: dict[str, dndspecs.NormalizedSpell] = {}

    for sp in database:
        spell: dndspecs.NormalizedSpell = dndspecs.NormalizedSpell(
            name=sp["name"],
            level=sp["level"],
            concentration=sp["concentration"],
            ritual=sp["ritual"],
            school=sp["school"]["name"],
            range_=sp["range"],
            components=", ".join(sp["components"]) + f". {sp.get('material', '')}",
            duration=sp["duration"],
            casting_time=sp["casting_time"],
            classes=", ".join([c["name"] for c in sp["classes"]]),
            higher_level=False if not sp["higher_level"] else True,
            description=sp["desc"]
            + [f"At Higher Levels: {' '.join(' '.join(sp['higher_level']).split())}"]
            if sp["higher_level"]
            else sp["desc"],
            url="https://www.dnd5eapi.co" + sp["url"],
        )
        spell.tags = add_tags(spell=spell, derived_f=dndspecs.DERIVED_FIELDS)
        spells[spell.name] = spell

    return spells


def add_tags(
    spell: dndspecs.NormalizedSpell, derived_f: list[dndspecs.DerivedField]
) -> dict[str, list[str] | bool]:
    """Orchestrates tag extraction using DerivedValues methods.
    Input: a NormalizedSpell instance and a list of DerivedField dataclasses.
    Return: a dictionary with tags for the spell, organized by field."""
    tags: dict[str, list[str] | bool] = {}

    for field in derived_f:
        matches: list = []
        matches.extend(field.derive_tags(spell))
        if matches:
            tags[field.name] = matches

    return tags


# very inefficient, I can change this later; fine for cached indices
def create_indices(
    spells: dict,
    scalar_f: list,
    derived_f: list,
) -> dict[str, defaultdict]:
    """Creates reverse indices from spell attributes, including tags.
    Input: a NormalizedSpell object, lists of spell attributes (scalar and derived).
    Return: reverse lookup indices dictionary"""
    indices: dict = (
        {field.name: defaultdict(set) for field in scalar_f}
        | {
            field.name: defaultdict(set)
            for field in derived_f
            if field.name != "spell_name"
        }
        | {"spell_name": set()}
    )
    for spell_name, spell in spells.items():
        # scalar fields
        indices["spell_name"].add(spell.name)
        for field in scalar_f:
            if field.name != "spell_name":
                field_value = getattr(spell, field.name)
                indices[field.name][field_value].add(spell_name)
        # derived fields, i.e., tags
        for field in derived_f:
            for tag in spell.tags.get(field.name, []):
                indices[field.name][tag].add(spell_name)
    return indices
