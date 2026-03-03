import json
from src.specs import DERIVED_FIELDS


## helper functions

spell_schools = {
    school[0]: school
    for school in [
        "Abjuration",
        "Conjuration",
        "Divination",
        "Enchantment",
        "Illusion",
        "Necromancy",
        "Transmutation",
    ]
} | {"V": "Evocation"}


# class extraction from specific class source list
with open(file="src/data/class_sources.json", mode="r") as class_json:
    class_source = json.load(class_json)


def flatten_classes(spell: dict, class_source=class_source) -> set:
    entry = class_source.get(spell["name"], {})
    raw_classes = entry.get("class") or entry.get("classVariant", [])
    classes_ = set()
    for class_ in raw_classes:
        if class_["name"] not in classes_:
            classes_.add(class_["name"])
    if not classes_:
        return ", ".join(c["name"] for c in spell["classes"])
    return ", ".join(classes_)


# description extraction
def flatten_description(spell):
    description = []
    for item in spell.get("entries"):
        if isinstance(item, str):
            description.append(item)
        elif isinstance(item, dict):
            name = item.get("name")
            text = " ".join(item.get("entries", []))
            description.append(f"{name}: {text}")
    return description


# components extractions
def flatten_components(spell):
    if isinstance(spell["components"], dict):
        components: str = ", ".join(spell["components"].keys())
        m: str = spell["components"].get("m", "")
        m_text = f". {m.get('text', '')}" if isinstance(m, dict) else ""
    else:
        components: str = ", ".join(spell["components"])
        m: str = spell.get("material", "")
        m_text = f". {m}" if m else ""
    return components.upper() + m_text


def flatten_higher_level(spell):
    top_level_sources = {
        "higher_level",
        "entriesHigherLevel",
        "scalingLevelDice",
    }
    for source in top_level_sources:
        if spell.get(source):
            return True
    nested_sources = {"damage_at_slot_level", "damage_at_character_level"}
    for source in nested_sources:
        if spell.get("damage", {}).get(source):
            return True
    return False


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
                    "damage_at_slot_level": SRD_sp.get("damage", {}).get(
                        "damage_at_slot_level", {}
                    )
                    if SRD_sp.get("damage", {}).get("damage_at_slot_level", {})
                    else None,
                    "damage_at_character_level": SRD_sp.get("damage", {}).get(
                        "damage_at_character_level", {}
                    )
                    if SRD_sp.get("damage", {}).get("damage_at_character_level", {})
                    else None,
                    "damage_instances": [],
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
    srd_names = {s["name"] for s in SRD_spell_list}
    non_duplicates = []
    for spell in non_SRD_spells:
        if spell["name"] not in srd_names:
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
                    "damage_at_slot_level": "TBD"
                    if non_SRD_sp.get("entriesHigherLevel")
                    else None,
                    "damage_at_character_level": non_SRD_sp.get("scalingLevelDice", {})
                    if non_SRD_sp.get("scalingLevelDice")
                    else None,
                    "damage_instances": [],
                }
            },
        }
        non_SRD_list.append(non_SRD_spell)

    return non_SRD_list


non_SRD_spell_list = normalizing_non_SRD_json(eliminating_SRD_duplicates())


## tagging
def extract_tags(
    spell: dict, derived_f: list = DERIVED_FIELDS
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
            spell["tags"]["damage"]["damage_instances"] = spell_tags[k]
        else:
            spell["tags"][k] = v


spells = SRD_spell_list + non_SRD_spell_list
sorted_list = sorted(spells, key=lambda x: x["name"])

for spell in sorted_list:
    add_tags_to_JSON(spell, extract_tags(spell))

## writing to the final normalized and tagged JSON

# writing the curated and consolidated JSON, with tags
with open(file="src/data/TAGGED_spells.json", mode="w") as tagged_spells:
    json.dump(sorted_list, fp=tagged_spells, indent=2)
