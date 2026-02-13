import streamlit as st
from pages.analytics import track_search


def clickables(badges, comment=None):
    if isinstance(badges[0], str):
        badges = [badges]
    query = " ".join(term for _, term in badges)
    label = " ".join(f":{color}-badge[{term}]" for color, term in badges)

    if st.button(label, use_container_width=True):
        st.session_state.query = query
        track_search(query)
        st.switch_page("pages/search_results.py")

    if comment:
        st.caption(comment)


st.header("syntax guide", divider=True)
st.markdown(
    """**dndfall** offers keywords and expressions you can use to search through
D&D resources. See below for a quick overwivew of basic commands, and jump to the other specific
sections as needed. We're in beta and new functionalities are added almost everyday,
so make sure to review the guide from time to time."""
)
st.markdown("""**Jump to:**""")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
                - Basic spell characteristics (e.g., level, school, class)""")

st.divider()
st.markdown("#### basic behavior")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
Search terms must be in **`<field><operator><value>`** format, so this is how you
would search for all 3rd level spells, or spells that do not cause fire damage, or those
that require concentration.

Most keywords have some form of shorthand notation. E.g., you can use :violet-badge[l]
for :violet-badge[level], :green-badge[st] for :green-badge[saving_throw], or :orange-badge[dt] for
:orange-badge[damage_type].""")

with col2:
    examples = [
        [("violet", "level:3")],
        [("orange", "dt!=fire")],
        [("blue", "concentration:yes")],
    ]
    for badges in examples:
        clickables(badges)
    st.caption("Click any example to perform the command!")

st.markdown("""This is where it gets fun, **you can put multiple terms together and create really
    specific search commands.**""")

AND_examples = [
    [("violet", "level:3"), ("orange", "dt:fire")],
    [
        ("red", "school:evocation"),
        ("green", "st:dexterity"),
        ("blue", "concentration:no"),
    ],
    [("yellow", "da>20"), ("orange", "up:yes"), ("grey", "ash:sphere")],
]

for badges in AND_examples:
    clickables(badges)
st.caption("Fireball! Then Fireball plus friends. And then another one!")

st.markdown(""" By default, all input terms must match to find a spell (i.e., implicit **AND**).
If you want to search over a set of options instead of combining them, nest the values inside `( )`.""")

OR_examples = [
    [("violet", "level:3"), ("orange", "dt:fire"), ("orange", "dt:lightning")],
    [("violet", "level:3"), ("orange", "dt:(fire lightning)")],
]

for badges in OR_examples:
    clickables(badges)
st.caption("""No matches on the first one, no 3rd level spells deal **BOTH** fire
**AND** lightning damage. The second one searches for fire **OR** lightning damage, so match!""")

st.markdown("""**Operators are a big part of the magic.** All searchable fields accept
equality or inequality operators (:violet-badge[:] or :violet-badge[!=]), and numeric fields also accept
comparison operators (:violet-badge[>], :violet-badge[>=], :violet-badge[<], or :violet-badge[<=]).
            
Most values have been worked on to allow custom comparisons you wouldn't expect, such as range and
casting time between different D&D units.
            


            
            only numbers as input (e.g., `3`, not `three`), and accept
different ranges (e.g., :violet-badge[level] supports numbers from :violet-badge[0] (cantrips)
to :violet-badge[9]). In addition to equality and inequality, numeric fields also
            
            
            
            and accept field-specific values based on D&D rules. For instance:""")

text_examples = [
    (
        [("green", "saving_throw:constitution"), ("grey", "cond:deafened")],
        "This is a valid search command, the values match the fields.",
    )
]

for badges, comment in text_examples:
    clickables(badges, comment)

if st.button(
    ":green-badge[saving_throw:]:red-badge[cold] :grey-badge[condition:]:green-badge[dexterity]",
    use_container_width=False,
):
    st.session_state.query = "saving_throw:cold condition:dexterity"
    st.switch_page("pages/search_results.py")
st.caption(
    "These field-value pairs don't match, right? Try the search, you'll get an error."
)

st.markdown("""
Numeric fields accept only numbers as input (e.g., `3`, not `three`), and accept
different ranges (e.g., :violet-badge[level] supports numbers from :violet-badge[0] (cantrips)
to :violet-badge[9]). In addition to equality and inequality, numeric fields also accept
comparison operators (:violet-badge[>], :violet-badge[>=], :violet-badge[<], or :violet-badge[<=]).""")

range_examples = [
    (
        [("violet", "level<=2"), ("green", "st:wisdom")],
        "Are you a low level caster wanting to take advantage of dumb enemies? Say no more.",
    ),
    (
        [
            ("blue", "range>=150"),
            ("green", "st:dexterity"),
            ("yellow", "asz:40"),
            ("yellow", "ash:sphere"),
        ],
        "Guess who's back? Yep, good ole' **Fireball**!",
    ),
]

for badges, comment in range_examples:
    clickables(badges, comment)


st.markdown("""
### supported fields (new ones are added everyday)
Input for all fields and values is case insensitive, e.g., both "evocation" or "Evocation"
are valid school values.
            
#### Numeric fields
These only accept numbers (e.g., `3`, not `three`). To accommodate comparison operations,
distance and time values have been normalized to feet and seconds (i.e., :violet-badge[duration:60] finds
spells with 1 minute duration, and :green-badge[range:5280] finds range of 1 mile).  
        
**Level:** :violet-badge[level] or :violet-badge[l]. Accepts values from :violet-badge[0] to :violet-badge[9].  
            
**Damage Amount:** :yellow-badge[damage_average] or :yellow-badge[davg]. Calculated by the applicable
die's average roll. You can also search for maximum damage (:yellow-badge[damage_maximum]
or :yellow-badge[dmax]).
            
**Material Cost:** :red-badge[gp_cost] or :red-badge[gp]. For those pesky spells that require
a specific GP amount of some component.  
            
**Area of Effect (_size_):** :green-badge[aoe_size] or :green-badge[asz]. In addition to normalizing
for feet, radius measures were normalized to diameter for comparison. For shapes that
have multiple measures (e.g., distance, height, depth), returns whichever makes more practical
sense in-game (e.g., length of line vs. width).  
            
**Range:** :blue-badge[range] or :blue-badge[rg]. Don't forget that all values are normalized
to feet, so to enable comparisons, :blue-badge[self] is equal to :blue-badge[1.0] foot, and :blue-badge[touch]
is equal to :blue-badge[5] feet.  
            
#### Textual fields  
These accept specific values per SRD 5e rules.  
            
**School:** :red-badge[school] or :red-badge[sch]. Valid values are :red-badge[abjuration],
:red-badge[conjuration], :red-badge[divination], :red-badge[enchantment], :red-badge[evocation],
:red-badge[illusion], :red-badge[necromancy], or :red-badge[transmutation].  
            
**Classes:** :violet-badge[class] or :violet-badge[cls]. Valid values are :violet-badge[wizard],
:violet-badge[sorcerer], :violet-badge[cleric], :violet-badge[paladin], :violet-badge[ranger],
:violet-badge[bard], :violet-badge[druid], or :violet-badge[warlock].
            
**Condition:** :gray-badge[condition] or :gray-badge[cond]. Valid values are :gray-badge[blinded],
:gray-badge[charmed], :gray-badge[deafened], :gray-badge[frightened], :gray-badge[grappled],
:gray-badge[incapacitated], :gray-badge[invisible], :gray-badge[paralyzed], or :gray-badge[petrified].  
            
**Saving Throw:** :blue-badge[saving_throw] or :blue-badge[st]. Valid values are :blue-badge[strength],
:blue-badge[dexterity], :blue-badge[constitution], :blue-badge[wisdom], :blue-badge[intelligence], or
:blue-badge[charisma]. By design, this won't match on any mention of saving throws, but specifically on spells
that force a save (e.g., you wouldn't want to see **Bless** as a result of this search, right?).
            
**Damage Type:** :orange-badge[damage_type] or :orange-badge[dt]. Valid values are :orange-badge[acid],
:orange-badge[cold], :orange-badge[fire], :orange-badge[force], :orange-badge[lightning],
:orange-badge[necrotic], :orange-badge[poison], :orange-badge[psychic], :orange-badge[radiant],
:orange-badge[thunder], :orange-badge[piercing], :orange-badge[bludgeoning], or :orange-badge[slashing].

**Area of Effect (_shape_):** :green-badge[aoe_shape] or :green-badge[ash]. Valid values are
:green-badge[cone], :green-badge[cube], :green-badge[cylinder], :green-badge[line], or :green-badge[sphere].


                        
#### Boolean fields
These accept only `true`/`false` (or `yes`/`no`, if you prefer them) as values.  
            
**Concentration:** :blue-badge[concentration] or :blue-badge[conc].  
            
**Ritual:** :green-badge[ritual] or :green-badge[r].  
            
**Upcastable:** :yellow-badge[upcast] or :yellow-badge[up], for spells that scale when casted at
higher slots.
            
### known quirks
- **Web** shows up if you search for :orange-badge[dt:fire], because the web is flammable
and deals fire damage to creatures stuck in it if burned.          
- Don't expect to find any references to Tasha, Otiluke, or Mordenkainen in spell names;
these are proprietary D&D names, and source data for this tool is the SRD.
- A few weirdly written spells may not match on some searches, such as **Hallow**
("nor can such creatures charm, frighten or possess") or **Arcane Hand** ("attempts to grapple").
- Some conditions result in others (e.g., a paralyzed creature is also incapacitated), and the
tool will only match the one you actually search for.""")
