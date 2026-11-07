from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "MediVision AI"
    environment: str = "development"
    secret_key: str = "development-only-change-this-secret"
    access_token_expire_minutes: int = 45
    database_url: str = "sqlite:///./medivision.db"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "uploads"
    max_upload_mb: int = 8
    storage_backend: str = "local"
    s3_bucket: str = ""
    aws_endpoint_url_s3: str = ""
    aws_region: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.frontend_origins.split(",") if item.strip()]

    @model_validator(mode="after")
    def validate_production_configuration(self):
        if self.environment.lower() == "production":
            if len(self.secret_key) < 32 or self.secret_key == "development-only-change-this-secret":
                raise ValueError("SECRET_KEY must be a unique random value of at least 32 characters.")
            if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://", "postgres://")):
                raise ValueError("Production requires a managed PostgreSQL DATABASE_URL.")
            if self.storage_backend.lower() != "s3":
                raise ValueError("Production requires private S3-compatible object storage.")
            if not all([self.s3_bucket, self.aws_endpoint_url_s3, self.aws_region,
                        self.aws_access_key_id, self.aws_secret_access_key]):
                raise ValueError("Production object-storage configuration is incomplete.")
            if not self.origins or "*" in self.origins:
                raise ValueError("Production CORS must use explicit trusted origins.")
        if self.max_upload_mb < 1 or self.max_upload_mb > 25:
            raise ValueError("MAX_UPLOAD_MB must be between 1 and 25.")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
