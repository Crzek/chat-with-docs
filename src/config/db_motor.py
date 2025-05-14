import motor.motor_asyncio
from src.config.settings import env


async def connection():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        env.mongo_initdb_full_uri,
        serverSelectionTimeoutMS=3000  # 3 segundos
    )
    db = client[env.mongo_db_name]  # nombre de la base de datos ne mongo
    return db
