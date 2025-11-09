import functools
import logging
import sqlite3
from typing import Any, Callable


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("alx.decorators.connection")


def with_db_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Open an SQLite connection, pass it to the wrapped function,
    and close it afterwards.
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


@with_db_connection
def get_user_by_id(
    conn: sqlite3.Connection,
    user_id: int,
) -> tuple[Any, ...] | None:
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        logger.info("Closed cursor after fetching user %s", user_id)


if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
