from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import AppContextType, get_app_context, logger, mcp

# Import tools to register them with the MCP server
from thenvoi_mcp.tools import agents  # noqa: F401
from thenvoi_mcp.tools import chats  # noqa: F401
from thenvoi_mcp.tools import messages  # noqa: F401
from thenvoi_mcp.tools import participants  # noqa: F401


@mcp.tool()
def health_check(ctx: AppContextType) -> str:
    """Test MCP server and API connectivity."""
    try:
        client = get_app_context(ctx).client
        if not client or not settings.thenvoi_api_key:
            return "MCP server operational (API not configured)"

        # Make actual API call to verify connectivity
        profile = client.my_profile.get_my_profile()
        return f"MCP server operational\nBase URL: {settings.thenvoi_base_url}\nAuthenticated user: {profile.id}"
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
