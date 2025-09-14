from fastapi import APIRouter, Depends, HTTPException
from app.services import user_service

user_router = APIRouter()

@user_router.post("/getByMail")
async def get_user_by_mail(mail: str):
    return await user_service.get_user_by_mail(mail)