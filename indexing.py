from collections import defaultdict
from dndspecs import DIRECT_FIELDS, DERIVED_FIELDS


def extract_tags(spell, fields=DERIVED_FIELDS) -> dict[str, list[str] | bool]:
    """Extracts tags from spell attributes, based on D&D schema.
    Input: a NormalizedSpell object and each DerivedField dataclass
    Return: a dictionary with tags, organized by category, for each spell."""
    tags: dict[str, list[str] | bool] = {}

    for field in fields:
        for value_, value_info_ in field.values.items():
            found_tag: list[str] = []

            source_text: str | bool = getattr(spell, value_info_["source"])
            if not isinstance(source_text, str):
                continue

            for regex in field.derive_patterns(value=value_info_):
                if regex[1].search(string=source_text):
                    found_tag.append(regex[0])
            if found_tag:
                tags[value_] = found_tag

    # def place_derivation_tags(tags):
    #     for k, v in dndspecs.DERIVATION_TAGS.items():
    #         if v not in tags:
    #             tags[k] = [True]
    # place_derivation_tags(tags)
    return tags


# creates helpful indices to expedite search (loops over appropriate index vs. all spells)
def create_indices(
    spells: dict, direct_f: list = DIRECT_FIELDS, derived_f: list = DERIVED_FIELDS
) -> dict[str, defaultdict]:
    """Creates reverse indices from spell attributes, including tags.
    Input: a NormalizedSpell object, lists of spell attributes (direct and derived).
    Return: reverse lookup indices dictionary"""

    indices: dict = {field.name: defaultdict(list) for field in direct_f} | {
        key: defaultdict(list) for field in derived_f for key in field.values
    }

    for spell_name, spell in spells.items():
        for field in direct_f:
            field_value = getattr(spell, field.name)
            indices[field.name][field_value].append(spell_name)
        for field in derived_f:
            for category in field.values:
                for tag in spell.tags.get(category, set()):
                    indices[category][tag].append(spell_name)

    return indices
