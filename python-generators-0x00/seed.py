#!/usr/bin/env python3
"""
Database seeding script for ALX_prodev MySQL database.
Creates database, table, and populates with user data from CSV.
"""

import mysql.connector
from mysql.connector import Error
import csv
import os
from typing import Optional


def connect_db() -> Optional[mysql.connector.MySQLConnection]:
    """
    Connects to the MySQL database server.
    
    Returns:
        MySQL connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            port=3306
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL server: {e}")
        return None


def create_database(connection: mysql.connector.MySQLConnection) -> None:
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev() -> Optional[mysql.connector.MySQLConnection]:
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        MySQL connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev',
            port=3306
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection: mysql.connector.MySQLConnection) -> None:
    """
    Creates a table user_data if it does not exist with the required fields:
    - user_id (Primary Key, UUID, Indexed)
    - name (VARCHAR, NOT NULL)
    - email (VARCHAR, NOT NULL)
    - age (DECIMAL, NOT NULL)
    
    Args:
        connection: MySQL connection object connected to ALX_prodev database.
    """
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(10, 2) NOT NULL,
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection: mysql.connector.MySQLConnection, csv_file: str) -> None:
    """
    Inserts data from CSV file into the database if it does not exist.
    
    Args:
        connection: MySQL connection object connected to ALX_prodev database.
        csv_file: Path to the CSV file containing user data.
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return
    
    try:
        cursor = connection.cursor()
        inserted_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                user_id = row.get('user_id', '').strip()
                name = row.get('name', '').strip()
                email = row.get('email', '').strip()
                age = row.get('age', '').strip()
                
                # Validate required fields
                if not all([user_id, name, email, age]):
                    print(f"Skipping row with missing data: {row}")
                    skipped_count += 1
                    continue
                
                # Check if record already exists
                check_query = "SELECT user_id FROM user_data WHERE user_id = %s"
                cursor.execute(check_query, (user_id,))
                existing = cursor.fetchone()
                
                if not existing:
                    # Insert new record
                    insert_query = """
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (user_id, name, email, age))
                    inserted_count += 1
                else:
                    skipped_count += 1
        
        connection.commit()
        print(f"Data insertion complete: {inserted_count} inserted, {skipped_count} skipped")
        cursor.close()
        
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
    except Exception as e:
        print(f"Error reading CSV file: {e}")

