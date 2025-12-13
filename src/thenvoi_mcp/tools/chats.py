"""Chat room management tools.

This module provides tools for managing chat rooms where the agent
participates using the agent-centric API.
"""

import logging
from typing import Optional

from thenvoi_rest import ChatRoomRequest

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def listAgentChats(
    ctx: AppContextType,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
) -> str:
    """List chat rooms where the agent is a participant.

    Retrieves a list of chat rooms that the authenticated agent participates in.
    Supports pagination.

    Args:
        page: Page number for pagination (optional).
        pageSize: Number of items per page (optional).

    Returns:
        JSON string containing the list of chat rooms.
    """
    logger.debug("Fetching agent's chat rooms")
    client = get_app_context(ctx).client
    result = client.agent_api.list_agent_chats(
        page=page,
        page_size=pageSize,
    )
    chat_count = len(result.data or []) if hasattr(result, "data") else 0
    logger.info(f"Retrieved {chat_count} chats")
    return serialize_response(result)


@mcp.tool()
def getAgentChat(ctx: AppContextType, chatId: str) -> str:
    """Get a specific chat room by ID.

    Retrieves detailed information about a single chat room where
    the agent is a participant.

    Args:
        chatId: The unique identifier of the chat room (required).

    Returns:
        JSON string containing the chat room details.
    """
    logger.debug(f"Fetching chat with ID: {chatId}")
    client = get_app_context(ctx).client
    result = client.agent_api.get_agent_chat(id=chatId)
    logger.info(f"Retrieved chat: {chatId}")
    return serialize_response(result)


@mcp.tool()
def createAgentChat(
    ctx: AppContextType,
    taskId: Optional[str] = None,
) -> str:
    """Create a new chat room with the agent as owner.

    Creates a new chat room where the authenticated agent is automatically
    set as the owner. Optionally associates the chat with a task.

    Args:
        taskId: Optional ID of an associated task.

    Returns:
        JSON string containing the created chat room details.
    """
    logger.debug("Creating new chat room")
    client = get_app_context(ctx).client

    # Build request
    chat_request = ChatRoomRequest(task_id=taskId) if taskId else ChatRoomRequest()

    result = client.agent_api.create_agent_chat(chat=chat_request)

    if result.data is None:
        logger.error("Chat room created but response data is None")
        raise RuntimeError("Chat room created but data not available in response")

    logger.info(f"Chat room created successfully: {result.data.id}")
    return serialize_response(result)
