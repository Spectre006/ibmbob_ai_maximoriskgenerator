"""Application settings and configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # IBM Maximo API Configuration
    maximo_api_url: str
    maximo_api_key: str
    maximo_username: str
    maximo_password: str
    maximo_site_id: str = "BEDFORD"  # Default site ID
    maximo_cookie: Optional[str] = None  # Optional session cookie

    # IBM Watsonx.ai Configuration
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "ibm/granite-3-8b-instruct"

    # IBM Cloudant Configuration
    cloudant_url: str
    cloudant_api_key: str
    cloudant_database: str = "jha_reports"

    # Application Configuration
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Performance Configuration
    maximo_cache_ttl: int = 300  # 5 minutes
    ai_timeout: int = 30  # seconds
    max_retries: int = 3

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"


# Global settings instance
settings = Settings()

# Made with Bob
