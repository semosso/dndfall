# just thinking some things up
from dataclasses import dataclass
from typing import Literal
import re

operators: dict = {
    "equality": Literal["==", "!="],
    "comparison": Literal["<", "<=", ">=", ">"],
    "boolean": Literal["is", "is not"],  # TBC
}


# @dataclass
# class SearchCommand:
#     # [level, l], [saving_throw, st], [damage_type, dt]; should it be tuple?
#     command: list
#     # what operators apply to it; >, <, ==, !=
#     operators: list


# @dataclass
# class LevelSearch(SearchCommand):
#     command: list = ["l", "level"]
#     operators: list = [operators["equality"], [operators["comparison"]]]
#     level: int

#     def matches(self, spell):  # ?
#         pass


class QueryParser:
    """Receives user input, returns query objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:


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


class SearchEngine:
    """Receives search commands, returns search results over
    indexes or NormalizedSpell objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, logic):
        self.logic = logic
