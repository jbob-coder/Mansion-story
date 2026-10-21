#!/usr/bin/env python3
"""Validate the Eirenfall world atlas with the Python standard library."""
import json
import math
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1] / "data" / "world" / "atlas.json"

def validate(a):
    failures = []
    def check(ok, message):
        if not ok:
            failures.append(message)
    groups = ["frames","layers","eras","ability_domains","sub_abilities","locations",
              "entities","routes","events","relations"]
    objects = [a["world"]] + [v for g in groups for v in a[g]]
    ids = [o["id"] for o in objects]
    check(len(ids) == len(set(ids)), "Duplicate global IDs")
    by_id = {o["id"]: o for o in objects}
    abilities = {o["id"] for o in a["ability_domains"]}
    sub = {o["id"]: o for o in a["sub_abilities"]}
    places = {o["id"]: o for o in a["locations"]}
    events = {o["id"]: o for o in a["events"]}
    for obj in [a["world"], *a["layers"], *a["locations"], *a["entities"]]:
        check(obj.get("core_ability_id") in abilities, "Invalid/missing core ability: " + obj["id"])
    for obj in a["entities"]:
        check(obj.get("anchor_location_id") in places, "Unmapped anchor: " + obj["id"])
    for loc in a["locations"]:
        check(loc["frame_id"] in by_id, "Unknown coordinate frame: " + loc["id"])
        for axis in ("x_km","y_km","z_m"):
            check(isinstance(loc["position"].get(axis), (int, float)) and
                  math.isfinite(loc["position"][axis]), "Invalid coordinate: " + loc["id"])
    for r in a["routes"]:
        p, q = places.get(r["from_id"]), places.get(r["to_id"])
        check(bool(p and q), "Unknown route endpoint: " + r["id"])
        if p and q:
            dx = p["position"]["x_km"] - q["position"]["x_km"]
            dy = p["position"]["y_km"] - q["position"]["y_km"]
            dz = (p["position"]["z_m"] - q["position"]["z_m"]) / 1000
            check(p["frame_id"] == q["frame_id"], "Mixed chart route: " + r["id"])
            check(r["distance_km"] + 1e-9 >= math.hypot(dx,dy,dz), "Short route: " + r["id"])
    for s in a["sub_abilities"]:
        check(s["domain_id"] in abilities, "Unknown domain: " + s["id"])
        for pre in s["prerequisite_ids"]:
            check(pre in sub and sub[pre]["domain_id"] == s["domain_id"],
                  "Invalid prerequisite: " + s["id"])
    for e in a["events"]:
        check(e["provenance"] in {"authored_fact","observed_simulation","character_belief","rumor"},
              "Invalid provenance: " + e["id"])
        check(1 <= e["when"]["day_of_year"] <= 360, "Invalid day: " + e["id"])
        check(all(p in by_id for p in e["participants"]), "Unknown participant: " + e["id"])
        check(not e["location_id"] or e["location_id"] in places, "Unknown event location: " + e["id"])
        for predecessor in e["cause_event_ids"]:
            check(predecessor in events and
                  events[predecessor]["when"]["year"] < e["when"]["year"],
                  "Missing/nonpreceding cause: " + e["id"])
    for person in (x for x in a["entities"] if x["type"] == "person"):
        acquired = set()
        for u in person["unlocks"]:
            s = sub.get(u["sub_ability_id"])
            e = events.get(u["event_id"])
            check(bool(s and s["domain_id"] == person["core_ability_id"]),
                  "Wrong ability branch: " + person["id"])
            check(bool(e and e.get("sub_ability_id") == u["sub_ability_id"] and
                  person["id"] in e["participants"] and e["when"]["year"] >= person["born_year"]),
                  "Unverified unlock: " + person["id"])
            if s:
                check(set(s["prerequisite_ids"]).issubset(acquired),
                      "Unmet unlock prerequisites: " + person["id"])
            acquired.add(u["sub_ability_id"])
    es = sorted(a["eras"], key=lambda x: x["start_year"])
    check(es[0]["start_year"] == 0, "First era must start at 0")
    for prev, nxt in zip(es, es[1:]):
        check(prev["end_year"] + 1 == nxt["start_year"], "Era gap/overlap")
    check(es[-1]["end_year"] is None and es[-1]["start_year"] <= a["clock"]["year"],
          "Final era doesn't include snapshot")
    for rel in a["relations"]:
        check(rel["from_id"] in by_id and rel["to_id"] in by_id, "Invalid relation: " + rel["id"])
    return failures

if __name__ == "__main__":
    archive = json.loads(ATLAS.read_text(encoding="utf-8"))
    problems = validate(archive)
    for problem in problems:
        print("FAIL: " + problem)
    if problems:
        raise SystemExit(1)
    print("PASS: {} locations, {} entities, {} events, {} routes".format(
        len(archive["locations"]),len(archive["entities"]),len(archive["events"]),len(archive["routes"])))
