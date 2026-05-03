from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    app_name: str = "Toán Socratic API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Anthropic API
    anthropic_api_key: str

    # LLM Configuration
    llm_provider: str = "anthropic"  # anthropic, openai, cohere, azure, qwen, gemini
    llm_model: str = "claude-sonnet-4-6"
    llm_api_key: Optional[str] = None  # Falls back to provider-specific key if not set
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # Provider-specific API keys
    openai_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/toansc"

    # JWT Configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # NextAuth
    nextauth_secret: str
    nextauth_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
