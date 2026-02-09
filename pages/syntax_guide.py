import streamlit as st

st.header("syntax guide", divider=True)

st.markdown("""Search terms must be in `<field>``<operator>``<value>` format.""")

st.subheader("Combining terms")

st.markdown("""This is where the magic happens: You can put multiple terms together and create really specific search commands. By default, all terms are combined, i.e., all terms must match to find a spell.

**For example:**
- :violet-badge[level:3] :orange-badge[dt:fire] returns 3rd level fire damage spells, **Fireball** anyone?
- :red-badge[school:Evocation] :gray-badge[st:dexterity] :blue-badge[conc:false] returns Evocation spells with Dexterity saves that don't require concentration. **Fireball** and friends!
- :gray-badge[st:wisdom] :orange-badge[cond:charmed] :violet-background[class:Bard] returns charm spells, available to Bards, with Wisdom saves like **Charm Person**""")

st.subheader("Numeric fields")

st.markdown(
    """Searches on numeric fields accept equality/inequality (:violet-badge[:] or :violet-badge[!=]) and comparison (:violet-badge[>], :violet-badge[>=], :violet-badge[<], :violet-badge[<=]) operators.
    Different fields accept different ranges of values, but they all must be numeric (e.g., `3`, not `three`). E.g., :red-badge[level] supports numbers from 0 (cantrips) to 9, while :green-badge[range] or :blue-badge[duration] accept any positive number.

Currently, supported numeric fields are :red-badge[level], :green-badge[range] or :blue-badge[duration]."""
)

st.subheader("Level")

st.markdown("""
Use the :violet-badge[level] keyword, or simply :violet-badge[l] (most keywords have some shorthand notation), to search spells by level.
Level searches accept only numeric values, from 0 (cantrips) to 9, and may be performed with equality (:violet-badge[:]), inequality (:violet-badge[!=]) or comparison (:violet-badge[>], :violet-badge[>=], :violet-badge[<], :violet-badge[<=]) operators.
            
**For example:** :violet-badge[l:3] gets you all 3rd level spells, :violet-badge[l>=5] those higher than or from the 5th level. :violet-badge[level!=0] will show only leveled spells (i.e., excluding cantrips).""")

st.subheader("School")

st.markdown("""
Use :red-badge[school] or :red-badge[sch] to find spells from a specific school of magic. School searches may be performed with equality (:red-badge[:]) or inequality (:red-badge[!=]) operators.

**For example:** :red-badge[school:Evocation] results in all spells from the Evocation school, while :red-badge[sch!=Illusion] shows all spells except those from the Illusion school.""")


st.markdown("""
## Concentration

Use `concentration:` or `conc:` to find spells that require (or don't require) concentration.

**Examples:**

- :blue-badge[concentration:true] — Spells requiring concentration
- :blue-badge[conc:false] — Spells that don't require concentration
- :blue-badge[concentration!=false] — Same as `conc:true`

---

## Ritual

Use `ritual:` or `r:` to find spells that can (or can't) be cast as rituals.

**Examples:**

- :green-badge[ritual:true] — Spells that can be cast as rituals
- :green-badge[r:false] — Spells that cannot be ritual cast
- :green-badge[ritual!=true] — Non-ritual spells

---

## School

Use `school:` or `sch:` to find spells from a specific school of magic.

**Examples:**

- :red-badge[school:Evocation] — Evocation school spells
- :red-badge[sch:Necromancy] — Necromancy school spells
- :red-badge[school!=Illusion] — All spells except Illusion

---

## Condition

Use `condition:` or `cond:` to find spells that inflict status conditions.

**Examples:**

- :orange-badge[condition:frightened] — Spells that can cause the frightened condition
- :orange-badge[cond:charmed] — Spells involving charm effects
- :orange-badge[condition:invisible] — Spells that grant invisibility

---

## Damage Type

Use `damage_type:`, `dmg_type:`, or `dt:` to find spells that deal specific damage types.

**Examples:**

- :orange-badge[damage_type:fire] — Fire damage spells
- :orange-badge[dt:lightning] — Lightning damage spells
- :orange-badge[dmg_type!=poison] — Spells that don't deal poison damage

---

## Damage Amount

Use `damage_amount:`, `dmg_amt:`, or `da:` to find spells by their damage dice.

**Examples:**

- :orange-badge[damage_amount:8d6] — Spells dealing exactly 8d6 damage
- :orange-badge[da:8d6] — Same as above

---

## Saving Throw

Use `saving_throw:` or `st:` to find spells that require specific saving throws.

**Examples:**

- :gray-badge[saving_throw:dexterity] — Spells requiring a Dexterity save
- :gray-badge[st:wisdom] — Spells requiring a Wisdom save
- :gray-badge[saving_throw!=constitution] — Spells that don't use Constitution saves

---

## Material Cost

Use `material:`, `gp_cost:`, or `gp:` to find spells by their material component cost in gold pieces.

**Examples:**

- :rainbow-badge[gp_cost>=100] — Spells with materials costing 100gp or more
- :rainbow-badge[material<50] — Spells with cheap material components
- :rainbow-badge[gp:0] — Spells with no material cost

---

## Class

Use `class:` or `cls:` to find spells available to specific classes.

**Examples:**

- :violet-background[class:Wizard] — Spells on the Wizard spell list
- :violet-background[cls:Cleric] — Spells available to Clerics
- :violet-background[class!=Warlock] — Spells not available to Warlocks""")
