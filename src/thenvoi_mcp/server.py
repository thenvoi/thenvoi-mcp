from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import AppContextType, get_app_context, logger, mcp

# Import tools to register them with the MCP server
from thenvoi_mcp.tools import identity  # noqa: F401
from thenvoi_mcp.tools import chats  # noqa: F401
from thenvoi_mcp.tools import participants  # noqa: F401
from thenvoi_mcp.tools import messages  # noqa: F401
from thenvoi_mcp.tools import events  # noqa: F401
from thenvoi_mcp.tools import lifecycle  # noqa: F401


@mcp.tool()
def healthCheck(ctx: AppContextType) -> str:
    """Test MCP server and API connectivity.

    Validates that the MCP server is running and can communicate with the
    Thenvoi API using the configured agent API key.
    """
    try:
        client = get_app_context(ctx).client
        if not client or not settings.thenvoi_api_key:
            return "MCP server operational (API not configured)"

        # Verify agent connectivity via agent_api
        agent = client.agent_api.get_agent_me()
        return f"MCP server operational\nBase URL: {settings.thenvoi_base_url}\nAuthenticated agent: {agent.data.name} ({agent.data.id})"
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
