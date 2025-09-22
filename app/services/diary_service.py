from datetime import datetime
from app.db import db
from transformers import pipeline

from app.models.diary import Diary
from app.models.user import User

emotion_pipeline = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-emotion-multilabel-latest",
    top_k=None
)

async def create_diary_entry(user_id: str, title: str, text: str):
    payload = {
        "title": title,
        "text": text,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.diary_entries.insert_one(payload)
    doc = await db.diary_entries.find_one({"_id": result.inserted_id})
    return doc

async def get_all_diary_entries():
    cursor = db.diary_entries.find()
    return [doc async for doc in cursor]

async def update_diary_entry(entry_id: str, entry: Diary):
    sentiment = sentiment_analysis(entry.user, entry.content)
    update_data = {
        "$set": {
            "title": entry.title,
            "text": entry.content,
            "updated_at": datetime.utcnow(),
            "sentiment": sentiment,
        }
    }
    result = await db.diary_entries.update_one({"_id": entry_id}, update_data)
    if result.modified_count == 0:
        return None
    doc = await db.diary_entries.find_one({"_id": entry_id})
    return doc

async def sentiment_analysis(user: User, text: str) -> dict:
    result = emotion_pipeline(text)
    sentiments = result[0]
    best = max(sentiments, key=lambda x: x['score'])

    return {
        "sentiment": best['label'],
        "score": best['score'],
        "sentiments": sentiments
    }