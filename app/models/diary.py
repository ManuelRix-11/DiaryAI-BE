from beanie import Document, Link
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

from app.models.user import User

class Diary(Document):
    title: str
    user: Link[User]
    created_at: datetime
    updated_at: datetime
    text: str
    sentiment: Optional[dict] = None
