import re
from enum import StrEnum
from dataclasses import dataclass

import dndspecs

## initialization for easier testing
import json
from normalization import normalizing_spells, create_indices
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
            int(value) if self.field_rules.operator is dndspecs.NumericOp else value
            for value in self.values
        }
        if self.validate_operator() and self.validate_values():
            # each different command must be instantiated separately
            return SearchExecution(
                field=command_field, operator=command_operator, values=command_values
            )


class SearchExecution:
    # TBD how this looks when I no longer have "indices" initiated in the same module
    op_by_strategy: dict = {
        "direct_lookup": {
            dndspecs.NumericOp.EQ,
            dndspecs.TextOp.EQ,
            dndspecs.BooleanOp.IS,
        },
        "exclusion_lookup": {
            dndspecs.NumericOp.N_EQ,
            dndspecs.TextOp.N_EQ,
            dndspecs.BooleanOp.N_IS,
        },
        "range_lookup": {
            dndspecs.NumericOp.GT_E,
            dndspecs.NumericOp.GT,
            dndspecs.NumericOp.LT_E,
            dndspecs.NumericOp.LT,
        },
    }

    STRATEGY_MAPPINGS: dict = {
        op: strategy for strategy, ops in op_by_strategy.items() for op in ops
    }

    def __init__(self, field, operator, values):
        self.c_field = field
        self.c_operator = operator
        self.c_values = values

    # change the lookups to subclasses? and use execute() and wrap_results()
    # to get additional context info, sort of like a wrapper function
    # i.e., they can perform the searches and record information one by one
    # i.e., orchestrator to processes results and show a customer friendly version
    def execute(self):
        method_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, method_name)
        return strategy()

    def wrap_results(self, results):
        return {
            "field": f"{self.c_field}",
            "operator": f"{self.c_operator}",
            "values": f"{self.c_values}",
            "results": results,
        }

    def direct_lookup(self):
        return set().union(*(INDICES[self.c_field][v] for v in self.c_values))

    def exclusion_lookup(self):
        # sets_to_merge: list = [
        #     INDICES[self.c_field][not_value]
        #     for not_value in INDICES[self.c_field]
        #     if not_value not in self.c_values
        # ]
        # if not sets_to_merge:
        #     return set()
        # return set().union(*sets_to_merge)
        return set(SPELLS.keys()) - set().union(
            *(INDICES[self.c_field][v] for v in self.c_values)
        )

    def range_lookup(self):
        # level is the only one I have today, but soon casting time, duration,
        # range, material cost etc.
        target = next(iter(self.c_values))
        op: dict = {
            dndspecs.NumericOp.GT_E: lambda x: x >= target,
            dndspecs.NumericOp.GT: lambda x: x > target,
            dndspecs.NumericOp.LT_E: lambda x: x <= target,
            dndspecs.NumericOp.LT: lambda x: x < target,
        }
        match_keys: list = [
            k for k in INDICES[self.c_field].keys() if op[self.c_operator](k)
        ]
        return set().union(*(INDICES[self.c_field][k] for k in match_keys))
        # matching = set()
        # for k in INDICES[self.c_field].keys():
        #     for v in self.c_values:
        #         if op[self.c_operator](k, v):
        #             matching.update(INDICES[self.c_field][k])
        # return matching


## testing things

user_input = "level<4"
search_command = SearchEngine(user_input).parse_query()
rich.print(search_command)
composing_command = search_command.compose_command()
rich.print(composing_command)
executing_search = composing_command.execute()
rich.print(executing_search)
