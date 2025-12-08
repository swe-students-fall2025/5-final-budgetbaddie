import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, close_mongo_connection, create_indexes

async def init_database():
    await connect_to_mongo()
    await create_indexes()
    await close_mongo_connection()
    print("database initialization complete")

if __name__ == "__main__":
    asyncio.run(init_database())

