from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.diary import Diary
from app.services import diary_service

diary_router = APIRouter(prefix="/diaries", tags=["Diaries"])

@diary_router.get("/")
async def list_entries():
    try:
        return await diary_service.get_all_diary_entries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@diary_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entry(title, text, user_id):
    try:
        return await diary_service.create_diary_entry(
            title=title,
            text=text,
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@diary_router.put("/{entry_id}")
async def update_entry(entry_id: str, diary: Diary):
    updated = await diary_service.update_diary_entry(entry_id, diary)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated
