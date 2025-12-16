from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import AppContextType, get_app_context, logger, mcp

from thenvoi_mcp.tools.agent import (  # noqa: F401
    agent_chats,
    agent_events,
    agent_identity,
    agent_lifecycle,
    agent_messages,
    agent_participants,
)
from thenvoi_mcp.tools.human import (  # noqa: F401
    human_agents,
    human_chats,
    human_messages,
    human_participants,
    human_profile,
)


@mcp.tool()
def health_check(ctx: AppContextType) -> str:
    """Test MCP server and API connectivity."""
    client = get_app_context(ctx).client

    if not settings.thenvoi_api_key:
        return "MCP server operational (no API key configured)"

    # Try agent first, then user
    try:
        result = client.agent_api.get_agent_me()
        agent = result.data
        return f"OK | Agent: {agent.name} | {settings.thenvoi_base_url}"
    except Exception:
        pass

    try:
        user = client.human_api.get_my_profile()
        # get_my_profile returns UserDetails directly (no .data wrapper)
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        return f"OK | User: {name} | {settings.thenvoi_base_url}"
    except Exception as e:
        return f"Failed: {e}"


def run() -> None:
    """Run the MCP server with STDIO transport."""
    logger.info("Starting thenvoi-mcp-server v1.0.0")
    logger.info(f"Base URL: {settings.thenvoi_base_url}")
    logger.info("Server ready - listening for MCP protocol messages on STDIO")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
