from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    thenvoi_api_key: str = ""
    thenvoi_base_url: str = "https://app.thenvoi.com"

    # Tool Filtering
    enabled_tools: str = (
        ""  # Comma-separated list of enabled tools (empty = all enabled)
    )
    read_only_mode: bool = False  # If True, only allow read operations

    # Transport settings
    mcp_transport: Literal["stdio", "sse"] = "stdio"
    mcp_host: str = "127.0.0.1"  # SSE server host
    mcp_port: int = 8000  # SSE server port

    # Logging and Debug
    mcp_very_verbose: bool = False  # Detailed logging
    mcp_logging_stdout: bool = False  # Log to stdout

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
