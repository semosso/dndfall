import json  # for data intake from SRD
import rich  # better visualization of data structures

# my modules
from normalization import normalizing_spells
from tagging import extract_tags
from indexing import create_indices


# initializes the basic structures: normalized and curated spells
def main():
    # gets JSON data, will evolve tio API calls to 5e SRD database
    with open(file="data/spells.json", mode="r") as raw_source:
        raw_spells: list[dict] = json.load(raw_source)

    # normalizes JSON data into scheme I defined
    normalized_spells: dict[str, dict] = normalizing_spells(raw_spells)

    # # REPLACE TypedDict WITH dataclass, it's my canonical form
    # class CuratedSpell(TypedDict):
    #     # spell_id: int
    #     name: str
    #     level: int
    #     description: str
    #     tags: NotRequired[dict[str, list[str]]]

    # from normalized, add tags; normalized is "static", this changes with tags
    spells: dict[str, dict] = {}
    for (
        norm_spell,
        spell_dict,
    ) in normalized_spells.items():
        # for key in dict, "Fireball"
        # print(norm_spell) # testing
        spells[norm_spell] = {
            # "spell_id": spell["index"],
            "name": spell_dict["name"],  # "name": "Fireball"
            "level": spell_dict["level"],
            "school": spell_dict["school"],
            "description": spell_dict["description"],
            "tags": extract_tags(spell_description=spell_dict["description"].lower()),
        }

    # testing
    indices: dict = create_indices(spells)
    print("Fireball" in indices["no_damage"])
    print("Suggestion" in indices["no_damage"])
    for spell in set(indices["damage_type"]["fire"]) & set(
        (indices["saving_throw"]["dexterity"])
    ):
        print(spell)
    rich.print(spells["Web"])


if __name__ == "__main__":
    main()


# PART 5, test suite, see notes on Obsidian
# e.g., expand spells and try language not captured by regex
# e.g., "heals" vs. "regains" HP, "{dmg}" vs. "of {dmg}", "takes damage"

# PART 6, user interface, still a long way away from having to think about this
# TBD what information will be shown; e.g., list of spells that meet the criteria? links to SRD?
