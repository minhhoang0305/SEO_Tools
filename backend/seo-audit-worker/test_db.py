import asyncio
import asyncpg

from app.core.config import DATABASE_URL


async def main():

    conn = await asyncpg.connect(
        DATABASE_URL
    )

    version = await conn.fetchval(
        "SELECT version();"
    )

    print(version)

    await conn.close()


asyncio.run(main())