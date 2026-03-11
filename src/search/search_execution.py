class SearchExecution:
    OP_BY_STRAT: dict = {
        "direct_lookup": {
            dndspecs.NumericOp.EQ,
            dndspecs.TextOp.EQ,
            dndspecs.BooleanOp.IS,
        },
        "range_lookup": {
            dndspecs.NumericOp.GT_E,
            dndspecs.NumericOp.GT,
            dndspecs.NumericOp.LT_E,
            dndspecs.NumericOp.LT,
        },
    }

    STRATEGY_MAPPINGS: dict = {
        op: strategy for strategy, ops in OP_BY_STRAT.items() for op in ops
    }

    def __init__(self, field, operator, values, rules, modifier=None):
        self.c_field: str = field
        self.c_operator: str = operator
        self.c_values: set = values
        self.c_rules = rules
        self.modifier: str | None = modifier

    def execute(self):
        strat_name = self.STRATEGY_MAPPINGS.get(self.c_operator, "")
        strategy = getattr(self, strat_name)
        return strategy()

    # create different strategies for num vs text, too many convert to int things
    # or adapt like in final section of search creation
    def direct_lookup(self):
        if self.c_field == "spell_name":
            return {
                spell
                for spell in INDICES["spell_name"]
                if any(v in spell.lower() for v in self.c_values)
            }
        if self.c_field in ["description", "desc"]:
            return {
                spell
                for spell in SPELLS.keys()
                if any(
                    v in " ".join(" ".join(SPELLS[spell].description).split()).lower()
                    for v in self.c_values
                )
            }
        matches = {
            self._extract_ratio(v) if isinstance(v, str) else v for v in self.c_values
        }
        return set().union(
            *(INDICES[self.c_field][v] for v in matches),
        )

    def range_lookup(self):
        # adapt for text comparison; e.g., if isinstance str normalize
        target = next(iter(self.c_values))

        if isinstance(target, str):
            target = self._extract_ratio(target)

        op: dict = {
            dndspecs.NumericOp.GT_E: lambda x: x >= target,
            dndspecs.NumericOp.GT: lambda x: x > target,
            dndspecs.NumericOp.LT_E: lambda x: x <= target,
            dndspecs.NumericOp.LT: lambda x: x < target,
        }
        match_keys: list = []

        for k in INDICES[self.c_field].keys():
            try:
                numeric_k = float(k)
                if op[self.c_operator](numeric_k):
                    match_keys.append(k)
            except (ValueError, TypeError):
                pass

        return set().union(*(INDICES[self.c_field][k] for k in match_keys))

    def _extract_ratio(self, value):
        value_lower = value.lower()

        for category in ["self", "touch", "foot", "mile"]:
            if value_lower in dndspecs.LENGTH_UNIT[category]["aliases"]:
                return dndspecs.LENGTH_UNIT[category]["ratio"]

        for category in [
            "instantaneous",
            "second",
            "minute",
            "hour",
            "day",
            "year",
            "dnd_economy",
        ]:
            if value_lower in dndspecs.TIME_UNIT[category]["aliases"]:
                return dndspecs.TIME_UNIT[category]["ratio"]

        return value

    def applying_modifier(self, pre_result):
        if self.modifier == "NOT":
            if len(self.c_values) == 0:
                all_field_values = set().union(*(INDICES[self.c_field].values()))
                return set(SPELLS.keys()) - all_field_values
            return set(SPELLS.keys()) - pre_result
        if self.modifier == "ANY":
            if self.c_field in ["condition", "saving_throw", "damage_type"]:
                return set().union(*(INDICES[self.c_field].values()))
            else:
                raise ValueError(
                    f"'*' modifier incompatible with '{self.c_field}' searches"
                )
        return pre_result
