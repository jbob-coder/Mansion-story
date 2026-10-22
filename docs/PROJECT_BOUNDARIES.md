# Project boundaries — Mansion Story and companion game

Status: project governance decision, 2026-10-22.

## Two distinct projects, one selectively shared setting

**Mansion Story (this repository)** is the public canonical source for the authored medieval-fantasy world's genesis, chronology, mapped locations, world IDs, abilities, cultures, ethics and provenance. The data registries and documented rules are authoritative **for the Mansion Story world**, subject to the existing correction/supersession protocol. This is a lore/registry project with a standalone SQLite character-memory component, **not** a running world simulation or a complete playable game.

**Eirenfall: Unbound** is a **separate, privately stored, original, offline playable RPG prototype** that draws on selected Mansion Story setting concepts. Its implementation, game mechanics, UI, local saves, maps, APK packaging, test results and release versions belong to the game project. It uses an independent gameplay dataset; it is **not** a faithful or authoritative import of every `data/world/*.json` record in this repository.

These projects are **related, not the same product, repository, version history, or runtime**. In particular, a Mansion Story canon change does **not** automatically change Eirenfall, and an Eirenfall event, location variant, balancing change, NPC behavior or save does **not** become Mansion Story canon.

## Source of truth by concern

| Concern | Authority |
| --- | --- |
| Created world history, lore, evidence classes, canonical IDs, chronology, surveyed coordinates and social definitions | Mansion Story's `data/world/` registries and `docs/`, subject to recorded provenance |
| Standalone canonical actor-memory library and cognition seeds | Mansion Story's `engine/character_memory.py` and associated data; **not** automatically used by the companion game |
| Interactive gameplay, player and NPC state, encounters, navigation presentation, story UI, economy balancing and save schema | Eirenfall's **private** game code and versioned release documentation |
| Build status, APK compatibility and game release number | Eirenfall only; no Mansion Story engine or release version implied |

## Integration policy

1. **No automatic synchronization or implicit canon promotion.** Treat any reuse as a proposed, reviewed import/change.
2. When referencing a canonical location, event, character, domain or route, preserve its Mansion Story stable ID or maintain an explicit versioned mapping `canon ID -> game ID`; never silently repurpose an ID.
3. Record source path, source commit/ref, imported fields, transformations, accepted deviations and known omissions before claiming canonical compatibility. Validate world geography, coordinate reference frames, route length and time units rather than inferring them from game-map images.
4. A game-only addition remains game-specific until intentionally proposed and recorded in this repository with provenance. Likewise, additions to Mansion Story do not mandate game changes.
5. Keep data and execution separate: authored estimates and lore events are **not** observations from a live simulation; simulated memories, beliefs and rumors are **not** world facts.
6. Preserve backward-compatible migrations for existing game saves if a future approved integration changes schemas. Run each project's tests separately; success in one does not verify the other.
7. **Privacy boundary:** This repository is public. Never push the private game's source, saves, APKs, signing materials, purchased reference assets or proprietary content here. Its private repository URL/branch is intentionally not published by this document.

## Work routing

- Worldbuilding, continuity, ID governance, history and canonical reference data -> **Mansion Story**.
- Playable RPG features, interface, narrative delivery, mobile packaging, saves, NPC gameplay and game-specific content -> **Eirenfall: Unbound** in its private repository.
- A request affecting both -> write an impact/mapping plan first, make two explicit, separately tested changes, and record each repository commit independently.

The companion game's version numbering is separate from this repository. Consult its private release and status documents for its current version.