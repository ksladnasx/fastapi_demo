from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://fastapi:fastapi@localhost:3306/fastapi_demo?charset=utf8mb4"
    DATABASE_ECHO: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
