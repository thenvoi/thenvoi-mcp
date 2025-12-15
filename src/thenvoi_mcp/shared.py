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
from thenvoi_rest import RestClient

from thenvoi_mcp.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("thenvoi-mcp")


@dataclass
class AppContext:
    """Type-safe container for application dependencies."""

    client: RestClient


AppContextType = Context[ServerSession, AppContext, None]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Lifespan context manager for MCP server."""
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
    """Helper to extract AppContext from the lifespan context.

    Usage in tools:
        app_ctx = get_app_context(ctx)
        client = app_ctx.client
    """
    return ctx.request_context.lifespan_context


def serialize_response(result: Any, **kwargs) -> str:
    """Serialize a Pydantic model response to JSON.

    Args:
        result: A Pydantic model or any object with model_dump() method.
        **kwargs: Additional arguments passed to model_dump().

    Returns:
        JSON string representation of the result.
    """
    # Check for model_dump method (duck typing) or isinstance (type checking)
    if hasattr(result, "model_dump") and callable(result.model_dump):
        return json.dumps(result.model_dump(**kwargs), indent=2, default=str)
    if isinstance(result, BaseModel):
        return json.dumps(result.model_dump(**kwargs), indent=2, default=str)
    return json.dumps(result, indent=2, default=str)


mcp = FastMCP(name="thenvoi-mcp-server", lifespan=app_lifespan)
