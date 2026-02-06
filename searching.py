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
class SearchEngine:
    def __init__(self, user_input: str):
        self.user_input: str = user_input
        self.parsed_inputs: list

    # think of flags (ANY, NOT)
    def parse_query(self) -> list[ParsedQuery]:
        """Parses user input into field, operator and value parts.
        Input: user query
        Return: one ParsedQuery object per (f, o, v) match"""
        parsed_inputs: list = []
        pattern = r"(\w+)(<=|>=|!=|<|>|:)\(([^)]+)\)|(\w+)(<=|>=|!=|<|>|:)([^\s()]+)"
        for match in re.finditer(pattern, self.user_input):
            if match.group(1):
                f_: str = match.group(1)
                o_: str = match.group(2)
                v_: list = match.group(3).split()
                parsed_inputs.append(
                    ParsedQuery(p_field=f_, p_operator=o_, p_values=v_)
                )
            else:
                f_: str = match.group(4)
                o_: str = match.group(5)
                v_: list = match.group(6).split()
                parsed_inputs.append(
                    ParsedQuery(p_field=f_, p_operator=o_, p_values=v_)
                )
        return parsed_inputs

    # to use when I add the OR/ANY/NOT flags
    def results_wrapper(self):
        pass


@dataclass
class ParsedQuery:
    p_field: str
    p_operator: str
    p_values: list[str]

    # think of error messages
    def validate_field(self) -> SearchCommand:
        if self.p_field in dndspecs.FIELD_BY_ALIAS:
            field_rules = dndspecs.FIELD_BY_ALIAS[self.p_field]
            return SearchCommand(p_query=self, field_rules=field_rules)
        else:
            raise ValueError(f"{self.p_field} is not a valid search field")


class SearchCommand:
    def __init__(self, p_query: ParsedQuery, field_rules: dndspecs.SpellField):
        self.sc_field: str = p_query.p_field
        self.sc_operator: StrEnum = p_query.p_operator
        self.sc_values: list = p_query.p_values
        self.field_rules: dndspecs.SpellField = field_rules

    # think of error messages
    def validate_operator(self):
        try:
            self.field_rules.operator(self.sc_operator)
        except ValueError:
            raise ValueError(
                f"'{self.sc_operator}' is not a valid operator for '{self.sc_field}'"
            )
        return True

    # think of error messages
    def validate_values(self):
        for value in self.sc_values:
            try:
                val_check: int | str = (
                    int(value)
                    if self.field_rules.operator == dndspecs.NumericOp
                    else value
                )
            except ValueError:
                raise ValueError(
                    f"Value for {self.sc_field} must be a number (e.g., 3, not three)"
                )
            if val_check not in self.field_rules.values:
                raise ValueError(
                    f"Invalid value ('{val_check}') for field '{self.sc_field}'"
                )
        return True

    def compose_command(self):
        comm_field: str = self.field_rules.name
        comm_operator: StrEnum = self.sc_operator
        comm_values: set = {
            int(value) if self.field_rules.operator is dndspecs.NumericOp else value
            for value in self.sc_values
        }
        if self.validate_operator() and self.validate_values():
            # each different command must be instantiated separately
            return SearchExecution(
                field=comm_field, operator=comm_operator, values=comm_values
            )


class SearchExecution:
    # TBD how this looks when I no longer have "indices" initiated in the same module
    OP_BY_STRAT: dict = {
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
        op: strategy for strategy, ops in OP_BY_STRAT.items() for op in ops
    }

    def __init__(self, field, operator, values):
        self.c_field: str = field
        self.c_operator: str = operator
        self.c_values: set = values

    def execute(self):
        strat_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, strat_name)
        # testing
        print(self.c_field, self.c_operator, self.c_values)
        return strategy()

    # create different strategies for num vs text, too many convert to int things
    # or adapt like in final section of search creation
    def direct_lookup(self):
        return set().union(*(INDICES[self.c_field][v] for v in self.c_values))

    def exclusion_lookup(self):
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
            k for k in INDICES[self.c_field].keys() if op[self.c_operator](int(k))
        ]
        return set().union(*(INDICES[self.c_field][k] for k in match_keys))


def orchestrate_search(query: str):
    parsed_queries: list[ParsedQuery] = SearchEngine(user_input=query).parse_query()
    results: list = []
    for pq in parsed_queries:
        results.append(pq.validate_field().compose_command().execute())
    return set.intersection(*results)


## testing things

user_input = "gp>500 st:wisdom"
rich.print(orchestrate_search(user_input))
rich.print(INDICES["gp_cost"])
