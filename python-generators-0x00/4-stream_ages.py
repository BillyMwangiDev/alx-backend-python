#!/usr/bin/env python3
"""
Memory-efficient average age calculation using generators.
"""

import seed


def stream_user_ages():
    """
    Generator function that yields user ages one by one from the database.
    
    Yields:
        int: User age (converted from Decimal to int).
    """
    connection = seed.connect_to_prodev()
    
    if not connection:
        return
    
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        for row in cursor:
            age = row[0]
            # Convert Decimal to int
            yield int(age) if age is not None else 0
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculates the average age of all users using the stream_user_ages generator.
    Uses memory-efficient approach without loading entire dataset.
    
    Returns:
        float: Average age of all users.
    """
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0.0
    
    return total_age / count


if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")

