import streamlit as st
from pages.analytics import track_search


def clickables(badges, comment=None):
    if isinstance(badges[0], str):
        badges = [badges]
    query = " ".join(term for _, term in badges)
    label = " ".join(f":{color}-badge[{term}]" for color, term in badges)

    if st.button(label, use_container_width=False):
        st.session_state.query = query
        track_search(query)
        st.switch_page("pages/search_results.py")

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
    [("blue", "concentration:yes")],
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
            ("red", "school:evocation"),
            ("green", "st:dexterity"),
            ("blue", "concentration:no"),
        ],
        "Fireball again! Plus friends.",
    ),
    (
        [("yellow", "da>20"), ("orange", "up:yes")],
        """Spells that average more than 20 points of damage AND also upscale
when cast at higher levels. BTW, Fireball is one of them.""",
    ),
]

for badges, comment in AND_examples:
    clickables(badges, comment)

st.markdown("""If you want to search over a set of options instead of combining them,
nest the values inside `( )`.""")

OR_examples = [
    (
        [("violet", "level:3"), ("orange", "dt:(fire lightning)")],
        "3rd level spells that deal either fire **OR** lightning damage.",
    ),
    (
        [("violet", "level:3"), ("orange", "dt:fire"), ("orange", "dt:lightning")],
        "No match, since no 3rd level spells deal **BOTH** fire **AND** lightning damage",
    ),
]

for badges, comment in OR_examples:
    clickables(badges, comment)

st.markdown("""
### operators
All searchable fields accept equality or inequality operators (:violet-badge[:] or
:violet-badge[!=]), and accept field-specific values based on D&D rules. For instance:""")

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
            
**Damage Amount:** :yellow-badge[damage_amount] or :yellow-badge[da]. Calculated by the applicable
die's average roll. You can also search for maximum damage (:yellow-badge[damage_amount_max]
or :yellow-badge[da_max]).
            
**Material Cost:** :red-badge[gp_cost] or :red-badge[gp]. For those pesky spells that require
a specific GP amount of some component.  
            
**Area of Effect (_size_):** :green-badge[aoe_size] or :green-badge[asz]. In addition to normalizing
for feet, radius measures were normalized to diameter for comparison. For shapes that
have multiple measures (e.g., distance, height, depth), returns whichever makes more practical
sense in-game (e.g., length of line vs. width).  
            
**Range:** :blue-badge[range] or :blue-badge[rg]. Don't forget that all values are normalized
to feet.  
            
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
