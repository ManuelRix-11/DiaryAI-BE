from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.controllers.user_controller import user_router
from app.controllers.diary_controller import diary_router
from app.db import connect_to_mongo, close_mongo_connection

app = FastAPI(title="DiaryAI API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title= "DiaryAI", lifespan=lifespan)
app.include_router(user_router)
app.include_router(diary_router)