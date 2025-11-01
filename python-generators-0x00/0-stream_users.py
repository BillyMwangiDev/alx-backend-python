#!/usr/bin/env python3
"""
Generator function to stream users from the user_data table one by one.
"""

import seed
from typing import Dict, Any, Optional


def stream_users():
    """
    Generator function that streams rows from the user_data table one by one.
    
    Yields:
        Dict[str, Any]: Dictionary containing user_id, name, email, and age
    """
    connection = seed.connect_to_prodev()
    
    if not connection:
        return
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        for row in cursor:
            yield {
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': int(row['age']) if row['age'] is not None else row['age']
            }
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

