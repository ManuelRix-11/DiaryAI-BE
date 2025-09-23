from pymongo import AsyncMongoClient
from bson import ObjectId
from beanie import init_beanie

from app.models.user import User
from app.models.diary import Diary

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "DiaryAI"

client: AsyncMongoClient | None = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncMongoClient(MONGO_URI)
    db = client[DB_NAME]

    await init_beanie(database=db, document_models=[User, Diary])

    print("✅ Connected to Mongo")


async def close_mongo_connection():
    global client
    if client:
        await client.close()
        print("🛑 Closed Mongo connection")


def get_collection(name: str):
    if db is None:
        raise RuntimeError("Database not initialized. Did you call connect_to_mongo()?")

    return db[name]


def id_to_str(document: dict):
    if not document:
        return None
    document["_id"] = str(document["_id"])
    return document