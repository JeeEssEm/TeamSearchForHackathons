from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 0
    DB_NAME: str = 'db'
    DB_USER: str = 'pguser'
    DB_PASSWORD: str = 'password'

    DEBUG: bool = True
    TRUST_FACTOR: bool = False
    INIT_MODELS: bool = True

    S3_ACCESS_KEY_ID: str = 'access key'
    S3_SECRET_ACCESS_KEY: str = 'secret key'
    S3_ENDPOINT: str = 'endpoint url'


settings = Settings()


def get_database_url():
    return 'sqlite+aiosqlite:///./db.sqlite'
