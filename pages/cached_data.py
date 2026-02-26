import streamlit as st
from collections import defaultdict
import json

from src.dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS
from src.normalization import normalizing_spells, create_indices


@st.cache_data
def load_spells():
    with open(file="src/data/srd_spells.json", mode="r") as srd_source:
        srd_raw: list[dict] = json.load(srd_source)
    with open(file="src/data/non_srd_spells.json", mode="r") as non_srd_source:
        non_srd_raw: list[dict] = json.load(non_srd_source)

    spells: dict[str, NormalizedSpell] = normalizing_spells(srd_raw + non_srd_raw)
    indices: dict[str, defaultdict] = create_indices(
        spells=spells, scalar_f=SCALAR_FIELDS, derived_f=DERIVED_FIELDS
    )

    return spells, indices


SPELLS, INDICES = load_spells()
