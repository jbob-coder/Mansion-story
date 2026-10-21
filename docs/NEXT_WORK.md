# Next Work — No Pretend Completion

## Built in this milestone
- Genesis premise; chronological framework from Year 0 through selected medieval era.
- Canonical world layers and MAP-001 spatial frame.
- Governed seed region with location IDs, geographical relationships and distance rules.
- First Thread ability domain and sub-ability rules.
- Immutable IDs, evidence/provenance and event design.

## Next technical tasks
1. Implement append-only event ledger and validation of temporal consequences.
2. Add dynamic state snapshots distinct from historical facts (population, inventories, roofs, roads and authority).
3. Implement NPC needs, memory, perception, opportunity discovery and decision selection with non-scripted goals.
4. Implement actual jobs, tools, resource extraction, crafting and construction as verifiable transactions.
5. Generate roads, settlement clustering and political institutions from agent actions rather than pre-authored mission stages.
6. Add nested indoor geometry and room/floor coordinates with parent transformations.
7. Define dimensional portals as graph edges with explicit crossing time and conditions.
8. Add borders as polygons, claims and contested jurisdiction.
9. Implement ability unlock events, costs and proficiencies.
10. Add seeded deterministic simulation tests: migration, craft, bridge/road building, political election, death, destruction and historical replay.

## Scientific and simulation caution
This world currently has **authored historic outcomes**, not a million-year physics simulation. Its laws and history are descriptive canon. Autonomous NPC action, procedural kingdoms, gameplay, time stepping and validation CI require actual engines and tests before being called implemented.

## Expansion principle
Each new era and region should have three levels of evidence: underlying rules; dated changes to world state; observers with limited information. A world that records only royal legends but not farms, roads, trade and ecological consequences will not feel alive.

## Shadow canon milestone — verified repository objects (not live game systems)
- Added documented evil through historical coercion, institutional abuse, and the sapient hostile Veil entity.
- Added wildlife and Hornborn taxonomy, 5 additional mapped locations, 8 traversable routes, and a dated historical/organizational expansion.
- Added `data/world/ethics.json` with enacted laws, diverse taboo categories, false rumors and moral case records.
- Added `scripts/validate_ethics.py` and regression tests for timeline, route geometry, one-core inheritance, personhood, criminal responsibility and provenance.

**Outstanding:** an autonomous morality engine is not yet implemented. Data-driven welfare, predators, social memory, coercive pact resistance, illegal trade, investigations, consequences, and institutional change require executable world-state engines with event logs. Do not report an authored kidnapping or rescue as if it were simulated.

## Human Dominion and full system inventory — documented phase
- Record humans as the current dominant sapient civilization **only in the known inhabited world**; add human history from early cultural expansion to the First Crowns.
- Survey 10 settlement service areas with 80,850 authored inhabitants, of whom 64,520 are humans; keep the estimates separate from unobserved state.
- Expand site coordinates, species, named persons, towns, paths and dated founding events.
- Add material economy, ecology, culture, religion, roles and occupations as structured data, not fake functioning NPCs.
- Establish `data/world/system_catalog.json` with 68 pending systems across nine categories. Read `docs/COMPLETE_WORLD_INVENTORY.md`.
- Add `scripts/validate_civilization.py` and tests for population arithmetic, single ability, route connectivity, ecology, ethics and provenance.

**NEXT REQUIRED ENGINE MILESTONE:** a versioned world-state journal with deterministic simulation tick and material transactions. Until that exists, farming, reproduction, caravans, trade, autonomous citizens, buildings and war remain planning data.

## Implemented subcomponent: intelligence-dependent permanent memory

- Built `engine/character_memory.py` as a reusable SQLite durable-archive and retrieval library with per-character actor scoping, corrections, rehearsal and backup.
- Assigned individual intelligence values to all 24 currently registered characters in `data/world/character_cognition.json`. Runtime character registration supports future NPC IDs.
- Added bootstrap and regression tests; can preserve subjective records even when characters forget, die, or revise knowledge.
- **Still blocked:** actual event-sourced world tick, perception pipeline, NPC intent selection, rumor spread, dialogue, inter-NPC communication and synchronized save-state. Those must be connected before calling NPCs autonomous or alive.
- Canonical profile edits do not override intelligence changes already stored in a running campaign's save.
