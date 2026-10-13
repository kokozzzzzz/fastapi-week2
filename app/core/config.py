
from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Week 2"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


setting = Settings()


