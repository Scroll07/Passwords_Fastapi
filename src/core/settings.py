# import pydantic_settings

# class Settings(pydantic_settings.BaseSettings):
#    DB_HOST: str
#    DB_PORT: str
#    DB_NAME: str
#    DB_USER: str
#    DB_PASSWORD: str

#    BOT_TOKEN: str

#    model_config = pydantic_settings.SettingsConfigDict(
#        env_file=".env",
#        env_file_encoding="utf-8",
#        )


# settings = Settings() # type: ignore

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKUPS = BASE_DIR / "BACKUPS_DATA"


class Settings:
    DB_HOST: str = os.getenv("DB_HOST", default="localhost")
    DB_PORT: str = os.getenv("DB_PORT", default="5432")
    DB_NAME: str = os.getenv("DB_NAME", default="test_db")
    DB_USER: str = os.getenv("DB_USER", default="test_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", default="test_password")
    SECRET_TOKEN_KEY: str = os.getenv("SECRET_TOKEN_KEY", default="test_token")

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", default="test_token")


settings = Settings()
