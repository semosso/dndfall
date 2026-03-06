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

    def flatten_tags(self):
        flattened = {
            "damage_type": {
                value
                for dt in self.tags["damage"]["base_damage"]
                if dt is not None
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
            # "damage_at_slot": {
            #     slot: {
            #         "damage_average": value["damage_average"],
            #         "damage_maximum": value["damage_maximum"],
            #     }
            #     for slot, value in (self.tags["damage"]["damage_at_slot"] or {}).items()
            # }
            # if isinstance(self.tags["damage"]["damage_at_slot"], dict)
            # else {},
            "condition": {
                value for value in self.tags["condition"] if value is not None
            },
        }
        # for k, v in self.tags.items():
        #     if isinstance(v, dict):
        #         pass
        #     if isinstance(v, list) and v is not None:
        #         flattened[k][v] = set()
        #         for element in v:
        #             if isinstance(element, dict):
        #                 flattened[v]
        #             flattened[k][v].add(element)
        #     if isinstance(v, float):
        #         flattened[k] = v
        return flattened


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
