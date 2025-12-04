import json
import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from pydantic import BaseModel
from thenvoi.client.rest import RestClient

from thenvoi_mcp.config import settings

# Configure logging to stderr only
# CRITICAL: NEVER log to stdout - it's used for STDIO transport communication
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # NEVER stdout for STDIO transport
)
logger = logging.getLogger("thenvoi-mcp")


@dataclass
class AppContext:
    """
    Type-safe container for application dependencies.
    """

    client: RestClient


AppContextType = Context[ServerSession, AppContext, None]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    logger.info("Initializing Thenvoi API client")
    client = RestClient(
        api_key=settings.thenvoi_api_key,
        base_url=settings.thenvoi_base_url,
    )

    app_context = AppContext(client=client)
    logger.info("Thenvoi MCP server lifespan started successfully")

    try:
        yield app_context
    finally:
        logger.info("Thenvoi MCP server lifespan shutdown complete")


def get_app_context(ctx: AppContextType) -> AppContext:
    """
    Helper to extract AppContext from the lifespan context.

    Usage in tools:
        app_ctx = get_app_context(ctx)
        client = app_ctx.client
    """
    return ctx.request_context.lifespan_context


def serialize_response(result: Any, **kwargs) -> str:
    """
    Serialize a Pydantic model response to JSON.

    Uses model_dump() for Pydantic models, enabling clean serialization
    without manual field extraction.

    Args:
        result: A Pydantic model or any object with model_dump() method.
        **kwargs: Additional arguments passed to model_dump() (e.g., exclude, include).

    Returns:
        JSON string representation of the result.
    """
    if isinstance(result, BaseModel):
        return json.dumps(result.model_dump(**kwargs), indent=2, default=str)
    # Fallback for non-Pydantic objects
    return json.dumps(result, indent=2, default=str)


# MCP server instance with lifespan for proper dependency injection
mcp = FastMCP(name="thenvoi-mcp-server", lifespan=app_lifespan)
