from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Connection to whole server
motor_client = AsyncIOMotorClient('mongodb://localhost:27017')
# Single database instance
database = motor_client['c6_mongo']

def get_database() -> AsyncIOMotorDatabase:
    return database