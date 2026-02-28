import streamlit as st
import pandas as pd
import uuid

from pages.cached_data import SPELLS
from src.data.json_handlers import SRD_spells
from src.searching import orchestrate_search
from pages.analytics import (
    track_page_view,
    track_search,
    track_result_click,
    track_feature_usage,
)

st.set_page_config(layout="wide")

## initialization

track_page_view("search_results", "/search_results")

# for tracking purposes
if "client_id" not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())

if "selected_spell" not in st.session_state:
    st.session_state.selected_spell = None

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "grid"

st.title("search results")
query = st.session_state.get("query")

## searching functions


def execute_search():
    query = st.session_state.search_input_widget
    st.session_state.query = query


input_query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
    value=query,
    key="search_input_widget",
    on_change=execute_search,
)

## search processing

if query:
    try:
        results: set = orchestrate_search(query)
    except Exception as e:
        st.error(f"An error occurred: {type(e).__name__}: {str(e)}")
    else:
        if results:
            track_search(query, result_count=len(results))
            data: list = [SPELLS[name].__dict__ for name in results]
            df = pd.DataFrame(data=data, columns=["name", "level", "school", "url"])


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
    if spell.name.lower() in SRD_spells:
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
        st.markdown("""**Since this spell is not in the SRD, we can't display its full
        content. You can find it at the official D&D Beyond search link above!**""")


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
            use_container_width=True,
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
