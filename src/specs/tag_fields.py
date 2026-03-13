import re
from dataclasses import dataclass

import src.specs.units as units
import src.specs.regex as regex
from src.specs.schema import TagField


@dataclass
class DamageField(TagField):
    compiled_patterns = re.compile(regex.DAMAGE_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.results = []
        for match in self.compiled_patterns.finditer(string=source_text):
            groups = match.groupdict()
            result = {
                "number": groups.get("number") or 0.0,
                "die": groups.get("die") or 0.0,
                "fixed": groups.get("fixed") or 0.0,
                "type": groups.get("type") or None,
            }
            self.results.append(result)
        return self.get_values()

    def get_values(self):
        values = []
        if self.results:
            for result in self.results:
                value = {
                    "damage_type": result["type"],
                    "damage_average": units.DiceRoll.avg_roll(
                        units.DiceRoll, result["number"], result["die"]
                    )
                    + float(result["fixed"]),
                    "damage_maximum": units.DiceRoll.max_roll(
                        units.DiceRoll, result["number"], result["die"]
                    )
                    + float(result["fixed"]),
                }
                values.append(value)
            # return values[0] if len(values) == 1 else values
            return values
        return [None]


@dataclass
class GpCostField(TagField):
    compiled_patterns = re.compile(pattern=regex.GP_COST_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.number, self.unit = 0.0, "gold"
        result = self.compiled_patterns.search(string=source_text)
        if result:
            groups = result.groupdict()
            if "number" in groups:
                self.number = groups.get("number").replace(",", "") or 0.0
                self.unit = groups.get("unit") or ""
            return self.get_values()
        return 0.0

    def get_values(self):
        unit_ratio = units.find_ratio(
            value=self.unit,
            categories=["gold", "platinum", "electrum", "silver", "copper"],
        )
        return float(self.number) * unit_ratio


@dataclass
class RangeField(TagField):
    patterns = regex.RANGE_PATTERNS

    compiled_patterns = [
        re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns
    ]

    def process_patterns(self, source_text):
        self.number, self.unit, self.text = "", "", ""
        for pattern in self.compiled_patterns:
            result = pattern.search(string=source_text)
            if result:
                groups = result.groupdict()
                if "number" in groups:
                    self.number = groups.get("number") or 0.0
                    self.unit = groups.get("unit") or ""
                if "text" in groups:
                    self.text = groups.get("text") or ""
                break

        return self.get_values()

    def get_values(self):
        text_value = self.unit if self.unit else self.text
        text_ratio = units.find_ratio(
            value=text_value, categories=["self", "touch", "foot", "mile"]
        )
        if self.number:
            return float(self.number) * text_ratio
        if self.text:
            return text_ratio
        return None


@dataclass
class DurationField(TagField):
    patterns = regex.DURATION_PATTERNS

    compiled_patterns = [
        re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns
    ]

    def process_patterns(self, source_text):
        self.number, self.unit, self.text = "", "", ""
        for pattern in self.compiled_patterns:
            result = pattern.search(string=source_text)
            if result:
                groups = result.groupdict()
                if groups.get("number") is not None:
                    self.number = groups.get("number") or 0.0
                    self.unit = groups.get("unit") or ""
                if groups.get("text") is not None:
                    self.text = groups.get("text") or ""
                break
        return self.get_values()

    def get_values(self):
        text_value = self.unit if self.unit else self.text
        text_ratio = units.find_ratio(
            value=text_value,
            categories=[category for category in units.TIME_UNIT],
        )
        if self.number:
            return float(self.number) * text_ratio
        if self.text:
            return text_ratio
        return None


@dataclass
class CastingTimeField(TagField):
    compiled_patterns = re.compile(regex.CASTING_TIME_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.number, self.unit = "", ""
        result = self.compiled_patterns.search(string=source_text)
        if result:
            self.number = result.group(1)
            self.unit = result.group(2)
            return self.get_values()
        return None

    def get_values(self):
        if not self.number:
            return None
        text_ratio = units.find_ratio(
            value=self.unit,
            categories=["second", "minute", "hour", "day", "year", "dnd_economy"],
        )
        return float(self.number) * text_ratio


@dataclass
class AreaOfEffectField(TagField):
    compiled_patterns = [
        re.compile(pattern, flags=re.IGNORECASE) for pattern in regex.AOE_PATTERNS
    ]

    def process_patterns(self, source_text):
        self.results = []
        for pattern in self.compiled_patterns:
            matches = pattern.finditer(string=source_text)
            for match in matches:
                groups = match.groupdict()
                result = {
                    "number": groups.get("number") or 0.0,
                    "number2": groups.get("number2") or 1.0,
                    "unit": groups.get("unit") or "",
                    "rad_diam": groups.get("rad_diam") or "",
                    "shape": groups.get("shape") or "",
                }
                self.results.append(result)
        return self.get_values()

    def get_values(self):
        values = []
        if self.results:
            for result in self.results:
                value = {
                    "aoe_size": float(result["number"])
                    * float(result["number2"])
                    * units.find_ratio(result["unit"], ["foot", "mile"])
                    if result["unit"]
                    else 1.0 * units.find_ratio(result["rad_diam"], ["rad", "diam"])
                    if result["rad_diam"]
                    else 1.0,
                    "aoe_shape": "line"
                    if result.get("shape") == "wall"
                    else result.get("shape", None),
                }
                values.append(value)
            # return values[0] if len(values) == 1 else values
            return values
        return [{"aoe_size": None, "aoe_shape": None}]
