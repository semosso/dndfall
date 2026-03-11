import json
from collections import defaultdict

# initializes spell objects and indices
from src.specs.schema import NormalizedSpell
from src.search import SEARCH_FIELDS

from src.search.query_handler import ParsedQuery, QueryParsing
from src.search.command_handler import CommandValidation, SearchCommand
from src.search.search_handler import SearchExecution


with open(file="src/data/TAGGED_spells.json", mode="r") as spell_JSON:
    spell_source = json.load(spell_JSON)


def spell_objects_from_JSON(database: list = spell_source):
    spells: dict[str, NormalizedSpell] = {}
    for sp in database:
        spell: NormalizedSpell = NormalizedSpell(
            name=sp["name"],
            level=sp["level"],
            concentration=sp["concentration"],
            ritual=sp["ritual"],
            school=sp["school"],
            range=sp["range"],
            components=sp["components"],
            duration=sp["duration"],
            casting_time=sp["casting_time"],
            classes=sp["classes"],
            higher_level=sp["higher_level"],
            higher_description=sp["higher_description"],
            description=sp["description"],
            url=sp["url"],
            srd_flag=sp["srd_flag"],
            tags=sp["tags"],
        )
        spells[spell.name] = spell
    return spells


def create_indices(spells: dict):
    indices: dict = {
        field.name: defaultdict(set)
        for field in SEARCH_FIELDS
        if field.name != "spell_name"
    } | {"spell_name": set()}
    for spell_name, spell_obj in spells.items():
        indices["spell_name"].add(spell_name)
        info = spell_obj.extract_index_info()
        for k, v in info.items():
            for value in v:
                indices[k][value].add(spell_name)
    return indices


# search engine
def orchestrate_search(query: str, spells: dict, indices: dict):
    parsed_queries: list[ParsedQuery] = QueryParsing(query).parse_query()
    if not parsed_queries:
        raise ValueError(
            f"Could not parse query: '{query}'. Please review our syntax guide!"
        )
    results: list = []
    for p_q in parsed_queries:
        command: SearchCommand = CommandValidation(parsed_query=p_q).compose_command()
        execution_process: SearchExecution = SearchExecution(command, spells, indices)
        pre_result: set = execution_process.execute()
        results.append(execution_process.applying_NOT_ANY_modifier(pre_result))
    return set.intersection(*results)
