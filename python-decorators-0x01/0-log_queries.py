import functools
import logging
import sqlite3
from typing import Any, Callable, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("alx.decorators.log_queries")


def log_queries(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log the SQL query passed to the decorated function before execution."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        query: Optional[str] = kwargs.get("query")
        if query is None and args:
            query = args[0]

        if query:
            LOGGER.info("Executing SQL query: %s", query)
        else:
            LOGGER.warning(
                "No SQL query argument supplied to %s",
                func.__name__,
            )

        return func(*args, **kwargs)

    return wrapper


@log_queries
def fetch_all_users(query: str) -> list[tuple[Any, ...]]:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)
