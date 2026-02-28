import src.specs.units as units

# common aliases used throughout patterns
foot_aliases = "|".join(units.LENGTH_UNIT["foot"]["aliases"])
mile_aliases = "|".join(units.LENGTH_UNIT["mile"]["aliases"])
rad_aliases = "|".join(units.LENGTH_UNIT["rad"]["aliases"])
diam_aliases = "|".join(units.LENGTH_UNIT["diam"]["aliases"])
text_length_aliases = "|".join(
    units.LENGTH_UNIT["self"]["aliases"] + units.LENGTH_UNIT["touch"]["aliases"]
)
shapes = "|".join(units.SHAPE_UNIT["aliases"])

time_aliases = "|".join(
    sorted(
        units.TIME_UNIT["second"]["aliases"]
        + units.TIME_UNIT["minute"]["aliases"]
        + units.TIME_UNIT["hour"]["aliases"]
        + units.TIME_UNIT["day"]["aliases"]
        + units.TIME_UNIT["year"]["aliases"]
        + units.TIME_UNIT["dnd_economy"]["aliases"],
        key=len,
        reverse=True,
    )
)
text_time_aliases = "|".join(units.TIME_UNIT["instantaneous"]["aliases"])
currency_aliases = "|".join(
    sorted(
        units.CURRENCY_UNIT["gold"]["aliases"]
        + units.CURRENCY_UNIT["electrum"]["aliases"]
        + units.CURRENCY_UNIT["silver"]["aliases"]
        + units.CURRENCY_UNIT["copper"]["aliases"]
        + units.CURRENCY_UNIT["platinum"]["aliases"],
        key=len,
        reverse=True,
    )
)

# regex patterns for each field
UPCAST_PATTERNS = patterns = {
    r"\bwhen you reach \w+\s+level(s)?",
    r"\busing a spell slot of \w+ level or higher",
    r"\bat higher levels",
}

DICE_AMOUNT_PATTERNS = r"""(?x)
        \b(?P<number>[0-9]+)
        (?P<die>d[0-9]+).\s*
        (?:\+\s*
        (?P<fixed>[0-9]+).)?\s*\w+\s*damage"""

GP_COST_PATTERNS = rf"""(?x)
    \b(?P<number>[0-9,]+)\s*
    (?P<unit>{currency_aliases})\b"""

RANGE_PATTERNS = {
    rf"""(?x)
    \b(?P<number>[0-9,]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})?\b
    """,
    rf"""(?x)
    \b(?P<text>{text_length_aliases})\b""",
}

DURATION_PATTERNS = {
    rf"""(?x)
    \b(?P<number>[0-9]+)\s*
    (?P<unit>{time_aliases})\b
    """,
    rf"""(?x)
    \b(?P<text>{text_time_aliases})\b""",
}

CASTING_TIME_PATTERNS = rf"""(?x)
    \b([0-9]+)\s*
    ({time_aliases})\b
    """

AOE_PATTERNS = {
    # walls are built in blocks; specifics ahead of generic, learned the hard way
    rf"""(?x)
    \b(?P<number>[0-9]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
    (?:by|x)\s*-?\s*
    (?P<number2>[0-9]+)\s*-?\s*
    (?P<unit2>{foot_aliases}|{mile_aliases})
    """,
    # cone, sphere, cube (most)
    rf"""(?x)
    \b(?P<number>[0-9]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
    (?P<rad_diam>{rad_aliases}|{diam_aliases})?\s*-?\s*
    (?P<shape>{shapes})
    """,
    # cylinder after radius, I won't track height
    # 10-foot-radius, 40-foot-high cylinder
    rf"""(?x)
    \b(?P<number>[0-9]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
    (?P<rad_diam>{rad_aliases}|{diam_aliases})\s*-?\s*.*?
    (?P<shape>cylinder)
    """,
    # cylinder before radius, I won't track height
    rf"""(?x)
    \b(?P<shape>cylinder)\s+.*?
    (?P<number>[0-9]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*.?
    (?P<rad_diam>{rad_aliases}|{diam_aliases})
    """,
    # line after long
    rf"""(?x)
    \b(?P<number>[0-9]+)\s*-?\s*
    (?P<unit>{foot_aliases}|{mile_aliases})\s*-?\s*
    (?:\w+\s+)?
    (?P<shape>line)
    """,
    # line before long
    rf"""(?x)
    \b(?P<shape>line)
    (?:\s+of\s+strong\s+wind)?
    \s+
    (?!\s+of\s+sight)
    (?P<number>[0-9]+)\s+
    (?P<unit>{foot_aliases}|{mile_aliases})
    (?:\s+long)?
    """,
    # walls are also lines
    rf"""(?x)
    \b(?P<shape>wall)\s+.*?
    (?P<number>[0-9]+)\s+
    (?P<unit>{foot_aliases}|{mile_aliases})
    (?:\s+long)?
        """,
}

DAMAGE_TYPE_PATTERNS = {
    r"\b[0-9]+\s?d\s?[0-9]+.\s?(\+\s?[0-9]+.)?\s?{value} damage\b",
    r"\btake(s)? {value} damage\b",
}

SAVING_THROW_PATTERNS = {
    r"\b(make(s)?|succeed(s)? on|fail(s)?)\s+(?!all\s).*?\b{value} saving throw(s)?",
    r"\bsaving throw of {value}\b",
}

CONDITION_PATTERNS = {r"\b{value}\b"}

CLASS_PATTERNS = {r"\b{value}\b"}

SCHOOL_PATTERNS = {r"\b{value}\b"}
