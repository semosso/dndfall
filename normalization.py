# scheme that I want for my base, normalized, spells dict
NORMALIZED_SCHEME: dict = {
    "index": lambda x: x["index"],
    "name": lambda x: x["name"],
    "level": lambda x: x["level"],
    "concentration": lambda x: x["concentration"],
    "ritual": lambda x: x["ritual"],
    "school": lambda x: x["school"]["name"],
    "range": lambda x: x["range"],
    "components": lambda x: x["components"],
    "material": lambda x: x.get("material"),
    "duration": lambda x: x["duration"],
    "casting_time": lambda x: x["casting_time"],
    "classes": lambda x: [c["name"] for c in x["classes"]],
    "higher_level": lambda x: x.get("higher_level"),
    # joins all str in list, splits on any whitespace, joins on single space
    "description": lambda x: " ".join(" ".join(x["desc"]).split()),
}


# goes over dict created from raw JSON data, normalizes it based on the scheme above
def normalizing_spells(source: list, scheme: dict = NORMALIZED_SCHEME):
    normalized_spells: dict[str, dict] = {}
    for spell in source:  # for Fireball (spell, dict) in list of spells (source)
        normalized: dict = {}
        for key, operation in scheme.items():  # for "name", lambda in scheme above
            normalized[key] = operation(spell)
        normalized_spells[spell["name"]] = normalized
    return normalized_spells
