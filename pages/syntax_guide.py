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
st.markdown(
    """Jump to [supported fields](#supported-fields-new-ones-added-almost-daily) for
field-specific detials, or see a [list of search examples](#supported-fields-new-ones-added-almost-daily)
below for a glimpse into how powerful this tool can be."""
)

st.markdown("### basic behavior")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
Search terms must be in **`<field><operator><value>`** format, so this is how you
would search for all 3rd level spells, or spells that do not cause fire damage, or those
that require concentration.

Most keywords have some form of shorthand notation. E.g., you can use :violet-badge[l]
for :violet-badge[level], :green-badge[st] for :green-badge[saving_throw], or :orange-badge[dt] for
:orange-badge[damage_type]. Input for all fields and values is case insensitive, e.g., both
"evocation" or "Evocation" are valid school values.""")

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
st.caption("**Fireball**! Then **Fireball** plus friends. And then another one!")

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

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""**Operators are a big part of the magic.** All searchable fields accept
equality or inequality operators (:violet-badge[:] or :violet-badge[!=]), and numeric fields also accept
comparison operators (:violet-badge[>], :violet-badge[>=], :violet-badge[<], or :violet-badge[<=]).
                
Most values have been worked on to allow custom comparisons you wouldn't expect, such as range and
casting time between different time and D&D units.""")
with col2:
    range_ct_dur_examples = [
        (
            [("blue", "range<=5"), ("yellow", "da>20")],
            "Touch- and self-range spells.",
        ),
        (
            [("blue", "cast<=action"), ("orange", "dt:necrotic")],
            "Casting time of a single action, bonus or reaction.",
        ),
    ]

    for badges, comments in range_ct_dur_examples:
        clickables(badges, comments)

st.markdown(
    """Acceptable values follow D&D 5e rules, or better, those rules as they are part of
the [SRD](https://www.dndbeyond.com/srd), so this first one is a valid search command:"""
)
clickables([("green", "saving_throw:constitution"), ("grey", "cond:deafened")])
st.markdown("""While this second one isn't, since the values don't match the fields. Go ahead,
try it and you'll get an error message:""")
if st.button(
    ":green-badge[saving_throw:]:orange-badge[cold] :grey-badge[condition:]:green-badge[dexterity]",
    use_container_width=True,
):
    st.session_state.query = "saving_throw:cold condition:dexterity"
    st.switch_page("pages/search_results.py")


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

st.divider()
st.markdown("""
### supported fields (new ones added almost daily)""")
with st.expander("**Spell characteristics**"):
    st.markdown("""
**Level:** :violet-badge[level] or :violet-badge[l]. Accepts values from :violet-badge[0] to :violet-badge[9],
always as digits (e.g., `3`, not `three`).
                       
**School:** :red-badge[school] or :red-badge[sch]. Accepts :red-badge[abjuration],
:red-badge[conjuration], :red-badge[divination], :red-badge[enchantment], :red-badge[evocation],
:red-badge[illusion], :red-badge[necromancy], or :red-badge[transmutation].

**Classes:** :violet-badge[class] or :violet-badge[cls]. Accepts :violet-badge[wizard],
:violet-badge[sorcerer], :violet-badge[cleric], :violet-badge[paladin], :violet-badge[ranger],
:violet-badge[bard], :violet-badge[druid], or :violet-badge[warlock].
               
**Upcastable:** :yellow-badge[upcast] or :yellow-badge[up], for spells that scale when casted at
higher slots. Accepts only `true`/`false` (or `yes`/`no`) as values.""")

with st.expander("**Targeting and effects**"):
    st.markdown("""

**Damage Amount:** :yellow-badge[damage_average] or :yellow-badge[da]. Accepts any number,
always as digits (e.g., `3`, not `three`). Damage amount is calculated by average dice roll.
You can also search for maximum damage (:yellow-badge[damage_maximum] or :yellow-badge[dmax]).

**Damage Type:** :orange-badge[damage_type] or :orange-badge[dt]. Accepts :orange-badge[acid],
:orange-badge[cold], :orange-badge[fire], :orange-badge[force], :orange-badge[lightning],
:orange-badge[necrotic], :orange-badge[poison], :orange-badge[psychic], :orange-badge[radiant],
:orange-badge[thunder], :orange-badge[piercing], :orange-badge[bludgeoning], or :orange-badge[slashing].
            
**Condition:** :gray-badge[condition] or :gray-badge[cond]. Accepts are :gray-badge[blinded],
:gray-badge[charmed], :gray-badge[deafened], :gray-badge[frightened], :gray-badge[grappled],
:gray-badge[incapacitated], :gray-badge[invisible], :gray-badge[paralyzed], :gray-badge[petrified],
:gray-badge[poisoned], :gray-badge[prone], :gray-badge[restrained], :gray-badge[stunned], or
:gray-badge[unconscious].
                
**Saving Throw:** :blue-badge[saving_throw] or :blue-badge[st]. Accepts :blue-badge[strength],
:blue-badge[dexterity], :blue-badge[constitution], :blue-badge[wisdom], :blue-badge[intelligence], or
:blue-badge[charisma]. By design, this won't match any mention of saving throws, but specifically spells
that force a save (e.g., you wouldn't want to see **Bless** as a result of this search, right?).
                
**Area of Effect (_size_):** :green-badge[aoe_size] or :green-badge[asz]. Accepts only numbers, and
sizes have been normalized to feet (i.e., :green-badge[range:5280] finds range of 1 mile) to
accommodate comparison opeations. Shapes have also been normalized to diameter (e.g., **Fireball**
covers a 20-foot sphere, you'll find it here as a 40-food diameter one). Finally, for shapes that
have multiple measures (e.g., distance, height, depth), it returns whichever makes more practical
sense in-game (e.g., length of line, rather than height or width).  

**Area of Effect (_shape_):** :green-badge[aoe_shape] or :green-badge[ash]. Accepts
:green-badge[cone], :green-badge[cube], :green-badge[cylinder], :green-badge[line], or :green-badge[sphere].
""")

with st.expander("**Casting requirements**"):
    st.markdown("""
**Material Cost:** :red-badge[gp_cost] or :red-badge[gp]. For those pesky spells that require
a specific GP amount of some component. Accepts any number, always as digits (e.g., `3`, not `three`).
            
**Range:** :blue-badge[range] or :blue-badge[rg]. Distances have been normalized to feet
(i.e., :green-badge[range:5280] matches range of 1 mile). Accepts any number, always as digits (e.g., `3`,
not `three`), plus :blue-badge[self] (normalized to 1 foot) and :blue-badge[touch] (normalized to 5 feet).  

**Concentration:** :blue-badge[concentration] or :blue-badge[conc]. Accepts only `true`/`false`
(or `yes`/`no`) as values.  
            
**Ritual:** :green-badge[ritual] or :green-badge[r]. Accepts only `true`/`false`
(or `yes`/`no`) as values.
                
**Casting Time:** :red-badge[casting time] or :red-badge[cast]. Time periods have been normalized to
seconds (i.e., :red-badge[cast:60] matches casting time of 1 minute). Accepts any number, always as digits (e.g., `3`,
not `three`), plus :red-badge[instantaneous] (equivalent to 1 second), and :red-badge[action], :red-badge[bonus],
or :red-badge[reaction] (each equivalent to 6 seconds).

""")

st.divider()
st.markdown("""### search examples
Notice how things can escalate quickly, you can easily compose quite complex search terms.""")

EXAMPLE_SEARCHES = [
    # Level
    (
        [("violet", "level:0"), ("yellow", "up:yes")],
        "Cantrips that will eventually pack a punch",
    ),
    (
        [("violet", "level>=7"), ("blue", "concentration:no")],
        "High-level spells you can cast and forget",
    ),
    # Damage Amount
    (
        [("yellow", "da>=30"), ("violet", "level<=5")],
        "Maximum damage efficiency for mid-level slots",
    ),
    (
        [("yellow", "da>0"), ("yellow", "upcast:yes")],
        "Every damage-dealing spell that scales",
    ),
    # Damage Maximum
    (
        [("yellow", "dmax>=50"), ("violet", "level<=6")],
        "Spells with massive damage ceiling",
    ),
    (
        [("yellow", "dmax>80"), ("blue", "concentration:no")],
        "Devastating instant burst damage",
    ),
    # Material Cost
    (
        [("red", "gp_cost>100"), ("red", "school:necromancy")],
        "Expensive necromancy spells",
    ),
    ([("red", "gp_cost<=50"), ("green", "ritual:yes")], "Affordable ritual spells"),
    # Area of Effect (size)
    ([("yellow", "asz>=60"), ("blue", "range>=100")], "Massive AoE from safe distance"),
    (
        [("yellow", "asz<=40"), ("green", "ash:sphere")],
        "Standard 20-foot radius sphere spells",
    ),
    # Range
    (
        [("blue", "range>=200"), ("violet", "level<=4")],
        "Sniper spells for low-level casters",
    ),
    # Duration
    (
        [("blue", "duration>=3600"), ("violet", "level<=3")],
        "Long-lasting low-level buffs (1+ hour)",
    ),
    ([("blue", "duration>=60"), ("orange", "dt:fire")], "Continued fire damage"),
    # Casting Time
    (
        [("blue", "cast:action"), ("yellow", "da>=25")],
        "High-damage spells castable as standard action",
    ),
    (
        [
            ("blue", "cast<=action"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=600"),
        ],
        "Quick-cast lasting buffs",
    ),
    # School
    (
        [("red", "school:conjuration"), ("blue", "duration>=3600")],
        "Long-lasting summons (1+ hour)",
    ),
    # Class
    (
        [("violet", "class:paladin"), ("violet", "class:cleric")],
        "Spells available to both holy warriors",
    ),
    ([("violet", "class:wizard"), ("violet", "class!=sorcerer")], "Wizard exclusives"),
    # Condition
    (
        [("gray", "condition:paralyzed"), ("green", "st:wisdom")],
        "Paralysis effects with CON saves",
    ),
    ([("gray", "condition:(frightened charmed)")], "Fear or charm spells"),
    # Saving Throw
    (
        [("green", "st:wisdom"), ("violet", "level<=2")],
        "Early-game exploitation of low Wisdom enemies",
    ),
    # Damage Type
    (
        [("orange", "dt:(radiant necrotic)"), ("violet", "class:cleric")],
        "Good cleric, bad cleric",
    ),
    (
        [("orange", "dt!=(fire cold lightning)")],
        "Non-elemental damage (bypassing common resistances)",
    ),
    # Area of Effect (shape)
    ([("green", "ash:line"), ("blue", "range>=60")], "Long-range linear effect"),
    ([("green", "ash:cone"), ("green", "st:dexterity")], "Dex-save cones"),
    # Concentration
    (
        [
            ("blue", "concentration:yes"),
            ("blue", "duration>=3600"),
            ("violet", "level<=3"),
        ],
        "Low-level, long-lasting buffs",
    ),
    (
        [("blue", "concentration:no"), ("yellow", "da>25"), ("green", "ash:sphere")],
        "Massive non-concentration nukes",
    ),
    # Ritual
    (
        [("green", "ritual:yes"), ("red", "school:divination")],
        "Information-gathering rituals",
    ),
    ([("green", "ritual:yes"), ("red", "gp_cost:0")], "Free ritual spells"),
    # Character Build Optimization
    (
        [
            ("violet", "class:warlock"),
            ("violet", "level<=5"),
            ("blue", "concentration:no"),
            ("yellow", "dmax>15"),
        ],
        "Warlock's best non-concentration damage",
    ),
    (
        [
            ("violet", "class:cleric"),
            ("red", "school:evocation"),
            ("orange", "dt:(radiant fire)"),
            ("blue", "cast<=6"),
        ],
        "Cleric's quick-cast holy wrath",
    ),
    (
        [
            ("violet", "class:bard"),
            ("violet", "level<=3"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=600"),
        ],
        "Bard's best long-lasting support spells",
    ),
    (
        [
            ("violet", "class:paladin"),
            ("violet", "level:2"),
            ("yellow", "upcast:yes"),
            ("blue", "cast:action"),
        ],
        "Quick smite alternatives that scale",
    ),
    (
        [
            ("violet", "class:druid"),
            ("green", "ash:sphere"),
            ("blue", "range>=90"),
            ("yellow", "asz>=30"),
        ],
        "Druid's massive-area artillery options",
    ),
    # Combat Tactics
    (
        [
            ("green", "st:dexterity"),
            ("green", "ash:cone"),
            ("blue", "range<=60"),
            ("yellow", "da>=20"),
            ("blue", "cast:action"),
        ],
        "Fast-cast close-range cone blasters",
    ),
    (
        [
            ("green", "st:wisdom"),
            ("gray", "condition:(frightened charmed)"),
            ("violet", "level<=4"),
            ("blue", "duration>=60"),
        ],
        "Mid-level mind control lasting multiple rounds",
    ),
    (
        [
            ("blue", "concentration:no"),
            ("orange", "dt:fire"),
            ("yellow", "dmax>=40"),
            ("green", "ash:sphere"),
        ],
        "Maximum fire burst damage without concentration",
    ),
    (
        [
            ("blue", "range>=150"),
            ("green", "st:dexterity"),
            ("yellow", "asz>=40"),
            ("violet", "level<=6"),
            ("blue", "cast:action"),
        ],
        "Quick-cast long-range AoE impact",
    ),
    (
        [
            ("yellow", "dmax>50"),
            ("yellow", "upcast:yes"),
            ("violet", "level:3"),
            ("blue", "cast:action"),
        ],
        "3rd level burst damage with maximum ceiling",
    ),
    # Action Economy
    (
        [
            ("blue", "cast<=action"),
            ("blue", "concentration:no"),
            ("yellow", "da>=20"),
            ("orange", "dt!=(fire cold lightning)"),
        ],
        "Fast non-elemental damage without concentration tax",
    ),
    (
        [
            ("blue", "cast:action"),
            ("gray", "condition:(paralyzed restrained)"),
            ("blue", "duration>=60"),
        ],
        "Instant lockdown lasting rounds",
    ),
    # Resource Management
    (
        [
            ("green", "ritual:yes"),
            ("red", "gp_cost:0"),
            ("blue", "duration>=600"),
        ],
        "Free long-lasting rituals",
    ),
    (
        [
            ("blue", "concentration:no"),
            ("green", "duration>=3600"),
            ("violet", "level<=2"),
            ("yellow", "cast:action"),
        ],
        "Fast set-and-forget low-level buffs (1+ hour)",
    ),
    (
        [
            ("yellow", "upcast:true"),
            ("violet", "level>=6"),
            ("yellow", "dmax>=60"),
            ("blue", "cast:action"),
        ],
        "High-level quick-action reliable damage, with scaling",
    ),
    (
        [
            ("red", "gp_cost<=100"),
            ("red", "school:abjuration"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=3600"),
        ],
        "Affordable all-day protective wards",
    ),
    # Battlefield Control
    (
        [
            ("gray", "condition:(paralyzed incapacitated)"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=600"),
        ],
        "Long-lasting physical lockdown",
    ),
    (
        [
            ("green", "ash:line"),
            ("yellow", "asz>=100"),
            ("violet", "level<=5"),
            ("blue", "cast:6"),
        ],
        "Instant massive line effects for hallways",
    ),
    (
        [
            ("green", "st:constitution"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=60"),
            ("orange", "dt:poison"),
        ],
        "Sustained poison damage over combat",
    ),
    # Dungeon Crawling
    (
        [
            ("red", "school:divination"),
            ("blue", "range>=1000"),
            ("blue", "duration>=600"),
        ],
        "Long-range persistent scouting",
    ),
    (
        [
            ("red", "school:conjuration"),
            ("blue", "duration>=600"),
            ("red", "gp_cost:0"),
            ("blue", "cast<=360"),
        ],
        "Quick and cheap summons for exploration",
    ),
    (
        [
            ("red", "school:transmutation"),
            ("blue", "concentration:yes"),
            ("blue", "duration>=3600"),
            ("violet", "level<=3"),
            ("blue", "cast:action"),
        ],
        "Instant all-day dungeon utility buffs",
    ),
    # Boss Fighting
    (
        [
            ("yellow", "dmax>=80"),
            ("violet", "level<=7"),
            ("yellow", "upcast:yes"),
            ("green", "st:dexterity"),
            ("blue", "duration:instantaneous"),
        ],
        "Maximum burst with instant effect",
    ),
    # Nova Rounds (Maximum Damage)
    (
        [
            ("yellow", "dmax>=60"),
            ("blue", "cast:action"),
            ("blue", "concentration:no"),
            ("violet", "level<=5"),
        ],
        "Instant massive damage at mid level",
    ),
    (
        [
            ("yellow", "dmax>40"),
            ("green", "ash:sphere"),
            ("yellow", "asz>=20"),
            ("blue", "range>=100"),
            ("blue", "cast:action"),
        ],
        "Maximum AoE burst from safety",
    ),
]
col1, col2 = st.columns(2)
with col1:
    for badges, comment in EXAMPLE_SEARCHES[::2]:
        clickables(badges, comment)
with col2:
    for badges, comment in EXAMPLE_SEARCHES[1::2]:
        clickables(badges, comment)
