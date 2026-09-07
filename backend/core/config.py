from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6"
    stockscan_api_token: str = "change-me"
    database_url: str = "sqlite:///./stockscan.db"
    max_image_mb: int = 12
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()
