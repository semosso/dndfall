import re
from enum import StrEnum
from dataclasses import dataclass

import dndspecs

## initialization for easier testing
import json
from normalization import normalizing_spells
from indexing import create_indices
import rich


# gets JSON data, will evolve to API calls to 5e SRD database
with open(file="data/spells.json", mode="r") as raw_source:
    raw_spells: list[dict] = json.load(raw_source)

# calls "normalization" to normalizes JSON data into dataclass objects
SPELLS: dict[str, dict] = normalizing_spells(database=raw_spells)
INDICES: dict = create_indices(
    spells=SPELLS, scalar_f=dndspecs.SCALAR_FIELDS, derived_f=dndspecs.DERIVED_FIELDS
)


## strategy classes
@dataclass
class ParsedQuery:
    p_field: str
    p_operator: str
    p_values: list[str]


class SearchEngine:
    # add repr or str
    def __init__(self, user_input):
        self.user_input: str = user_input

    # think of separators, error messages, etc. also only works for a single field
    # is parse_query doing too much? TBD
    def parse_query(self) -> SearchCommand:
        """Parses user input into field, operator and value parts.
        Input: user query
        Return: a ParsedQuery object"""

        parts: list[str] = re.split(pattern=r"(<=|>=|!=|<|>|:)", string=self.user_input)
        if len(parts) < 3:
            raise ValueError("no valid operator in query")
        else:
            f_, o_, *v_ = parts
            values_list: list[str] = [v.strip().lower() for v in "".join(v_).split(",")]
        field_rules: str = dndspecs.FIELD_BY_ALIAS.get(f_, "")
        match field_rules:
            case dndspecs.SpellField():
                parsed_input = ParsedQuery(
                    p_field=f_, p_operator=o_, p_values=values_list
                )
                return SearchCommand(
                    parsed_input,
                    field_rules=field_rules,
                )
            case _:
                raise ValueError("no valid field in query")


class SearchCommand:
    def __init__(self, p_query: ParsedQuery, field_rules: dndspecs.SpellField):
        self.field: str = p_query.p_field
        self.operator: StrEnum = p_query.p_operator
        self.values: list = p_query.p_values
        self.field_rules: dndspecs.SpellField = field_rules

    def validate_operator(self):
        try:
            self.field_rules.operator(self.operator)
        except ValueError:
            raise ValueError(
                f"'{self.operator}' is not a valid operator for '{self.field}'"
            )
        return True

    def validate_values(self):
        for value in self.values:
            try:
                val_check: int | str = (
                    int(value)
                    if self.field_rules.operator == dndspecs.NumericOp
                    else value
                )
            except ValueError:
                raise ValueError(
                    f"Value for {self.field} must be a number (e.g., 3, not three)"
                )
            if val_check not in self.field_rules.values:
                raise ValueError(
                    f"Invalid value ('{val_check}') for field '{self.field}'"
                )
        return True

    def compose_command(self):
        command_field: str = self.field_rules.name
        command_operator: StrEnum = self.operator
        command_values: set = {
            int(value) if self.operator in dndspecs.NumericOp else value
            for value in self.values
        }
        if self.validate_operator() and self.validate_values():
            return SearchExecution(
                field=command_field, operator=command_operator, values=command_values
            )


class SearchExecution:
    # TBD how this looks when I no longer have "indices" initiated in the same module
    STRATEGY_MAPPINGS: dict[str, str] = {
        dndspecs.NumericOp.EQ: "direct_lookup",
        dndspecs.NumericOp.N_EQ: "exclusion_lookup",
    }

    def __init__(self, field, operator, values):
        self.c_field = field
        self.c_operator = operator
        self.c_values = values

    def execute(self):
        method_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, method_name)
        return strategy()

    # do I want to return something ordered? additional info around it?
    # TBD, update() works for testing, not really for visualization
    def direct_lookup(self):
        results = set()
        for value in self.c_values:
            results.update(INDICES[self.c_field][value])
        return results

    # def exclusion_lookup(self):
    #     not_v_list: set = set()
    #     # this works, but might be doing more work than needed
    #     for not_v in INDICES[self.c_field]:
    #         if not_v not in self.c_values and not_v not in not_v_list:
    #             not_v_list.add((not_v, INDICES[self.c_field][not_v]))
    #     return not_v_list


## testing things

user_input = "l:3"
search_command = SearchEngine(user_input).parse_query()
rich.print(search_command)
composing_command = search_command.compose_command()
rich.print(composing_command)
executing_search = composing_command.execute()
rich.print(executing_search)
