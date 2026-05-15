from toan_socratic.config import Settings, normalize_database_url


def test_normalize_database_url_uses_asyncpg_for_plain_postgres_urls() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@host:5432/toansc")
        == "postgresql+asyncpg://user:pass@host:5432/toansc"
    )
    assert (
        normalize_database_url("postgres://user:pass@host:5432/toansc")
        == "postgresql+asyncpg://user:pass@host:5432/toansc"
    )


def test_database_url_uses_asyncpg_for_plain_postgresql_url() -> None:
    settings = Settings(
        database_url="postgresql://user:pass@host:5432/toansc",
        jwt_secret="jwt-secret",
        nextauth_secret="nextauth-secret",
    )

    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/toansc"


def test_database_url_keeps_explicit_async_driver() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://user:pass@host:5432/toansc",
        jwt_secret="jwt-secret",
        nextauth_secret="nextauth-secret",
    )

    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/toansc"
