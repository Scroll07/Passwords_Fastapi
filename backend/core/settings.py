from pathlib import Path
import os
from typing import Literal


BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKUPS = BASE_DIR / "BACKUPS_DATA"


class Settings:
    DB_HOST: str = os.getenv("DB_HOST", default="localhost")
    DB_PORT: str = os.getenv("DB_PORT", default="5432")
    DB_NAME: str = os.getenv("DB_NAME", default="test_db")
    DB_USER: str = os.getenv("DB_USER", default="test_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", default="test_pass")
    SECRET_KEY: str = os.getenv("SECRET_TOKEN_KEY", default="DyFQ5iJYbc_vDISsJWAW_tPoU9OJibzKhqorSFAiIdQ")

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", default="test_token")
    
    APP_MODE: str = os.getenv("APP_MODE", default="development")
    ADMIN_USERNAME: str | None = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD")
    

def get_settings() -> Settings:
    return Settings()