from mcp.server.fastmcp import Context

from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import mcp, logger, get_app_context

# Import tools to register them with the MCP server
from thenvoi_mcp.tools import agents  # noqa: F401
from thenvoi_mcp.tools import chats  # noqa: F401
from thenvoi_mcp.tools import messages  # noqa: F401
from thenvoi_mcp.tools import participants  # noqa: F401


@mcp.tool()
async def health_check(ctx: Context) -> str:
    """Test MCP server and API connectivity."""
    try:
        app_ctx = get_app_context(ctx)

        # Verify configuration exists
        if not app_ctx or not app_ctx.client:
            return "Health check failed: API client not initialized"

        if not settings.thenvoi_api_key or not settings.thenvoi_base_url:
            return "Health check failed: API key or base URL not configured"

        client = app_ctx.client
        client.agents.list_agents()

        return f"MCP server operational\nBase URL: {settings.thenvoi_base_url}"
    except Exception as e:
        return f"Health check failed: {str(e)}"

def run() -> None:
    """Run the MCP server with STDIO transport."""
    logger.info("Starting thenvoi-mcp-server v1.0.0")
    logger.info(f"Base URL: {settings.thenvoi_base_url}")
    logger.info("Server ready - listening for MCP protocol messages on STDIO")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
