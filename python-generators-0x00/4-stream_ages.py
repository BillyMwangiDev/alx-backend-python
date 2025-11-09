#!/usr/bin/env python3
"""
Memory-efficient average age calculation using generators.
"""

from typing import Iterator

import seed


def stream_user_ages() -> Iterator[int]:
    """Yield user ages one by one from the SQLite database."""
    connection = seed.connect_to_prodev()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT age FROM user_data")
        for (age,) in cursor.fetchall():
            yield int(age)
    finally:
        cursor.close()
        connection.close()


def calculate_average_age() -> float:
    """Calculate the average age of all users using the generator."""
    total_age = 0
    count = 0

    for age in stream_user_ages() or []:
        total_age += age
        count += 1

    if count == 0:
        return 0.0

    return total_age / count


if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")
