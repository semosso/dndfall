import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from pages.analytics import initialize_tracking

initialize_tracking()

st.set_page_config(
    page_title="dndfall | an advanced D&D search tool",
    page_icon="🔎",
)

pages = [
    st.Page("pages/home.py", title="home", icon="🏠", default=True),
    st.Page("pages/syntax_guide.py", title="syntax guide", icon="📖"),
    st.Page("pages/search_results.py", title="search results", icon="🔎"),
]
pg = st.navigation(pages, position="hidden")

# col1, col2 = st.columns([1, 7])
# with col1:
st.page_link("pages/home.py", label="🏠 Home")
# with col2:
st.page_link("pages/syntax_guide.py", label="📖 Syntax Guide")

pg.run()
