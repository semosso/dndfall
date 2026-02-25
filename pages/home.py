import streamlit as st
from pages.analytics import track_page_view, track_search

st.set_page_config(layout="centered")

track_page_view("Home", "/")

if "latest_update" not in st.session_state:
    st.toast(
        "Check out our latest update: support for non-SRD spells, plus table visualization in search results!",
        icon="🔥",
    )
    st.session_state.msg_shown = True

st.title("dndfall", text_alignment="center")
st.subheader("an advanced search tool for D&D", text_alignment="center", anchor=False)

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
**dndfall** is a search tool that understands how D&D is actually played, allows
players and DMs can mix and match criteria to form powerful commands, cut through the noise,
and quickly find what they need. This is a personal project inspired by the amazing [Scryfall](https://scryfall.com/).

**Feedback, bugs or comments?** Please [email](mailto:vnazambuja@gmail.com) me directly or send them via
[this form](https://forms.gle/hiVD5N5gQ45pAQBV7).

#### what's new?

**v. 0.2 (beta):** currently supports all [SRD 5.1](https://www.dndbeyond.com/srd) spells, plus
those from the PHB, TCE and XGE in a way that complies with Wizards of the Coast's Fan Content Policy.
"""
)
with st.expander("_**02/25/2026:** table visualization_"):
    st.markdown("""
    - Added support for non-SRD spells from the PHB, TCE and XGE, in a way that is
    fully compliant with Wizards' Fan Content Policy. It will look through those spells (e.g.,
    `dt:necrotic` will match **Hex**), but will display only its name, level, school, and
    a URL to an official spell resource.
    - You can now choose to visualize the results as a table, and sort them however you want (e.g., by
    level or spell name, in ascending or descending order), and get additional detail only for
    the spells you select.
                
    I also added my personal email for any feedback you have, please reach out!
    """)

with st.expander("_**02/15/2026:** name and description search, any/not modifiers_"):
    st.markdown(
        """
    Added new functionalities. Just like all other terms, you can mix
    and match between them to create some really specific searches. I also revised the syntax guide
    to reflect these changes.
    - **name search:** `fire` will look for any match in spell names, `-fire` for non-matches. NO
    operator needed, just type and enter.
    - **<any> and <not> modifiers for applicable fields**
        - `*dt` will return spells that deal any damage type
        - `-st` will return spells that do not force any saving throw
    - **inequality operator:** changed it from `!=` to `-` in front of the search field, aligned
    with Scryfall's syntax. So instead of `dt!=fire`, use `-dt:fire` to see all spells except
    those that deal fire damage
    - **description search:** `desc` or `description` looks for matches in spells descriptions  
    """,
        text_alignment="justify",
    )

if query:
    track_search(query)
    st.session_state.query = query
    st.switch_page("pages/search_results.py")

st.divider()
st.caption(
    """**dndfall** is unofficial Fan Content permitted under the Fan Content Policy.
Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards
of the Coast. ©Wizards of the Coast LLC.""",
    text_alignment="center",
)
