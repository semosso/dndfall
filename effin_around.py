# setting up
from types import GeneratorType, NoneType
import re
import rich
import json

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


# where should this live? inside each Operator class? Operator class, with specific subclasses?
# all these ifs and modifiers will live in the Operator classes above
# the ifs should be based of value_ind, i.e., the one I keep in system
# this is the responsability of SearchCommand
def apply_command(operator, value_user):
    if type(value_user) is str:
        if operator == ":":
            return lambda value_ind: value_ind.lower() == value_user.lower()
        elif operator == "!=":
            return lambda value_ind: value_ind.lower() != value_user.lower()
    elif type(value_user) is int:
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
            return lambda value_ind: value_ind != int(value_user)


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

valid_fields = {
    "level": ["level", "l"],
    "school": ["school", "sc"],
    "class": ["class", "cl"],
    "damage_type": ["damage_type", "dt"],
    # "saving_throw": ["saving_throw", "st"],
}  # TBH, could be a list of tuple, or namedtuple

valid_operators = {
    "numeric": r"(<=|>=|!=|<|>|:)",
    "text": r"(!=|:)",
    "boolean": r"(!=|:)",
}


def parsing_query(user_input: list) -> list:
    # think of whitespaces, separators, error messages, .lower for str, int for int
    # check if query meets the syntax (not content, only syntax)
    # match operator to NumericOperator at some point
    return [re.split(pattern=r"(<=|>=|!=|<|>|:)", string=u_i) for u_i in user_input]


parsed_ui: list = parsing_query(user_input)


## 2, MVP for composing the command
fields: list = [p_ui[0] for p_ui in parsed_ui]
operators: list = [p_ui[1] for p_ui in parsed_ui]
values: list = [p_ui[2:] for p_ui in parsed_ui]  # there could be more than 1


def validating_input(field, operator):
    # first, field
    try:
        field in valid_fields.values()
    except:
        print(f"{field} is not a valid search field")
        ind = fields.index(field)
        fields.pop(ind), operators.pop(ind), values.pop(ind)
    # second, operator, based on field
    if field in valid_fields["level"]:
        try:
            operator in valid_operators["numeric"]
        except:
            print(f"{operator} is not a valid operator for field 'level'")
            ind = operators.index(operator)
            fields.pop(ind), operators.pop(ind), values.pop(ind)
    else:
        try:
            operator in valid_operators.values()
        except:
            print(f"{operator} is not a valid operator for field {field}")
            ind = operators.index(operator)
            fields.pop(ind), operators.pop(ind), values.pop(ind)


for f, o, _ in parsed_ui:
    validating_input(f, o)

commands = list(zip(fields, operators, values))

# MVP, applying the command to levels
# commands[0][0] is levels, so k=1, 2, 3, 4, 5, 6, 7, 8, 9, and v=list of spells
# concers: int() values
for command in commands:
    for k, v in indices[command[0]].items():
        calculation = apply_command(operator=command[1], value_user=command[2])
        if k is None:
            rich.print("no match")
        elif k is not NoneType and calculation(k):
            rich.print(f"with query {command}, the result is:\n{v}")

# MVP, applying the command to school
# commands[2][0] is school, so k=Evo, Transf, Necro, etc., and v=list of spells
# # concerns .lower() values; have to change operator behavior, but works
# for k, v in indices[commands[2][0]].items():
#     calculation = apply_command(operator=commands[2][1], value_user=commands[2][2])
#     if calculation(k):
#         rich.print(f"with query {commands[2]}, the result is:\n{v}")
