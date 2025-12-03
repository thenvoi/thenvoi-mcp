import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP
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


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    logger.info("Initializing Thenvoi API client")
    client = RestClient(
        api_key=settings.thenvoi_api_key,
        base_url=settings.thenvoi_base_url,
    )
    
    app_context = AppContext(client=client)
    logger.info("Thenvoi MCP server lifespan started successfully")

    try:
        yield {"app_context": app_context}
    except Exception as e:
        logger.error(f"Error during lifespan: {e}", exc_info=True)
        raise
    finally:
        logger.info("Thenvoi MCP server lifespan shutting down...")
        # Perform any necessary cleanup here
        try:
            # Close any open connections if the client supports it
            if hasattr(client, "close"):
                client.close()
                logger.debug("Closed Thenvoi API client connection")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
        logger.info("Thenvoi MCP server lifespan shutdown complete")


def get_app_context(ctx: Context) -> AppContext:
    """
    Helper to extract AppContext from the lifespan context.
    
    Usage in tools:
        app_ctx = get_app_context(ctx)
        client = app_ctx.client
    
    Raises:
        RuntimeError: If the AppContext is not available or improperly configured.
    """
    lifespan_ctx = ctx.request_context.lifespan_context
    
    if isinstance(lifespan_ctx, dict):
        app_context = lifespan_ctx.get("app_context")
        if app_context is None:
            raise RuntimeError(
                "AppContext not found in lifespan context. "
                "Ensure the server lifespan is properly configured."
            )
        if not isinstance(app_context, AppContext):
            raise RuntimeError(
                f"Expected AppContext, got {type(app_context).__name__}. "
                "Lifespan context is misconfigured."
            )
        return app_context
    
    if isinstance(lifespan_ctx, AppContext):
        return lifespan_ctx
    
    raise RuntimeError(
        f"Invalid lifespan context type: {type(lifespan_ctx).__name__}. "
        "Expected dict or AppContext."
    )


# MCP server instance with lifespan for proper dependency injection
mcp = FastMCP(name="thenvoi-mcp-server", lifespan=app_lifespan)

# Module-level client for tools that import it directly
client = RestClient(
    api_key=settings.thenvoi_api_key,
    base_url=settings.thenvoi_base_url,
)
