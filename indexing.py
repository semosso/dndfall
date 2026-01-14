from collections import defaultdict


# creates helpful indices to expedite search (loops over appropriate index vs. all spells)
def create_indices(spells: dict) -> dict:
    indices: dict = {
        "level": defaultdict(list),  # all spells have it
        "school": defaultdict(list),  # all spells have it
        "condition": defaultdict(list),  # only add if tags exist
        "damage_type": defaultdict(list),  # only add if tags exist
        "saving_throw": defaultdict(list),  # only add if tags exist
        "no_damage": [],  # TBD, just an idea for now
                          # normalize all to dicts
    }

    for spell_name, spell_info in spells.items():
        # all spells have it
        indices["level"][spell_info["level"]].append(spell_name)
        indices["school"][spell_info["school"]].append(spell_name)
        
        # only add if tags exist
        for cond in spell_info["tags"].get("condition", set()):
            # set() because you need a default return that can be subject to the
            # same operations as the intended one (e.g., append, merge, iteration)
            indices["condition"][cond].append(spell_name)
        for dmg_type in spell_info["tags"].get("damage_type", set()):
            indices["damage_type"][dmg_type].append(spell_name)
        if spell_info["tags"][
            "no_damage"
        ]:  # same for no conditions? think and consolidate
            indices["no_damage"].append(spell_name)
        for st_ability in spell_info["tags"].get("saving_throw", set()):
            indices["saving_throw"][st_ability].append(spell_name)

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
