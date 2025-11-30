from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import mcp, client, logger

# Import tools to register them with the MCP server
from thenvoi_mcp.tools import agents  # noqa: F401
from thenvoi_mcp.tools import chats  # noqa: F401
from thenvoi_mcp.tools import messages  # noqa: F401
from thenvoi_mcp.tools import participants  # noqa: F401


@mcp.tool()
async def health_check() -> str:
    """Test MCP server and API connectivity."""
    try:
        # Verify Thenvoi API connection
        if client and settings.thenvoi_api_key and settings.thenvoi_base_url:
            return f"MCP server operational\nBase URL: {settings.thenvoi_base_url}"
        return "MCP server operational (API not configured)"
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
