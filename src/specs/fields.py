from dataclasses import dataclass
import re

import src.specs.units as units
import src.specs.regex as regex
from src.specs.schema import DerivedField


@dataclass
class UpcastableField(DerivedField):
    patterns = regex.UPCAST_PATTERNS

    compiled_patterns = [
        re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns
    ]

    def process_patterns(self, source_text):
        for pattern in self.compiled_patterns:
            result = pattern.search(source_text)
            if result:
                return True
        return False


@dataclass
class DamageField(DerivedField):
    compiled_patterns = re.compile(regex.DAMAGE_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.damage_results = []
        for match in self.compiled_patterns.finditer(string=source_text):
            groups = match.groupdict()
            result = {
                "number": groups.get("number") or 0,
                "die": groups.get("die") or 0,
                "fixed": groups.get("fixed") or 0,
                "type": groups.get("type") or None,
            }
            self.damage_results.append(result)
        return self.get_values()

    def get_values(self):
        values = []
        if self.damage_results:
            for result in self.damage_results:
                value = {
                    "damage_type": result["type"],
                    "damage_amount": units.DiceRoll.avg_roll(
                        result["number"], result["die"]
                    )
                    + int(result["fixed"]),
                    "damage_maximum": units.DiceRoll.max_roll(
                        result["number"], result["die"]
                    )
                    + int(result["fixed"]),
                }
                values.append(value)
            return values
        return [
            {
                "damage_type": None,
                "damage_amount": 0,
                "damage_maximum": 0,
                "damage_at_slot_level": 0,
                "damage_at_character_level": 0,
            }
        ]


@dataclass
class GpCostField(DerivedField):
    compiled_patterns = re.compile(pattern=regex.GP_COST_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.number, self.unit = 0, "gold"
        result = self.compiled_patterns.search(string=source_text)
        if result:
            groups = result.groupdict()
            if "number" in groups:
                self.number = groups.get("number").replace(",", "") or 0
                self.unit = groups.get("unit") or ""
        return self.get_values()

    def get_values(self):
        unit_ratio = units.find_ratio(
            value=self.unit,
            categories=["gold", "platinum", "electrum", "silver", "copper"],
        )
        return int(self.number) * unit_ratio


@dataclass
class RangeField(DerivedField):
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
                    self.number = groups.get("number") or ""
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
            return int(self.number) * text_ratio
        if self.text:
            return text_ratio


@dataclass
class DurationField(DerivedField):
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
                if "number" in groups:
                    self.number = groups.get("number") or ""
                    self.unit = groups.get("unit") or ""
                if "text" in groups:
                    self.text = groups.get("text") or ""
                break
        return self.get_values()

    def get_values(self):
        text_value = self.unit if self.unit else self.text
        text_ratio = units.find_ratio(
            value=text_value,
            categories=["instantaneous", "second", "minute", "hour", "day", "year"],
        )
        if self.number:
            return int(self.number) * text_ratio
        if self.text:
            return text_ratio


@dataclass
class CastingTimeField(DerivedField):
    compiled_patterns = re.compile(regex.CASTING_TIME_PATTERNS, flags=re.IGNORECASE)

    def process_patterns(self, source_text):
        self.number, self.unit = "", ""
        result = self.compiled_patterns.search(string=source_text)
        if result:
            self.number = result.group(1)
            self.unit = result.group(2)
        return self.get_values()

    def get_values(self):
        if not self.number:
            return None
        text_ratio = units.find_ratio(
            value=self.unit,
            categories=["second", "minute", "hour", "day", "year", "dnd_economy"],
        )
        return int(self.number) * text_ratio


@dataclass
class AreaOfEffectField(DerivedField):
    patterns = regex.AOE_PATTERNS

    compiled_patterns = [
        re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns
    ]

    def process_patterns(self, source_text):
        self.number, self.unit, self.rad_diam, self.shape = "", "", "", ""

        for pattern in self.compiled_patterns:
            result = re.search(pattern=pattern, string=source_text)
            if result:
                groups = result.groupdict()
                self.number = groups.get("number") or ""
                self.number2 = groups.get("number2") or ""
                self.unit = groups.get("unit") or ""
                self.rad_diam = groups.get("rad_diam") or ""
                self.shape = groups.get("shape") or ""
                break
        return self.get_values()

    def get_values(self):
        if not self.number:
            return None
        if self.modifier:
            if self.shape == "wall":
                return "line"
            return self.shape
        else:
            unit_ratio = units.find_ratio(self.unit, ["foot", "mile"])
            rad_diam_ratio = (
                units.find_ratio(self.rad_diam, ["rad", "diam"])
                if self.rad_diam
                else 1.0
            )

            # for calculating X by X blocks or areas
            if self.number2:
                area = int(self.number) * int(self.number2)
                return area * unit_ratio * rad_diam_ratio

            return int(self.number) * unit_ratio * rad_diam_ratio
