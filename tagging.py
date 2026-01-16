import dndspecs


def extract_tags(
    spell, rules: list = dndspecs.TAG_CATEGORIES
) -> dict[str, list[str] | bool]:
    # creates an empty tag dict, specific to each spell
    tags: dict[str, list[str] | bool] = {}
    # for dataclass object (e.g., condition) in list
    for category in rules:
        # creates an empty tag dic, specific to each object (e.g., condition)
        found_tag: list[str] = []
        # non-existent sources, e.g., some spells don't have material text
        source_text: str | bool = getattr(spell, category.source)
        if not isinstance(source_text, str):
            continue
        # for (value, regex) tuple returned
        for regex in category.derive_patterns():
            # if regex from tuple is found
            if regex[1].search(string=source_text):
                # add corresponding value to the tag list
                found_tag.append(regex[0])
        if found_tag:
            # if any tags were found, add the tag list as
            tags[category.name] = found_tag

    # e.g., no_damage, no_saving_throw etc., which derive from tag extraction
    # maybe I should un/de-nest this? nested to return a single dic, once
    def place_derivation_tags(tags):
        for k, v in dndspecs.DERIVATION_TAGS.items():
            if v not in tags:
                tags[k] = [True]

    place_derivation_tags(tags)
    return tags
