from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SprintSync"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./sprintsync.db"

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h

    # AI
    OPENAI_API_KEY: Optional[str] = None
    USE_AI_STUB: bool = False  # force stub even if key present

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
