from dataclasses import dataclass, field
from enum import StrEnum
import re


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
    description: list
    url: str
    srd_flag: bool
    tags: dict[str, list[str] | bool] = field(init=False)


# field structure
@dataclass(kw_only=True)
class SpellField:
    name: str
    aliases: set[str]
    operator: type[StrEnum] | set[type[StrEnum]]
    values: set[str | bool] | range


@dataclass
class ScalarField(SpellField):
    pass


@dataclass(kw_only=True)
class DerivedField(SpellField):
    source: str
    patterns: set[str] = field(default_factory=set)
    values: set[str | bool] | range = field(default_factory=set)
    # shortcut to modify behavior in getter/setter/helper functions
    modifier: bool | None = None

    def derive_tags(self, spell: dict):
        source_text: list | bool | None = spell.get(self.source, None)
        # some spells don't have source (e.g., when source is "material")
        if source_text is None:
            return []
        source_str = (
            (" ".join(source_text)) if isinstance(source_text, list) else source_text
        )
        matches: list[str] = []
        # for fields that require additional processing, with specific rules
        if not self.values:
            results: list = self.process_patterns(source_str)
            # i.e., let fields decide how and what to return, as long as it's not False
            if results is not None and results is not False:
                matches.extend(results) if isinstance(
                    results, list
                ) else matches.append(results)
        else:
            patterns: list = [
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
            for value, regex in patterns:
                if regex.search(string=source_str):
                    matches.append(value)
        return matches

    def process_patterns(self, *args, **kwargs):
        pass

    def get_values(self, *args, **kwargs):
        pass
