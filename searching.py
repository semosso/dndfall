# just thinking some things up
from dataclasses import dataclass


@dataclass
class Commands:
    pass


class QueryParser:
    """Parses through user input per my syntax rules,
    turning str into query objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, query):
        self.query: str = query


class SearchLogic:
    """Contains all search logic based on my syntax. Based on query objects,
    determines the applicable search operations"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, field, operator, value):
        self.field: str = field
        self.operator: str = operator
        self.value: str | int = value


class SearchEngine:
    """Applies commands from search logic to spell indexes or
    NormalizedSpell objects, as needed"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, logic):
        self.logic = logic
