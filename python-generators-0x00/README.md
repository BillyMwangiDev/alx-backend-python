# SQLite Database Seeding Script

This project seeds a local SQLite database with user data from `user_data.csv` and
provides generator utilities for streaming records efficiently.

## Overview

The `seed.py` module provides functions to:
- Connect to the configured SQLite database file
- Ensure the database file exists
- Create the `user_data` table
- Populate the database with data from a CSV file

## Database Schema

The `user_data` table has the following structure:

- `user_id` (`TEXT`, PRIMARY KEY)
- `name` (`TEXT`, NOT NULL)
- `email` (`TEXT`, NOT NULL)
- `age` (`INTEGER`, NOT NULL)

## Requirements

- Python 3.9+
- `python-decouple` (installed from `requirements.txt`)

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the SQLite database path (optional):
   - Copy `.env.example` to `.env` (create the example file if it does not exist).
   - Set `SQLITE_DB_PATH=/absolute/path/to/users.db` if you want to override the
     default location (`python-generators-0x00/users.db`).

## Usage

Run the setup script to create the database and load sample data:
```bash
python3 0-main.py
```

Or use the module interactively:
```python
import seed

connection = seed.connect_db()
seed.create_database(connection)
seed.create_table(connection)
seed.insert_data(connection, "user_data.csv")
connection.close()
```

## Functions

### `connect_db()`
Opens a connection to the SQLite database file and returns the connection object.

### `create_database(connection)`
Ensures the database file exists and logs its location.

### `connect_to_prodev()`
Backwards-compatible helper that returns a new SQLite connection or `None` on failure.

### `create_table(connection)`
Creates the `user_data` table if it does not exist.

### `insert_data(connection, csv_file)`
Reads data from the CSV file and inserts rows, skipping existing `user_id` values.

## CSV File Format

The CSV file should use the following columns:
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

- Duplicate records (same `user_id`) are skipped automatically.
- All writes run inside implicit SQLite transactions.
- Logging output can be enabled by configuring the root logger (see `0-main.py`).

