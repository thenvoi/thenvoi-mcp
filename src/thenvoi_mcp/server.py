import argparse
from typing import Literal

from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import mcp, logger, get_app_context, AppContextType

VERSION = "1.0.0"


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
        return f"OK | {key_type} | {settings.thenvoi_base_url}"
    except Exception as e:
        return f"Failed | {key_type} | {e}"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Thenvoi MCP Server - Connect AI agents to Thenvoi platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport Modes:
  stdio   Default mode for IDE integration (Cursor, Claude Desktop, etc.)
          Communication via standard input/output streams.

  sse     HTTP server mode for remote/Docker deployments.
          Runs as a persistent HTTP service with Server-Sent Events.
          Useful for cloud deployments, Docker containers, or shared
          team environments where multiple clients connect to a single
          server instance.

Examples:
  thenvoi-mcp                          # Run with STDIO (default)
  thenvoi-mcp --transport sse          # Run as HTTP server on 127.0.0.1:8000
  thenvoi-mcp --transport sse --port 3000 --host 0.0.0.0  # Custom host/port

Environment Variables:
  THENVOI_API_KEY       API key for Thenvoi platform (required)
  THENVOI_BASE_URL      Base URL for Thenvoi API (default: https://app.thenvoi.com)
  TRANSPORT             Transport mode: stdio or sse (default: stdio)
  HOST                  Host to bind for SSE mode (default: 127.0.0.1)
  PORT                  Port to bind for SSE mode (default: 8000)
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"thenvoi-mcp {VERSION}",
    )

    parser.add_argument(
        "--transport",
        "-t",
        type=str,
        choices=["stdio", "sse"],
        default=None,
        help="Transport mode: stdio (default) or sse",
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind for SSE mode (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=None,
        help="Port to bind for SSE mode (default: 8000)",
    )

    return parser.parse_args()


def run() -> None:
    """Run the MCP server with configurable transport mode.

    Supports two transport modes:
    - STDIO (default): For IDE integration with Cursor, Claude Desktop, etc.
    - SSE: For remote deployments, Docker containers, or shared team environments.

    Configuration can be set via:
    1. Command line arguments (highest priority)
    2. Environment variables
    3. Default values (lowest priority)
    """
    args = parse_args()

    # Determine transport mode (CLI args override env vars)
    transport: Literal["stdio", "sse"] = args.transport or settings.transport

    # Update settings for SSE mode if CLI args provided
    if args.host is not None:
        mcp.settings.host = args.host
    if args.port is not None:
        mcp.settings.port = args.port

    logger.info(f"Starting thenvoi-mcp-server v{VERSION}")
    logger.info(f"Base URL: {settings.thenvoi_base_url}")
    logger.info(f"API key type: {key_type}")

    if transport == "stdio":
        logger.info("Transport: STDIO (for IDE integration)")
        logger.info("Server ready - listening for MCP protocol messages on STDIO")
        mcp.run(transport="stdio")
    else:
        host = args.host or settings.host
        port = args.port or settings.port
        logger.info("Transport: SSE (HTTP server mode)")
        logger.info(f"Server ready - listening on http://{host}:{port}")
        logger.info("SSE endpoint: /sse | Messages endpoint: /messages/")
        mcp.run(transport="sse")


if __name__ == "__main__":
    run()
