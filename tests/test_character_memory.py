"""Persistent character memory regression tests: no world simulation required."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from engine.character_memory import MemoryStore, WorldTime
from scripts.bootstrap_character_memory import bootstrap, read_seed, validate_profiles


class CharacterMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "save" / "character.sqlite"
        self.store = MemoryStore(self.path)
        self.store.register("NPC-LOW", 20)
        self.store.register("NPC-HIGH", 90)
        self.t0 = WorldTime(30000, 1, 360)
        self.t3 = WorldTime(30003, 1, 360)

    def tearDown(self) -> None:
        self.store.close()
        self.dir.cleanup()

    def record(self, who: str, description: str = "The bridge was damaged", **kwargs) -> int:
        return self.store.remember(
            who, description, learned_at=kwargs.pop("learned_at", self.t0), **kwargs
        )

    def test_disk_persistence_across_restart(self):
        ident = self.record("NPC-LOW", tags=["bridge"])
        self.store.close()
        self.store = MemoryStore(self.path)
        actual = self.store.history("NPC-LOW")
        self.assertEqual([m["memory_id"] for m in actual], [ident])
        self.assertEqual(actual[0]["description"], "The bridge was damaged")

    def test_no_cross_character_memory_leak(self):
        self.record("NPC-LOW", "I heard a rumor about the queen")
        self.assertEqual(self.store.history("NPC-HIGH"), [])
        self.assertEqual(self.store.recall("NPC-HIGH", as_of=self.t0, query="queen"), [])

    def test_high_intelligence_better_durable_recall(self):
        for who in ("NPC-LOW", "NPC-HIGH"):
            self.record(who, "The old ford washed away", salience=0.4, emotion=0.2)
        low = self.store.recall("NPC-LOW", as_of=self.t3, minimum_strength=0)
        high = self.store.recall("NPC-HIGH", as_of=self.t3, minimum_strength=0)
        self.assertEqual(len(low), 1)
        self.assertEqual(len(high), 1)
        self.assertGreater(high[0]["strength"], low[0]["strength"])
        self.assertEqual(len(self.store.history("NPC-LOW")), 1)

    def test_storage_never_limited_by_intelligence(self):
        for number in range(40):
            self.record("NPC-LOW", f"Detail {number} of the village", salience=0.95)
        self.assertEqual(len(self.store.history("NPC-LOW")), 40)
        self.assertEqual(len(self.store.recall("NPC-LOW", as_of=self.t0)), 4)
        self.assertEqual(self.store.working_slots(90), 11)

    def test_forgetting_is_access_loss_not_archive_deletion(self):
        self.record("NPC-LOW", "Unremarkable footprint", salience=0)
        far_future = WorldTime(30100, 1, 360)
        self.assertEqual(self.store.recall("NPC-LOW", as_of=far_future), [])
        self.assertEqual(len(self.store.history("NPC-LOW")), 1)

    def test_recall_is_query_filtered(self):
        self.record("NPC-HIGH", "Saw a wolf by the ford", tags=["animal"])
        self.record("NPC-HIGH", "Bought copper ore", tags=["ore"])
        self.assertEqual(
            [x["description"] for x in self.store.recall("NPC-HIGH", as_of=self.t0, query="wolf")],
            ["Saw a wolf by the ford"]
        )

    def test_rumor_is_marked_not_promoted_to_truth(self):
        self.record("NPC-LOW", "Hornborn started the old scar", source_type="heard",
                    confidence=0.1, tags=["rumor"], world_event_id="EVT-020")
        recalled = self.store.recall("NPC-LOW", as_of=self.t0)
        self.assertEqual(recalled[0]["source_type"], "heard")
        self.assertEqual(recalled[0]["confidence"], 0.1)
        self.assertEqual(recalled[0]["world_event_id"], "EVT-020")

    def test_correction_appends_and_preserves_prior_claim(self):
        prior = self.record("NPC-LOW", "The market burned by lightning")
        changed = self.store.remember(
            "NPC-LOW", "The market was damaged in a revolt",
            learned_at=WorldTime(30000, 2, 0), supersedes_id=prior,
            kind="semantic", source_type="learned"
        )
        self.assertEqual(len(self.store.history("NPC-LOW")), 2)
        latest = self.store.recall("NPC-LOW", as_of=WorldTime(30000, 2, 0))
        self.assertEqual([x["memory_id"] for x in latest], [changed])
        self.assertEqual(len(self.store.recall("NPC-LOW", as_of=WorldTime(30000, 2, 0),
                                               include_superseded=True)), 2)

    def test_correction_must_belong_to_actor(self):
        foreign = self.record("NPC-LOW")
        with self.assertRaisesRegex(ValueError, "own memory"):
            self.store.remember("NPC-HIGH", "I changed my mind", learned_at=self.t0,
                                supersedes_id=foreign)

    def test_correction_does_not_retroactively_hide_memory(self):
        ident = self.record("NPC-LOW")
        self.store.remember("NPC-LOW", "A revised belief",
                            learned_at=WorldTime(30000, 3, 0),
                            supersedes_id=ident)
        self.assertEqual(self.store.recall("NPC-LOW", as_of=self.t0)[0]["memory_id"], ident)

    def test_future_memories_not_known_early(self):
        self.record("NPC-HIGH", "Tomorrow the bridge falls", learned_at=WorldTime(30000, 2, 0))
        self.assertEqual(self.store.recall("NPC-HIGH", as_of=self.t0), [])

    def test_a_story_from_the_past_can_be_learned_now(self):
        self.store.remember("NPC-HIGH", "Found a book about Year 18,420",
                            occurred_at=WorldTime(18420, 1, 0),
                            learned_at=self.t0, kind="semantic", source_type="learned")
        self.assertEqual(len(self.store.history("NPC-HIGH")), 1)

    def test_learning_cannot_precede_event(self):
        with self.assertRaisesRegex(ValueError, "occurrence"):
            self.store.remember("NPC-HIGH", "Saw tomorrow", occurred_at=self.t3,
                                learned_at=self.t0)

    def test_stat_training_is_durable_and_historically_scoped(self):
        self.store.set_intelligence("NPC-LOW", 75, WorldTime(30000, 2, 0),
                                    "Completed advanced navigational lessons")
        self.assertEqual(self.store.actor("NPC-LOW")["intelligence"], 75)
        self.assertEqual(self.store.intelligence_at("NPC-LOW", self.t0), 20)
        self.assertEqual(self.store.intelligence_at("NPC-LOW", WorldTime(30000, 3, 0)), 75)
        self.store.close()
        self.store = MemoryStore(self.path)
        self.assertEqual(self.store.actor("NPC-LOW")["intelligence"], 75)
        self.store.register("NPC-LOW", 20)  # re-seeding must not overwrite trained stat
        self.assertEqual(self.store.actor("NPC-LOW")["intelligence"], 75)

    def test_new_memories_encode_with_time_effective_intelligence(self):
        self.store.set_intelligence("NPC-LOW", 85, WorldTime(30000, 2, 0), "Training")
        old = self.record("NPC-LOW", learned_at=self.t0)
        new = self.record("NPC-LOW", learned_at=WorldTime(30000, 3, 0))
        archive = {x["memory_id"]: x for x in self.store.history("NPC-LOW")}
        self.assertGreater(archive[new]["encoding"], archive[old]["encoding"])

    def test_animal_can_remember_without_being_person(self):
        self.store.register("NPC-BEAST", 17, kind="animal")
        self.store.remember("NPC-BEAST", "Danger scent by the river", learned_at=self.t0,
                            kind="instinctive", source_type="instinct", tags=["danger"])
        self.assertEqual(self.store.recall("NPC-BEAST", as_of=self.t0)[0]["kind"], "instinctive")

    def test_veil_actor_has_no_fake_surface_location(self):
        self.store.register("ENT-SHADE", 95, kind="veiled_consciousness")
        self.store.remember("ENT-SHADE", "An echo in the Veil", learned_at=self.t0,
                            kind="magical", location_id=None)
        self.assertIsNone(self.store.history("ENT-SHADE")[0]["location_id"])

    def test_dead_actor_cannot_gain_lived_or_background_memories(self):
        self.store.register("NPC-DEAD", 85, alive=False)
        for source_type in ("direct", "background"):
            with self.assertRaisesRegex(ValueError, "Deceased"):
                self.store.remember("NPC-DEAD", "Afterlife rumor",
                                    learned_at=self.t0, source_type=source_type)
        with self.assertRaisesRegex(ValueError, "Deceased"):
            self.store.set_intelligence("NPC-DEAD", 90, self.t0, "No")

    def test_rehearsal_strengthens_access_but_not_archive(self):
        ident = self.record("NPC-LOW", salience=0.25)
        before = self.store.recall("NPC-LOW", as_of=self.t3, minimum_strength=0)[0]["strength"]
        self.store.rehearse("NPC-LOW", ident, WorldTime(30002, 1, 0))
        after = self.store.recall("NPC-LOW", as_of=self.t3, minimum_strength=0)[0]["strength"]
        self.assertGreater(after, before)
        self.assertEqual(len(self.store.history("NPC-LOW")), 1)

    def test_rehearsal_must_belong_to_character(self):
        ident = self.record("NPC-LOW")
        with self.assertRaisesRegex(ValueError, "belong"):
            self.store.rehearse("NPC-HIGH", ident, self.t0)

    def test_append_only_sql_triggers(self):
        ident = self.record("NPC-HIGH")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.db.execute("DELETE FROM experience WHERE memory_id=?", (ident,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.db.execute("UPDATE experience SET description='fake' WHERE memory_id=?",
                                  (ident,))
        self.store.db.rollback()
        self.assertEqual(len(self.store.history("NPC-HIGH")), 1)

    def test_backup_snapshot_restores_memories(self):
        ident = self.record("NPC-LOW", "A carved sign")
        target = Path(self.dir.name) / "backup" / "memory.sqlite"
        self.store.backup(target)
        with MemoryStore(target) as restored:
            self.assertEqual(restored.history("NPC-LOW")[0]["memory_id"], ident)

    def test_bad_values_are_rejected(self):
        for score in (-1, 101, 0.2, True):
            with self.assertRaises(ValueError):
                self.store.register("NPC-BAD", score)
        with self.assertRaises(ValueError):
            self.record("NPC-LOW", salience=float("nan"))
        with self.assertRaises(ValueError):
            self.record("NPC-LOW", source_type="omniscient")
        with self.assertRaises(ValueError):
            self.store.recall("NPC-LOW", as_of=self.t0, limit=0)
        with self.assertRaises(ValueError):
            WorldTime(30000, 361, 0)


class SeedConsistencyTests(unittest.TestCase):
    def test_all_canonical_persons_animals_and_veil_entities_have_stats(self):
        a, profiles = read_seed()
        self.assertEqual(validate_profiles(a, profiles), [])
        eligible = [x for x in a["entities"] if x["type"] in
                    {"person", "animal", "veiled_consciousness"}]
        self.assertEqual(len(eligible), len(profiles["profiles"]))

    def test_seed_bootstraps_once_and_omits_deceased(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memories.sqlite"
            first = bootstrap(path)
            second = bootstrap(path)
            self.assertEqual(first["registered"], 24)
            self.assertEqual(first["new_starting_backgrounds"], 23)
            self.assertEqual(second["new_starting_backgrounds"], 0)
            with MemoryStore(path) as saved:
                self.assertEqual(saved.history("NPC-007"), [])
                self.assertEqual(len(saved.history("NPC-001")), 1)
                self.assertEqual(saved.actor("ENT-001")["kind"], "veiled_consciousness")
                self.assertEqual(saved.actor("NPC-010")["kind"], "animal")

    def test_new_future_character_can_register_without_editing_old_history(self):
        with tempfile.TemporaryDirectory() as folder:
            with MemoryStore(Path(folder) / "save.db") as save:
                save.register("NPC-024", 47)
                t = WorldTime(30000, 1, 370)
                save.remember("NPC-024", "Met a caravan at the ford", learned_at=t)
                self.assertEqual(len(save.history("NPC-024")), 1)


if __name__ == "__main__":
    unittest.main()
