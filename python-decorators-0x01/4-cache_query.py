import functools
import logging
import sqlite3
from typing import Any, Callable


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("alx.decorators.cache")


query_cache: dict[str, list[tuple[Any, ...]]] = {}


def with_db_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Open a connection to users.db, pass it to the wrapped function, and
    close it afterwards.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        connection = sqlite3.connect("users.db")
        logger.info("Opened connection to users.db")
        try:
            if "conn" in kwargs:
                kwargs["conn"] = connection
                return func(*args, **kwargs)
            return func(connection, *args, **kwargs)
        finally:
            connection.close()
            logger.info("Closed connection to users.db")

    return wrapper


def cache_query(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Cache query results based on the SQL string supplied to the wrapped
    function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        query: str | None = kwargs.get("query")
        if query is None:
            # Assume the second positional argument (after connection)
            # is the SQL query string.
            if len(args) >= 2 and isinstance(args[1], str):
                query = args[1]

        if query is None:
            logger.warning(
                "cache_query missing query argument; skipping cache"
            )
            return func(*args, **kwargs)

        if query in query_cache:
            logger.info("Cache hit for query: %s", query)
            return query_cache[query]

        logger.info("Cache miss for query: %s", query)
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result

    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(
    conn: sqlite3.Connection, query: str
) -> list[tuple[Any, ...]]:
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        logger.info("Closed cursor for cached query: %s", query)


if __name__ == "__main__":
    print("First call (cache miss):")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)

    print("\nSecond call (cache hit):")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
