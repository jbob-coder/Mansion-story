# Permanent Character Memory — Intelligence-Dependent Cognition

**Implemented:** a standalone, SQLite-backed, persistent character-memory library with bootstrap tooling and regression tests. **Not implemented:** integration with a live NPC simulation, gameplay clock, sensory perception, planning, dialogue or save-state coordinator.

## Canon versus private memory

The world atlas records objective authored history and eventual simulation events. The memory database records **what an individual thinks occurred**. Merely recording a historical event does not inject the truth into everyone else's brain. Rumors, lies, mistakes, uncertainty, dreams, and incomplete testimony may be remembered without changing canon.

Permanent means that recorded experiences, corrections and rehearsals survive a database close, reopening, and consistent backup. Recall can fade, become partial, or be supplanted without deleting the original experience. Never use an NPC memory to rewrite an objective species definition or legal historical record.

## Intelligence stat — 0 to 100

The character cognition registry, data/world/character_cognition.json, provides individually authored intelligence values for all **24 existing** persons, named animals and Veil consciousnesses. Future character instances register an individual intelligence value immediately when spawned or introduced. Intelligence is a game-cognition stat, **not** IQ, moral worth, power, inherited species destiny or a reason to deny personhood.

| Intelligence | Active retrieval slots | General RPG behavior |
|---|---:|---|
| 0–19 | 2–3 | Primitive or strongly cue-dependent recollection |
| 20–39 | 4–5 | Instinct, familiar places, strong danger cues |
| 40–59 | 6–7 | Practical and socially relevant memories |
| 60–79 | 8–9 | More durable history and useful patterns |
| 80–100 | 10–12 | Greater clarity and longer reliable recall, never omniscience |

**Every recorded experience is permanently stored regardless of intelligence.** Intelligence affects *encoding clarity*, *long-term retention* and *number of memories considered at once*, not archive size. Current rules are configurable engine constants:

    encoding = min(1, 0.30 + 0.0055*intelligence
                      + 0.12*salience + 0.08*emotion)

    half_life_days = (30 + 4*intelligence)*(1 + 8*salience + 4*emotion)
    strength = encoding * 2**(-days_since_learning_or_rehearsal/half_life_days)
    active_slots = 2 + intelligence//10

These are **design numbers**, not empirical neuroscience. Emotion can make an inaccurate rumor vivid, but never makes it fact. Training may improve intelligence by creating a dated stat-change record. Historical recall and encoding use the effective intelligence at the queried world time.

## Memory classification

Seven types: episodic, semantic, social, spatial, procedural, instinctive, magical. Seven sources: direct, heard, learned, inferred, dream, instinct and background. Records may include confidence (belief certainty), salience, emotion, learned time, the original event time, optional world event and location references, source actor, tags, and a correction link.

### Correction and forgetting

A subsequent correction creates a new experience row referencing the earlier memory with supersedes_id. Both versions remain in the permanent archive; queries scoped before the correction continue to return the old understanding. Rehearsal is a separately dated append-only record that refreshes retrieval accessibility without overwriting the original experience. SQL triggers prohibit normal UPDATE/DELETE on experience, rehearsal and intelligence-history tables.

This is data-integrity protection, **not** cryptographic tamper-proofing against someone with full database access.

### Species and death

Animals can retain instinctive danger/territory memories without being portrayed as speaking people. Sapient Hornborn, Deepkin, Reedfolk and humans have the same type of individual memory storage. Veil consciousnesses can remember without fake Surface coordinates. Deceased actors remain in history but cannot receive fresh memories, rehearse or increase intelligence. No character knows every atlas event by default.

## How to use

From the repository root:

    python scripts/bootstrap_character_memory.py --validate
    python scripts/bootstrap_character_memory.py --db saves/campaign_01/memory.sqlite
    python -m unittest discover -s tests -v

The bootstrap registers 24 known actor profiles. It adds one clearly sourced *authored starting familiarity* to each of the 23 living ones; the dead historical NPC receives none. Re-running the initializer is idempotent and never resets changed intelligence stats in existing saves.

Example integration (not a canonical event):

    from engine.character_memory import MemoryStore, WorldTime

    with MemoryStore("saves/campaign_01/memory.sqlite") as memory:
        moment = WorldTime(30000, 1, 390)
        memory.remember(
            "NPC-001", "A messenger reports a damaged eastern ford.",
            learned_at=moment, kind="semantic", source_type="heard",
            source_actor_id="NPC-006", location_id="LOC-001",
            confidence=0.55, salience=0.75, tags=["ford", "messenger"]
        )
        recall = memory.recall(
            "NPC-001", as_of=WorldTime(30000, 1, 420), query="ford"
        )
        memory.backup("saves/campaign_01/memory-backup.sqlite")

A new NPC needs only a unique ID and registered intelligence stat, e.g.:

    memory.register("NPC-024", intelligence=58, kind="person")

This library does not *generate* events or move characters. A gameplay host must decide what was perceptible and insert memory only after a valid interaction resolves.

## Save integrity and limitations

- SQLite transactions and WAL protect file-backed memory saves. The backup API makes a consistent copy even while WAL exists.
- Save-scoped SQLite data belongs outside the tracked lore repository. Do not commit private game saves; ignore generated save directories and SQLite sidecars.
- No autonomous memory journaling occurs in the background. Host runtime must call it.
- Per-character recall is isolated by actor ID; a character has no direct API to read another's mind.
- Text retrieval uses lexical tokens; no embeddings, omniscient inference, or fabricated missing recollections.
- Current retrieval scans an actor's records; a very large simulated population will require actor-level paging and retrieval indexes.
- Memory writes are not yet atomic with the future world-state transaction log. This is a real integration milestone to finish before claiming an end-to-end living game.

## Integration sequence

1. Register each generated actor with individually selected intelligence and life status.
2. Implement actual perception constraints: distance, light, sound, language, skill and attention.
3. Append personally observed, reported and inferred experiences after real events.
4. Query only the deciding actor's accessible memories to choose goals and dialogue.
5. Record memory updates and feedback without erasing earlier subjective history.
6. Integrate world tick, event journal, crash-safe save state, replay and tests.
7. Add optimized searchable storage when actual NPC population becomes large.

Result: the persistence and recall library is working, but NPC autonomous consciousness and gameplay integration remain unimplemented.
