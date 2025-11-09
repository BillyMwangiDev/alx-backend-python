import functools
import logging
import sqlite3
from typing import Any, Callable, Optional

# Configure logging once for this script (move to main entrypoint if preferred)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("alx.decorators.sql")


def log_queries(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that logs the SQL statement a function is about to execute.

    The wrapped function must receive the SQL string either as the first
    positional argument or via a ``query`` keyword argument.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        query: Optional[str] = kwargs.get("query")
        if query is None and args:
            # assume first positional argument holds the SQL string
            query = args[0]

        if query:
            logger.info("Executing SQL query: %s", query)
        else:
            logger.warning(
                "Executing %s with no SQL query argument.",
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
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return results


if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)
