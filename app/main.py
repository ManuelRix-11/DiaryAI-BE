from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.controllers.diary_controller import diary_router
from app.controllers.user_controller import user_router
from app.db import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="DiaryAI",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.include_router(user_router)
app.include_router(diary_router)


@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title="DiaryAI API Docs",
    )