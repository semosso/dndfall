import src.specs.units as units
from src.search.command_handler import SearchCommand

OP_BY_STRAT: dict = {
    "direct_lookup": {
        units.NumericOp.EQ,
        units.TextOp.EQ,
        units.BooleanOp.IS,
    },
    "range_lookup": {
        units.NumericOp.GT_E,
        units.NumericOp.GT,
        units.NumericOp.LT_E,
        units.NumericOp.LT,
    },
}

STRATEGY_MAPPINGS: dict = {
    op: strategy for strategy, ops in OP_BY_STRAT.items() for op in ops
}


class SearchExecution:
    def __init__(self, command, spells, indices):
        self.command: SearchCommand = command
        self.spells: dict = spells
        self.indices: dict = indices

    def execute(self):
        strat_name = STRATEGY_MAPPINGS.get(self.command.operator, "")
        strategy = getattr(self, strat_name)
        return strategy()

    def direct_lookup(self):
        if self.command.field == "spell_name":
            return {
                spell
                for spell in self.indices["spell_name"]
                if any(v in spell.lower() for v in self.command.values)
            }
        if self.command.field in ["description", "desc"]:
            return {
                spell
                for spell in self.spells.keys()
                if any(
                    v
                    in " ".join(
                        " ".join(self.spells[spell].description).split()
                    ).lower()
                    for v in self.command.values
                )
            }
        matches = {
            self._extract_ratio(v) if isinstance(v, str) else v
            for v in self.command.values
        }
        return set().union(
            *(
                self.indices[self.command.field][v]
                for v in matches
                if v in self.indices[self.command.field]
            ),
        )

    def range_lookup(self):
        # adapt for text comparison; e.g., if isinstance str normalize
        target = next(iter(self.command.values))

        if isinstance(target, str):
            target = self._extract_ratio(target)

        op: dict = {
            units.NumericOp.GT_E: lambda x: x >= target,
            units.NumericOp.GT: lambda x: x > target,
            units.NumericOp.LT_E: lambda x: x <= target,
            units.NumericOp.LT: lambda x: x < target,
        }
        match_keys: list = []

        for k in self.indices[self.command.field].keys():
            try:
                numeric_k = float(k)
                if op[self.command.operator](numeric_k):
                    match_keys.append(k)
            except (ValueError, TypeError):
                pass

        return set().union(
            *(
                self.indices[self.command.field][k]
                for k in match_keys
                if k in self.indices[self.command.field]
            )
        )

    def _extract_ratio(self, value):
        value_lower = value.lower()

        for category in ["self", "touch", "foot", "mile"]:
            if value_lower in units.LENGTH_UNIT[category]["aliases"]:
                return units.LENGTH_UNIT[category]["ratio"]

        for category in [
            "instantaneous",
            "second",
            "minute",
            "hour",
            "day",
            "year",
            "dnd_economy",
            "until_dispelled",
        ]:
            if value_lower in units.TIME_UNIT[category]["aliases"]:
                return units.TIME_UNIT[category]["ratio"]

        return value

    def applying_NOT_ANY_modifier(self, pre_result):
        if self.command.modifier == "NOT":
            if len(self.command.values) == 0:
                all_field_values = set().union(
                    *(self.indices[self.command.field].values())
                )
                return set(self.spells.keys()) - all_field_values
            return set(self.spells.keys()) - pre_result
        if self.command.modifier == "ANY":
            if self.command.field in ["condition", "saving_throw", "damage_type"]:
                return set().union(*(self.indices[self.command.field].values()))
            else:
                raise ValueError(
                    f"'*' modifier incompatible with '{self.command.field}' searches"
                )
        return pre_result
