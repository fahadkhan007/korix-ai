from pydantic_settings import BaseSettings, SettingsConfigDict # type: ignore
from pydantic import PostgresDsn #type: ignore

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    DATABASE_URL: PostgresDsn
    GEMINI_API_KEY: str





settings = Settings()  # type: ignore
