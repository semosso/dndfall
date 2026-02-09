import streamlit as st

from app import SPELLS
from searching import orchestrate_search

st.title("search results")

if "query" in st.session_state:
    query = st.session_state.query
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
                            **Classes:** {spell.classes}""")
                st.write(spell.description)
                st.write("**View it in SRD:**", spell.url)

st.page_link("app.py", label="<< Back to Search")
