from collections import defaultdict
from dndspecs import TAG_CATEGORIES


# creates helpful indices to expedite search (loops over appropriate index vs. all spells)
def create_indices(spells: dict) -> dict[str, defaultdict]:
    indices: dict = {
        # all spells have it
        "level": defaultdict(list),
        "school": defaultdict(list),
        # only add if tags exist
        "condition": defaultdict(list),
        "damage_type": defaultdict(list),
        "saving_throw": defaultdict(list),
        "no_saving_throw": defaultdict(list),
        "no_damage": defaultdict(list),
    }
    for name, spell in spells.items():
        # all spells have it
        # if I put together a list of all of these, I can abstract further
        indices["level"][spell.level].append(name)
        indices["school"][spell.school].append(name)
        # ONLY ADD IF TAGS EXIST
        for category in TAG_CATEGORIES:
            for tag in spell.tags.get(category.name, set()):
                indices[category.name][tag].append(name)
        # LANGUAGE WITH GETTER METHOD
        # for category, tags in spell.get_tags().items():
        #     for tag in tags:
        #         indices[category][tag].append(name)

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
