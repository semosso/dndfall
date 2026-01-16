from dataclasses import dataclass, field

from tagging import extract_tags


@dataclass
class NormalizedSpell:
    name: str
    level: int
    concentration: bool
    ritual: bool
    school: str
    range_: str  # range is a reserved/built-in term
    components: list[str]  # easier to loop through, I think
    material: str | None
    duration: str
    casting_time: str
    classes: list[str]
    higher_level: bool | tuple[bool, str]  # could be just bool | str, TBH
    description: str

    # derived from init attributes
    tags: dict[str, list[str] | bool] = field(init=False, default_factory=dict)


# goes over dict created from JSON, casts spells as NormalizedSpell objects
def normalizing_spells(database: list):
    spells: dict[str, NormalizedSpell] = {}
    # for spell (dict) in list of raw spells
    for sp in database:
        spell: NormalizedSpell = NormalizedSpell(
            name=sp["name"],
            level=sp["level"],
            concentration=sp["concentration"],
            ritual=sp["ritual"],
            school=sp["school"]["name"],
            range_=sp["range"],
            components=sp["components"],
            material=sp.get("material"),  # capture "gp" through tags later
            duration=sp["duration"],
            casting_time=sp["casting_time"],
            classes=[c["name"] for c in sp["classes"]],
            higher_level=False
            if "higher_level" not in sp
            else (True, " ".join(" ".join(sp["higher_level"]).split())),
            description=" ".join(" ".join(sp["desc"]).split()),
        )
        spell.tags: dict[str, list[str] | bool] = extract_tags(spell)
        spells[spell.name] = spell

    return spells
