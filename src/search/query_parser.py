import re
from dataclasses import dataclass

from src.search import FIELD_BY_ALIAS, NAME, DESCRIPTION


PARSING_PATTERN = r"""(?x)
        (-)?(\w+)([<>=:]+)\(([^)]+)\)|# -dt:(fire cold)
        (-)?(\w+)([<>=:]+)([^\s()]+)|# -dt:fire
        ([-*])(\w+)|# NOT and ANY applicable fields
        (-)?(\w+)# name search
        """


@dataclass
class ParsedQuery:
    field: str
    operator: str
    values: list | None
    modifier: str | None = None

    def parse_query(user_input):
        parsed_inputs: list = []
        pattern: str = PARSING_PATTERN
        for match in re.finditer(pattern, user_input):
            if match.group(2):
                mod_: str = "NOT" if match.group(1) == "-" else ""
                f_: str = match.group(2)
                o_: str = match.group(3)
                v_: list = match.group(4).split()
                parsed_inputs.append(
                    ParsedQuery(field=f_.lower(), operator=o_, values=v_, modifier=mod_)
                )
            elif match.group(6):
                mod_: str = "NOT" if match.group(5) == "-" else ""
                f_: str = match.group(6)
                o_: str = match.group(7)
                v_: list = match.group(8).split()
                parsed_inputs.append(
                    ParsedQuery(field=f_.lower(), operator=o_, values=v_, modifier=mod_)
                )
            elif match.group(10):
                mod_ = "ANY" if match.group(9) == "*" else "NOT"
                f_ = match.group(10)
                o_: str = ":"
                v_: None = None
                parsed_inputs.append(
                    ParsedQuery(field=f_, operator=o_, values=None, modifier=mod_)
                )
            else:
                mod_ = "NOT" if match.group(11) == "-" else ""
                f_ = "spell_name"
                o_ = ":"
                v_ = [match.group(12)]
                parsed_inputs.append(
                    ParsedQuery(field=f_, operator=o_, values=v_, modifier=mod_)
                )
        return parsed_inputs

    # still have to figure out a better way to make name/description work
    def validate_field(self):
        if self.field == "spell_name":
            field_rules = NAME
        elif self.field in FIELD_BY_ALIAS:
            field_rules = FIELD_BY_ALIAS[self.field]
        elif self.field in ["description", "desc"]:
            field_rules = DESCRIPTION
        else:
            raise ValueError(f"'{self.field}' is not a valid search field")
        return self, field_rules
