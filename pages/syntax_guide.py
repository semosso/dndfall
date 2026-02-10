import streamlit as st

st.header("syntax guide", divider=True)

st.markdown("""Search terms must be in **`<field><operator><value>`** format. For example:
- :violet-badge[level:3] gets you all 3rd level spells
- :blue-badge[concentration:true] returns all spells requiring concentration
- :orange-badge[damage_type!:fire] returns all spells that do not cause Fire damage""")

st.markdown("""
### aliases
Most keywords have some form of shorthand notation. E.g., you can use :violet-badge[l]
for :violet-badge[level], :green-badge[st] for :green-badge[saving_throw], or :orange-badge[dt] for
:orange-badge[damage_type]. See below for a full list.""")

st.markdown("""
### combining search terms
This is where it gets fun. You can put multiple terms together and create really specific search commands.
By default, all terms are combined, i.e., all must match to find a spell.
            
- :violet-badge[level:3] :orange-badge[dt:fire] returns 3rd level fire damage spells, **Fireball** anyone?
- :red-badge[school:Evocation] :green-badge[st:dexterity] :blue-badge[conc:false] returns Evocation spells,
with Dexterity saves, that don't require concentration. **Fireball** again, but this time with friends!
            
If you want to search over a set of options instead of combining them, nest the values inside `( )` .
            
- :violet-badge[level:3] :orange-badge[dt:(fire cold)] returns 3rd level spells that deal either Fire **OR** Cold damage
- :violet-badge[level:3] :orange-badge[dt:fire] :orange-badge[dt:cold] won't match anything,
as no 3rd level spells deal both Fire **AND** Cold damage
- :orange-badge[dt:fire] :orange-badge[dt:cold] will let you know that **Prismatic Spray** and **Prismatic Wall**
are, unsurprisingly, the only ones with this weird mix!""")

st.markdown("""
### operators
All fields accept equality or inequality operators (:violet-badge[:] or :violet-badge[!=]),

[including boolean]
                       
Numeric fields also accept comparison operators (:violet-badge[>], :violet-badge[>=], :violet-badge[<],or :violet-badge[<=]).
Different numeric fields accept different ranges, but they all must be numeric
(e.g., `3`, not `three`). E.g., :red-badge[level] supports numbers from 0 (cantrips) to 9,
while :green-badge[range] or :blue-badge[duration] accept any positive number.

[EXAMPLES]

Currently supported numeric fields are :red-badge[level], :green-badge[range] or :blue-badge[duration].""")

st.markdown("""
### supported fields
**Level:** :violet-badge[level] or :violet-badge[l]  
**School:** :red-badge[school] or :red-badge[sch]  
**Concentration:** :blue-badge[concentration] or :blue-badge[conc]  
**Ritual:** :green-badge[ritual] or :green-badge[r]  
**Condition:** :gray-badge[condition] or :gray-badge[cond]  
**Saving Throw:**   
**Damage Type:** :orange-badge[damage_type] or :orange-badge[dt]  
**Damage Amount:** :yellow-badge[damage_amount] or :yellow-badge[da]



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
