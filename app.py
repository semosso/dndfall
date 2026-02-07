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

st.title("dndfall", text_alignment="center")
st.subheader("an advanced D&D search tool", text_alignment="center", anchor=False)


# help, autocomplete, on_change, args, kwargs, icon, width
query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
)

# examples = [
#     ("Fire damage 3rd level", ":violet-badge[level:3] :orange-badge[dmg_type:fire]"),
#     ("Bonus action spells", "cast:bonus action"),
#     ("Concentration 1+ hour", "conc:true cd>=3600"),
#     ("AOE no concentration", "targets:aoe conc:false"),

col_text, col_link = st.columns([4, 1])
with col_text:
    st.text(
        "Check the syntax guide for an overview of the keywords and operators that will\
 supercharge your D&D searches."
    )
with col_link:
    st.page_link("pages/syntax_guide.py", label="syntax guide", icon="📖")


st.subheader("Examples")
st.markdown(
    "Fire damage, 3rd level: :violet-badge[level:3] :orange-badge[dmg_type:fire]"
)

if query:
    st.session_state.query = query
    st.switch_page("pages/search_results.py")
    # try:
    #     results: set = orchestrate_search(query)
    # except ValueError as e:
    #     st.error(str(e))
    # else:
    #     st.success(f"Found {len(results)} matches!")
    #     if not results:
    #         st.warning(f"no matches for '{query}'")
    #     else:
    #         for name in sorted(results):
    #             spell = SPELLS[name]
    #             with st.expander(
    #                 f"**{spell.name}** _(Level {spell.level} {spell.school})_"
    #             ):
    #                 st.write(f"""**Casting Time:** {spell.casting_time}
    #                          **Range:** {spell.range_}
    #                          **Components:** {spell.components}
    #                          **Duration:** {spell.duration}
    #                          **Classes:** {spell.classes}""")
    #                 st.write(spell.description)
    #                 st.write("**View it in SRD:**", spell.url)
