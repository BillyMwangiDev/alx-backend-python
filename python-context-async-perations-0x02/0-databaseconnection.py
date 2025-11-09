import sqlite3
from pathlib import Path
from typing import Optional

DATABASE_PATH = Path("python-generators-0x00/users.db")


class DatabaseConnection:
    """
    Class-based context manager that handles opening and closing SQLite
    connections.
    """

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    with DatabaseConnection(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            print(row)
        cursor.close()
