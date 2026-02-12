import streamlit as st
import uuid

from pages.cached_data import SPELLS
from src.searching import orchestrate_search
from pages.analytics import track_search

st.set_page_config(layout="wide")

# for tracking purposes
if "client_id" not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())


def handle_search():
    query = st.session_state.search_input_widget
    st.session_state.query = query
    track_search(query)


st.title("search results")
query = st.session_state.get("query")

input_query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
    value=query,
    key="search_input_widget",
    on_change=handle_search,
)

if query:
    try:
        results: set = orchestrate_search(query)
    except Exception as e:
        st.error(f"An error occurred: {type(e).__name__}: {str(e)}")
    else:
        if not results:
            st.warning(f"no matches for '{query}'")
        else:
            st.success(f"Found {len(results)} matches for query '{query}'")
            col1, col2 = st.columns(2)
            sorted_results = sorted(list(results))
            with col1:
                for name in sorted(results)[::2]:
                    spell = SPELLS[name]
                    st.subheader(
                        f"**{spell.name}** _(Level {spell.level} {spell.school})_"
                    )
                    st.write(f"""**Casting Time:** {spell.casting_time}  
    **Range:** {spell.range_}  
    **Components:** {spell.components}. {spell.material}  
    **Duration:** {spell.duration}  
    **Concentration:** {spell.concentration}  
    **Classes:** {spell.classes}  
    **SRD API url:** {spell.url}""")
                    with st.expander("Description"):
                        for string in spell.description:
                            st.write(string)
            with col2:
                for name in sorted(results)[1::2]:
                    spell = SPELLS[name]
                    st.subheader(
                        f"**{spell.name}** _(Level {spell.level} {spell.school})_"
                    )
                    st.write(f"""**Casting Time:** {spell.casting_time}  
                **Range:** {spell.range_}  
                **Components:** {spell.components}. {spell.material}  
                **Duration:** {spell.duration}  
                **Concentration:** {spell.concentration}  
                **Classes:** {spell.classes}  
                **SRD API url:** {spell.url}""")
                    with st.expander("Description"):
                        for string in spell.description:
                            st.write(string)


st.page_link("pages/home.py", label="**[<] Back to search**")
