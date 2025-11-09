from __future__ import annotations

from pathlib import Path
from typing import Final

from decouple import config

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH: Final[Path] = PROJECT_ROOT / "users.db"


def get_sqlite_path() -> Path:
    """
    Return the configured SQLite database path and ensure its directory exists.
    """
    raw_path = config("SQLITE_DB_PATH", default=str(DEFAULT_SQLITE_PATH))
    db_path = Path(raw_path).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path
