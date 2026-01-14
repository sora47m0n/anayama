import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool: asyncpg.Pool | None = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def close_db():
    await pool.close()
