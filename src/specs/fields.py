from dataclasses import dataclass
import re

import src.specs.units as units
import src.specs.regex as regex
from src.specs.schema import DerivedField


@dataclass
class UpcastField(DerivedField):
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
class DiceAmountField(DerivedField):
    compiled_patterns = re.compile(regex.DICE_AMOUNT_PATTERNS, flags=re.IGNORECASE)

    # see if I broke this
    def process_patterns(self, source_text):
        self.number, self.die, self.fixed = "", "", ""
        result = self.compiled_patterns.search(string=source_text)
        if result:
            groups = result.groupdict()
            if "number" in groups:
                self.number = groups.get("number") or ""
                self.die = groups.get("die") or ""
                self.fixed = groups.get("fixed") or "0"

            return self.get_values()

    def get_values(self):
        if self.modifier:
            return units.DiceRoll.max_damage(self.number, self.die) + int(self.fixed)
        return units.DiceRoll.avg_damage(self.number, self.die) + int(self.fixed)


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
