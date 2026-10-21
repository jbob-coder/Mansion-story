"""Protect recorded human dominance and cross-registry world integrity."""
import copy
import json
import unittest
from pathlib import Path

from scripts.validate_civilization import validate_civilization

ROOT = Path(__file__).resolve().parents[1] / "data/world"
FILES = {
    stem: json.loads((ROOT / f"{stem}.json").read_text(encoding="utf-8"))
    for stem in ("atlas", "ethics", "civilization", "system_catalog")
}


class CivilizationChecks(unittest.TestCase):
    def setUp(self):
        self.a = copy.deepcopy(FILES["atlas"])
        self.e = copy.deepcopy(FILES["ethics"])
        self.c = copy.deepcopy(FILES["civilization"])
        self.s = copy.deepcopy(FILES["system_catalog"])

    def issues(self):
        return validate_civilization(self.a, self.e, self.c, self.s)

    def rejects(self, substring):
        errors = self.issues()
        self.assertTrue(any(substring in e for e in errors), errors)

    def test_seed_consistent(self):
        self.assertEqual(self.issues(), [])

    def test_humans_are_sapient(self):
        next(x for x in self.a["species"] if x["id"] == "SPC-005")["sapient"] = False
        self.rejects("Human biological register")

    def test_all_people_have_species(self):
        next(x for x in self.a["entities"] if x["id"] == "NPC-001").pop("species_id")
        self.rejects("missing or invalid species")

    def test_demographic_subtotals_balanced(self):
        self.c["demographics"][0]["species_estimates"]["SPC-005"] += 1
        self.rejects("Population subtotal mismatch")

    def test_human_share_cannot_be_claimed_without_accurate_math(self):
        self.c["human_predominance"]["observed_sample_human_share_percent"] = 93.2
        self.rejects("Human demographic percentage mismatch")

    def test_majority_must_stay_human_in_documented_sample(self):
        row = self.c["demographics"][0]
        row["species_estimates"]["SPC-005"] = 0
        row["species_estimates"]["SPC-006"] += 44000
        self.rejects("Humans are not majority")

    def test_cannot_claim_full_global_population(self):
        self.c["human_predominance"]["scope"] = "every_continent_and_realm"
        self.rejects("Do not claim unobserved globe-wide census")

    def test_unknown_ore_production_rejected(self):
        self.c["industries"][0]["resource_id"] = "RES-999"
        self.rejects("Unknown production output")

    def test_negative_material_output_rejected(self):
        self.c["industries"][0]["baseline_output_quantity"] = -9
        self.rejects("Negative production capacity")

    def test_route_segments_must_connect(self):
        self.c["trade"][0]["route_ids"] = ["RTE-011"]
        self.rejects("disconnected segment")

    def test_trade_path_must_arrive(self):
        self.c["trade"][0]["route_ids"] = ["RTE-019"]
        self.rejects("does not end at destination")

    def test_bad_species_habitat_rejected(self):
        self.a["species"][-1]["habitats"] = ["LOC-999"]
        self.rejects("references unknown habitat")

    def test_culture_cannot_reference_unmapped_settlement(self):
        self.c["cultures"][0]["associated_settlement_ids"] = ["SET-999"]
        self.rejects("unknown settlement")

    def test_ancient_faith_must_stay_belief_not_world_fact(self):
        self.c["faiths"][0]["ontology"] = "objectively_proven_god"
        self.rejects("promotes beliefs")

    def test_skills_are_not_all_implemented_because_documented(self):
        self.s["systems"][0]["simulation_runtime"] = "fully_implemented"
        self.rejects("unjustified running implementation")

    def test_global_ids_cannot_be_reused(self):
        self.c["resources"][0]["id"] = "NPC-001"
        self.rejects("Duplicate global registry ID")

    def test_ecosystem_species_must_exist(self):
        self.c["ecosystems"][0]["species_ids"].append("SPC-999")
        self.rejects("unknown species")

    def test_stocks_and_trade_are_not_simulated_yet(self):
        self.c["trade"][0]["volumes"] = 12345
        self.rejects("invents market volume")


if __name__ == "__main__":
    unittest.main()
