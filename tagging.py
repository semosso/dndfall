from dndspecs import DERIVED_FIELDS


def extract_tags(spell, fields=DERIVED_FIELDS) -> dict[str, list[str] | bool]:
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

    # maybe I should un/de-nest this? nested to return a single dic, once
    # def place_derivation_tags(tags):
    #     for k, v in dndspecs.DERIVATION_TAGS.items():
    #         if v not in tags:
    #             tags[k] = [True]

    # place_derivation_tags(tags)
    return tags
