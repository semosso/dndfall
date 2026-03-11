import json

from src.specs import TAG_FIELDS
from data.JSON_helpers import (
    flatten_classes,
    flatten_components,
    flatten_description,
    flatten_higher_level,
    higher_level_roll,
    spell_schools,
)
from data.manual_corrections import hard_coded_corrections


## SRD JSON handling
# first pass, normalizing SRD json from raw, no tag addition yet
def normalizing_SRD_json(database: list):
    SRD_list = []
    SRD_spell = {}

    for SRD_sp in database:
        SRD_spell = {
            "name": SRD_sp["name"],
            "level": SRD_sp["level"],
            "concentration": SRD_sp["concentration"],
            "ritual": SRD_sp["ritual"],
            "school": SRD_sp["school"]["name"]
            if isinstance(SRD_sp["school"], dict)
            else SRD_sp["school"],
            "range": SRD_sp["range"],
            "components": flatten_components(SRD_sp),
            "duration": SRD_sp["duration"],
            "casting_time": SRD_sp["casting_time"],
            "classes": flatten_classes(SRD_sp),
            "higher_level": flatten_higher_level(SRD_sp),
            "higher_description": " ".join(" ".join(SRD_sp["higher_level"]).split())
            if SRD_sp.get("higher_level")
            else False,
            "description": SRD_sp["desc"],
            "url": "https://www.dnd5eapi.co" + SRD_sp["url"],
            "srd_flag": True,
            "tags": {
                "damage": {
                    "damage_at_slot": higher_level_roll(
                        SRD_sp.get("damage", {}).get("damage_at_slot_level", {})
                    )
                    if SRD_sp.get("damage", {}).get("damage_at_slot_level", {})
                    else None,
                    "damage_at_level": higher_level_roll(
                        SRD_sp.get("damage", {}).get("damage_at_character_level", {})
                    )
                    if SRD_sp.get("damage", {}).get("damage_at_character_level", {})
                    else None,
                    "base_damage": [],
                }
            },
        }
        SRD_list.append(SRD_spell)

    return SRD_list


with open(file="src/data/RAW_srd_spells.json", mode="r") as SRD_source:
    raw_SRD: list[dict] = json.load(SRD_source)

SRD_spell_list = normalizing_SRD_json(raw_SRD)


## non-SRD JSON handling
# removing SRD spells from non-SRD spell normalization process
def eliminating_SRD_duplicates():
    with open(file="src/data/RAW_non_srd_spells.json", mode="r") as non_SRD_source:
        non_SRD_spells: list[dict] = json.load(non_SRD_source)
    srd_names = {s["name"].lower() for s in SRD_spell_list}
    non_duplicates = []
    for spell in non_SRD_spells:
        if spell["name"].lower() not in srd_names:
            non_duplicates.append(spell)
    return non_duplicates


# first pass, normalizing non-SRD json from raw, no tag addition yet
def normalizing_non_SRD_json(database: list):
    non_SRD_list = []
    non_SRD_spell = {}

    for non_SRD_sp in database:
        non_SRD_spell = {
            "name": non_SRD_sp["name"],
            "level": non_SRD_sp["level"],
            "concentration": True
            if "concentration" in non_SRD_sp["duration"][0]
            else False,
            "ritual": True if "ritual" in non_SRD_sp.get("meta", "") else False,
            "school": spell_schools[non_SRD_sp["school"]],
            "range": str(non_SRD_sp["range"]["distance"].get("amount", ""))
            + " "
            + non_SRD_sp["range"]["distance"].get("type", ""),
            "components": flatten_components(non_SRD_sp),
            "duration": "Instantaneous"
            if non_SRD_sp["duration"][0]["type"] == "instant"
            else str(non_SRD_sp["duration"][0].get("duration", {}).get("amount", ""))
            + " "
            + non_SRD_sp["duration"][0].get("duration", {}).get("type", ""),
            "casting_time": str(non_SRD_sp["time"][0].get("number", ""))
            + " "
            + non_SRD_sp["time"][0].get("unit", ""),
            "classes": flatten_classes(non_SRD_sp),
            "higher_level": flatten_higher_level(non_SRD_sp),
            "higher_description": " ".join(
                non_SRD_sp["entriesHigherLevel"][0]["entries"]
            ).strip()
            if non_SRD_sp.get("entriesHigherLevel")
            else False,
            "description": flatten_description(non_SRD_sp),
            "url": f"https://www.dndbeyond.com/spells?filter-search={'+'.join(non_SRD_sp['name'].lower().split())}",
            "srd_flag": False,
            "tags": {
                "damage": {
                    "damage_at_slot": "TBD"
                    if non_SRD_sp.get("entriesHigherLevel")
                    else None,
                    "damage_at_level": non_SRD_sp.get("scalingLevelDice", {})
                    if non_SRD_sp.get("scalingLevelDice")
                    else None,
                    "base_damage": [],
                }
            },
        }
        non_SRD_list.append(non_SRD_spell)

    return non_SRD_list


non_SRD_spell_list = normalizing_non_SRD_json(eliminating_SRD_duplicates())


## tagging
def generate_tags(
    spell: dict, derived_f: list = TAG_FIELDS
) -> dict[str, dict | list | float | None]:
    tags: dict[str, dict | list | float | None] = {}
    for field in derived_f:
        source = spell.get(field.source, None)
        source_text = (" ".join(source)) if isinstance(source, list) else source
        result = field.process_patterns(source_text)
        tags[field.name] = result
    return tags


def add_tags_to_JSON(spell, spell_tags):
    for k, v in spell_tags.items():
        if k == "damage":
            spell["tags"]["damage"]["base_damage"] = spell_tags[k]
        else:
            spell["tags"][k] = v


spells = SRD_spell_list + non_SRD_spell_list
sorted_list = sorted(spells, key=lambda x: x["name"])

for spell in sorted_list:
    add_tags_to_JSON(spell, generate_tags(spell))

# handling edge cases before writing the finalized and tagged JSON
sorted_dict = {spell["name"]: spell for spell in sorted_list}
hard_coded_corrections(sorted_dict)

# writing the curated and consolidated JSON, with tags
with open(file="src/data/TAGGED_spells.json", mode="w") as tagged_spells:
    json.dump(sorted_list, fp=tagged_spells, indent=2)
