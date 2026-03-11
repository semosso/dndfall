from enum import StrEnum
from dataclasses import dataclass, field

import src.specs.units as units
from src.search import FIELD_BY_ALIAS, NAME, DESCRIPTION
from src.search.query_handler import ParsedQuery
from src.specs.schema import SearchField


@dataclass
class SearchCommand:
    field: str
    operator: str
    values: set
    rules: SearchField
    modifier: str | None = field(default=None)


class CommandValidation:
    def __init__(self, parsed_query: ParsedQuery):
        self.field: str = parsed_query.field
        self.operator: StrEnum = parsed_query.operator
        self.values: list = parsed_query.values
        self.modifier: str | None = parsed_query.modifier

        if self.field == "spell_name":
            self.field_rules = NAME
        elif self.field in FIELD_BY_ALIAS:
            self.field_rules = FIELD_BY_ALIAS[self.field]
        elif self.field in ["description", "desc"]:
            self.field_rules = DESCRIPTION
        else:
            raise ValueError(f"'{self.field}' is not a valid search field")

    def validate_operator(self):
        try:
            self.field_rules.operator(self.operator)
        except ValueError:
            raise ValueError(
                f"'{self.operator}' is not a valid operator for '{self.field}'"
            )
        return True

    def validate_values(self):
        validated_values = set()
        # in case of modifiers
        if self.values is None:
            return set()
        for value in self.values:
            match self.field_rules.operator:
                case units.NumericOp:
                    try:
                        val_check = int(value)
                    except ValueError:
                        if not self._valid_text(value):
                            raise ValueError(
                                f"'{value}' is not a valid number for '{self.field}'"
                            )
                        val_check = value
                case units.BooleanOp:
                    lower_val = value.lower()
                    if lower_val in ("true", "yes"):
                        val_check = True
                    elif lower_val in ("false", "no"):
                        val_check = False
                    else:
                        raise ValueError(
                            f"'{value}' is not a valid value for '{self.field}'"
                        )
                case units.TextOp:
                    val_check = value.lower()
                case _:
                    raise ValueError(
                        f"Invalid value ('{value}') for field '{self.field}'"
                    )
            if self.field_rules.values and val_check not in self.field_rules.values:
                raise ValueError(
                    f"Invalid value ('{val_check}') for field '{self.field}'"
                )
            validated_values.add(val_check)
        return validated_values

    def _valid_text(self, value):
        value_lower = value.lower()

        if value_lower in units.LENGTH_UNIT["self"]["aliases"]:
            return True

        if (
            value_lower
            in units.TIME_UNIT["dnd_economy"]["aliases"]
            + units.TIME_UNIT["until_dispelled"]["aliases"]
        ):
            return True

    def compose_command(self):
        valid_values: set = self.validate_values()
        self.validate_operator()
        return SearchCommand(
            field=self.field_rules.name.lower(),
            operator=self.operator,
            values=valid_values,
            rules=self.field_rules,
            modifier=self.modifier,
        )
