# just thinking some things up
from dataclasses import dataclass
from enum import StrEnum  # sugestão Takai
import re
import rich  # testing purposes

from indexing import create_indices

## 0, creating operator classes


class NumericOperator(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    def operation(self, user_value):
        operations: dict = {
            NumericOperator.EQ: lambda x: x == int(user_value),
            NumericOperator.N_EQ: lambda x: x != int(user_value),
            NumericOperator.HT_o_E: lambda x: x >= int(user_value),
            NumericOperator.HT: lambda x: x > int(user_value),
            NumericOperator.LT_o_E: lambda x: x <= int(user_value),
            NumericOperator.LT: lambda x: x < int(user_value),
        }
        return operations[self]


class TextOperator(StrEnum):
    IS = ":"
    N_IS = "!="

    def operation(self, user_value):
        operations: dict = {
            TextOperator.IS: lambda x: x.lower() == user_value.lower(),
            TextOperator.N_IS: lambda x: x.lower() != user_value.lower(),
        }
        return operations[self]


# class BooleanOperators(StrEnum):
#     IS = "=="
#     I_N = "!="
#     pass


## 1, MVP of parser: takes user input, breaks it into [field, operator, value]
# user input, following hard formal syntax: <field><operator><value>
# WHERE CHANGE MATTERS
user_input: list = [
    "level>=8",
    "level:3",
    "school!=evocation",
    "class:bard",
    "damage_type!=fire",
    "sainvg_throw:cold, acid",
]


def parsing_query(user_input: list) -> list:
    # think of whitespaces, separators, error messages, .lower for str, int for int
    # check if query meets the syntax (not content, only syntax)
    # match operator to NumericOperator at some point
    return [re.split(pattern=r"(<|<=|:|>=|>|!=)", string=u_i) for u_i in user_input]


parsed_ui: list = parsing_query(user_input)


## 2, MVP for composing the command
fields: list = [p_ui[0] for p_ui in parsed_ui]
operators: list = [p_ui[1] for p_ui in parsed_ui]
values: list = [p_ui[2:] for p_ui in parsed_ui]  # there could be more than 1

for f in fields:
    pass

for o in operators:
    pass

for v in values:
    pass


def validating_input(field, operator, value):
    try:
        field in indices



# class SearchCommand:
#     """Contains all search logic based on app syntax.
#     Receives query objects, returns search commands"""

#     SEARCH_COMMAND = None

#     # def __init__(self, field, operator, value):
#     #     self.field: str = field
#     #     self.operator = operator
#     #     self.value: str | int = value


# class SearchLevel(SearchCommand):
#     SEARCH_COMMAND = ["l", "level"]

#     def __init__(self, field, operator, value):
#         # SearchCommand.__init__(self, value)
#         self.field: list = ["l", "level"]
#         self.operator = NumericOperator
#         self.value = value
#         pass


## 3, MVP, applying the command to levels
# # commands[0][0] is levels, so k=1, 2, 3, 4, 5, 6, 7, 8, 9, and v=list of spells
# # concers: int() values
for command in commands[0:2]:
    for k, v in indices[command[0]].items():
        calculation = apply_command(operator=command[1], value_user=command[2])
        if calculation(k):
            rich.print(f"with query {command}, the result is:\n{v}")
