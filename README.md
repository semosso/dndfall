# about dndfall

Scryfall-like D&D app. If that doesn't make much sense to you, read on.

[Scryfall](https://scryfall.com/) is a powerful and popular search plaform for Magic: the Gathering. Its [extensive syntax guide](https://scryfall.com/docs/syntax) allows users to perform highly detailed and customizable searches over virtually every piece of information on MTG's 100,000+ cards.

This project aims to replicate Scryfall's functionalities for Dungeons & Dragons 5th edition, specifically the [5th Edition System Reference Document (SRD)](https://www.dndbeyond.com/srd).

This IS NOT be a NLP/fuzzy matching search engine, which makes little sense given how ubiquitous D&D information is online.

# motivation

I'm taking this personal project on as a Python and related tools (e.g., FastAPI, SQL, some front-end down the road) learning mechanism.

# structure

 As of Feb 10, 2026, the beta is live [here](dndfall.com).

# to-dos

- better testing routines
- move away from local source file for intake, should be easy enough
- improve on tagging, indices and regex functions
- dnd improvements (in addition to adding monsters, etc.): many more derived fields to come,
e.g., immunity/resistance, healing, support effects, debuff effects
- start working on the front end (ideally moving to React)

# known quirks
- **Web** shows up if you search for :orange-badge[dt:fire], because the web is flammable
and deals fire damage to creatures stuck in it if burned.          
- Don't expect to find any references to Tasha, Otiluke, or Mordenkainen in spell names;
these are proprietary D&D names, and source data for this tool is the SRD.
- A few weirdly written spells may not match on some searches, such as **Hallow**
("nor can such creatures charm, frighten or possess") or **Arcane Hand** ("attempts to grapple").
- Some conditions result in others (e.g., a paralyzed creature is also incapacitated), and the
tool will only match the one you actually search for.

