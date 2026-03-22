"""
FastAPI application configuration.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AHP Portfolio Selector"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Data settings
    default_period_years: int = 2
    max_stocks_per_index: int = 50

    # WebSocket settings
    ws_poll_interval_seconds: int = 30

    # Cache TTL (seconds)
    market_cache_ttl: int = 60
    analysis_cache_ttl: int = 300

    class Config:
        env_prefix = "AHP_"


settings = Settings()
