import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

DATABASE_PATH = Path("python-generators-0x00/users.db")


class ExecuteQuery:
    """
    Context manager that executes a query with parameters and returns the
    resulting rows.
    """

    def __init__(self, query: str, params: Iterable[Any]):
        self.query = query
        self.params = tuple(params)
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.results: list[tuple[Any, ...]] = []

    def __enter__(self) -> list[tuple[Any, ...]]:
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    sql = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery(sql, (25,)) as rows:
        for row in rows:
            print(row)
