import os

from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file = ".env" if os.path.exists(".env") else ".env.example"


class Settings(BaseSettings):

    DB_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    APP_ENV: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()