import json
import rich

# both because of type hints only
from collections import defaultdict
from dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS

# my modules
from normalization import normalizing_spells, create_indices
from searching import orchestrate_search


# initializes the dict of curated spells
def main():
    with open(file="data/spells.json", mode="r") as raw_source:
        raw_spells: list[dict] = json.load(raw_source)

    spells: dict[str, NormalizedSpell] = normalizing_spells(raw_spells)
    indices: dict[str, defaultdict] = create_indices(
        spells=spells, scalar_f=SCALAR_FIELDS, derived_f=DERIVED_FIELDS
    )

    return spells, indices


SPELLS, INDICES = main()
user_input = "l:7"
rich.print(orchestrate_search(user_input))
rich.print(SPELLS["Raise Dead"])
rich.print(SPELLS["Prismatic Spray"])
rich.print(INDICES["damage_amount"])


if __name__ == "__main__":
    main()

# PART 5, test suite, see notes on Obsidian
# e.g., expand spells and try language not captured by regex
# e.g., "heals" vs. "regains" HP, "{dmg}" vs. "of {dmg}", "takes damage"

# PART 6, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
