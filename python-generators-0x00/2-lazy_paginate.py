#!/usr/bin/env python3
"""
Lazy pagination generator to fetch users from the database in pages.
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database.
    
    Args:
        page_size: Number of users per page.
        offset: Starting offset for the query.
    
    Returns:
        List of user dictionaries.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    # Convert age from Decimal to int
    for row in rows:
        if 'age' in row and row['age'] is not None:
            row['age'] = int(row['age'])
    cursor.close()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator function that lazily loads pages of users from the database.
    Only fetches the next page when needed, starting at offset 0.
    
    Args:
        page_size: Number of users per page.
    
    Yields:
        List[Dict]: A page of users (list of user dictionaries).
    """
    offset = 0
    
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size

