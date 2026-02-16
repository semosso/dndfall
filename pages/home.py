import streamlit as st
from pages.analytics import track_page_view, track_search

track_page_view("Home", "/")

st.title("dndfall", text_alignment="center")
st.subheader("an advanced D&D search tool", text_alignment="center", anchor=False)

query = st.text_input(
    "Search",
    placeholder="e.g., level:3 dt:fire",
    label_visibility="hidden",
)

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

st.markdown(
    """
#### about dndfall
Inspired by the amazing [Scryfall](https://scryfall.com/), **dndfall** is a search tool that
understands how D&D is actually played. Players and DMs can mix and match criteria to
form powerful commands, cut through the noise, and quickly find what they need. This is
a personal project I came up with as a programming/Python learning-companion, and
relies on the [D&D 5e API](https://www.dnd5eapi.co/) for source data.

#### what's new?
**_02/15/2026:_** Added new functionalities. Just like all other terms, you can mix
and match between them to create some really specific searches. I also revised the syntax guide
to reflect these changes.
- **name search:** `fire` will look for any match in spell names, `-fire` for non-matches. NO
operator needed, just type and enter.
- **<any> and <not> modifiers for applicable fields**
    - `*dt` will return spells that deal any damage type
    - `-st` will return spells that force any saving throw
- **inequality operator:** changed it from `!=` to `-` in front of the search field, aligned
with Scryfall's syntax. So instead of `dt!=fire`, use `-dt:fire` to see all spells except
those that deal fire damage
- **description search:** `desc` or `description` looks for matches in spells descriptions  

**_v. 0.1 (beta):_** supports all [SRD](https://www.dndbeyond.com/srd) spells! Additional
functionality to follow soon (monsters, class abilities, features, etc.).
""",
    text_alignment="justify",
)

if query:
    track_search(query)
    st.session_state.query = query
    st.switch_page("pages/search_results.py")
