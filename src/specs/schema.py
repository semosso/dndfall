import re
from enum import StrEnum
from dataclasses import dataclass, field


# basic spell structure
@dataclass
class NormalizedSpell:
    name: str
    level: int
    concentration: bool
    ritual: bool
    school: str
    range: str
    components: str
    duration: str
    casting_time: str
    classes: list[str]
    higher_level: str | bool
    higher_description: str | bool
    description: list
    url: str
    srd_flag: bool
    tags: dict[str, dict | list[str] | bool]

    def extract_index_info(self):
        index_info = {
            "level": {self.level},
            "concentration": {self.concentration if True else None},
            "ritual": {self.ritual if True else None},
            "school": {self.school},
            "range": {self.tags["range"]},
            "gp_cost": {self.tags["gp_cost"]},
            "duration": {self.tags["duration"]},
            "casting_time": {self.tags["casting_time"]},
            # should I just plit classes, instead of creating a dedicated tag?
            "classes": {value.strip() for value in self.classes.split(",")},
            "upcast": {self.higher_level},
            "condition": {
                value for value in self.tags["condition"] if value is not None
            },
            "saving_throw": {
                value for value in self.tags["saving_throw"] if value is not None
            },
            "aoe_size": {
                area["aoe_size"]
                for area in self.tags["aoe"]
                if area["aoe_size"] is not None
            },
            "aoe_shape": {
                area["aoe_shape"]
                for area in self.tags["aoe"]
                if area["aoe_shape"] is not None
            },
            "damage_type": {
                value
                for dt in self.tags["damage"]["base_damage"]
                if dt is not None
                # avoid double counting alternative damage types (stored as base_damage: [alt1, alt2])
                for value in (
                    dt["damage_type"]
                    if isinstance(dt["damage_type"], list)
                    else [dt["damage_type"]]
                )
            },
            "damage_average": {
                sum(
                    value["damage_average"]
                    for value in self.tags["damage"]["base_damage"]
                    if value is not None
                )
            },
            "damage_maximum": {
                sum(
                    value["damage_maximum"]
                    for value in self.tags["damage"]["base_damage"]
                    if value is not None
                )
            },
        }
        return index_info


# taggable field structure
@dataclass(kw_only=True)
class TagField:
    name: str
    source: str
    patterns: str | set[str] = field(default_factory=set)
    values: set[str | bool] = field(default_factory=set)

    def process_patterns(self, source_text):
        compiled_patterns: list = [
            (
                value,
                re.compile(
                    pattern=template.format(value=re.escape(pattern=value)),
                    flags=re.IGNORECASE,
                ),
            )
            for value in self.values
            for template in self.patterns
        ]

        matches: list = []
        for value, regex in compiled_patterns:
            if regex.search(string=source_text):
                matches.append(value)
        return matches if matches else [None]

    def get_values(self):
        pass


# searchable field structure
@dataclass(kw_only=True)
class SearchField:
    name: str
    aliases: set[str]
    operator: type[StrEnum]
    values: set[str | float] = field(default_factory=set)
    scalar: bool = False
    not_any: bool = False
