import re
from enum import StrEnum
from dataclasses import dataclass

import dndspecs

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
INDICES: dict = create_indices(
    spells=SPELLS, scalar_f=dndspecs.SCALAR_FIELDS, derived_f=dndspecs.DERIVED_FIELDS
)


## strategy classes
class SearchStrategy:
    VALID_STRATEGIES: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        SearchStrategy.VALID_STRATEGIES.append(cls)

    # @classmethod
    # def build_strategy_by_operator():
    #     """Generates lookup dict matching operator and strategies."""
    #     return {
    #         alias: value
    #         for field in DERIVED_FIELDS
    #         for value in field.values
    #         for alias in value.aliases
    #     } | {alias: field for field in SCALAR_FIELDS for alias in field.aliases}
    #     pass

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
        return [
            (
                f"QUERY= field: '{field}', operator: '{op}', value: '{v}'",
                INDICES[field].get(v, set()),
            )
            for v in value
        ]


class ExclusionStrategy(SearchStrategy):
    @classmethod
    def execute(cls, field, op, value):
        # put this inside LEVEL, or adapt it here (e.g., if level)
        if field == "level":
            # try:
            return [
                [
                    f"QUERY= field: '{field}', operator: '{op}', value: '{value}'",
                    INDICES[field].get(not_v, set()),
                ]
                for not_v in range(0, 10)
                if not_v not in value
            ]
        else:
            # tyr to make this into a list comprehension
            not_v_list: list = [
                f"QUERY= field: '{field}', operator: '{op}', value: '{value}'",
            ]
            for not_v in INDICES[field]:
                # this if works, but might be doing more work than needed
                if not_v not in value and not_v not in not_v_list:
                    not_v_list.append((not_v, INDICES[field][not_v]))
            return not_v_list


## search engine
@dataclass
class ParsedQuery:
    field: str
    operator: str
    values: list[str]


class SearchCommand:
    def __init__(self, parsed_q: ParsedQuery):
        self.field: str = parsed_q.field
        self.operator: StrEnum = parsed_q.operator
        self.values: list = parsed_q.values

    def value_extraction(self):
        return self.values

    def validate_values(self, values):
        pass


class ScalarFieldCommand(SearchCommand):
    # TBD the best home for this
    # SUPPORTED_STRATEGIES: dict[str, type[SearchStrategy]] = {
    #     NumericOp.EQ: DirectLookupStrategy,
    #     NumericOp.N_EQ: ExclusionStrategy,
    # }

    def __init__(self, parsed_q: ParsedQuery, strat=None):
        super().__init__(parsed_q)
        # self.strategy: SearchStrategy = self.SUPPORTED_STRATEGIES[op]

    def value_extraction(self):
        try:
            return [int(v) for v in self.values]
        except ValueError:
            raise ValueError(
                f"All values for field '{self.field}' must {NumericOp.value_error_msg}"
            )

    def apply_command(self):
        values = self.value_extraction()
        self.validate_values(values)
        # if False, don't even call strategy, so no error handling there
        if values:
            return self.strategy.execute(
                field=self.field, op=self.operator, value=values
            )


class DerivedFieldCommand(SearchCommand):
    # TBD the best home for this
    # SUPPORTED_STRATEGIES: dict[str, type[SearchStrategy]] = {
    #     TextOp.IS: DirectLookupStrategy,
    #     TextOp.N_IS: ExclusionStrategy,
    # }

    def __init__(self, parsed_q: ParsedQuery, strat=None):
        super().__init__(parsed_q)
        self.strategy: SearchStrategy = self.SUPPORTED_STRATEGIES[op]

    def validate_values(self, values):
        invalid_v = [v for v in values if v not in INDICES[self.field]]
        if invalid_v:
            raise ValueError(
                f"Invalid values: {invalid_v}.\
                    Values for field '{self.field}' must {TextOp.value_error_msg}"
            )

    def apply_command(self):
        values = self.value_extraction()
        self.validate_values(values)
        # if False, don't even call strategy, so no error handling there
        if values:
            return self.strategy.execute(
                field=self.field, op=self.operator, value=values
            )


class SearchEngine:
    def __init__(self, user_input):
        self.user_input: str = user_input

    # think of separators, error messages (pure static syntax for now)
    # "value" can have multiple values, keep in mind when composing command
    # only works for a single field search for now

    def parse_query(self) -> ParsedQuery:
        """Parses user input into field, operator and value parts.
        Input: user query
        Return: a ParsedQuery object"""

        parts: list[str] = re.split(pattern=r"(<=|>=|!=|<|>|:)", string=self.user_input)
        if len(parts) < 3:
            raise ValueError("no valid operator in query")
        else:
            f_, o_, *v_ = parts
            values_list: list[str] = [v.strip().lower() for v in "".join(v_).split(",")]
            return ParsedQuery(
                field=f_.strip().lower(), operator=o_.strip(), values=values_list
            )

    def validate_field(self, parsed_q):
        """Validates a query's field, operator and value.
        Input: a ParsedQuery object
        Return: raise error if validation fails, else returns a SearchCommand object"""

        field_: str = dndspecs.FIELD_BY_ALIAS.get(parsed_q.field)

        match field_:
            case dndspecs.ScalarField():
                return ScalarFieldCommand(parsed_q)
            case dndspecs.DerivedField():
                return DerivedFieldCommand(parsed_q)
            case _:
                raise ValueError(f"no valid field in query ('{parsed_q.field}')")


# testing
# print(NumericOp.EQ)
# print([c for c in NormalizedSpell.__dataclass_fields__])
# print(SearchCommand.SEARCH_COMMANDS)
# print(SearchCommand.validation_lookup())
u_i = SearchEngine(user_input="school>fire")
pq = u_i.parse_query()
u_i.validate_field(pq)
