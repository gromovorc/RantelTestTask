from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    app_name: str
    debug: bool
    database_url: str

    model_config = SettingsConfigDict(
        env_file= ENV_PATH
    )

settings = Settings()