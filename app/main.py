from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import models
from app.db.database import (
    DATABASE_URL,
    Base,
    apply_schema_patches,
    ensure_postgres_database,
    engine,
)
from app.routes.sales import router as sales_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_postgres_database(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    apply_schema_patches()
    yield


app = FastAPI(title="API de ventas", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sales_router, prefix="/api/v1")
