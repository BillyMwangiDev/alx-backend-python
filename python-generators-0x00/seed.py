#!/usr/bin/env python3
"""
Database seeding script for the local SQLite database.
Creates the schema and populates it with user data from CSV.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Optional

import sqlite3

from config import get_sqlite_path

logger = logging.getLogger("alx.generators.seed")


def connect_db() -> sqlite3.Connection:
    """Return a connection to the configured SQLite database."""
    db_path = get_sqlite_path()
    logger.info("Connecting to SQLite database at %s", db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def create_database(connection: sqlite3.Connection) -> None:
    """Ensure the database file exists (implicit with SQLite)."""
    db_path = get_sqlite_path()
    logger.info("Database ready at %s", db_path)


def connect_to_prodev() -> Optional[sqlite3.Connection]:
    """Maintain compatibility with previous interface."""
    try:
        return connect_db()
    except sqlite3.Error as exc:  # pragma: no cover - log and return None
        logger.error("Failed to connect to SQLite database: %s", exc)
        return None


def create_table(connection: sqlite3.Connection) -> None:
    """Create the user_data table if it does not already exist."""
    create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        );
    """
    with connection:
        connection.execute(create_table_query)
    logger.info("Table user_data created or already exists")


def insert_data(connection: sqlite3.Connection, csv_file: str) -> None:
    """Insert CSV records into the database, skipping existing user_ids."""
    csv_path = Path(csv_file)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).resolve().parent / csv_path

    if not csv_path.exists():
        logger.error("CSV file not found: %s", csv_file)
        return

    inserted_count = 0
    skipped_count = 0

    try:
        with csv_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            with connection:
                for row in reader:
                    user_id = row.get("user_id", "").strip()
                    name = row.get("name", "").strip()
                    email = row.get("email", "").strip()
                    age_raw = row.get("age", "").strip()

                    if not all([user_id, name, email, age_raw]):
                        logger.warning(
                            "Skipping row with missing data: %s",
                            row,
                        )
                        skipped_count += 1
                        continue

                    try:
                        age = int(float(age_raw))
                    except ValueError:
                        logger.warning(
                            "Invalid age '%s' for user %s",
                            age_raw,
                            user_id,
                        )
                        skipped_count += 1
                        continue

                    existing = connection.execute(
                        "SELECT 1 FROM user_data WHERE user_id = ?",
                        (user_id,),
                    ).fetchone()

                    if existing:
                        skipped_count += 1
                        continue

                    connection.execute(
                        "INSERT INTO user_data (user_id, name, email, age) "
                        "VALUES (?, ?, ?, ?)",
                        (user_id, name, email, age),
                    )
                    inserted_count += 1

        logger.info(
            "Data insertion complete: %s inserted, %s skipped",
            inserted_count,
            skipped_count,
        )

    except (OSError, csv.Error) as exc:
        logger.error("Failed to read CSV data: %s", exc)
