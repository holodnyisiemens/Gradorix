from pathlib import Path

from pydantic import BaseModel,SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            BASE_DIR / ".env",
            BASE_DIR / ".env.local",
        ],
        extra="ignore",
    )

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_NAME: str

    SECRET_KEY: str
    HASH_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    GIGACHAT_TOKEN: str = ''

    VAPID_PRIVATE_KEY: str = ''
    VAPID_PUBLIC_KEY: str = ''
    VAPID_SUBSCRIBER: str = 'admin@gradorix.ru'

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "admin"
    MINIO_SECRET_KEY: str = "supersecret"
    MINIO_BUCKET: str = "uploads"

    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "gradorix"
    MONGO_PASSWORD: SecretStr = SecretStr("gradorix")
    MONGO_DB: str = "gradorix_chat"

    run: RunConfig = RunConfig()

    @property
    def database_url_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_psycopg(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def mongo_url(self) -> str:
        password = self.MONGO_PASSWORD.get_secret_value()
        return (
            f"mongodb://{self.MONGO_USER}:{password}@"
            f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
        )


settings = Settings()
