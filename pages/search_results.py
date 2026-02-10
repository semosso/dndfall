import streamlit as st

from pages.cached_data import SPELLS
from src.searching import orchestrate_search

st.title("search results")
st.page_link("dndfall.py", label="<< Back to Search")

query_from_params = st.query_params.get("q", "")

input_query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
    value=query_from_params,
)

st.page_link("pages/syntax_guide.py", label="syntax guide", icon="📖")

query = input_query if input_query else query_from_params

if input_query and input_query != query_from_params:
    st.query_params["q"] = input_query
    st.rerun()

if query:
    try:
        results: set = orchestrate_search(query)
    except ValueError as e:
        st.error(str(e))
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
