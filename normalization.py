import json

with open(file="raw_spells.json", mode="r", encoding="utf-8") as raw_json:
    RAW_SPELLS: list[dict] = json.load(raw_json)


def normalize_json(db: list = RAW_SPELLS):
    FIELDS_TO_KEEP: dict = {
        "index": lambda x: x,
        "name": lambda x: x,
        "level": lambda x: x,
        "concentration": lambda x: x,
        "ritual": lambda x: x,
        "school": lambda x: x["name"],
        "range": lambda x: x,
        "components": lambda x: list(x),  # do I need this to avoid aliasing?
        "material": lambda x: x if "GP" in x else None,
        "duration": lambda x: x,
        "casting_time": lambda x: x,
        "classes": lambda x: [c["name"] for c in x],
        "description": lambda x: " ".join([s.strip() for s in x["desc"]]),
    }

    normalized_db = []
    for spell in RAW_SPELLS:
        normalized_spell = {}
        for key, func in FIELDS_TO_KEEP.items():
            if key in spell:
                normalized_spell[key] = func(spell[key])
        normalized_db.append(normalized_spell)

    return normalized_db


print(normalize_json(RAW_SPELLS))
