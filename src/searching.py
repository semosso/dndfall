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

    def parse_query(self) -> list[ParsedQuery]:
        """Parses user input into field, operator and value parts.
        Input: user query
        Return: one ParsedQuery object per (f, o, v) match"""
        parsed_inputs: list = []
        pattern = r"""(?x)
        (-)?(\w+)([<>=:]+)\(([^)]+)\)|# -dt:(fire cold)
        (-)?(\w+)([<>=:]+)([^\s()]+)|# -dt:fire
        ([-*])(\w+)|# NOT and ANY applicable fields
        (-)?(\w+)#name search
        """
        for match in re.finditer(pattern, self.user_input):
            if match.group(2):
                mod_: str = "NOT" if match.group(1) == "-" else ""
                f_: str = match.group(2)
                o_: str = match.group(3)
                v_: list = match.group(4).split()
                parsed_inputs.append(
                    ParsedQuery(
                        p_field=f_.lower(), p_operator=o_, p_values=v_, modifier=mod_
                    )
                )
            elif match.group(6):
                mod_: str = "NOT" if match.group(5) == "-" else ""
                f_: str = match.group(6)
                o_: str = match.group(7)
                v_: list = match.group(8).split()
                parsed_inputs.append(
                    ParsedQuery(
                        p_field=f_.lower(), p_operator=o_, p_values=v_, modifier=mod_
                    )
                )
            elif match.group(10):
                mod_ = "ANY" if match.group(9) == "*" else "NOT"
                f_ = match.group(10)
                o_: str = ":"
                v_: None = None
                parsed_inputs.append(
                    ParsedQuery(p_field=f_, p_operator=o_, p_values=None, modifier=mod_)
                )
            else:
                mod_ = "NOT" if match.group(11) == "-" else ""
                f_ = "spell_name"
                o_ = ":"
                v_ = [match.group(12)]
                parsed_inputs.append(
                    ParsedQuery(p_field=f_, p_operator=o_, p_values=v_, modifier=mod_)
                )
        return parsed_inputs

    # to use when I add the OR/ANY/NOT flags
    def results_wrapper(self):
        pass


@dataclass
class ParsedQuery:
    p_field: str
    p_operator: str
    p_values: list[str] | None
    modifier: str | None = None

    def validate_field(self) -> SearchCommand:
        if self.p_field == "spell_name":
            field_rules = dndspecs.NAME
        elif self.p_field in dndspecs.FIELD_BY_ALIAS:
            field_rules = dndspecs.FIELD_BY_ALIAS[self.p_field]
        elif self.p_field in ["description", "desc"]:
            field_rules = dndspecs.DESCRIPTION
        else:
            raise ValueError(f"'{self.p_field}' is not a valid search field")
        return SearchCommand(
            p_query=self,
            field_rules=field_rules,
            modifier=self.modifier,
        )


class SearchCommand:
    def __init__(
        self,
        p_query: ParsedQuery,
        field_rules: dndspecs.SpellField,
        modifier: str | None = None,
    ):
        self.sc_field: str = p_query.p_field
        self.sc_operator: StrEnum = p_query.p_operator
        self.sc_values: list = p_query.p_values
        self.field_rules: dndspecs.SpellField = field_rules
        self.modifier: bool = modifier

    def validate_operator(self):
        try:
            self.field_rules.operator(self.sc_operator)
        except ValueError:
            raise ValueError(
                f"'{self.sc_operator}' is not a valid operator for '{self.sc_field}'"
            )
        return True

    def validate_values(self):

        validated_values = set()
        if self.sc_values is None:
            return set()
        for value in self.sc_values:
            match self.field_rules.operator:
                case dndspecs.NumericOp:
                    if isinstance(self.field_rules, dndspecs.DerivedField):
                        try:
                            val_check = int(value)
                        except ValueError:
                            if not self._valid_text(value):
                                raise ValueError(
                                    f"'{value}' is not a valid number for '{self.sc_field}'"
                                )
                            val_check = value
                    else:
                        try:
                            val_check = int(value)
                        except ValueError:
                            raise ValueError(
                                f"'{value}' is not a valid number for '{self.sc_field}'"
                            )
                case dndspecs.BooleanOp:
                    lower_val = value.lower()
                    if lower_val in ("true", "yes"):
                        val_check = True
                    elif lower_val in ("false", "no"):
                        val_check = False
                    else:
                        raise ValueError(
                            f"'{value}' is not a valid value for '{self.sc_field}'"
                        )
                case dndspecs.TextOp:
                    val_check = value.lower()
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

    def _valid_text(self, value):
        value_lower = value.lower()

        for category in ["self", "touch", "foot", "mile"]:
            if value_lower in dndspecs.LENGTH_UNIT[category]["aliases"]:
                return True

        for category in [
            "instantaneous",
            "second",
            "minute",
            "hour",
            "day",
            "year",
            "dnd_economy",
        ]:
            if value_lower in dndspecs.TIME_UNIT[category]["aliases"]:
                return True

    def compose_command(self):
        comm_values: set = self.validate_values()
        self.validate_operator()
        return SearchExecution(
            field=self.field_rules.name.lower(),
            operator=self.sc_operator,
            values=comm_values,
            rules=self.field_rules,
            modifier=self.modifier,
        )


class SearchExecution:
    OP_BY_STRAT: dict = {
        "direct_lookup": {
            dndspecs.NumericOp.EQ,
            dndspecs.TextOp.EQ,
            dndspecs.BooleanOp.IS,
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

    def __init__(self, field, operator, values, rules, modifier=None):
        self.c_field: str = field
        self.c_operator: str = operator
        self.c_values: set = values
        self.c_rules = rules
        self.modifier: str | None = modifier

    def execute(self):
        strat_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, strat_name)
        return strategy()

    # create different strategies for num vs text, too many convert to int things
    # or adapt like in final section of search creation
    def direct_lookup(self):
        if self.c_field == "spell_name":
            return {
                spell
                for spell in INDICES["spell_name"]
                if any(v in spell.lower() for v in self.c_values)
            }
        if self.c_field in ["description", "desc"]:
            return {
                spell
                for spell in SPELLS.keys()
                if any(
                    v in " ".join(" ".join(SPELLS[spell].description).split()).lower()
                    for v in self.c_values
                )
            }
        matches = {
            self._extract_ratio(v) if isinstance(v, str) else v for v in self.c_values
        }
        return set().union(
            *(INDICES[self.c_field][v] for v in matches),
        )

    def range_lookup(self):
        # adapt for text comparison; e.g., if isinstance str normalize
        target = next(iter(self.c_values))

        if isinstance(target, str):
            target = self._extract_ratio(target)

        op: dict = {
            dndspecs.NumericOp.GT_E: lambda x: x >= target,
            dndspecs.NumericOp.GT: lambda x: x > target,
            dndspecs.NumericOp.LT_E: lambda x: x <= target,
            dndspecs.NumericOp.LT: lambda x: x < target,
        }
        match_keys: list = []

        for k in INDICES[self.c_field].keys():
            try:
                numeric_k = float(k)
                if op[self.c_operator](numeric_k):
                    match_keys.append(k)
            except (ValueError, TypeError):
                pass

        return set().union(*(INDICES[self.c_field][k] for k in match_keys))

    def _extract_ratio(self, value):
        value_lower = value.lower()

        for category in ["self", "touch", "foot", "mile"]:
            if value_lower in dndspecs.LENGTH_UNIT[category]["aliases"]:
                return dndspecs.LENGTH_UNIT[category]["ratio"]

        for category in [
            "instantaneous",
            "second",
            "minute",
            "hour",
            "day",
            "year",
            "dnd_economy",
        ]:
            if value_lower in dndspecs.TIME_UNIT[category]["aliases"]:
                return dndspecs.TIME_UNIT[category]["ratio"]

        return value

    def applying_modifier(self, pre_result):
        if self.modifier == "NOT":
            if len(self.c_values) == 0:
                all_field_values = set().union(*(INDICES[self.c_field].values()))
                return set(SPELLS.keys()) - all_field_values
            return set(SPELLS.keys()) - pre_result
        if self.modifier == "ANY":
            if self.c_field in ["condition", "saving_throw", "damage_type"]:
                return set().union(*(INDICES[self.c_field].values()))
            else:
                raise ValueError(
                    f"'*' modifier incompatible with '{self.c_field}' searches"
                )
        return pre_result


def orchestrate_search(query: str):
    parsed_queries: list[ParsedQuery] = SearchEngine(user_input=query).parse_query()
    if not parsed_queries:
        raise ValueError(
            f"Could not parse query: '{query}'. Please review our syntax guide!"
        )
    results: list = []
    for pq in parsed_queries:
        search_execution: set = pq.validate_field().compose_command()
        pre_result: set = search_execution.execute()
        results.append(search_execution.applying_modifier(pre_result))
    return set.intersection(*results)
