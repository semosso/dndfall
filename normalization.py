from dndspecs import NormalizedSpell
from indexing import extract_tags


def normalizing_spells(database: list):
    """Casts spells from JSON into NormalizedSpell instances.
    Input: list of spells, each a dictionary.
    Return: dicionary of spell names and spells (as NormalizedSpell instances)."""
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
            url=sp["url"],
        )
        spell.tags = extract_tags(spell=spell)
        spells[spell.name] = spell

    return spells
