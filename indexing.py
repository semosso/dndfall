from collections import defaultdict


def add_tags(spell, derived_f) -> dict[str, list[str] | bool]:
    """Orchestrates tag extraction using DerivedValues methods.
    Input: a NormalizedSpell instance and a list of DerivedField dataclasses.
    Return: a dictionary with tags for the spell, organized by field."""
    tags: dict[str, list[str] | bool] = {}

    for field in derived_f:
        matches: list = []
        for d_value in field.values:
            matches.extend(d_value.derive_tags(spell))
        if matches:
            tags[field.name] = matches

    return tags


def create_indices(
    spells: dict,
    direct_f: list,
    derived_f: list,
) -> dict[str, defaultdict]:
    """Creates reverse indices from spell attributes, including tags.
    Input: a NormalizedSpell object, lists of spell attributes (direct and derived).
    Return: reverse lookup indices dictionary"""
    indices: dict = {field.name: defaultdict(set) for field in direct_f} | {
        field.name: defaultdict(set) for field in derived_f
    }

    for spell_name, spell in spells.items():
        # direct fields
        for field in direct_f:
            field_value = getattr(spell, field.name)
            if isinstance(field_value, bool):
                if field_value:
                    indices[field.name][True].add(spell_name)
            else:
                indices[field.name][field_value].add(spell_name)
        # derived fields, i.e., tags
        for field in derived_f:
            for tag in spell.tags.get(field.name, []):
                indices[field.name][tag].add(spell_name)

    return indices
