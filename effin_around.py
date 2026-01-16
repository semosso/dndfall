# setting up
import re
import rich
import json
from enum import StrEnum # sugestão Takai

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
    EQ = "==" # = would be more natural for users
    N_EQ = "!="
    HT_o_E = ">="
    HT = ">"
    LT_o_E = "<="
    LT = "<"

    # SearchCommand gets the string operator from QueryParser
    # SearchCommand calls get_operator with the string operator, gets the applicable operation
    # maybe SearchCommand also has to pass the first and second param
    def get_operator(self, str_operator):
        pass

class TextOperators(StrEnum):
    IS = "=="
    I_N = "!="


class BooleanOperators(StrEnum):
    IS = "=="
    I_N = "!="

# categorizing the operations from the operators

# 

def compare(x, y):
    return x >= y  # IF THIS CHANGES


# user input, following hard formal syntax
user_input = "level:>=8"  # IF THIS CHANGES

# MVP of parser: takes user input, breaks it into category, operator, query
parsing_collon: list = re.split(pattern=r"(:)", string=user_input)
rich.print("first break is: ", parsing_collon)  # 0 before, 1 :, 2 command and query
parsing_operator: list = [
    s for s in re.split(pattern=r"(>=)", string=parsing_collon[2]) if s
]  # IF THIS CHANGES
rich.print("second break is: ", parsing_operator)

# MVP of SearchCommand: takes pieces from parser, composes command
full_command: list = [parsing_collon[0], parsing_operator[0], parsing_operator[1]]

# MVP of SearchEngine: takes command, applies to indices
for k, v in indices[full_command[0]].items():  # k=3, v=spells
    if compare(k, int(full_command[2])):
        rich.print(k, v)
