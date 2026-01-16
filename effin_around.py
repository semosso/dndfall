# setting up
import re
import rich
import json
from enum import Enum

from normalization import normalizing_spells
from indexing import create_indices


def compare(x, y):
    return x == y  # IF THIS CHANGES


with open(file="data/spells.json", mode="r") as raw_source:
    raw_spells: list[dict] = json.load(raw_source)

spells: dict[str, dict] = normalizing_spells(raw_spells)

indices: dict = create_indices(spells)
# for k in sorted_indices:
#     sorted_indices[k]: dict = dict(sorted(sorted_indices[k].items()))
# rich.print(sorted_indices)

# testing searching functions
user_query = "level:==3"  # IF THIS CHANGES

proc_query: list = re.split(pattern=r"(:)", string=user_query)
rich.print("first break is: ", proc_query)  # 0 before, 1 :, 2 command and query
breaking_query: list = [
    s for s in re.split(pattern=r"(==)", string=proc_query[2]) if s
]  # IF THIS CHANGES
rich.print("second break is: ", breaking_query)

full_command: list = [proc_query[0], breaking_query[0], breaking_query[1]]

for k, v in indices[full_command[0]].items():  # k=3, v=spells
    if compare(k, int(full_command[2])):
        rich.print(k, v)


# user_query2 = "st:==dexterity, l:==2"
# what happens then?
# QueryParser(user_query2)
