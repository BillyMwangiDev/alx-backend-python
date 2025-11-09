import functools
import logging
import sqlite3
import time
from typing import Any, Callable


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("alx.decorators.retry")


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


def retry_on_failure(
    retries: int = 3, delay: float = 2.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Retry a database operation when an exception is raised, waiting the
    configured delay between attempts.
    """

    if retries < 1:
        raise ValueError("retries must be at least 1")
    if delay < 0:
        raise ValueError("delay cannot be negative")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt >= retries:
                        logger.error(
                            "Operation failed after %s attempts; raising %s",
                            attempt,
                            exc,
                        )
                        raise

                    logger.warning(
                        "Attempt %s/%s failed with %s; retrying in %.2f s",
                        attempt,
                        retries,
                        exc.__class__.__name__,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    attempt += 1

        return wrapper

    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn: sqlite3.Connection) -> list[tuple[Any, ...]]:
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    finally:
        cursor.close()
        logger.info("Closed cursor after fetching users")


if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)
