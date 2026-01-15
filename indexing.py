from collections import defaultdict
from dndspecs import TAG_CATEGORIES


# creates helpful indices to expedite search (loops over appropriate index vs. all spells)
def create_indices(spells: dict) -> dict[str, defaultdict]:
    indices: dict = {
        "level": defaultdict(list),  # all spells have it
        "school": defaultdict(list),  # all spells have it
        "condition": defaultdict(list),  # only add if tags exist
        "damage_type": defaultdict(list),  # only add if tags exist
        "saving_throw": defaultdict(list),  # only add if tags exist
        # "no_damage": defaultdict(list),  # TBD, just an idea for now
        # normalize all to dicts
    }

    for name, spell in spells.items():
        # all spells have it
        indices["level"][spell.level].append(name)
        indices["school"][spell.school].append(name)

        # only add if tags exist
        for category in TAG_CATEGORIES:
            for tag in spell.tags.get(category.name, set()):
                indices[category.name][tag].append(name)

    return indices


def has_tag():
    # is spell in tag index?
    # intersection of spells in multiple indices
    pass


def numeric_search():
    pass


def text_search():
    pass


def set_search():
    pass


def match_spell():
    # will call on the helper ones depending on type
    # figure out the formal synta, how to match user's input to my operatores and helpers)
    # replicate scryfall's formal syntax (e.g., l:/level: (<, <=, \==, >=, >, !=),
    # c:/condit ion: (T/F, \==, fuzzy later, !=))
    pass
