import re
from enum import StrEnum
from dataclasses import dataclass

## initialization for easier testing
import json
from normalization import normalizing_spells
from indexing import create_indices
import rich


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
    value_error_msg = "be numeric (e.g., 3, not three)"

class TextOp(StrEnum):
    IS = ":"
    N_IS = "!="
    value_error_msg = "follow formal syntax (e.g., 'fire' for damage_type)"

class BoolOp(StrEnum):
    IS = "=="
    I_N = "!="
    pass

## strategy classes
class SearchStrategy():

    @classmethod
    # will be overriden by specific strategies
    def execute(cls, field, op, value):
        pass

class DirectLookupStrategy(SearchStrategy):

    @classmethod
    def execute(cls, field, op, value):
        # empty set or list, TBD
        # list of tuples?
        # verbose for testing
        return [(f"QUERY= field: '{field}', operator: '{op}', value: '{v}'",
                 INDICES[field].get(v, set())) for v in value]


class ExclusionStrategy(SearchStrategy):

    @classmethod
    def execute(cls, field, op, value):
        # put this inside LEVEL, or adapt it here (e.g., if level)
        if field == "level":
            # try:
            return [[f"QUERY= field: '{field}', operator: '{op}', value: '{value}'",
                     INDICES[field].get(not_v, set())]
                    for not_v in range(0,10) if not_v not in value]
        else:
            # tyr to make this into a list comprehension
            not_v_list: list = [f"QUERY= field: '{field}', operator: '{op}', value: '{value}'",]
            for not_v in INDICES[field]:
                # this if works, but might be doing more work than needed
                if not_v not in value and not_v not in not_v_list:
                    not_v_list.append((not_v, INDICES[field][not_v]))
            return not_v_list
            pass


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
    def initial_validation(cls, pq: ParsedQuery) -> SearchCommand:
        """Validates field and operator from ParsedQuery.
        Input: a ParsedQuery object
        Return: False if validation fails, else a <field> SearchCommand object"""

        validation_dict = cls.validation_lookup()
        if pq.field not in validation_dict:
            raise ValueError(
                f"'{pq.field}' is not a valid field")
        elif pq.operator not in validation_dict[pq.field][1]:
            raise ValueError(
                f"'{pq.operator}' is not a valid operator for field '{pq.field}'")
        else:
            return validation_dict[pq.field][0](pq.field, pq.operator, pq.values)

    def __init__(self, field: str, op: StrEnum, values: list, strat = None):
        self.field: str = field
        self.operator: StrEnum = op
        self.values: list = values

    # is this efficient? does this look at all subs declared or instantiated?
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        SearchCommand.SEARCH_COMMANDS.append(cls)

    # repeated for all commands. should be at class level?
    # need int() in level (and other cases?); "if level, int, else ..."? TBD
    def value_extraction(self):
        return self.values

    def validate_values(self, values):
        pass

    def apply_command(self):
        values = self.value_extraction()
        self.validate_values(values)
    # if False, don't even call strategy, so no error handling there
        if values: 
            return self.strategy.execute(field=self.field, 
                                        op=self.operator,
                                        value=values)
        

class Level(SearchCommand):

    SUPPORTED_COMMANDS: set = {"level", "l"}
    SUPPORTED_OPERATORS: set = {op for op in NumericOp}
    # add strategies
    SUPPORTED_STRATEGIES: dict[str, type[SearchStrategy]] = {
        NumericOp.EQ: DirectLookupStrategy,
        NumericOp.N_EQ: ExclusionStrategy,
    }
    
    def __init__(self, field: str, op: StrEnum, values: list, strat = None):
        super().__init__(field, op, values)
        # can I tie "field" to NormalizedSpell object (for fields), or TAG_CATEGORIES
        # (for tag information)? avoids typos, single source of truth etc.
        self.field: str = "level"
        self.strategy: SearchStrategy = self.SUPPORTED_STRATEGIES[op]

    def value_extraction(self):
        try:
            return [int(v) for v in self.values]
        except ValueError:
            raise ValueError(
                f"All values for field '{self.field}' must {NumericOp.value_error_msg}"
            )
        

class DamageType(SearchCommand):

    SUPPORTED_COMMANDS: set = {"damage_type", "dt"}
    SUPPORTED_OPERATORS: set = {op for op in TextOp}
    # add strategies
    SUPPORTED_STRATEGIES: dict[str, type[SearchStrategy]] = {
        TextOp.IS: DirectLookupStrategy,
        TextOp.N_IS: ExclusionStrategy,
    }

    def __init__(self, field: str, op: StrEnum, values: list, strat = None):
        super().__init__(field, op, values)
        self.field: str = "damage_type"
        self.strategy: SearchStrategy = self.SUPPORTED_STRATEGIES[op]


    def validate_values(self, values):
        invalid_v = [v for v in values if v not in INDICES[self.field]]
        if invalid_v:
            raise ValueError(
                    f"Invalid values: {invalid_v}.\
                    Values for field '{self.field}' must {TextOp.value_error_msg}"
                )

## search engine
@dataclass
class ParsedQuery:
    field: str
    operator: str
    values: list[str]


class SearchEngine():
    
    def query_parser(user_input: str) -> ParsedQuery | None:
        """Parses user input into field, operator and value. Static syntax check.
        Input: user query
        Return: a ParsedQuery object, ready for context validation"""

        # think of separators, error messages (pure static syntax for now)
        # "value" can have multiple values, keep in mind when composing command
        # "\s*(<=|>=|!=|<|>|:)\s*"
        # only works for a single field search for now
        parts: list = re.split(pattern=r"(<=|>=|!=|<|>|:)", string=user_input)
        # this doesn't work 100% like I want it to
        try:
            f, o, *vs = parts
            values_list: list[str] = [v.strip().lower() for v in "".join(vs).split(",")]
            return ParsedQuery(field=f.strip().lower(), operator=o, values=values_list)
        except ValueError:
            raise ValueError(
                "no valid operator in query, must be one of ':', '!=', '<=', '<', '>=', or '>'")

# testing
# print(NumericOp.EQ)
# print([c for c in NormalizedSpell.__dataclass_fields__])
# print(SearchCommand.SEARCH_COMMANDS)
# print(SearchCommand.validation_lookup())
u_i = "dt!=fire, acid, poison, cold"
qp = SearchEngine.query_parser(u_i)
# print(qp)
# print(type(SearchCommand.initial_validation(qp)))
vqp = SearchCommand.initial_validation(qp)
# print(type(vqp))
# print(vqp.value_extraction())
rich.print(vqp.apply_command())
