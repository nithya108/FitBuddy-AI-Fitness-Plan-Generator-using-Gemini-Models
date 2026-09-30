from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy – AI Fitness Plan Generator"

    database_url: str = "sqlite:///./fitbuddy.db"

    gemini_api_key: str | None = None

    # These can be changed in .env if required.
    gemini_workout_model: str = "gemini-3.5-flash"
    gemini_tip_model: str = "gemini-3.5-flash"

    # true = application works without an API key
    # false = use Gemini
    demo_mode: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()