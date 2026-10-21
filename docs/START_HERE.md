# Start Here — Authoring Protocol

## Binding intent
- Starting at creation, build historical causality toward the selected medieval-fantasy era.
- Never fabricate an unseen historical decision as if it had been simulated; **authored background** and **simulation-observed events** have distinct provenance.
- Provide every registered in-world entity exactly one **core ability domain**, even if its expression is inert. Living actors may learn sub-abilities through life, practice and choices.
- Make geography, distance, stratification, dates, organization and authority machine-referenceable.
- There is no required quest order or chapter gating.

## Canon priorities
1. IDs, coordinates, events and claims recorded in `data/world/atlas.json`.
2. Rules and definitions in the `docs/` reference files.
3. Future event logs and simulation snapshots, once implemented.
4. Author brainstorming — **not canon** until adopted through a recorded change.

Do not silently change a historical event, established coordinate, old ID or birth date. Add a correction/supersession record with a reason.

## Current scope
- **Genesis through year 30,000** is outlined in authored history.
- One surveyed surface region in the kingdom of Vael Taryn exists in the atlas.
- Other continents, dimensions, settlement interiors and institutions are intentionally unmapped.
- Locations and citizens at year 30,000 are **authored initial state**, not evidence that autonomous NPC systems actually built them.
- Ability templates and unlock rules are specified; no ability engine has yet been implemented.

## Expanding the universe safely
1. Register stable ID, type, name, layer, parent (where relevant) and one core ability domain.
2. Pick coordinates in that layer's reference frame and record measurement confidence.
3. Register traversable route distances separately from geometric distances.
4. Record founding, transfers, birth/death, disasters and awakenings as dated events.
5. Add relations for social allegiance, rulership, parenthood, ownership and trade. Hierarchy is **not** the same as mind control.
6. Append causes/consequences and source provenance for major facts.
7. Run `python scripts/validate_world.py`; inspect conflicts before committing.

## Naming
WORLD-`NNN`, LYR-`NNN`, LOC-`NNN`, BLD-`NNN`, SET-`NNN`, POL-`NNN`, ORG-`NNN`, NPC-`NNN`, ABI-`NNN`, SUB-`NNN`, EVT-`NNN`, RTE-`NNN`, REL-`NNN`. Identifiers never recycle. Names may change and identities need not.

This repository is the historical/worldbuilding authority for Mansion Story only; it is not automatically coupled to other game repositories.

## Civilizational expansion entrypoints
Read `docs/HUMAN_DOMINION.md`, `docs/CREATURE_CODEX.md`, `docs/CIVILIZATION_AND_ECONOMY.md` and `docs/COMPLETE_WORLD_INVENTORY.md`. The machine-readable registries now include `data/world/civilization.json` (known-world demographic estimates, settlements and economic capacities) and `data/world/system_catalog.json` (68 RPG/simulation systems; documented does **not** mean implemented). Run `python scripts/validate_civilization.py` and `python -m unittest discover -s tests -v` after touching data or validation logic. New global IDs must be unique **across all registries**.
