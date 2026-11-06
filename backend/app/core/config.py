from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "MediVision AI"
    environment: str = "development"
    secret_key: str = "development-only-change-this-secret"
    access_token_expire_minutes: int = 720
    database_url: str = "sqlite:///./medivision.db"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "uploads"
    max_upload_mb: int = 8
    openai_api_key: str = ""
    openai_model: str = "gpt-6-mini"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def origins(self):
        return [x.strip() for x in self.frontend_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
