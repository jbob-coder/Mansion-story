# Mansion Story — The World Before the Story

**Canonical medieval-fantasy RPG universe and living-world archive.**

Creation begins at **year 0**, not at a castle or a quest. The creator establishes physical and metaphysical laws and records how land, life, societies and histories arise. The requested destination is the **medieval-fantasy era, beginning in world year 30,000**. The archive currently contains the first complete chronological framework and an initial mapped region for that era.

The creator establishes conditions, not a compulsory script for sentient beings. A world's history is a ledger of things that happened, not chapters the population must obey.

## Reading order
1. [The First Dawn](docs/THE_FIRST_DAWN.md) — genesis, the creator's limits, and emergence of reality.
2. [World Bible](docs/WORLD_BIBLE.md) — themes, realms and what is and is not established.
3. [Time and History](docs/TIME_AND_HISTORY.md) — dates, eras, time and the journey to the selected era.
4. [Spatial System](docs/SPATIAL_SYSTEM.md) — world layers, coordinates, distances and containment.
5. [Abilities](docs/ABILITIES.md) — one core domain per entity and unlockable branches.
6. [Hierarchies](docs/HIERARCHIES.md) — settlements, families, crowns and overlapping authority.
7. [Canon and Continuity](docs/CANON_AND_CONTINUITY.md) — IDs, claims, revisions and event history.
8. [Start Here](docs/START_HERE.md) — repository layout, current state and expansion workflow.
9. [Next Work](docs/NEXT_WORK.md) — explicit unimplemented systems.
10. [Shadows and Evil](docs/SHADOWS_AND_EVIL.md) — confirmed wrongdoing, a malignant Veil intelligence, factions and resistance.
11. [Beasts, Beastfolk and Taboos](docs/BEASTS_BEASTFOLK_AND_TABOOS.md) — personhood, creature ecology, discriminatory customs and forbidden practices.
12. [Shadow History](docs/SHADOW_HISTORY.md) — dated harm, resistance, law and political consequences.
13. [Moral Causality](docs/MORAL_CAUSAL_MODEL.md) — design contract for a future unscripted ethical/social simulation.
14. [Human Dominion](docs/HUMAN_DOMINION.md) — human political, demographic and economic ascendancy in the known world.
15. [Creature Codex](docs/CREATURE_CODEX.md) — sapient species, ordinary wildlife and rare fantasy beasts.
16. [Civilization and Economy](docs/CIVILIZATION_AND_ECONOMY.md) — populations, religions, guilds, production and trade.
17. [Complete World Inventory](docs/COMPLETE_WORLD_INVENTORY.md) — 68 specified world systems and truthful implementation states.
18. [Creator Decisions](docs/CREATOR_DECISIONS.md) — canon priorities, scope and continuity decisions.

## Data
`data/world/atlas.json` is the structured initial world registry. `scripts/validate_world.py` validates IDs, references, dates, ability ownership, coordinates and routes with Python's standard library.

**Scope boundary:** This is an authored seed and world history, **not** an executing NPC simulation or complete planetary atlas. Coordinates within the charted region are fictional internal survey coordinates. A documented historical event does not imply the simulation was run.

## Permanent Character Memory (standalone component)

Every one of the **24 registered characters** has an individually authored intelligence stat in [Cognition Profiles](data/world/character_cognition.json). The reusable [SQLite memory engine](engine/character_memory.py) saves each actor's observed or learned experiences and preserves false beliefs, corrections, and historical states across program restarts. Intelligence affects accessible recall, not permanent archival capacity. See [Character Memory](docs/CHARACTER_MEMORY.md).

Check the seed with `python scripts/bootstrap_character_memory.py --validate`, create a local save with `python scripts/bootstrap_character_memory.py --db saves/campaign_01/memory.sqlite`, and run tests with `python -m unittest discover -s tests -v`. Save files are ignored by Git. **This is working memory persistence, not yet a live NPC mind or gameplay simulation.**
