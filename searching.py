# just thinking some things up
from dataclasses import dataclass


@dataclass
class Commands:
    
    pass


class QueryParser:
    """Receives user input, returns query objects"""

    # WHAT DATA REPRESENTS THESE OBJECTS?
    # A:
    # WHAT PROCEDURES APPLY TO THAT DATA?
    # A:
    def __init__(self, query):
        self.query: str = query


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
