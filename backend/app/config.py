"""
Central configuration, loaded from environment variables (or a .env file).
See .env.example for the full list of supported settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/epicenter"

    # --- Auth ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # --- Optional LLM summarization (Claude) ---
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Scheduler ---
    etl_schedule_hours: int = 24  # how often the scheduled ETL job re-runs
    usgs_feed_url: str = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    )


settings = Settings()
