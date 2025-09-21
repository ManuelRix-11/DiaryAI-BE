from app.db import db
from transformers import pipeline

from app.models.user import User

emotion_pipeline = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-emotion-multilabel-latest",
    top_k=None
)

async def sentiment_analysis(user: User, text: str) -> dict:
    result = emotion_pipeline(text)
    sentiments = result[0]
    best = max(sentiments, key=lambda x: x['score'])

    return {
        "sentiment": best['label'],
        "score": best['score'],
        "sentiments": sentiments
    }