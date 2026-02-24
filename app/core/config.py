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


settings = Settings()
