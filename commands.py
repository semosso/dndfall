
import re
from enum import StrEnum
from dataclasses import dataclass

## initialization for easier testing
import json
from normalization import normalizing_spells
from indexing import create_indices


# gets JSON data, will evolve to API calls to 5e SRD database
with open(file="data/spells.json", mode="r") as raw_source:
    raw_spells: list[dict] = json.load(raw_source)

# calls "normalization" to normalizes JSON data into dataclass objects
SPELLS: dict[str, dict] = normalizing_spells(database=raw_spells)
INDICES: dict = create_indices(spells=SPELLS)

## operator classes
# with logic delegated to commands and strategies, operators are only validators
class NumericOp(StrEnum):
    EQ = ":"  # replicating scryfall's syntax
    N_EQ = "!="  # not replicating their syntax (-<field>)
    GT_E = ">="
    GT = ">"
    LT_E = "<="
    LT = "<"

class TextOp(StrEnum):
    IS = ":"
    N_IS = "!="

class BoolOp(StrEnum):
    IS = "=="
    I_N = "!="
    pass

## strategy classes
class SearchStrategy():
    # # should operator be here?
    # def __init__(self, field: str, value: list[str], indices: dict[str, defaultdict]):
    #     self.field = field
    @classmethod
    # will be overriden by specific strategies
    def execute(self, field, value):
        pass

class DirectLookupStrategy(SearchStrategy):
    # consolidate init in super class later on
    # def __init__(self):
    #     pass

    @classmethod
    def execute(cls, field, value):
        # empty set or list, TBD
        return [[f"{field} {v}:", INDICES[field].get(v, set())] for v in value]


class ExclusionStrategy(SearchStrategy):

    @classmethod
    def execute(cls, field, value):
        # put this inside LEVEL, or adapt it here (e.g., if level)
        return [[f"{field} {nv}:", INDICES[field].get(nv, set())] for nv in range(0,10) if nv not in value]


## command classes
class SearchCommand():

    # # creating a list of commands
    # # I DONT NEED THIS IF I'M USING SUPPORTED_COMMANDS IN EACH SUBCLASS
    # COMMANDS: list = ([c for c in NormalizedSpell.__dataclass_fields__] + 
    # [tc.name for tc in TAG_CATEGORIES])

    # for instantiating the right subclass
    SEARCH_COMMANDS: list = []

    @classmethod
    def validation_lookup(cls) -> dict:
        return {command: [sub, [op for op in sub.SUPPORTED_OPERATORS]]
                for sub in cls.SEARCH_COMMANDS
                for command in sub.SUPPORTED_COMMANDS
                }
    

    @classmethod
    def initial_validation(cls, pq: ParsedQuery) -> bool | type[SearchCommand]:
        """Validates field and operator from ParsedQuery.
        Input: a ParsedQuery object
        Return: False if validation fails, else a <field> SearchCommand object"""

        validation_dict = cls.validation_lookup()
        if pq.field not in validation_dict:
            print(f"'{pq.field}' is not a valid field")
            return False
        elif pq.operator not in validation_dict[pq.field][1]:
            print(f"'{pq.operator}' is not a valid operator for field '{pq.field}'")
            return False
        else:
            return validation_dict[pq.field][0](pq.operator, pq.values)


    def __init__(self, op: StrEnum, values: list):
        self.operator: StrEnum = op
        self.values: list = values

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        SearchCommand.SEARCH_COMMANDS.append(cls)


class Level(SearchCommand):

    SUPPORTED_COMMANDS: list = ["level", "l"]
    SUPPORTED_OPERATORS: list = [op for op in NumericOp]
    # add strategies
    OP_TO_STRATEGY: dict[str, type[SearchStrategy]] = {
        NumericOp.EQ: DirectLookupStrategy,
        NumericOp.N_EQ: ExclusionStrategy,
    }
    
    def __init__(self, op: StrEnum, values: list, strat = None):
        super().__init__(op, values)
        # can I tie "field" to NormalizedSpell object (for fields), or TAG_CATEGORIES
        # (for tag information)? avoids typos, single source of truth etc.
        self.field: str = "level"
        self.strategy: SearchStrategy = self.OP_TO_STRATEGY[op]

    # this must be repeated for every command (ie, could be at class level)
    # but I need to account for int() in level and there might be other cases
    # maybe "if level, int, else just pass the levels?" TBD
    def value_extraction(self):
        try:
            return [int(v) for v in self.values]
        except ValueError:
            print("all values for field 'level' must be numeric (e.g., 3, not three)")

    def apply_command(self):
        return self.strategy.execute(field=self.field, value=self.value_extraction())
    
        

class DamageType(SearchCommand):

    SUPPORTED_COMMANDS: list = ["damage_type", "dt"]
    SUPPORTED_OPERATORS: list = [op for op in TextOp]
    
    # is value str or list?
    def __init__(self, op: StrEnum, values: list, strat = None):
        super().__init__(op, values)


print(NumericOp.EQ)
# print([c for c in NormalizedSpell.__dataclass_fields__])
# print(SearchCommand.SEARCH_COMMANDS)
print(SearchCommand.validation_lookup())



## search engine
@dataclass
class ParsedQuery:
    field: str
    operator: str
    values: list[str]


class SearchEngine():
    
    def query_parser(user_input: str) -> ParsedQuery:
        """Parses user input into field, operator and value. Static syntax check.
        Input: user query
        Return: a ParsedQuery object, ready for context validation"""

        # think of separators, error messages (pure static syntax for now)
        # "value" can have multiple values, keep in mind when composing command
        parts: list = re.split(pattern=r"\s*(<=|>=|!=|<|>|:)\s*", string=user_input)
        f, o, *vs = parts # MOBRAL * 
        values_list: list[str] = [v.strip().lower() for v in "".join(vs).split(",")]
        return ParsedQuery(field=f.strip().lower(), operator=o, values=values_list)
    

# testing
u_i = "level!=3,4"
qp = SearchEngine.query_parser(u_i)
print(qp)
print(type(SearchCommand.initial_validation(qp)))
vqp = SearchCommand.initial_validation(qp)
print(type(vqp))
print(vqp.value_extraction())
print(vqp.apply_command())
