import streamlit as st
import pandas as pd
import uuid

from src.data.JSON_normalizing import non_duplicats_non_SRD
from src.orchestration import orchestrate_search
from pages.cached_data import SPELLS, INDICES
from pages.analytics import (
    track_page_view,
    track_search,
    track_result_click,
    track_feature_usage,
)

# st.set_page_config(layout="wide")

## initialization

if st.session_state.get("current_page") != "search_results":
    track_page_view("search_results", "/search_results")

# for tracking purposes
if "client_id" not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())

if "selected_spell" not in st.session_state:
    st.session_state.selected_spell = None

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "grid"

st.title("search results")

## searching functions

# query sync
nav_query = st.session_state.pop("query", None)

if nav_query is not None:
    st.session_state["search_input_widget"] = nav_query


st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
    key="search_input_widget",
)

query = st.session_state.get("search_input_widget", "")

## search processing
results = set()
df = pd.DataFrame()

if query:
    try:
        results: set = orchestrate_search(query, SPELLS, INDICES)
    except Exception as e:
        st.error(f"An error occurred: {type(e).__name__}: {str(e)}")
    else:
        if results:
            track_search(query, result_count=len(results))
        data: list = [SPELLS[name].__dict__ for name in results]
        df = pd.DataFrame(data=data, columns=["name", "level", "school"])


## display helpers


def display_handler(spell):
    st.subheader(f"**{spell.name}** _(Level {spell.level} {spell.school})_")
    st.write(f"""**Casting Time:** {spell.casting_time}  
    **Range:** {spell.range}  
    **Components:** {spell.components}  
    **Duration:** {spell.duration}  
    **Concentration:** {spell.concentration}  
    **Classes:** {spell.classes}  
    **Url:** {spell.url}""")
    if spell.name.lower() in non_duplicats_non_SRD:
        with st.expander("Description"):
            track_result_click(
                item_type="spell",
                item_name=spell.name,
                search_query=query,
            )
            for string in spell.description:
                st.write(string)
            if spell.higher_level:
                st.markdown(spell.higher_level)
    else:
        st.markdown("""**This spell is not in the SRD, so we can't display its full
        content. You can find it at the D&D Beyond search link above!**""")


## display logic

if query and not results:
    st.warning(f"no matches for '{query}'")
elif results:
    if len(results) == 1:
        st.success(f"Found 1 match for query '{query}'")
    else:
        st.success(f"Found {len(results)} matches for query '{query}'")

# table view
table_view = st.toggle(label="Show as table (select spells for additional detail)")

if table_view:
    track_feature_usage("table_view_toggle", "toggled")
    if results:
        st.session_state.view_mode = "table"
        table = st.dataframe(
            df,
            hide_index=True,
            key="spell_table",
            width="stretch",
            on_select="rerun",
            selection_mode="multi-row",
        )
        # detailed view on selected spells
        st.subheader("selected spells")
        selected_rows = table.selection.rows
        col1, col2 = st.columns(2)
        for num, index in enumerate(selected_rows):
            spell_name = df.iloc[index]["name"]
            with col1 if num % 2 == 0 else col2:
                display_handler(SPELLS[spell_name])

    else:
        st.info("No results to display. Try searching for 'level:3 dt:fire'!")

# basic view
else:
    sorted_results = sorted(list(results))
    col1, col2 = st.columns(2)
    for num, name in enumerate(sorted(results)):
        with col1 if num % 2 == 0 else col2:
            display_handler(SPELLS[name])


st.page_link("pages/home.py", label="**[<] Back to search**")
