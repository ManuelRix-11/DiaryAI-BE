from typing import List, Dict, Any, Optional

from pydantic import BaseModel, EmailStr

# Definizione dei modelli di richiesta/risposta
class DiaryCreate(BaseModel):
    title: str
    user_id: str


class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


class UserShortResponse(BaseModel):
    id: str
    username: str
    email: EmailStr

class DiaryResponse(BaseModel):
    id: str
    title: str
    text: str
    created_at: str
    updated_at: str
    user: Optional[UserShortResponse] = None
    sentiment: Optional[Dict[str, Any]] = None

class SentimentResponse(BaseModel):
    sentiment: str
    score: float
    sentiments: List[Dict[str, Any]]
