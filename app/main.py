from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import items, recruitment, users
from app.core.config import settings
from app.db.manager import db_manager
from app.exceptions import register_exception_handlers
from app.utils.common import success_response


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

# 中间件
app.add_middleware(
    CORSMiddleware,
    # Do not use allow_origins=["*"] when allow_credentials=True.
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # Allow cross-origin requests to include cookies.
)

register_exception_handlers(app)
# 路由分发，将所有以 /users 开头的请求交给 users.router 处理
app.include_router(users.router)
app.include_router(items.router)
app.include_router(recruitment.router)


@app.get("/")
def root():
    return success_response(
        data={
            "docs": "/docs",
            "redoc": "/redoc",
        },
        message="FastAPI Demo",
    )
