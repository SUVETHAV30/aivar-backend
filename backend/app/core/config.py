import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Agent Behavioral Baseline Builder"
    environment: str = "development"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    openai_api_key: str = ""
    model: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
