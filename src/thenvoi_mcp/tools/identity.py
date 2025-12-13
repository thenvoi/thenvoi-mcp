"""Agent identity and peer discovery tools.

This module provides tools for:
- Agent identity (getAgentMe) - get current agent's profile
- Peer discovery (listAgentPeers) - find agents to recruit
"""

import logging
from typing import Optional

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def getAgentMe(ctx: AppContextType) -> str:
    """Get the current agent's profile.

    Returns the profile of the authenticated agent, including ID, name,
    description, and other metadata. Also serves as connection validation -
    if this returns successfully, the API key is valid.

    Returns:
        JSON string containing the agent's profile.
    """
    logger.debug("Fetching agent profile")
    client = get_app_context(ctx).client
    result = client.agent_api.get_agent_me()
    logger.info(f"Retrieved agent profile: {result.data.name}")
    return serialize_response(result)


@mcp.tool()
def listAgentPeers(
    ctx: AppContextType,
    notInChat: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
) -> str:
    """List agents that can be recruited by the current agent.

    Returns a list of peers (other agents) that can be added to chat rooms.
    Includes sibling agents (same owner) and global agents. Excludes self.

    Use the notInChat parameter to filter out agents already in a specific
    chat room - useful when looking for new collaborators to add.

    Args:
        notInChat: Exclude agents already in this chat room ID (optional).
        page: Page number for pagination (optional).
        pageSize: Number of items per page (optional).

    Returns:
        JSON string containing the list of available peers.
    """
    logger.debug("Fetching agent peers")
    client = get_app_context(ctx).client
    result = client.agent_api.list_agent_peers(
        not_in_chat=notInChat,
        page=page,
        page_size=pageSize,
    )
    peer_count = len(result.data or []) if hasattr(result, "data") else 0
    logger.info(f"Retrieved {peer_count} peers")
    return serialize_response(result)
