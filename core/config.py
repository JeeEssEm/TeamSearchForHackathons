from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "db"  # Имя сервиса базы данных в docker-compose
    DB_PORT: int = 5432  # Порт PostgreSQL по умолчанию
    DB_NAME: str = "project_db"  # Имя базы данных
    DB_USER: str = "user"  # Имя пользователя базы данных
    DB_PASSWORD: str = "password"  # Пароль пользователя

    DEBUG: bool = True
    TRUST_FACTOR: bool = False
    INIT_MODELS: bool = True

    S3_ACCESS_KEY_ID: str = "access key"
    S3_SECRET_ACCESS_KEY: str = "secret key"
    S3_ENDPOINT: str = "endpoint url"

    MODERATOR_FORM_ROTATION_DAYS: int = 2


settings = Settings()


# Функция для генерации строки подключения к базе данных PostgreSQL
def get_database_url():
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
