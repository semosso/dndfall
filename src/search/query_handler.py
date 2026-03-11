import re
from dataclasses import dataclass

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


class QueryParsing:
    def __init__(self, query: str):
        self.raw_query = query

    def parse_query(self):
        parsed_inputs: list = []
        pattern: str = PARSING_PATTERN
        for match in re.finditer(pattern, string=self.raw_query):
            if match.group(2):
                m_: str = "NOT" if match.group(1) == "-" else ""
                f_: str = match.group(2)
                o_: str = match.group(3)
                v_: list = match.group(4).split()
                parsed_inputs.append(
                    ParsedQuery(field=f_.lower(), operator=o_, values=v_, modifier=m_)
                )
            elif match.group(6):
                m_: str = "NOT" if match.group(5) == "-" else ""
                f_: str = match.group(6)
                o_: str = match.group(7)
                v_: list = match.group(8).split()
                parsed_inputs.append(
                    ParsedQuery(field=f_.lower(), operator=o_, values=v_, modifier=m_)
                )
            elif match.group(10):
                m_ = "ANY" if match.group(9) == "*" else "NOT"
                f_ = match.group(10)
                o_: str = ":"
                v_: None = None
                parsed_inputs.append(
                    ParsedQuery(field=f_, operator=o_, values=None, modifier=m_)
                )
            else:
                m_ = "NOT" if match.group(11) == "-" else ""
                f_ = "spell_name"
                o_ = ":"
                v_ = [match.group(12)]
                parsed_inputs.append(
                    ParsedQuery(field=f_, operator=o_, values=v_, modifier=m_)
                )
        return parsed_inputs
