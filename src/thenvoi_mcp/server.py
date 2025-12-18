from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import AppContextType, get_app_context, logger, mcp


def get_key_type(key: str) -> str:
    """Get API key type.

    Key formats:
    - User keys: thnv_u_<timestamp>_<random>
    - Agent keys: thnv_a_<timestamp>_<random>
    - Legacy keys: thnv_<timestamp>_<random> (loads all tools)
    """
    if key.startswith("thnv_u_"):
        return "user"
    elif key.startswith("thnv_a_"):
        return "agent"
    elif key.startswith("thnv_"):
        return "legacy"
    return "unknown"


key_type = get_key_type(settings.thenvoi_api_key)

# Import tools based on API key type - they register via @mcp.tool() decorator
if key_type in ("agent", "legacy"):
    from thenvoi_mcp.tools.agent import (  # noqa: F401
        agent_chats,
        agent_events,
        agent_identity,
        agent_lifecycle,
        agent_messages,
        agent_participants,
    )

if key_type in ("user", "legacy"):
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
    try:
        if key_type == "user":
            client.human_api.list_my_agents()
        elif key_type == "agent":
            client.agent_api.get_agent_me()
        else:  # legacy - try both
            client.human_api.list_my_agents()
            client.agent_api.get_agent_me()
        return f"OK | {key_type} | {settings.thenvoi_base_url}"
    except Exception as e:
        return f"Failed | {key_type} | {e}"


def run() -> None:
    """Run the MCP server with STDIO transport."""
    logger.info("Starting thenvoi-mcp-server v1.0.0")
    logger.info(f"Base URL: {settings.thenvoi_base_url}")
    logger.info(f"API key type: {key_type if settings.thenvoi_api_key else 'none'}")
    logger.info("Server ready - listening for MCP protocol messages on STDIO")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
