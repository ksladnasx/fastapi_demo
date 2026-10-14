from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://fastapi:123456@localhost:3306/fastapi_demo?charset=utf8mb4"
    DATABASE_ECHO: bool = False
    SECRET_KEY: str = "123456"   #用于服务端加密的密钥
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    SESSION_COOKIE_NAME: str = "fastapi_demo_session"
    VISIBLE_COOKIE_NAME: str = "fastapi_demo_visible"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
