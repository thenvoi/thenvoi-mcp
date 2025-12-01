"""Shared MCP server and client instances."""

import logging
import sys

from mcp.server.fastmcp import FastMCP
from thenvoi_api import ThenvoiClient

from thenvoi_mcp.config import settings

# Configure logging to stderr only
# CRITICAL: NEVER log to stdout - it's used for STDIO transport communication
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # NEVER stdout for STDIO transport
)
logger = logging.getLogger("thenvoi-mcp")

# Global client instance
client = ThenvoiClient(
    api_key=settings.thenvoi_api_key,
    base_url=settings.thenvoi_base_url,
)

# Global MCP server instance
mcp = FastMCP(
    name="thenvoi-mcp-server",
    host=settings.mcp_host,
    port=settings.mcp_port,
)
