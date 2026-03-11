import re
from enum import StrEnum
from dataclasses import dataclass

from pages.cached_data import SPELLS, INDICES

from src.search.query_parser import ParsedQuery
from src.search.command_composer import CommandValidation
from src.search.search_execution import SearchExecution

user_input = ""


def orchestrate_search(query: str):
    parsed_queries: list[ParsedQuery] = ParsedQuery.parse_query(user_input)
    if not parsed_queries:
        raise ValueError(
            f"Could not parse query: '{query}'. Please review our syntax guide!"
        )
    results: list = []
    for p_q in parsed_queries:
        parsed_query, field_rules = p_q.validate_field(p_q)
        command = CommandValidation(pq=parsed_query, field_rules=field_rules).compose_command()
        pre_result: set = command.execute()
        results.append(command.applying_modifier(pre_result))
    return set.intersection(*results)
