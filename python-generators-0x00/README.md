# Database Seeding Script

This project contains a Python script to set up and seed a MySQL database with user data.

## Overview

The `seed.py` module provides functions to:
- Connect to MySQL database server
- Create the `ALX_prodev` database
- Create the `user_data` table with required fields
- Populate the database with data from a CSV file

## Database Schema

The `user_data` table has the following structure:

- `user_id` (VARCHAR(36), PRIMARY KEY, INDEXED) - UUID identifier
- `name` (VARCHAR(255), NOT NULL) - User's name
- `email` (VARCHAR(255), NOT NULL) - User's email address
- `age` (DECIMAL(10, 2), NOT NULL) - User's age

## Requirements

- Python 3.6+
- MySQL Server 5.7+ or MySQL 8.0+
- mysql-connector-python library

## Setup

1. **Install MySQL server on your system if not already installed.**
   - See `INSTALL_MYSQL.md` for detailed installation instructions for Windows, Linux, and macOS.
   - **Quick Windows install:** Download MySQL Installer from https://dev.mysql.com/downloads/installer/ and run the installer.
   - **Docker alternative:** See `INSTALL_MYSQL.md` for Docker setup (recommended for development).

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure MySQL connection:
   - Edit `seed.py` and update the connection parameters in `connect_db()` and `connect_to_prodev()` functions:
     - `host`: MySQL server hostname (default: 'localhost')
     - `user`: MySQL username (default: 'root')
     - `password`: MySQL password (default: '')
     - `port`: MySQL port (default: 3306)

## Usage

Run the test script:
```bash
python3 0-main.py
```

Or use the module interactively:
```python
import seed

# Connect to MySQL server
connection = seed.connect_db()
if connection:
    # Create database
    seed.create_database(connection)
    connection.close()
    
    # Connect to ALX_prodev database
    connection = seed.connect_to_prodev()
    if connection:
        # Create table
        seed.create_table(connection)
        
        # Insert data from CSV
        seed.insert_data(connection, 'user_data.csv')
        
        connection.close()
```

## Functions

### `connect_db()`
Connects to the MySQL database server without specifying a database.
Returns a MySQL connection object or None if connection fails.

### `create_database(connection)`
Creates the `ALX_prodev` database if it does not exist.

### `connect_to_prodev()`
Connects specifically to the `ALX_prodev` database.
Returns a MySQL connection object or None if connection fails.

### `create_table(connection)`
Creates the `user_data` table with the required schema if it does not exist.

### `insert_data(connection, csv_file)`
Reads data from the specified CSV file and inserts it into the `user_data` table.
Skips records that already exist (based on user_id) to avoid duplicates.

## CSV File Format

The CSV file should have the following columns:
- `user_id`: UUID string
- `name`: User's full name
- `email`: User's email address
- `age`: User's age (numeric)

Example:
```csv
user_id,name,email,age
00234e50-34eb-4ce2-94ec-26e3fa749796,Dan Altenwerth Jr.,Molly59@gmail.com,67
```

## Notes

- The script checks for duplicate records based on `user_id` before inserting.
- All database operations use transactions and proper error handling.
- The script prints status messages for each operation.

