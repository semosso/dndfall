import streamlit as st
from collections import defaultdict
import json

from src.dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS
from src.normalization import spell_objects_from_JSON, create_indices


@st.cache_data
def load_spells():
    with open(file="src/data/TAGGED_spells.json", mode="r") as spell_JSON:
        spell_source = json.load(spell_JSON)

    spells: dict[str, NormalizedSpell] = spell_objects_from_JSON(spell_source)
    indices: dict[str, defaultdict] = create_indices(
        spells=spells, scalar_f=SCALAR_FIELDS, derived_f=DERIVED_FIELDS
    )

    return spells, indices


SPELLS, INDICES = load_spells()
