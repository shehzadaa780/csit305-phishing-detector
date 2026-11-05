"""De-identified audit log (SQLite). Stores NO message text and NO URLs -
only what is needed to evaluate the system: format, model version, label,
risk, band, latency and flags. Written only when the user permits it."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .data import ROOT

DEFAULT_DB = ROOT / "results" / "audit_log.sqlite"

SCHEMA = """CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    input_type TEXT NOT NULL,
    model_version TEXT NOT NULL,
    label TEXT NOT NULL,
    risk INTEGER NOT NULL,
    band TEXT NOT NULL,
    n_urls INTEGER NOT NULL,
    latency_ms REAL NOT NULL,
    flags TEXT
)"""


class AuditLog:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as con:
            con.execute(SCHEMA)

    def write(self, input_type: str, result: dict) -> None:
        with sqlite3.connect(self.path) as con:
            con.execute(
                "INSERT INTO audit (ts, input_type, model_version, label, risk, band, n_urls, latency_ms, flags)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), input_type,
                 result["model_version"], result["label"], result["risk"], result["band"],
                 len(result["checked_urls"]), result["timing_ms"]["total"],
                 ";".join(result["notes"])[:500]),
            )

    def rows(self) -> list[tuple]:
        with sqlite3.connect(self.path) as con:
            return con.execute("SELECT * FROM audit ORDER BY id").fetchall()
