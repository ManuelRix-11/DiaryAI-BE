from pymongo import AsyncMongoClient
from bson import ObjectId

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "DiaryAI"

client: AsyncMongoClient = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncMongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("Connected to Mongo")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Closed Mongo connection")

def id_to_str(document: dict):
    if not document:
        return document
    return str(document["_id"])