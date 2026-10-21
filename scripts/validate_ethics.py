#!/usr/bin/env python3
"""Validate dark-world expansion, cross-file morality records, chronology and agency."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_world import validate  # noqa: E402

ATLAS = ROOT / "data" / "world" / "atlas.json"
ETHICS = ROOT / "data" / "world" / "ethics.json"


def validate_expansion(atlas: dict, ethics: dict) -> list[str]:
    """Return integrity failures; do not mutate input records."""
    problems = validate(atlas)

    def check(ok: bool, message: str) -> None:
        if not ok:
            problems.append(message)

    groups = ["frames", "layers", "eras", "ability_domains", "sub_abilities",
              "locations", "entities", "routes", "events", "relations", "species"]
    ethical_groups = ["laws", "taboos", "claims", "cases"]
    records = [atlas["world"]]
    records.extend(obj for group in groups for obj in atlas[group])
    records.extend(obj for group in ethical_groups for obj in ethics[group])
    ids = [r["id"] for r in records]
    check(len(ids) == len(set(ids)), "Duplicate ID across atlas + ethics")
    by_id = {r["id"]: r for r in records}
    domain_ids = {r["id"] for r in atlas["ability_domains"]}
    event_map = {r["id"]: r for r in atlas["events"]}
    species_map = {r["id"]: r for r in atlas["species"]}
    location_map = {r["id"]: r for r in atlas["locations"]}
    eras = atlas["eras"]

    check(ethics["world_id"] == atlas["world"]["id"], "Ethics belongs to wrong world")
    check(ethics["schema_version"] == 1, "Unsupported ethics schema")
    check(atlas["clock"]["paused"] is True, "Seed should not claim to be running")
    clock_key = (atlas["clock"]["year"], atlas["clock"]["day_of_year"], atlas["clock"]["minute_of_day"])

    for species in atlas["species"]:
        check(species.get("core_ability_id") in domain_ids, f"Species {species['id']} missing core domain")
        check(isinstance(species.get("sapient"), bool), f"Species {species['id']} missing sapience flag")
        for habitat in species["habitats"]:
            check(habitat in location_map, f"Species {species['id']} references unknown habitat")

    for entity in atlas["entities"]:
        if entity.get("species_id"):
            check(entity["species_id"] in species_map, f"{entity['id']} unknown species")
        if entity["type"] == "animal":
            check(entity.get("sapient") is False, f"{entity['id']} animal must explicitly be nonsapient")
            if entity.get("species_id") in species_map:
                check(species_map[entity["species_id"]]["sapient"] is False,
                      f"{entity['id']} classifies sapient species as animal")
        if entity["type"] == "person" and entity.get("species_id") in species_map:
            check(species_map[entity["species_id"]]["sapient"] is True,
                  f"{entity['id']} person assigned nonsapient species")
        if entity["type"] == "veiled_consciousness":
            check(entity["layer_id"] == "LYR-004", f"{entity['id']} not in Veil")
            check(entity.get("anchor_location_id") is None,
                  f"{entity['id']} has invented physical position in Veil")
        if "born_year" in entity and "died_year" in entity:
            check(entity["born_year"] < entity["died_year"] <= atlas["clock"]["year"],
                  f"{entity['id']} invalid lifespan")
        if "founded_year" in entity:
            check(entity["founded_year"] <= atlas["clock"]["year"],
                  f"{entity['id']} founding lies in future")

    def timestamp(event: dict) -> tuple[int, int, int]:
        when = event["when"]
        return when["year"], when["day_of_year"], when["minute_of_day"]

    last_time = (-1, -1, -1)
    for event in atlas["events"]:
        now = timestamp(event)
        check(now >= last_time, f"Events out of chronological order: {event['id']}")
        last_time = now
        check(now <= clock_key, f"Event takes place after paused snapshot: {event['id']}")
        check(0 <= now[2] < 1440, f"Event minute invalid: {event['id']}")
        for parent_id in event["cause_event_ids"]:
            if parent_id in event_map:
                check(timestamp(event_map[parent_id]) < now,
                      f"Cause must precede effect: {event['id']}")
        for participant_id in event["participants"]:
            participant = by_id.get(participant_id)
            if participant:
                start = participant.get("born_year", participant.get("founded_year",
                        participant.get("manifest_year")))
                end = participant.get("died_year")
                if start is not None:
                    check(start <= now[0], f"Participant not yet existing: {event['id']} {participant_id}")
                if end is not None:
                    check(now[0] <= end, f"Deceased participant in event: {event['id']} {participant_id}")

    for relation in atlas["relations"]:
        check(relation["since_year"] <= atlas["clock"]["year"],
              f"Future relation {relation['id']}")
        for endpoint_id in (relation["from_id"], relation["to_id"]):
            endpoint = by_id.get(endpoint_id)
            if endpoint:
                effective = endpoint.get("born_year", endpoint.get("founded_year",
                            endpoint.get("manifest_year")))
                if effective is not None:
                    check(effective <= relation["since_year"],
                          f"Relation predates existence: {relation['id']} {endpoint_id}")
                if "died_year" in endpoint:
                    check(relation["since_year"] <= endpoint["died_year"],
                          f"Relation formed after death: {relation['id']} {endpoint_id}")

    for law in ethics["laws"]:
        check(law["jurisdiction_id"] in by_id, f"Law {law['id']} unknown jurisdiction")
        event = event_map.get(law["enacted_event_id"])
        check(event is not None, f"Law {law['id']} has no enacted event")
        if event:
            check(event["when"]["year"] == law["enacted_year"] and
                  event["kind"] in {"legislation", "conservation", "founding"},
                  f"Law {law['id']} conflicts with dated enactment")

    valid_tabs = {"protective_prohibition", "ecological_prohibition", "discriminatory_custom",
                  "bodily_autonomy", "dangerous_rite", "cultural_dietary_custom"}
    for taboo in ethics["taboos"]:
        check(taboo["category"] in valid_tabs, f"Taboo {taboo['id']} unknown category")
        for holder in taboo["held_by"]:
            check(holder in by_id, f"Taboo {taboo['id']} unknown culture/holder {holder}")
        for evt in taboo["evidence_event_ids"]:
            check(evt in event_map, f"Taboo {taboo['id']} missing evidence event {evt}")

    for claim in ethics["claims"]:
        check(claim["provenance"] in {"character_belief", "rumor"},
              f"Claim {claim['id']} mislabels belief as objective fact")
        check(claim["truth_status"] in {"contradicted_by_canon", "false_as_stated",
              "unsupported", "unresolved", "corroborated"}, f"Claim {claim['id']} unknown truth status")
        for owner in claim["holder_entity_ids"]:
            check(owner in by_id, f"Claim {claim['id']} unknown holder {owner}")
        for evt in claim["associated_event_ids"]:
            check(evt in event_map, f"Claim {claim['id']} unknown event {evt}")

    permitted_assessments = {"deliberate_abuse", "lawful_but_potentially_unjust",
                            "non_moral_predation", "protection", "contested"}
    for case in ethics["cases"]:
        event = event_map.get(case["event_id"])
        check(event is not None, f"Case {case['id']} references missing event")
        check(case["assessment"] in permitted_assessments,
              f"Case {case['id']} unknown assessment")
        for actor in case["actor_ids"]:
            check(actor in by_id, f"Case {case['id']} actor missing")
            if event:
                check(actor in event["participants"], f"Case {case['id']} actor absent from event")
        for target in case["affected_entity_ids"]:
            check(target in by_id, f"Case {case['id']} target missing")
        nonsapient_actors = [x for x in case["actor_ids"]
                             if x in by_id and by_id[x].get("type") == "animal" and
                             by_id[x].get("sapient") is False]
        if nonsapient_actors:
            check(case["assessment"] == "non_moral_predation",
                  f"Case {case['id']} wrongly criminalizes nonsapient predator")
        if case["consent"] == "coerced":
            check(case["assessment"] == "deliberate_abuse",
                  f"Case {case['id']} failed to classify intentional coercion")

    check(ethics["constraints"]["species_never_implies_alignment"] is True,
          "A species may not carry innate moral alignment")
    check(ethics["constraints"]["sexual_content_involving_animals"] is False,
          "Animal-related sexual content is excluded from the world specification")
    check(ethics["constraints"]["no_scalar_evil_alignment"] is True,
          "Universal scalar evil alignment violates canon")
    return problems


def main() -> int:
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    ethics = json.loads(ETHICS.read_text(encoding="utf-8"))
    errors = validate_expansion(atlas, ethics)
    if errors:
        for error in errors:
            print("FAIL:", error)
        print(f"FAILED: {len(errors)} world and ethics integrity issues")
        return 1
    print(f"PASS: {len(atlas['locations'])} locations, {len(atlas['entities'])} entities, "
          f"{len(atlas['species'])} species, {len(atlas['events'])} events, "
          f"{len(ethics['laws'])} laws, {len(ethics['taboos'])} taboos, "
          f"{len(ethics['cases'])} moral cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
