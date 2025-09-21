from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.diary import Diary
from app.services import diary_service

diary_router = APIRouter(prefix="/diaries", tags=["Diaries"])

@diary_router.post("/getAll")
async def get_user_by_mail(mail: str):
    return {"Ciao"}