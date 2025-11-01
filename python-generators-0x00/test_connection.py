#!/usr/bin/env python3
"""
Test MySQL connection script.
Use this to verify your MySQL connection settings.
"""

import mysql.connector
from mysql.connector import Error

def test_connection(password=''):
    """Test MySQL connection with given password."""
    try:
        print("Attempting to connect to MySQL...")
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password,
            port=3306
        )
        if connection.is_connected():
            print("Connection successful!")
            db_info = connection.get_server_info()
            print(f"MySQL Server version: {db_info}")
            connection.close()
            return True
    except Error as e:
        print(f"X Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("MySQL Connection Test")
    print("=" * 40)
    
    # Try with empty password first
    if test_connection(''):
        print("\nConnection works with empty password!")
        print("You can use seed.py with password='' in the connection settings.")
    else:
        print("\nPassword is required. Please enter your MySQL root password:")
        print("(Press Enter if you want to try empty password again)")
        password = input("Password: ")
        if test_connection(password):
            print(f"\nConnection successful with password!")
            print(f"Update seed.py to use password='{password}'")
        else:
            print("\nX Connection still failed. Please check:")
            print("1. MySQL service is running")
            print("2. Password is correct")
            print("3. User 'root' has proper permissions")

