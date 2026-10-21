"""Regression tests for geography, ethics, evil, memory and historical integrity."""
import copy
import json
import unittest
from pathlib import Path

from scripts.validate_ethics import validate_expansion

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "data/world/atlas.json").read_text(encoding="utf-8"))
ETHICS = json.loads((ROOT / "data/world/ethics.json").read_text(encoding="utf-8"))


class WorldIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.a = copy.deepcopy(SOURCE)
        self.e = copy.deepcopy(ETHICS)

    def assert_rejects(self, substring):
        errors = validate_expansion(self.a, self.e)
        self.assertTrue(any(substring in failure for failure in errors), errors)

    def test_canonical_seed_is_valid(self):
        self.assertEqual(validate_expansion(self.a, self.e), [])

    def test_global_ids_must_be_unique(self):
        self.e["claims"][0]["id"] = "NPC-001"
        self.assert_rejects("Duplicate ID across")

    def test_every_species_must_have_one_core(self):
        self.a["species"][0]["core_ability_id"] = "ABI-999"
        self.assert_rejects("missing core domain")

    def test_beastfolk_personhood_cannot_be_erased_by_type(self):
        rauka = next(x for x in self.a["entities"] if x["id"] == "NPC-009")
        rauka["type"] = "animal"
        rauka["sapient"] = False
        self.assert_rejects("classifies sapient species as animal")

    def test_animal_predation_cannot_be_criminalized_in_fact_register(self):
        predation = next(x for x in self.e["cases"] if x["id"] == "CASE-004")
        predation["assessment"] = "deliberate_abuse"
        self.assert_rejects("wrongly criminalizes nonsapient predator")

    def test_veiled_consciousness_cannot_use_surface_anchor(self):
        archivist = next(x for x in self.a["entities"] if x["id"] == "ENT-001")
        archivist["anchor_location_id"] = "LOC-008"
        self.assert_rejects("invented physical position")

    def test_coercive_rite_cannot_be_reclassified_as_benign(self):
        victim = next(x for x in self.e["cases"] if x["id"] == "CASE-003")
        victim["assessment"] = "contested"
        self.assert_rejects("failed to classify intentional coercion")

    def test_missing_evidence_reference_is_rejected(self):
        self.e["taboos"][0]["evidence_event_ids"] = ["EVT-999"]
        self.assert_rejects("missing evidence event")

    def test_law_cannot_precede_its_event(self):
        self.e["laws"][0]["enacted_year"] = 28860
        self.assert_rejects("conflicts with dated enactment")

    def test_rumor_must_not_become_objective_fact(self):
        self.e["claims"][0]["provenance"] = "authored_fact"
        self.assert_rejects("mislabels belief")

    def test_no_route_can_be_shorter_than_geometric_distance(self):
        route = next(x for x in self.a["routes"] if x["id"] == "RTE-015")
        route["distance_km"] = 1.0
        self.assert_rejects("Short route")

    def test_cause_must_precede_effect(self):
        event = next(x for x in self.a["events"] if x["id"] == "EVT-030")
        event["cause_event_ids"] = ["EVT-039"]
        self.assert_rejects("Missing/nonpreceding cause")

    def test_dead_person_cannot_participate_centuries_later(self):
        event = next(x for x in self.a["events"] if x["id"] == "EVT-036")
        event["participants"].append("NPC-007")
        self.assert_rejects("Deceased participant")

    def test_extra_core_domain_is_not_allowed(self):
        e = next(x for x in self.a["entities"] if x["id"] == "NPC-008")
        e["core_ability_id"] = ["ABI-006", "ABI-007"]
        self.assert_rejects("Invalid/missing core ability")

    def test_unlock_requires_matching_single_core_domain(self):
        e = next(x for x in self.a["entities"] if x["id"] == "NPC-008")
        e["unlocks"][1]["sub_ability_id"] = "SUB-018"
        self.assert_rejects("Wrong ability branch")


if __name__ == "__main__":
    unittest.main()
