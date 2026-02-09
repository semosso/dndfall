import streamlit as st
from collections import defaultdict
import json

from dndspecs import NormalizedSpell, DERIVED_FIELDS, SCALAR_FIELDS
from normalization import normalizing_spells, create_indices

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

st.title("dndfall", text_alignment="center")
st.subheader("an advanced D&D search tool", text_alignment="center", anchor=False)


# with st.form("search_form", clear_on_submit=False, border=False):
query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
)
# submitted = st.form_submit_button()

col_guide, col_feedback, col_github = st.columns(
    3, vertical_alignment="center", border=True
)
with col_guide:
    st.page_link("pages/syntax_guide.py", label="syntax guide", icon="📖")
with col_feedback:
    st.page_link(
        "https://forms.gle/hiVD5N5gQ45pAQBV7",
        label="feedback form",
        icon=":material/feedback:",
    )
with col_github:
    st.page_link(
        "https://github.com/semosso/dndfall", label="GitHub", icon=":material/code:"
    )

st.markdown("""
### about dndfall
            
Inspired by the amazing [Scryfall](https://scryfall.com/), **dndfall** is a search tool that understands how D&D is actually played,
allowing players and DMs to mix and match criteria to form powerful commands, cut through the noise, and quickly find what they need.

[SRD source]
            
**v. 0.1:** dndfall is in beta and currently supports all [SRD](https://www.dndbeyond.com/srd) spells, with additional functionality to follow soon (monsters, class abilities, features etc.).""")

if query:
    st.session_state.query = query
    st.switch_page("pages/search_results.py")
