#!/usr/bin/env python3
"""
Batch processing functions to fetch and process users from the database in batches.
"""

import seed
from typing import List, Dict, Any


def stream_users_in_batches(batch_size: int):
    """
    Generator function that fetches rows in batches from the user_data table.
    
    Args:
        batch_size: Number of rows to fetch per batch.
    
    Yields:
        List[Dict[str, Any]]: List of user dictionaries in each batch.
    """
    connection = seed.connect_to_prodev()
    
    if not connection:
        return
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            
            # Convert rows to dictionaries and convert age to int using list comprehension
            batch = [{
                'user_id': row['user_id'],
                'name': row['name'],
                'email': row['email'],
                'age': int(row['age']) if row['age'] is not None else row['age']
            } for row in rows]
            
            yield batch
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size: int):
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size: Number of rows to fetch per batch.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)

