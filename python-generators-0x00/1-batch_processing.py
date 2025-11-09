#!/usr/bin/env python3
"""
Batch processing helpers to fetch and process users from the database in
batches.
"""

from typing import List, Dict, Any, Iterator

import seed


def stream_users_in_batches(batch_size: int) -> Iterator[List[Dict[str, Any]]]:
    """
    Generator that fetches rows in batches from the user_data table.

    Args:
        batch_size: Number of rows to fetch per batch.

    Yields:
        Lists of user dictionaries in each batch.
    """
    connection = seed.connect_to_prodev()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            batch = [
                {
                    "user_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "age": int(row[3]),
                }
                for row in rows
            ]

            yield batch
    finally:
        cursor.close()
        connection.close()


def batch_processing(batch_size: int) -> None:
    """Process each batch to filter users over the age of 25."""
    for batch in stream_users_in_batches(batch_size) or []:
        for user in batch:
            if user["age"] > 25:
                print(user)
