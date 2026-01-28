from dndspecs import NormalizedSpell
import json  # for data intake from SRD
import rich  # better visualization of data structures

# my modules
from normalization import normalizing_spells
# from indexing import create_indices


# initializes the dict of curated spells
def main():
    # gets JSON data, will evolve to API calls to 5e SRD database
    with open(file="data/spells.json", mode="r") as raw_source:
        raw_spells: list[dict] = json.load(raw_source)

    # calls "normalization" to normalizes JSON data into dataclass objects
    spells: dict[str, NormalizedSpell] = normalizing_spells(raw_spells)
    # indices: dict = create_indices(spells)

    rich.print(spells["Prismatic Spray"])
    rich.print(spells["Fireball"])


if __name__ == "__main__":
    main()

# PART 5, test suite, see notes on Obsidian
# e.g., expand spells and try language not captured by regex
# e.g., "heals" vs. "regains" HP, "{dmg}" vs. "of {dmg}", "takes damage"

# PART 6, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
