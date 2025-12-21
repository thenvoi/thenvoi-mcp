import argparse
from typing import Literal

from mcp.server.fastmcp import Context

from thenvoi_mcp.config import settings
from thenvoi_mcp.shared import mcp, logger, get_app_context

# Import tools to register them with the MCP server
from thenvoi_mcp.tools import agents  # noqa: F401
from thenvoi_mcp.tools import chats  # noqa: F401
from thenvoi_mcp.tools import messages  # noqa: F401
from thenvoi_mcp.tools import participants  # noqa: F401

VERSION = "1.0.0"


@mcp.tool()
def health_check(ctx: Context) -> str:
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
