#!/usr/bin/env python3
"""Validate human predominance, civilization economy and comprehensive system catalog.

Narrative records and estimates do not imply a running simulation.
Only built-in Python dependencies are required.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_ethics import validate_expansion  # noqa: E402

DATA = ROOT / "data/world"


def validate_civilization(atlas: dict, ethics: dict, civ: dict, catalog: dict) -> list[str]:
    issues = list(validate_expansion(atlas, ethics))

    def check(condition: bool, message: str) -> None:
        if not condition:
            issues.append(message)

    ids: set[str] = set()
    groups = ("frames", "layers", "eras", "ability_domains", "sub_abilities",
              "locations", "entities", "routes", "events", "relations", "species")
    ethics_groups = ("laws", "taboos", "claims", "cases")
    civil_groups = ("demographics", "resources", "industries", "trade", "cultures",
                    "faiths", "social_roles", "occupations", "ecosystems", "technologies")
    all_entries = [atlas["world"], *[r for g in groups for r in atlas[g]],
                   *[r for g in ethics_groups for r in ethics[g]],
                   *[civ["human_predominance"]],
                   *[r for g in civil_groups for r in civ[g]],
                   *catalog["systems"], *catalog["delivery_phases"]]
    for obj in all_entries:
        identity = obj["id"]
        check(identity not in ids, f"Duplicate global registry ID {identity}")
        ids.add(identity)

    check(civ["schema_version"] == 1 and catalog["schema_version"] == 1,
          "Unsupported civil or catalog schema")
    check(civ["world_id"] == atlas["world"]["id"] == catalog["world_id"],
          "World ID mismatch across registries")
    clock = atlas["clock"]
    check(civ["reference_time"] == {
        "year": clock["year"], "day_of_year": clock["day_of_year"],
        "minute_of_day": clock["minute_of_day"]
    }, "Demographic reference time must match world snapshot")

    people = [x for x in atlas["entities"] if x["type"] == "person"]
    species = {sp["id"]: sp for sp in atlas["species"]}
    for person in people:
        spid = person.get("species_id")
        check(spid in species, f"Person {person['id']} missing or invalid species")
        if spid in species:
            check(species[spid]["sapient"] is True, f"Person {person['id']} assigned nonsapient species")
        check(isinstance(person["core_ability_id"], str),
              f"Person {person['id']} has non-scalar First Thread")
    for animal in (e for e in atlas["entities"] if e["type"] == "animal"):
        check(animal.get("species_id") in species, f"Animal {animal['id']} missing species")
    check("SPC-005" in species and species["SPC-005"]["name"] == "Human"
          and species["SPC-005"]["sapient"] is True, "Human biological register missing")

    d = civ["human_predominance"]
    check(d["species_id"] == "SPC-005", "Dominant species must be human")
    check(d["scope"] == "known_documented_inhabited_world", "Do not claim unobserved globe-wide census")
    check(d["status"] == "authored_canon" and d["provenance"] == "authored_estimate",
          "Demographic assertions must retain authored provenance")

    used: set[str] = set()
    species_totals: dict[str, int] = {}
    total = 0
    for record in civ["demographics"]:
        sid = record["settlement_id"]
        check(sid in ids, f"Population row {record['id']} missing settlement")
        settlement = next((e for e in atlas["entities"] if e["id"] == sid), None)
        check(settlement is not None and settlement["type"] == "settlement",
              f"Population row {record['id']} is not a settlement")
        check(sid not in used, f"Duplicate population settlement {sid}")
        used.add(sid)
        check(record["provenance"] == "authored_estimate", f"Row {record['id']} falsely claims observed census")
        total_population = record["total_estimate"]
        check(isinstance(total_population, int) and total_population >= 0,
              f"Invalid total population in {record['id']}")
        summation = 0
        for spid, count in record["species_estimates"].items():
            check(spid in species and species[spid]["sapient"], f"Invalid demographic species {spid}")
            check(type(count) is int and count >= 0, f"Invalid species count {record['id']}:{spid}")
            summation += count
            species_totals[spid] = species_totals.get(spid, 0) + count
        check(summation == total_population, f"Population subtotal mismatch in {record['id']}")
        total += total_population
    humans = species_totals.get("SPC-005", 0)
    check(total > 0 and 2 * humans > total, "Humans are not majority of surveyed sample")
    check(humans > max([0, *[value for sid, value in species_totals.items() if sid != "SPC-005"]]),
          "Humans are not largest surveyed sapient population")
    check(d["authored_sample_total"] == total, "Dominance sample total mismatch")
    check(d["authored_sample_humans"] == humans, "Dominance human total mismatch")
    if total:
        check(math.isclose(d["authored_sample_human_share_percent"], round(humans * 100 / total, 2),
                           abs_tol=0.005), "Human demographic percentage mismatch")

    res = {r["id"]: r for r in civ["resources"]}
    location_by_id = {l["id"]: l for l in atlas["locations"]}
    entity_by_id = {e["id"]: e for e in atlas["entities"]}
    route_by_id = {r["id"]: r for r in atlas["routes"]}
    events = {e["id"]: e for e in atlas["events"]}

    for industry in civ["industries"]:
        check(industry["site_entity_id"] in entity_by_id, f"Unknown production site {industry['id']}")
        check(industry["resource_id"] in res, f"Unknown production output {industry['id']}")
        for rid in industry["input_resource_ids"]:
            check(rid in res, f"Unknown production input {industry['id']}:{rid}")
        check(isinstance(industry["baseline_output_quantity"], (int, float))
              and industry["baseline_output_quantity"] >= 0,
              f"Negative production capacity {industry['id']}")
        check(industry["production_runtime"] == "not_implemented",
              f"Industry {industry['id']} falsely claims simulated production")
        check(industry["provenance"] == "authored_capacity_estimate",
              f"Industry {industry['id']} has invalid provenance")
    for link in civ["trade"]:
        check(link["resource_id"] in res, f"Missing trade material {link['id']}")
        start = entity_by_id.get(link["from_entity_id"])
        end = entity_by_id.get(link["to_entity_id"])
        check(start is not None and end is not None, f"Trade {link['id']} unknown endpoint")
        if not start or not end:
            continue
        current = start["anchor_location_id"]
        check(bool(link["route_ids"]), f"Trade {link['id']} has no physical route")
        for rid in link["route_ids"]:
            route = route_by_id.get(rid)
            check(route is not None, f"Trade {link['id']} uses unknown route {rid}")
            if not route:
                continue
            check(current in (route["from_id"], route["to_id"]),
                  f"Trade {link['id']} has disconnected segment {rid}")
            if current in (route["from_id"], route["to_id"]):
                current = route["to_id"] if current == route["from_id"] else route["from_id"]
        check(current == end["anchor_location_id"], f"Trade {link['id']} does not end at destination")
        check(link["volumes"] == "unknown_not_simulated",
              f"Trade {link['id']} invents market volume")

    for culture in civ["cultures"]:
        check(culture["majority_species_id"] in species and
              species[culture["majority_species_id"]]["sapient"], f"Culture {culture['id']} wrong species")
        for x in culture["associated_settlement_ids"]:
            check(x in entity_by_id and entity_by_id[x]["type"] == "settlement",
                  f"Culture {culture['id']} unknown settlement {x}")
    for faith in civ["faiths"]:
        check(faith["center_entity_id"] in ids, f"Faith {faith['id']} has unknown center")
        if faith["principal_organization_id"] is not None:
            check(faith["principal_organization_id"] in ids, f"Faith {faith['id']} unknown institution")
        check(faith["origin_event_id"] in events, f"Faith {faith['id']} unknown founding event")
        check(faith["ontology"] == "cultural_belief_not_proven_cosmology",
              f"Faith {faith['id']} promotes beliefs to absolute reality")
    for role in civ["social_roles"]:
        check(role["authority_id"] in ids, f"Social role {role['id']} unknown authority")
    for occupation in civ["occupations"]:
        for rid in occupation["resource_ids"]:
            check(rid in res, f"Occupation {occupation['id']} missing resource {rid}")
        for site in occupation["possible_sites"]:
            check(site in entity_by_id, f"Occupation {occupation['id']} unknown site {site}")
    for eco in civ["ecosystems"]:
        for spid in eco["species_ids"]:
            check(spid in species, f"Ecology {eco['id']} unknown species {spid}")
        for lid in eco["location_ids"]:
            check(lid in location_by_id, f"Ecology {eco['id']} unknown location {lid}")
        check(eco["simulation_status"] == "not_implemented",
              f"Ecology {eco['id']} falsely reports an operating simulation")
    for tech in civ["technologies"]:
        for rid in tech["resource_ids"]:
            check(rid in res, f"Technology {tech['id']} unknown material {rid}")

    allowed_status = {"registry_or_canon_defined", "design_outlined"}
    check(len(catalog["systems"]) >= 40, "Incomplete initial systems inventory")
    for system in catalog["systems"]:
        check(system["canon_status"] in allowed_status, f"Bad documentation status {system['id']}")
        check(system["simulation_runtime"] == "not_implemented",
              f"System {system['id']} claims unjustified running implementation")
    return issues


def main() -> int:
    records = {stem: json.loads((DATA / f"{stem}.json").read_text(encoding="utf-8"))
               for stem in ("atlas", "ethics", "civilization", "system_catalog")}
    failures = validate_civilization(
        records["atlas"], records["ethics"], records["civilization"], records["system_catalog"]
    )
    if failures:
        for issue in failures:
            print("FAIL:", issue)
        print(f"FAIL: {len(failures)} integrity error(s)")
        return 1
    civ = records["civilization"]
    print(f"PASS: {len(civ['demographics'])} demographic areas, "
          f"{civ['human_predominance']['authored_sample_humans']} human residents "
          f"among {civ['human_predominance']['authored_sample_total']} sample residents, "
          f"{len(records['system_catalog']['systems'])} cataloged systems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
