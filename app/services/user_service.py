from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import EmailStr

from app.db import db

async def create_user(username: str, email: EmailStr, password: str):
    payload = {"username": username, "email": email, "password": password}

    result = await db.Utenti.insert_one(payload)
    return result

async def get_user_by_mail(email: EmailStr):
    if email and email != "":
        query = {"email": email}
        doc = await db.Utenti.find_one(query)
        return doc