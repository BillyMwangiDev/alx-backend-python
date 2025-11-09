import functools
import logging
import sqlite3
from typing import Any, Callable


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("alx.decorators.transaction")


def with_db_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """Open a connection to the users.db database and close it after use."""

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


def transactional(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Wrap a database operation in a transaction, committing on success and
    rolling back on failure.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        connection: sqlite3.Connection | None = None
        if "conn" in kwargs:
            connection = kwargs["conn"]
        elif args and isinstance(args[0], sqlite3.Connection):
            connection = args[0]

        if connection is None:
            raise ValueError(
                "transactional decorator requires sqlite3.Connection"
            )

        try:
            logger.info("Beginning transaction")
            result = func(*args, **kwargs)
            connection.commit()
            logger.info("Transaction committed")
            return result
        except Exception as exc:
            logger.exception(
                "Error during transaction; rolling back",
                exc_info=exc,
            )
            connection.rollback()
            raise

    return wrapper


@with_db_connection
@transactional
def update_user_email(
    conn: sqlite3.Connection,
    user_id: int,
    new_email: str,
) -> None:
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (new_email, user_id),
        )
        logger.info("Updated user %s email to %s", user_id, new_email)
    finally:
        cursor.close()
        logger.info("Closed cursor after updating user %s", user_id)


if __name__ == "__main__":
    update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")
    print("User email updated.")
