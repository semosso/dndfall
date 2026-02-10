import streamlit as st


def clickables(badges, comment=None):
    if isinstance(badges[0], str):
        badges = [badges]
    query = " ".join(term for _, term in badges)
    label = " ".join(f":{color}-badge[{term}]" for color, term in badges)

    st.page_link(
        "pages/search_results.py",
        label=label,
        query_params={"q": query},
    )
    if comment:
        st.caption(comment)


st.header("syntax guide", divider=True)
st.markdown(
    """Search terms must be in **`<field><operator><value>`** format.
That sounds more complicated than it really is, trust me. For example, this is how
you would search for all 3rd level spells, or spells that do not cause fire damage, or those
that require concentration"""
)

examples = [
    [("violet", "level:3")],
    [("orange", "dt!=fire")],
]

for badges in examples:
    clickables(badges)
st.caption("Click any example to perform its search command!")

st.markdown("""
### aliases
Most keywords have some form of shorthand notation. E.g., you can use :violet-badge[l]
for :violet-badge[level], :green-badge[st] for :green-badge[saving_throw], or :orange-badge[dt] for
:orange-badge[damage_type]. [See below](#supported-fields) for a full list of supported terms.""")

st.markdown("""
### combining search terms
This is where it gets fun! You can put multiple terms together and create really
specific search commands. By default, all terms must match to find a spell (i.e., implicit **AND**).""")

AND_examples = [
    ([("violet", "level:3"), ("orange", "dt:fire")], "Fireball, NICE!"),
    (
        [
            ("red", "school:Evocation"),
            ("green", "st:dexterity"),
            ("blue", "concentration:yes"),
        ],
        "no Fireball 😔",
    ),
]

for badges, comment in AND_examples:
    clickables(badges, comment)

st.markdown("""If you want to search over a set of options instead of combining them,
nest the values inside `( )`.""")

OR_examples = [
    (
        [("violet", "level:3"), ("orange", "dt:(fire lightning)")],
        "3rd level spells that deal either fire **OR** lightning damage. **Fireball** and friends!",
    ),
    (
        [("violet", "level:3"), ("orange", "dt:fire"), ("orange", "dt:lightning")],
        "no match, since no 3rd level spells deal **BOTH** fire **AND** lightning damage",
    ),
]

for badges, comment in OR_examples:
    clickables(badges, comment)

st.markdown("""
### operators
All fields accept equality or inequality operators (:violet-badge[:] or :violet-badge[!=]).
Fields can be textual, boolean (i.e., True or False values), and numeric.

[including boolean]

Input for numeric fields must be numbers (e.g., `3`, not `three`), and different fields accept
different ranges (e.g., :violet-badge[level] supports numbers from :violet-badge[0] (cantrips)
to :violet-badge[9]). In addition to equality and inequality, numeric fields also accept
comparison operators (:violet-badge[>], :violet-badge[>=], :violet-badge[<], or :violet-badge[<=]).""")

range_examples = [
    (
        [("violet", "level<=2"), ("grey", "st:intelligence")],
        "Are you a low level caster wanting to take advantage of dumb enemies? Say no more.",
    ),
    (
        [
            ("blue", "range>=150"),
            ("green", "st:dexterity"),
            ("yellow", "aoe_sz:40"),
            ("yellow", "aoe_sh:sphere"),
        ],
        "Guess who's back? Yep, good ole' **Fireball**!",
    ),
]

for badges, comment in range_examples:
    clickables(badges, comment)

# st.markdown("""
# ### supported fields
# **Level:** :violet-badge[level] or :violet-badge[l]
# **School:** :red-badge[school] or :red-badge[sch]
# **Concentration:** :blue-badge[concentration] or :blue-badge[conc]
# **Ritual:** :green-badge[ritual] or :green-badge[r]
# **Condition:** :gray-badge[condition] or :gray-badge[cond]
# **Saving Throw:**
# **Damage Type:** :orange-badge[damage_type] or :orange-badge[dt]
# **Damage Amount:** :yellow-badge[damage_amount] or :yellow-badge[da]
# **Material Cost:**
