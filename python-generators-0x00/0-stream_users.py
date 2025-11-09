#!/usr/bin/env python3
"""
Generator function to stream users from the user_data table one by one.
"""

from typing import Dict, Any, Iterator

import seed


def stream_users() -> Iterator[Dict[str, Any]]:
    """Yield user records from the SQLite database one at a time."""
    connection = seed.connect_to_prodev()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        for user_id, name, email, age in cursor.fetchall():
            yield {
                "user_id": user_id,
                "name": name,
                "email": email,
                "age": int(age),
            }
    finally:
        cursor.close()
        connection.close()
