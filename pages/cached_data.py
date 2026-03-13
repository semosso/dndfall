import streamlit as st
import json

from src.orchestration import spell_objects_from_JSON, create_indices


@st.cache_data
def initialize_spells_and_indices():
    with open(file="src/data/TAGGED_spells.json", mode="r") as spell_JSON:
        spell_source = json.load(spell_JSON)
    spells: dict = spell_objects_from_JSON(spell_source)
    indices: dict = create_indices(spells)
    return spells, indices


SPELLS, INDICES = initialize_spells_and_indices()
