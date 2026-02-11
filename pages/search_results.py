import streamlit as st
from pages.cached_data import SPELLS
from src.searching import orchestrate_search
from pages.analytics import init_analytics, track_search

init_analytics()

st.title("search results")

query_from_session = st.session_state.get("search_query", "")
query_from_params = st.query_params.get("q", "")
initial_query = query_from_session or query_from_params

input_query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
    value=initial_query,
)

_, col2, _ = st.columns(3)
with col2:
    st.page_link("pages/syntax_guide.py", label="syntax guide", icon="📖")

query = input_query

if query:
    st.session_state.search_query = query
    if query != query_from_params:
        st.query_params["q"] = query

if query:
    try:
        results: set = orchestrate_search(query)
        track_search(query)
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred: {type(e).__name__}: {str(e)}")
        with st.expander("Show full error:"):
            st.exception(e)
    else:
        if not results:
            st.warning(f"no matches for '{query}'")
        else:
            st.success(f"Found {len(results)} matches for query '{query}'")
            for name in sorted(results):
                spell = SPELLS[name]
                st.subheader(f"**{spell.name}** _(Level {spell.level} {spell.school})_")
                st.write(f"""**Casting Time:** {spell.casting_time}  
**Range:** {spell.range_}  
**Components:** {spell.components}  
**Duration:** {spell.duration}  
**Concentration:** {spell.concentration}  
**Classes:** {spell.classes}  
**SRD API url:** {spell.url}""")
                with st.expander("Description"):
                    for string in spell.description:
                        st.write(string)

st.page_link("pages/home.py", label="**[<] Back to search**")
