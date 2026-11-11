from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import errors, uploads
from app.api import VERSION, router
from app.config import get_settings
from app.db import SessionLocal


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not get_settings().near_ai_api_key:
        raise RuntimeError("NEAR_AI_API_KEY is not set. Copy .env.example to backend/.env and add the key.")
    with SessionLocal() as db:
        uploads.purge_expired(db)  # NFR-11: drop uploads past the retention window
    yield


app = FastAPI(title="Patent Inference API", version=VERSION, lifespan=lifespan)
errors.install(app)
app.include_router(router)
