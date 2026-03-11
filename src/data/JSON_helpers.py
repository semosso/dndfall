import json
import re

import src.specs.units as units


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


# higher level extraction and calculation
def flatten_higher_level(spell):
    top_level_sources = {
        "higher_level",
        "entriesHigherLevel",
        "scalingLevelDice",
    }
    for source in top_level_sources:
        if spell.get(source):
            return True
    nested_sources = {"damage_at_slot", "damage_at_level"}
    for source in nested_sources:
        if (
            spell.get("damage", {}).get(source)
            and len(spell.get("damage", {}).get(source)) > 1
        ):
            return True
    return False


def higher_level_roll(scale_dict):

    roll_dict = {}

    pattern = r"""(?x)
    \b(?P<number>[0-9]+)
    (?P<die>d[0-9]+)\s*
    (?:\+\s*
    (?P<fixed>[0-9]+)(?!d))?\s*"""

    compiled_pattern = re.compile(pattern, flags=re.IGNORECASE)

    for level, amount in scale_dict.items():
        avg_roll_sum = 0
        max_roll_sum = 0
        fixed = 0
        results = compiled_pattern.finditer(string=amount)
        for result in results:
            match = result.groupdict()
            number = match.get("number")
            die = match.get("die")
            fixed = match.get("fixed") or 0.0
            avg_roll_sum += units.DiceRoll.avg_roll(
                units.DiceRoll, number=number, die=die
            )
            max_roll_sum += units.DiceRoll.max_roll(
                units.DiceRoll, number=number, die=die
            )
        roll_dict[level] = {
            "damage_average": avg_roll_sum + float(fixed),
            "damage_maximum": max_roll_sum + float(fixed),
        }
    return roll_dict
