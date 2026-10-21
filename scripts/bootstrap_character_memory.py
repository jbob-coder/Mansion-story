#!/usr/bin/env python3
"""Initialize a local save's character memories from the authored atlas.

Examples:
    python scripts/bootstrap_character_memory.py --validate
    python scripts/bootstrap_character_memory.py --db saves/campaign_01/memory.sqlite

The second command writes a *local save*, not world canon. A live game must
call MemoryStore.remember when characters actually perceive or learn things.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine.character_memory import MemoryStore, WorldTime  # noqa: E402

DATA = ROOT / "data" / "world"


def read_seed() -> tuple[dict, dict]:
    atlas = json.loads((DATA / "atlas.json").read_text(encoding="utf-8"))
    profiles = json.loads((DATA / "character_cognition.json").read_text(encoding="utf-8"))
    return atlas, profiles


def validate_profiles(atlas: dict, config: dict) -> list[str]:
    errors: list[str] = []
    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(config["schema_version"] == 1, "Unsupported cognition schema")
    check(config["world_id"] == atlas["world"]["id"], "Wrong world")
    check(config["clock_snapshot"] == atlas["clock"], "Clock snapshot differs from atlas")
    seed_actors = {
        e["id"]: e for e in atlas["entities"]
        if e["type"] in {"person", "animal", "veiled_consciousness"}
    }
    ids = [p["actor_id"] for p in config["profiles"]]
    check(len(ids) == len(set(ids)), "Duplicate cognition actor")
    check(set(ids) == set(seed_actors), "Cognition profiles must cover all character IDs")
    for p in config["profiles"]:
        actor = seed_actors.get(p["actor_id"])
        if not actor:
            continue
        check(p["name"] == actor["name"], f"Name mismatch: {p['actor_id']}")
        check(p["kind"] == actor["type"], f"Kind mismatch: {p['actor_id']}")
        check(type(p["intelligence"]) is int and 0 <= p["intelligence"] <= 100,
              f"Invalid intelligence: {p['actor_id']}")
        dead = actor.get("died_year") is not None and actor["died_year"] <= atlas["clock"]["year"]
        check(p["alive"] is (not dead), f"Death mismatch: {p['actor_id']}")
        check(p["bootstrap_kind"] in {"semantic", "instinctive", "magical"},
              f"Invalid memory kind: {p['actor_id']}")
        check(bool(p["bootstrap_background"].strip()), f"Empty initial background: {p['actor_id']}")
    return errors


def bootstrap(db_path: str | Path) -> dict[str, int]:
    atlas, data = read_seed()
    errors = validate_profiles(atlas, data)
    if errors:
        raise ValueError("Cognition profile problems: " + "; ".join(errors))
    clock = atlas["clock"]
    now = WorldTime(clock["year"], clock["day_of_year"], clock["minute_of_day"])
    registered, backgrounds = 0, 0
    with MemoryStore(db_path) as memory:
        for p in data["profiles"]:
            memory.register(p["actor_id"], p["intelligence"], kind=p["kind"], alive=p["alive"])
            registered += 1
            if not p["alive"]:
                continue
            # One authored starting-familiarity record; no fabricated game action
            # or invented awareness of objective secrets.
            if any("starting_background" in h["tags"] for h in memory.history(p["actor_id"])):
                continue
            memory.remember(
                p["actor_id"], p["bootstrap_background"], learned_at=now,
                kind=p["bootstrap_kind"], source_type="background",
                tags=("starting_background", "identity"),
                salience=0.95, confidence=0.95
            )
            backgrounds += 1
    return {"registered": registered, "new_starting_backgrounds": backgrounds}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, help="save-scoped SQLite memory file")
    parser.add_argument("--validate", action="store_true", help="validate seed without writing a save")
    args = parser.parse_args()
    if not args.validate and args.db is None:
        parser.error("Use --db PATH to create a save, or --validate to inspect profiles")
    atlas, data = read_seed()
    errors = validate_profiles(atlas, data)
    if errors:
        for issue in errors:
            print("FAIL:", issue)
        return 1
    print(f"PASS: cognition seed defines {len(data['profiles'])} known characters")
    if args.validate:
        return 0
    result = bootstrap(args.db)
    print(f"Registered {result['registered']} actors; "
          f"{result['new_starting_backgrounds']} new starting-familiarity memories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
