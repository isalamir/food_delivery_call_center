"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Food Delivery Call Center"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./call_center.db"

    # Refund policy thresholds
    REFUND_STRIKE_LIMIT: int = 2
    MAX_AUTO_REFUND_AMOUNT: float = 50.0

    # No-show timer (seconds)
    NO_SHOW_TIMEOUT: int = 300

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
