from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import users
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_db()
    print(f"Database initialized: {settings.DATABASE_URL}")
    yield
    print("Shutting down...")


app = FastAPI(
    title="FastAPI Demo",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "FastAPI Demo",
        "docs": "/docs",
        "redoc": "/redoc",
    }
