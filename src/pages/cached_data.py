import streamlit as st
from collections import defaultdict
import json

from dndfall.dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS
from dndfall.normalization import normalizing_spells, create_indices

st.set_page_config(page_title="dndfall")


@st.cache_data
def load_spells():
    with open(file="data/spells.json", mode="r") as raw_source:
        raw: list[dict] = json.load(raw_source)

    spells: dict[str, NormalizedSpell] = normalizing_spells(raw)
    indices: dict[str, defaultdict] = create_indices(
        spells=spells, scalar_f=SCALAR_FIELDS, derived_f=DERIVED_FIELDS
    )

    return spells, indices


SPELLS, INDICES = load_spells()
