import json
import logging
from typing import Any, Dict, Optional, cast

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def list_chats(
    ctx: AppContextType,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    chat_type: Optional[str] = None,
) -> str:
    """List all accessible chat rooms.

    Retrieves a list of chat rooms with support for pagination and filtering.

    Args:
        page: Page number for pagination (optional).
        per_page: Number of items per page (optional).
        status: Filter by chat status: 'active', 'archived', or 'closed' (optional).
        chat_type: Filter by chat type: 'direct', 'group', or 'task' (optional).

    Returns:
        JSON string containing the list of chat rooms.
    """
    logger.debug("Fetching list of chats")
    client = get_app_context(ctx).client
    result = client.chat_rooms.list_chats(
        page=page,
        per_page=per_page,
        status=status,
        type=chat_type,
    )
    logger.info(f"Retrieved {len(result.data or [])} chats")
    return serialize_response(result)


@mcp.tool()
def get_chat(ctx: AppContextType, chat_id: str) -> str:
    """Get a specific chat room by ID.

    Retrieves detailed information about a single chat room.

    Args:
        chat_id: The unique identifier of the chat room to retrieve (required).

    Returns:
        JSON string containing the chat room details.
    """
    logger.debug(f"Fetching chat with ID: {chat_id}")
    client = get_app_context(ctx).client
    result = client.chat_rooms.get_chat(id=chat_id)
    logger.info(f"Retrieved chat: {chat_id}")
    return serialize_response(result)


@mcp.tool()
def create_chat(
    ctx: AppContextType,    
    chat_type: str,
    title: str,
    status: str = "active",
    task_id: Optional[str] = None,
    metadata: Optional[str] = None,
) -> str:
    """Create a new chat room.

    Creates a new chat room with the specified configuration. Chat rooms are
    conversation spaces where users and agents can interact.

    The authenticated user will automatically be set as the owner.

    Args:
        title: The title/name of the chat room (default: 'New Session').
        chat_type: The type of chat: 'direct', 'group', or 'task' (default: 'group').
        status: Initial status: 'active', 'archived', or 'closed' (default: 'active').
        task_id: Optional ID of an associated task.
        metadata: Optional JSON string containing additional metadata (will be parsed as JSON).

    Returns:
        Success message with the created chat room's ID.
    """
    logger.debug(f"Creating chat: {title}")
    client = get_app_context(ctx).client

    # Get authenticated user's ID to use as owner (ensures they have access)
    profile = client.my_profile.get_my_profile()
    owner_id = profile.id
    if not owner_id:
        raise RuntimeError("Could not get authenticated user's ID")

    # Build request as dict to avoid sending null values (API rejects them)
    request_data: Dict[str, Any] = {
        "title": title,
        "type": chat_type,
        "owner_id": owner_id,
        "owner_type": "User",
        "status": status,
    }

    if task_id is not None:
        request_data["task_id"] = task_id

    if metadata is not None:
        try:
            request_data["metadata"] = json.loads(metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for metadata: {e}")
            raise ValueError(f"Invalid JSON for metadata: {str(e)}")

    result = client.chat_rooms.create_chat(chat=cast(Any, request_data))
    chat = result.data

    if chat is None:
        logger.error("Chat room created but response data is None")
        raise RuntimeError("Chat room created but ID not available in response")

    logger.info(f"Chat room created successfully: {chat.id}")
    return f"Chat room created successfully: {chat.id}"


@mcp.tool()
def update_chat(
    ctx: AppContextType,
    chat_id: str,
    title: Optional[str] = None,
    status: Optional[str] = None,
    metadata: Optional[str] = None,
) -> str:
    """Update an existing chat room.

    Updates a chat room's configuration. Only the fields provided will be updated
    (partial updates are supported). Fields not provided will remain unchanged.

    Args:
        chat_id: The unique identifier of the chat room to update (required).
        title: New title for the chat room.
        status: New status: 'active', 'archived', or 'closed'.
        metadata: New JSON string containing metadata (will be parsed as JSON).

    Returns:
        Success message with the updated chat room's ID.
    """
    logger.debug(f"Updating chat: {chat_id}")
    client = get_app_context(ctx).client

    # Build request as dict to avoid sending null values (API rejects them)
    update_data: Dict[str, Any] = {}

    if title is not None:
        update_data["title"] = title
    if status is not None:
        update_data["status"] = status
    if metadata is not None:
        try:
            update_data["metadata"] = json.loads(metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for metadata: {e}")
            raise ValueError(f"Invalid JSON for metadata: {str(e)}")

    result = client.chat_rooms.update_chat(id=chat_id, chat=cast(Any, update_data))
    chat = result.data

    if chat is None:
        logger.error(f"Chat {chat_id} updated but response data is None")
        raise RuntimeError("Chat room updated but ID not available in response")

    logger.info(f"Chat room updated successfully: {chat.id}")
    return f"Chat room updated successfully: {chat.id}"


@mcp.tool()
def delete_chat(ctx: AppContextType, chat_id: str) -> str:
    """Delete a chat room.

    Permanently deletes a chat room. This action cannot be undone.

    Args:
        chat_id: The unique identifier of the chat room to delete (required).

    Returns:
        Success message confirming deletion.
    """
    logger.debug(f"Deleting chat: {chat_id}")
    client = get_app_context(ctx).client
    client.chat_rooms.delete_chat(id=chat_id)
    logger.info(f"Chat room deleted successfully: {chat_id}")
    return f"Chat room deleted successfully: {chat_id}"
