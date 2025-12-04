from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    thenvoi_api_key: str = ""
    thenvoi_base_url: str = "https://app.thenvoi.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
