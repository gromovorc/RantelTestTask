from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    app_name: str
    debug: bool
    database_url: str

    database_url: str
    redis_url: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore",
    )

settings = Settings()