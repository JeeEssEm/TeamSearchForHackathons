from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "tsfh_db"
    DB_USER: str = "jes"
    DB_PASSWORD: str = "pwd123qwe"

    DEBUG: bool = False
    TRUST_FACTOR: bool = False
    INIT_MODELS: bool = True

    S3_ACCESS_KEY_ID: str = "access key"
    S3_SECRET_ACCESS_KEY: str = "secret key"
    S3_ENDPOINT: str = "endpoint url"

    MODERATOR_FORM_ROTATION_DAYS: int = 2


settings = Settings()


def get_database_url():
    if settings.DEBUG:
        return "sqlite+aiosqlite:///./db.sqlite"
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
