from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


def normalize_database_url(value: str) -> str:
    """Use SQLAlchemy's asyncpg driver when providers expose a plain Postgres URL."""
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+asyncpg://", 1)
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+asyncpg://", 1)
    return value


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # API Configuration
    app_name: str = "Toán Socratic API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM Configuration
    llm_provider: str = "anthropic"  # anthropic, openai, cohere, azure, qwen, gemini
    llm_model: str = "claude-sonnet-4-6"
    llm_api_key: Optional[str] = None  # Generic API key (optional, falls back to provider-specific keys)
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024
    llm_timeout: int = 60  # Timeout in seconds for LLM API calls (default 60s, LiteLLM default is 120s)

    # Provider-specific API keys (optional, used if llm_api_key not set)
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/toansc"
    redis_url: str = "redis://redis:6379"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.0

    # JWT Configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    auth_bridge_secret: Optional[str] = None

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # NextAuth
    nextauth_secret: str
    nextauth_url: str = "http://localhost:3000"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        return normalize_database_url(value)

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_auth_bridge_secret(self) -> str:
        return self.auth_bridge_secret or self.nextauth_secret

settings = Settings()
