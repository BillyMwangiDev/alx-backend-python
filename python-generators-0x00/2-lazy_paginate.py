#!/usr/bin/env python3
"""
Lazy pagination generator to fetch users from the database in pages.
"""

from typing import Dict, Iterable, List

import seed


def paginate_users(page_size: int, offset: int) -> List[Dict[str, int | str]]:
    """Fetch a page of users from the SQLite database."""
    connection = seed.connect_to_prodev()
    if connection is None:
        return []

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT user_id, name, email, age FROM user_data LIMIT ? OFFSET ?",
            (page_size, offset),
        )
        rows = cursor.fetchall()
        return [
            {
                "user_id": row[0],
                "name": row[1],
                "email": row[2],
                "age": int(row[3]),
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def lazy_paginate(page_size: int) -> Iterable[List[Dict[str, int | str]]]:
    """
    Generator that lazily loads pages of users from the database.
    """
    offset = 0

    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
