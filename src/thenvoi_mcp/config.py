from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    thenvoi_api_key: str = ""
    thenvoi_base_url: str = "https://app.thenvoi.com"

    # Logging and Debug
    mcp_very_verbose: bool = False  # Detailed logging
    mcp_logging_stdout: bool = False  # Log to stdout

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
