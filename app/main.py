from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import users
from app.core.config import settings
from app.db.manager import db_manager
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    db_manager.init_db()
    print(f"Database initialized: {settings.DATABASE_URL}")
    yield
    db_manager.close()
    print("Shutting down...")


app = FastAPI(
    title="FastAPI Demo",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "FastAPI Demo",
        "docs": "/docs",
        "redoc": "/redoc",
    }
