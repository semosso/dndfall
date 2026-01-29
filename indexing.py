from collections import defaultdict
import dndspecs


def extract_tags(spell, fields=dndspecs.DERIVED_FIELDS) -> dict[str, list[str] | bool]:
    """Extracts tags from spell attributes, based on D&D schema.
    Input: a NormalizedSpell object and each DerivedField dataclass
    Return: a dictionary with tags, organized by category, for each spell."""
    tags: dict[str, list[str] | bool] = {}

    for field in fields:
        field_matches: list[str] = []

        for value in field.values:
            source_text: str | bool = getattr(spell, value.source)
            if not isinstance(source_text, str):
                continue

            for subvalue, regex in value.derive_patterns():
                if regex.search(string=source_text):
                    field_matches.append(subvalue)

            if field_matches:
                tags[field.name] = field_matches

    # def place_derivation_tags(tags):
    #     for k, v in dndspecs.DERIVATION_TAGS.items():
    #         if v not in tags:
    #             tags[k] = [True]
    # place_derivation_tags(tags)
    return tags


def create_indices(
    spells: dict,
    direct_f: list = dndspecs.DIRECT_FIELDS,
    derived_f: list = dndspecs.DERIVED_FIELDS,
) -> dict[str, defaultdict]:
    """Creates reverse indices from spell attributes, including tags.
    Input: a NormalizedSpell object, lists of spell attributes (direct and derived).
    Return: reverse lookup indices dictionary"""

    indices: dict = {field.name: defaultdict(list) for field in direct_f} | {
        field.name: defaultdict(list) for field in derived_f
    }

    for spell_name, spell in spells.items():
        # direct fields
        for field in direct_f:
            field_value = getattr(spell, field.name)
            indices[field.name][field_value].append(spell_name)

        # derived fields, i.e., tags
        for field in derived_f:
            for tag in spell.tags.get(field.name, []):
                indices[field.name][tag].append(spell_name)

    return indices
