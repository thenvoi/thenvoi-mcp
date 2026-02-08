from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API configuration
    thenvoi_api_key: str = ""
    thenvoi_base_url: str = "https://app.thenvoi.com"

    # Transport configuration
    transport: Literal["stdio", "sse"] = "stdio"

    # SSE server configuration (only used when transport="sse")
    host: str = "127.0.0.1"
    port: int = 8000

    # Transport security (DNS rebinding protection)
    # When enabled, only requests with Host headers in allowed_hosts are accepted.
    # For Docker/remote deployments, configure allowed hosts:
    #   ALLOWED_HOSTS='["localhost:*","host.docker.internal:*"]'
    enable_dns_rebinding_protection: bool = True
    allowed_hosts: list[str] = []
    allowed_origins: list[str] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
