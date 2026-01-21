
import json  # for data intake from SRD
import rich  # better visualization of data structures

# my modules
from normalization import normalizing_spells
from indexing import create_indices
import searching


# initializes the dict of curated spells
def main():
    # gets JSON data, will evolve to API calls to 5e SRD database
    with open(file="data/spells.json", mode="r") as raw_source:
        raw_spells: list[dict] = json.load(raw_source)

    # calls "normalization" to normalizes JSON data into dataclass objects
    spells: dict[str, dict] = normalizing_spells(raw_spells)
    indices: dict = create_indices(spells)

    user_input: list = [
        "level>=8", # how to print per level?
        "level:3",
        "school!=evocation", # how to print per school?
        # "class:bard", # flatten later; index later
        # "damage_type!=fire, acid", # not ready for multiples yet
        "sainvg_throw:dexterity",  # checking typo in field
        "st:dexterity",
        "damage_type>cold",  # checking wrong operator
    ]

    for u_i in user_input:
        pq: searching.ParsedQuery = searching.query_parser(u_i)
        vq: bool | searching.SearchCommand = searching.query_validator(pq)
        if isinstance(vq, searching.SearchCommand):
            for k, v in indices[vq.field].items():
                # flatten later
                if vq.operator.operation(vq.values[0])(k):
                    rich.print(f"for query {u_i}, the result is:\n{v}")

if __name__ == "__main__":
    main()

# PART 5, test suite, see notes on Obsidian
# e.g., expand spells and try language not captured by regex
# e.g., "heals" vs. "regains" HP, "{dmg}" vs. "of {dmg}", "takes damage"

# PART 6, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
