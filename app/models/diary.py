from beanie import Document
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

from app.models.user import User

class Diary(Document):
    user: User
    date: datetime
    text: str
    sentiment: dict
