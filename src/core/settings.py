from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        )
    
    
settings = Settings() # type: ignore