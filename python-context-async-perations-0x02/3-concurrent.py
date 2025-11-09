import asyncio
from pathlib import Path

import aiosqlite

DATABASE_PATH = Path("python-generators-0x00/users.db")


async def async_fetch_users() -> list[tuple]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def async_fetch_older_users() -> list[tuple]:
    age_threshold = 40
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute(
            "SELECT * FROM users WHERE age > ?",
            (age_threshold,),
        )
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def fetch_concurrently() -> None:
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
    )

    print("All users:")
    for user in all_users:
        print(user)

    print("\nUsers older than 40:")
    for user in older_users:
        print(user)


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
