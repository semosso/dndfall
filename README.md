# about dndfall

Scryfall-like D&D app. If that doesn't make much sense to you, read on.

[Scryfall](https://scryfall.com/) is a powerful and popular search plaform for Magic: the Gathering. Its [extensive syntax guide](https://scryfall.com/docs/syntax) allow users to perform highly detailed and customizable searches over virtually every piece of information on MTG's 100,000+ cards.

This project aims to replicate (some) of Scryfall's functionalities for Dungeons & Dragons 5th edition, specifically the [5th Edition System Reference Document (SRD)](https://www.dndbeyond.com/srd)https://www.https://www.dnd5eapi.co/.co/
See here for the [5e SRD API](https://www.dnd5eapi.co/), the consolidated source of truth for this project.

This WILL NOT be a NLP/fuzzy matching search engine, which makes little sense given how ubiquitous D&D information is online.

The value proposition is: users will be able to search for information that is not easily available. Say you're a DM preparing for a special encounter, you'll be able to [...]. Or if you're player preparing for your next level up or a special encounter, [...]. And that's just with spells! 

By using dndfall and sticking to its formal syntax, you'll get that info in no time. 

# motivation

I'm taking this personal project on as a Python and related tools (e.g., FastAPI, SQL, some front-end down the road) learning mechanism.

# structure

 As of Feb 3, 2026, this is the WIP structure:

- dndspecs.py
	- repository for all D&D rules and logic that the search engine needs, focusing on Spells first, will move to Monsters next
	- from minutiae (area of effect shapes, time and size units) to determining the schema and behavior of different searchable fields
	- in particular: NormalizedSpell and SpellField dataclasses, with normalized data and behaviors 

- main.py
	- supposed to orchestrate everything, from importing JSON from 5e SRD API to displaying results
	- still really underutilized 

- normalization.py
	- initialies each spell per schema defined in dndspecs
	- extracts and adds tags for all derived fields defined in dndspecs
	- "create_indices" in particular is still super inefficient, it loops through all spells and all tags multiple times

- searching.py
	- from user input to getting a search result
	- parses user input (SearchEngine) into field, operator, values, casts them as a ParsedQuery
	- ParsedQuery is passed into SearchCommand, which validates its components against field specific rules from dndspecs
	- if all is validated, a SearchExecution is initiated, and performs the search as determined by the operator
	- this was the latest thing I put together, so still a lot to improve

# to-dos

- better testing routines, ASAP
- move away from local source file for intake, should be easy enough
- lots to improve on "create_indices"
- more search strategies (and fix exclusion, I know if doesn't work after latest changes, it did at a prior iteration)
- dnd improvements (in addition to adding monsters, etc.): many more derived fields to come, e.g., immunity/resistance, AOE, range, healing, support effects, debuff effects, average damage
- start working on the front end (ideally starting with python friendly and moving to React)


