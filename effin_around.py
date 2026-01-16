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


## MVP of searching routines; "level" only at first


# categorizing the operators
class NumericOperators(StrEnum):
    EQ = "=="  # = would be more natural for users
    N_EQ = "!="
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    # SearchCommand gets the string operator from QueryParser, and the type (numeric, text etc.)
    # SearchCommand calls get_operator, gets the applicable operation
    # SearchCommand has to pass the str operator, and maybe the arguments as well?
    def get_operator(self, str_op):
        pass


class TextOperators(StrEnum):
    IS = "=="
    I_N = "!="


class BooleanOperators(StrEnum):
    IS = "=="
    I_N = "!="


# where should this live? inside each Operator class? Operator class, with specific subclasses?
def compare(x, y):
    return x >= y  # IF THIS CHANGES


# user input, following hard formal syntax
user_input = "level:>=8"  # IF THIS CHANGES

# MVP of parser: takes user input, breaks it into category, operator, query
gets_command: list = re.split(pattern=r"(:)", string=user_input)
rich.print("first break is: ", gets_command)  # 0 before, 1 :, 2 command and query
command = gets_command[0]

gets_operator: list = [
    s for s in re.split(pattern=r"(>=)", string=gets_command[2]) if s
]  # IF THIS CHANGES
rich.print("second break is: ", gets_operator)
operator = gets_operator[0]
content = gets_operator[1]


# MVP of SearchCommand: takes pieces from parser, composes command
full_command: list = [command, operator, content]

# MVP of SearchEngine: takes command, applies to indices
for k, v in indices[full_command[0]].items():  # k=3, v=spells
    if compare(k, int(full_command[2])):
        rich.print(k, v)
