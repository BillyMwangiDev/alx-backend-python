#!/usr/bin/env python3
"""Test SQLite connection script."""

import sqlite3

from config import get_sqlite_path


def test_connection() -> bool:
    """Verify the SQLite database file can be opened."""
    db_path = get_sqlite_path()
    try:
        connection = sqlite3.connect(db_path)
        connection.execute("SELECT 1")
        connection.close()
        print(f"Connection to {db_path} successful")
        return True
    except sqlite3.Error as exc:
        print(f"Connection failed: {exc}")
        return False


if __name__ == "__main__":
    test_connection()
