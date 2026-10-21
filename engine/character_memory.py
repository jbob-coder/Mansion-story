"""Durable, bounded-rationality character memory for Eirenfall.

Standard-library SQLite storage. This module persists experiences; it does not
implement perception, AI decision-making, NPC movement, or a real-time world tick.
All dates are *in-world* moments, never host wall-clock time.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sqlite3

DAYS_PER_YEAR = 360
MINUTES_PER_DAY = 1440
ALLOWED_KINDS = frozenset({
    "episodic", "semantic", "social", "spatial", "procedural",
    "instinctive", "magical"
})
ALLOWED_SOURCES = frozenset({
    "direct", "heard", "learned", "inferred", "dream", "instinct", "background"
})
ALLOWED_ACTORS = frozenset({"person", "animal", "veiled_consciousness"})
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True, order=True)
class WorldTime:
    year: int
    day_of_year: int
    minute_of_day: int

    def __post_init__(self) -> None:
        for field in ("year", "day_of_year", "minute_of_day"):
            value = getattr(self, field)
            if type(value) is not int:
                raise TypeError(f"{field} must be integer")
        if self.year < 0 or not 1 <= self.day_of_year <= DAYS_PER_YEAR:
            raise ValueError("Invalid world year/day")
        if not 0 <= self.minute_of_day < MINUTES_PER_DAY:
            raise ValueError("Invalid minute of day")

    @property
    def minute(self) -> int:
        return ((self.year * DAYS_PER_YEAR + self.day_of_year - 1) *
                MINUTES_PER_DAY + self.minute_of_day)


def _valid_unit(name: str, value: float) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return float(value)


def _valid_intelligence(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 100:
        raise ValueError("Intelligence must be an integer from 0 to 100")
    return value


def _tokens(text: str) -> set[str]:
    return {s.casefold() for s in TOKEN_RE.findall(text)}


class MemoryStore:
    """Per-character permanent experience archive with fallible recall.

    A character can forget or revise an experience without deleting it from the
    SQLite archive. Public lookups always enforce the character's own actor ID.
    """

    def __init__(self, db_path: str | Path):
        self.path = str(db_path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA busy_timeout = 10000")
        if self.path != ":memory:":
            self.db.execute("PRAGMA journal_mode = WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS character (
                actor_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL CHECK(kind IN ('person','animal','veiled_consciousness')),
                intelligence INTEGER NOT NULL CHECK(intelligence BETWEEN 0 AND 100),
                alive INTEGER NOT NULL DEFAULT 1 CHECK(alive IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS stat_changes (
                change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT NOT NULL REFERENCES character(actor_id),
                at_minute INTEGER NOT NULL,
                old_intelligence INTEGER NOT NULL,
                new_intelligence INTEGER NOT NULL,
                reason TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS experience (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT NOT NULL REFERENCES character(actor_id),
                learned_minute INTEGER NOT NULL,
                occurred_minute INTEGER NOT NULL,
                kind TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_actor_id TEXT,
                world_event_id TEXT,
                location_id TEXT,
                description TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
                salience REAL NOT NULL CHECK(salience BETWEEN 0 AND 1),
                emotion REAL NOT NULL CHECK(emotion BETWEEN 0 AND 1),
                encoding REAL NOT NULL CHECK(encoding BETWEEN 0 AND 1),
                supersedes_id INTEGER REFERENCES experience(memory_id),
                CHECK(occurred_minute <= learned_minute)
            );
            CREATE INDEX IF NOT EXISTS exp_actor_time
                ON experience(actor_id, learned_minute DESC);
            CREATE INDEX IF NOT EXISTS exp_actor_kind
                ON experience(actor_id, kind);
            CREATE INDEX IF NOT EXISTS exp_supersedes ON experience(supersedes_id);
            CREATE TABLE IF NOT EXISTS rehearsal (
                rehearsal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT NOT NULL REFERENCES character(actor_id),
                memory_id INTEGER NOT NULL REFERENCES experience(memory_id),
                at_minute INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS rehearse_actor ON rehearsal(actor_id, memory_id, at_minute);
        """)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def register(self, actor_id: str, intelligence: int, *,
                 kind: str = "person", alive: bool = True) -> None:
        """Register an actor once. Re-running a seed never resets changed stats."""
        _valid_intelligence(intelligence)
        if kind not in ALLOWED_ACTORS or not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("Invalid actor identity/kind")
        if type(alive) is not bool:
            raise ValueError("alive must be boolean")
        old = self.db.execute(
            "SELECT kind, intelligence, alive FROM character WHERE actor_id=?", (actor_id,)
        ).fetchone()
        if old is not None:
            if old["kind"] != kind:
                raise ValueError("Actor type mismatch; cannot change identity")
            return  # Existing saves outrank seed stat defaults.
        with self.db:
            self.db.execute(
                "INSERT INTO character(actor_id,kind,intelligence,alive) VALUES(?,?,?,?)",
                (actor_id, kind, intelligence, int(alive))
            )

    def actor(self, actor_id: str) -> dict:
        row = self.db.execute("SELECT * FROM character WHERE actor_id=?", (actor_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown character {actor_id}")
        return dict(row)

    def set_intelligence(self, actor_id: str, intelligence: int, when: WorldTime,
                         reason: str) -> None:
        """Change current intelligence with append-only evidence of the change."""
        _valid_intelligence(intelligence)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("A stat change requires a reason")
        old = self.actor(actor_id)
        last = self.db.execute(
            "SELECT MAX(at_minute) AS t FROM stat_changes WHERE actor_id=?", (actor_id,)
        ).fetchone()["t"]
        if last is not None and when.minute < last:
            raise ValueError("Cannot backdate intelligence changes")
        with self.db:
            self.db.execute(
                "INSERT INTO stat_changes(actor_id,at_minute,old_intelligence,new_intelligence,reason)"
                " VALUES(?,?,?,?,?)",
                (actor_id, when.minute, old["intelligence"], intelligence, reason)
            )
            self.db.execute(
                "UPDATE character SET intelligence=? WHERE actor_id=?",
                (intelligence, actor_id)
            )

    @staticmethod
    def working_slots(intelligence: int) -> int:
        """Budget for recalled *active* memories, not a storage deletion limit."""
        return 2 + _valid_intelligence(intelligence) // 10

    @staticmethod
    def encode(intelligence: int, salience: float, emotion: float) -> float:
        return min(1.0, 0.30 + 0.0055 * _valid_intelligence(intelligence)
                   + 0.12 * _valid_unit("salience", salience)
                   + 0.08 * _valid_unit("emotion", emotion))

    def remember(self, actor_id: str, description: str, *,
                 learned_at: WorldTime, occurred_at: WorldTime | None = None,
                 kind: str = "episodic", source_type: str = "direct",
                 source_actor_id: str | None = None,
                 world_event_id: str | None = None,
                 location_id: str | None = None,
                 tags: tuple[str, ...] | list[str] = (),
                 confidence: float = 0.8, salience: float = 0.5,
                 emotion: float = 0.0, supersedes_id: int | None = None) -> int:
        """Append a subjective experience, never world truth by itself."""
        person = self.actor(actor_id)
        if not isinstance(description, str) or not description.strip() or len(description) > 4000:
            raise ValueError("Description must be 1–4000 characters")
        if kind not in ALLOWED_KINDS or source_type not in ALLOWED_SOURCES:
            raise ValueError("Invalid memory kind or source")
        if not isinstance(learned_at, WorldTime):
            raise TypeError("learned_at must be WorldTime")
        if occurred_at is None:
            occurred_at = learned_at
        if not isinstance(occurred_at, WorldTime) or occurred_at > learned_at:
            raise ValueError("The occurrence cannot follow the learning moment")
        if person["alive"] == 0 and source_type != "background":
            raise ValueError("Deceased actor cannot acquire fresh lived memories")
        for name, value in (("source_actor_id", source_actor_id),
                            ("world_event_id", world_event_id), ("location_id", location_id)):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a nonempty ID or None")
        if not isinstance(tags, (tuple, list)) or not all(
            isinstance(t, str) and 0 < len(t) <= 100 for t in tags
        ):
            raise ValueError("Tags must be nonempty strings <=100 chars")
        if len(tags) > 24:
            raise ValueError("Too many memory tags")
        confidence = _valid_unit("confidence", confidence)
        salience = _valid_unit("salience", salience)
        emotion = _valid_unit("emotion", emotion)
        if supersedes_id is not None:
            old = self.db.execute(
                "SELECT actor_id, learned_minute FROM experience WHERE memory_id=?",
                (supersedes_id,)
            ).fetchone()
            if old is None or old["actor_id"] != actor_id:
                raise ValueError("A correction can only supersede the actor's own memory")
            if old["learned_minute"] > learned_at.minute:
                raise ValueError("Correction predates the earlier memory")
        encoding = self.encode(person["intelligence"], salience, emotion)
        with self.db:
            cur = self.db.execute("""
                INSERT INTO experience(actor_id,learned_minute,occurred_minute,kind,
                    source_type,source_actor_id,world_event_id,location_id,description,
                    tags_json,confidence,salience,emotion,encoding,supersedes_id)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (actor_id, learned_at.minute, occurred_at.minute, kind,
                  source_type, source_actor_id, world_event_id, location_id,
                  description.strip(), json.dumps(tags, ensure_ascii=False),
                  confidence, salience, emotion, encoding, supersedes_id))
            return int(cur.lastrowid)

    def rehearse(self, actor_id: str, memory_id: int, at: WorldTime) -> None:
        """Record retrieval/practice as a new immutable rehearsal entry."""
        memory = self.db.execute(
            "SELECT learned_minute FROM experience WHERE actor_id=? AND memory_id=?",
            (actor_id, memory_id)
        ).fetchone()
        if memory is None:
            raise ValueError("Memory does not belong to actor")
        if at.minute < memory["learned_minute"]:
            raise ValueError("Cannot rehearse before learning")
        prev = self.db.execute(
            "SELECT MAX(at_minute) AS t FROM rehearsal WHERE actor_id=? AND memory_id=?",
            (actor_id, memory_id)
        ).fetchone()["t"]
        if prev is not None and at.minute < prev:
            raise ValueError("Rehearsal cannot precede previous rehearsal")
        with self.db:
            self.db.execute(
                "INSERT INTO rehearsal(actor_id,memory_id,at_minute) VALUES(?,?,?)",
                (actor_id, memory_id, at.minute)
            )

    def history(self, actor_id: str, *, as_of: WorldTime | None = None) -> list[dict]:
        """Inspect the actor's immutable archive, including false or superseded records."""
        self.actor(actor_id)
        if as_of is None:
            rows = self.db.execute(
                "SELECT * FROM experience WHERE actor_id=? ORDER BY learned_minute,memory_id",
                (actor_id,)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT * FROM experience WHERE actor_id=? AND learned_minute<=?"
                " ORDER BY learned_minute,memory_id", (actor_id, as_of.minute)
            ).fetchall()
        return [dict(row) | {"tags": json.loads(row["tags_json"])} for row in rows]

    def recall(self, actor_id: str, *, as_of: WorldTime, query: str = "",
               minimum_strength: float = 0.15, limit: int | None = None,
               include_superseded: bool = False) -> list[dict]:
        """Return bounded, time-aware retrieval, not objective truth.

        Intelligence affects encoded clarity, half-life and active recall slots.
        Every remembered event remains in the permanent archive even if it fails
        this fallible recall threshold.
        """
        person = self.actor(actor_id)
        minimum_strength = _valid_unit("minimum_strength", minimum_strength)
        if not isinstance(query, str):
            raise ValueError("Query must be text")
        if limit is None:
            limit = self.working_slots(person["intelligence"])
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("limit must be an integer from 1 to 1000")
        tokens = _tokens(query)
        if tokens and len(tokens) > 30:
            raise ValueError("Query too broad")
        rows = self.db.execute(
            """SELECT e.*,
                  (SELECT MAX(r.at_minute) FROM rehearsal r
                   WHERE r.actor_id=e.actor_id AND r.memory_id=e.memory_id
                     AND r.at_minute <= ?) AS last_rehearsal
               FROM experience e WHERE e.actor_id=? AND e.learned_minute<=?
               ORDER BY e.learned_minute DESC,e.memory_id DESC""",
            (as_of.minute, actor_id, as_of.minute)
        ).fetchall()
        superseded = set()
        if not include_superseded:
            superseded = {int(r["supersedes_id"]) for r in rows if r["supersedes_id"] is not None}
        results: list[dict] = []
        for row in rows:
            if row["memory_id"] in superseded:
                continue
            tagset = _tokens(" ".join(json.loads(row["tags_json"])))
            textset = _tokens(row["description"]) | tagset
            if tokens and not tokens.issubset(textset):
                continue
            salience, emotion = row["salience"], row["emotion"]
            half_life_days = (30.0 + 4.0 * person["intelligence"]) * (
                1.0 + 8.0 * salience + 4.0 * emotion
            )
            anchor = max(row["learned_minute"], row["last_rehearsal"] or row["learned_minute"])
            elapsed_days = max(0, (as_of.minute - anchor) / MINUTES_PER_DAY)
            # Rehearsal restores accessible strength but does not edit original encoding.
            strength = row["encoding"] * math.exp(-math.log(2) * elapsed_days / half_life_days)
            if strength < minimum_strength:
                continue
            results.append({
                "memory_id": row["memory_id"],
                "actor_id": row["actor_id"],
                "description": row["description"],
                "kind": row["kind"],
                "source_type": row["source_type"],
                "source_actor_id": row["source_actor_id"],
                "world_event_id": row["world_event_id"],
                "location_id": row["location_id"],
                "learned_minute": row["learned_minute"],
                "occurred_minute": row["occurred_minute"],
                "supersedes_id": row["supersedes_id"],
                "tags": json.loads(row["tags_json"]),
                "confidence": row["confidence"],
                "strength": round(strength, 8)
            })
        results.sort(key=lambda m: (-m["strength"], -m["learned_minute"], -m["memory_id"]))
        return results[:limit]

    def backup(self, target_path: str | Path) -> None:
        """Create a consistent SQLite snapshot suitable for save/load transfer."""
        dest = Path(target_path)
        if self.path == str(dest):
            raise ValueError("Backup must use a different path")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(dest)) as copy:
            self.db.backup(copy)
