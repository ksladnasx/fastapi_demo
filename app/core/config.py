from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://fastapi:fastapi@localhost:3306/fastapi_demo?charset=utf8mb4"
    DATABASE_ECHO: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
