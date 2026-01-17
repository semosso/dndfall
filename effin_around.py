# setting up
import re
import rich
import json
from enum import StrEnum  # sugestão Takai

from normalization import normalizing_spells
from indexing import create_indices

## setting up mini-database and indices for testint purposes
with open(file="data/spells.json", mode="r") as raw_source:
    raw_spells: list[dict] = json.load(raw_source)

spells: dict[str, dict] = normalizing_spells(raw_spells)

indices: dict = create_indices(spells)


## MVP of search routines
# QueryParser
# breaks user input into <field><operator><value>
# passes it to Search Command
# SearchCommand (could merge with SearchEngine)
# validates the <field><operator> pair per field syntax
# composes the search command, and passes it to SearchEngine
# SearchEngine (could merge with SearchCommand)
# applies search command to indices<value>
# returns result to user


# categorizing the operators
class NumericOperators(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    def get_operator(self, str_op):
        pass


class TextOperators(StrEnum):
    IS = "=="
    I_N = "!="


class BooleanOperators(StrEnum):
    IS = "=="
    I_N = "!="


# where should this live? inside each Operator class? Operator class, with specific subclasses?
# all these ifs and modifiers will live in the Operator classes above
# the ifs should be based of value_ind, i.e., the one I keep in system
# this is the responsability of SearchCommand
def apply_command(operator, value_user):
    if operator == "<":
        return lambda value_ind: value_ind < int(value_user)
    elif operator == "<=":
        return lambda value_ind: value_ind <= int(value_user)
    elif operator == ":":
        return lambda value_ind: value_ind == int(value_user)
    elif operator == ">=":
        return lambda value_ind: value_ind >= int(value_user)
    elif operator == ">":
        return lambda value_ind: value_ind > int(value_user)
    elif operator == "!=":
        if type(value_user) is str:
            return (
                lambda value_ind: value_ind.lower() != value_user.lower()
            )  # if numeric, int()
    # if string, .lower()


# user input, following hard formal syntax
# syntax guide, <field>:<operator><value>
# WHERE CHANGE MATTERS
user_input = [
    "level>=8",
    "level:3",
    "school!=evocation",
    "class:bard",
    "damage_type!=fire",
]


# MVP of parser: takes user input, breaks it into category, operator, query
fields = []
operators = []
values = []

# think of whitespaces, separators, error messages, .lower for str, int for int
for u_i in user_input:
    parsed: list = re.split(pattern=r"(<|<=|:|>=|>|!=)", string=u_i)
    rich.print(parsed)
    fields.append(parsed[0])
    operators.append(parsed[1])
    values.append(parsed[2])

# MVP for composing the command
commands = list(zip(fields, operators, values))
rich.print(commands)

# MVP, applying the command to levels
# commands[0][0] is levels, so k=1, 2, 3, 4, 5, 6, 7, 8, 9, and v=list of spells
# concers: int() values
for command in commands[0:2]:
    for k, v in indices[command[0]].items():
        calculation = apply_command(operator=command[1], value_user=command[2])
        if calculation(k):
            rich.print(f"with query {command}, the result is:\n{v}")

# MVP, applying the command to school
# commands[2][0] is school, so k=Evo, Transf, Necro, etc., and v=list of spells
# # concerns .lower() values; have to change operator behavior, but works
# for k, v in indices[commands[2][0]].items():
#     calculation = apply_command(operator=commands[2][1], value_user=commands[2][2])
#     if calculation(k):
#         rich.print(f"with query {commands[2]}, the result is:\n{v}")
