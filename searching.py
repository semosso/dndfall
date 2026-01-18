# just thinking some things up
from dataclasses import dataclass
from enum import StrEnum  # sugestão Takai
import re

import rich  # testing purposes

## 0, creating operator classes


class NumericOperator(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    def oerator_behavior(self, user_value):
        operations: dict = {
            NumericOperator.EQ: lambda x: x == user_value,
            NumericOperator.N_EQ: lambda x: x != user_value,
            NumericOperator.HT_o_E: lambda x: x >= user_value,
            NumericOperator.HT: lambda x: x > user_value,
            NumericOperator.LT_o_E: lambda x: x <= user_value,
            NumericOperator.LT: lambda x: x < user_value,
        }
        return operations[self]


class TextOperators(StrEnum):
    IS = "=="
    I_N = "!="


class BooleanOperators(StrEnum):
    IS = "=="
    I_N = "!="

    def get_operator(self, str_op):
        pass


## 1, MVP of parser: takes user input, breaks it into [field, operator, value]
# user input, following hard formal syntax: <field><operator><value>
# WHERE CHANGE MATTERS
user_input = [
    "level>=8",
    "level:3",
    "school!=evocation",
    "class:bard",
    "damage_type!=fire",
]


class QueryParser:
    """Receives user input, returns query objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    pass


def query_parsing(user_input: str) -> list:
    # think of whitespaces, separators, error messages, .lower for str, int for int
    # if or try/except to check if query meets the syntax (not content, only syntax)
    parsed_input: list = [
        re.split(pattern=r"(<|<=|:|>=|>|!=)", string=u_i) for u_i in user_input
    ]
    # rich.print(parsed_input) # testing
    return parsed_input


## 2, MVP for composing the command
# commands = list(zip(fields, operators, values))
# rich.print(commands)


class SearchLogic:
    """Contains all search logic based on app syntax.
    Receives query objects, returns search commands"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, field, operator, value):
        self.field: str = field
        self.operator: str = operator
        self.value: str | int = value


# @dataclass | or class?
# class SearchCommand:
#     # [level, l], [saving_throw, st], [damage_type, dt]; should it be tuple?
#     command: list
#     # what operators apply to it; >, <, ==, !=
#     operators: list


# @dataclass | or class?
# class LevelSearch(SearchCommand):
#     command: list = ["l", "level"]
#     operators: list = [operators["equality"], [operators["comparison"]]]
#     level: int

#     def matches(self, spell):  # ?
#         pass


## 3, MVP, applying the command to levels
# # commands[0][0] is levels, so k=1, 2, 3, 4, 5, 6, 7, 8, 9, and v=list of spells
# # concers: int() values
# for command in commands[0:2]:
#     for k, v in indices[command[0]].items():
#         calculation = apply_command(operator=command[1], value_user=command[2])
#         if calculation(k):
#             rich.print(f"with query {command}, the result is:\n{v}")


class SearchEngine:
    """Receives search commands, returns search results over
    indexes or NormalizedSpell objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, logic):
        self.logic = logic
