import json
import logging
from typing import Optional, Any, Dict

from mcp.server.fastmcp import Context

from thenvoi_mcp.shared import mcp, get_app_context

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_chats(
    ctx: Context,
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
    chats_list = result.data if hasattr(result, "data") else []
    chats_list = chats_list or []

    chats_data = {
        "chats": [
            {
                "id": getattr(chat, "id", None),
                "title": getattr(chat, "title", None),
                "type": getattr(chat, "type", None),
                "status": getattr(chat, "status", None),
                "owner_id": getattr(chat, "owner_id", None),
                "owner_type": getattr(chat, "owner_type", None),
                "task_id": getattr(chat, "task_id", None),
                "metadata": getattr(chat, "metadata", None),
            }
            for chat in chats_list
        ]
    }
    if hasattr(result, "page"):
        chats_data["page"] = result.page
    if hasattr(result, "per_page"):
        chats_data["per_page"] = result.per_page
    if hasattr(result, "total"):
        chats_data["total"] = result.total

    logger.info(f"Retrieved {len(chats_list)} chats")
    return json.dumps(chats_data, indent=2)


@mcp.tool()
async def get_chat(ctx: Context, chat_id: str) -> str:
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
    chat = result.data if hasattr(result, "data") else result

    chat_data = {
        "id": getattr(chat, "id", None),
        "title": getattr(chat, "title", None),
        "type": getattr(chat, "type", None),
        "status": getattr(chat, "status", None),
        "owner_id": getattr(chat, "owner_id", None),
        "owner_type": getattr(chat, "owner_type", None),
        "task_id": getattr(chat, "task_id", None),
        "metadata": getattr(chat, "metadata", None),
    }
    logger.info(f"Retrieved chat: {chat_id}")
    return json.dumps(chat_data, indent=2)


@mcp.tool()
async def create_chat(
    ctx: Context,
    title: str,
    chat_type: str,
    owner_id: str,
    owner_type: str,
    status: str = "active",
    task_id: Optional[str] = None,
    metadata: Optional[str] = None,
) -> str:
    """Create a new chat room.

    Creates a new chat room with the specified configuration. Chat rooms are
    conversation spaces where users and agents can interact.

    Args:
        title: The title/name of the chat room (required).
        chat_type: The type of chat: 'direct', 'group', or 'task' (required).
        owner_id: ID of the owner (user or agent) (required).
        owner_type: Type of owner: 'User' or 'Agent' (required).
        status: Initial status: 'active', 'archived', or 'closed' (default: 'active').
        task_id: Optional ID of an associated task.
        metadata: Optional JSON string containing additional metadata (will be parsed as JSON).

    Returns:
        Success message with the created chat room's ID.
    """
    logger.debug(f"Creating chat: {title}")
    client = get_app_context(ctx).client

    # Parse metadata if provided
    metadata_dict = None
    if metadata is not None:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for metadata: {e}")
            raise ValueError(f"Invalid JSON for metadata: {str(e)}")

    # Build request with only non-None values
    request_data = {
        "title": title,
        "type": chat_type,
        "owner_id": owner_id,
        "owner_type": owner_type,
        "status": status,
    }
    if task_id is not None:
        request_data["task_id"] = task_id
    if metadata_dict is not None:
        request_data["metadata"] = metadata_dict

    result = client.chat_rooms.create_chat(chat=request_data)  # type: ignore
    chat = result.data if hasattr(result, "data") else result  # type: ignore

    if chat is None:
        logger.error("Chat room created but response data is None")
        raise RuntimeError("Chat room created but ID not available in response")

    chat_id = getattr(chat, "id", "unknown")
    logger.info(f"Chat room created successfully: {chat_id}")
    return f"Chat room created successfully: {chat_id}"


@mcp.tool()
async def update_chat(
    ctx: Context,
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

    # Build update request with only provided fields
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

    result = client.chat_rooms.update_chat(id=chat_id, chat=update_data)  # type: ignore
    chat = result.data if hasattr(result, "data") else result  # type: ignore

    if chat is None:
        logger.error(f"Chat {chat_id} updated but response data is None")
        raise RuntimeError("Chat room updated but ID not available in response")

    updated_chat_id = getattr(chat, "id", "unknown")
    logger.info(f"Chat room updated successfully: {updated_chat_id}")
    return f"Chat room updated successfully: {updated_chat_id}"


@mcp.tool()
async def delete_chat(ctx: Context, chat_id: str) -> str:
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
