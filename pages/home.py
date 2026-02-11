import streamlit as st

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
### about dndfall
Inspired by the amazing [Scryfall](https://scryfall.com/), **dndfall** is a search tool that
understands how D&D is actually played. Players and DMs can mix and match criteria to
form powerful commands, cut through the noise, and quickly find what they need. This is
a personal project I came up with as a programming/Python learning-companion, and
relies on the [D&D 5e API](https://www.dnd5eapi.co/) for source data.

**v. 0.1 (beta):** supports all [SRD](https://www.dndbeyond.com/srd) spells, with
additional functionality to follow soon (monsters, class abilities, features, etc.).
""",
    text_alignment="justify",
)

if query:
    st.session_state.search_query = query  # Use session_state
    st.switch_page("pages/search_results.py")
