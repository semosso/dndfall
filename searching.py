# search MVP

from dataclasses import dataclass
from enum import StrEnum
import re
# import rich  # testing purposes

## operator logic

class NumericOp(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    def operation(self, user_value):
        num_operations: dict = {
            NumericOp.EQ: lambda x: x == int(user_value),
            NumericOp.N_EQ: lambda x: x != int(user_value),
            NumericOp.HT_o_E: lambda x: x >= int(user_value),
            NumericOp.HT: lambda x: x > int(user_value),
            NumericOp.LT_o_E: lambda x: x <= int(user_value),
            NumericOp.LT: lambda x: x < int(user_value),
        }
        return num_operations[self]


class TextOp(StrEnum):
    IS = ":"
    N_IS = "!="

    def operation(self, user_value):
        txt_operations: dict = {
            TextOp.IS: lambda x: x.lower() == user_value.lower(),
            TextOp.N_IS: lambda x: x.lower() != user_value.lower(),
        }
        return txt_operations[self]

# class BooleanOperators(StrEnum):
#     IS = "=="
#     I_N = "!="
#     pass

## syntax structure, MVP
# too verbose, can I reference it from somewhere else?
# e.g., from the structure of NormalizedSpell? don't think so, this is syntax
# at the very least, break into a separate "syntax_rules" module

valid_fields: dict = {
    "level": ["level", "l"],
    "school": ["school", "sc"],
    "class": ["class", "cl"],
    "damage_type": ["damage_type", "dt"],
    "saving_throw": ["saving_throw", "st"],
}  # TBH, could be a list of tuple, or namedtuple

field_lookup: dict = {
    alias: field
    for field, aliases in valid_fields.items()
    for alias in aliases
}

valid_operators = {
    "level": NumericOp,
    "school": TextOp,
    "class": TextOp,
    "damage_type": TextOp,
    "saving_throw": TextOp,
    # "boolean": r"(!=|:)", # leaving this for later
}

## user input parsing and validation

@dataclass
class ParsedQuery:
    field: str
    operator: str
    values: list[str]

@dataclass
class SearchCommand:
    field: str
    operator: NumericOp | TextOp
    values: list[str]

def query_parser(user_input: str) -> ParsedQuery:
    # think of whitespaces, separators, error messages, .lower str, int user_input
    # "value" can have multiple values, keep in mind when composing command
    components: list = re.split(pattern=r"\s*(<=|>=|!=|<|>|:)\s*", string=user_input)
    f, o, *vs = components
    values_list = [v.strip() for v in "".join(vs).split(",")]
    return ParsedQuery(field=f.strip().lower(), operator=o, values=values_list)


def query_validator(pq: ParsedQuery) -> bool | SearchCommand:
    # validating fields, MVP
    # if field is level, some function needs to int(user_value)
    valid_field: str | None = field_lookup.get(pq.field)

    if valid_field is None:
        print(f"'{pq.field}' is not a valid field")
        return False
    
    # validating operators, MVP
    # do boolean later
    try:
        applicable_op = valid_operators[valid_field]
        op = applicable_op(pq.operator)
        # can I have if True, call command_search?
    except ValueError:
        print(f"'{pq.operator}' is not a valid operator for '{pq.field}'")
        return False
    
    # validate value at some point; including multiple, OR, AND
    return SearchCommand(valid_field, op, pq.values)
        
          
# def create_command(command: SearchCommand) -> SearchCommand:
#     # if level, match the operator to the NumOperator operation
#     # if others, match the operator to the TxtOperator operation
#     return command

# def search_indices():
#     # for command in parsed_ui:
#     #     for k, v in indices[command[0]].items():
#     #         calculation = apply_command(operator=command[1], value_user=command[2])
#     #         if calculation(k):
#     #             rich.print(f"with query {command}, the result is:\n{v}")

#     pass
