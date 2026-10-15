from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/prices"
    redis_url: str = "redis://localhost:6379/0"
    deribit_base_url: str = "https://www.deribit.com/api/v2"
    fetch_interval_seconds: int = 60
    request_timeout_seconds: float = 10.0
