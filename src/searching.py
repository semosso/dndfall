from __future__ import annotations
import re
from enum import StrEnum
from dataclasses import dataclass

from src import dndspecs
from pages.cached_data import SPELLS, INDICES


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
        validated_values = set()
        for value in self.sc_values:
            match self.field_rules.operator:
                case dndspecs.NumericOp:
                    val_check = int(value)
                case dndspecs.BooleanOp:
                    lower_val = value.lower()
                    if lower_val in ("true", "yes"):
                        val_check = True
                    elif lower_val in ("false", "no"):
                        val_check = False
                case dndspecs.TextOp:
                    val_check = value.lower()
                # case set(dndspecs.NumericOp, dndspecs.TextOp):
                #     pass
                case _:
                    raise ValueError(
                        f"Invalid value ('{value}') for field '{self.sc_field}'"
                    )
            # think about this (avoids duplication in compose_command())
            validated_values.add(val_check)
            if self.field_rules.values and val_check not in self.field_rules.values:
                raise ValueError(
                    f"Invalid value ('{val_check}') for field '{self.sc_field}'"
                )
        return validated_values

    def compose_command(self):
        comm_field: str = self.field_rules.name
        comm_operator: StrEnum = self.sc_operator
        comm_values: set = self.validate_values()
        if self.validate_operator() and self.validate_values():
            return SearchExecution(
                field=comm_field,
                operator=comm_operator,
                values=comm_values,
                rules=self.field_rules,
            )


class SearchExecution:
    OP_BY_STRAT: dict = {
        "direct_lookup": {
            dndspecs.NumericOp.EQ,
            dndspecs.TextOp.EQ,
            dndspecs.BooleanOp.IS,
        },
        "exclusion_lookup": {
            dndspecs.NumericOp.N_EQ,
            dndspecs.TextOp.N_EQ,
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

    def __init__(self, field, operator, values, rules):
        self.c_field: str = field
        self.c_operator: str = operator
        self.c_values: set = values
        self.c_rules = rules

    def execute(self):
        strat_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, strat_name)
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


print(INDICES["range"])
