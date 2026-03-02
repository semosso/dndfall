import re
from dataclasses import dataclass, field


# basic spell structure
@dataclass
class NormalizedSpell:
    name: str
    level: int
    concentration: bool
    ritual: bool
    school: str
    range_: str
    components: str
    duration: str
    casting_time: str
    classes: list[str]
    higher_level: str | bool
    description: list
    url: str
    srd_flag: bool
    tags: dict[str, list[str] | bool] = field(init=False)


# field structure
@dataclass(kw_only=True)
class TagField:
    source: str | None
    patterns: set[str] = field(default_factory=set)
    values: set[str | bool] | range = field(default_factory=set)

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
        return matches

    def get_values(self, *args, **kwargs):
        pass
