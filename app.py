import streamlit as st
from collections import defaultdict
import json

from dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS
from normalization import normalizing_spells, create_indices
from searching import orchestrate_search

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

st.title("dndfall\nan advanced D&D search tool")

# help, autocomplete, on_change, args, kwargs, icon, width
query = st.text_input(
    "Search",
    placeholder="level:3 dt:fire",
    label_visibility="hidden",
)
if query:
    try:
        results = orchestrate_search(query)
        for name in sorted(results):
            spell = SPELLS[name]
            with st.expander(f"{spell.name} (Level {spell.level})"):
                st.write(spell.description)
    except ValueError as e:
        st.error(str(e))
