import json
import logging
from typing import List, Optional

from thenvoi_api.core.api_error import ApiError

from thenvoi_mcp.shared import mcp, client

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_chat_messages(
    chat_id: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    since: Optional[str] = None,
    message_type: Optional[str] = None,
) -> str:
    """List messages in a chat room with sender names.

    Retrieves a list of messages from a specific chat room with support for
    pagination and filtering. Each message includes the sender's name (not just ID)
    so you can easily tag them when responding.

    Args:
        chat_id: The unique identifier of the chat room (required).
        page: Page number for pagination (optional).
        per_page: Number of items per page (optional).
        since: ISO 8601 timestamp to filter messages after this time (optional).
        message_type: Filter by message type: 'text', 'system', 'action', 'thought',
                      'guidelines', 'error', 'tool_call', 'tool_result', 'task' (optional).

    Returns:
        JSON string containing messages with sender_name field for easy tagging.
        Example: "sender_name": "john" means you can reply with "@john" to tag them.
    """
    logger.debug(f"Fetching messages for chat: {chat_id}")

    # Parse since timestamp if provided
    since_dt = None
    if since is not None:
        from datetime import datetime

        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError as e:
            logger.error(f"Invalid ISO 8601 timestamp for since: {e}")
            raise ValueError(f"Invalid ISO 8601 timestamp for since: {str(e)}")

    result = client.chat_messages.list_chat_messages(
        chat_id=chat_id,
        page=page,
        per_page=per_page,
        since=since_dt,
        message_type=message_type,
    )

    messages_list = result.data if hasattr(result, "data") else []
    messages_list = messages_list or []

    # Fetch participants to get sender names
    participants_result = client.chat_participants.list_chat_participants(
        chat_id=chat_id
    )
    participants_data = (
        participants_result.data if hasattr(participants_result, "data") else []
    )
    participants_data = participants_data or []

    # Build participant map with names
    participant_map = {}
    for p in participants_data:
        p_id = (
            p.participant_id
            if hasattr(p, "participant_id")
            else (p.id if hasattr(p, "id") else None)
        )
        if p_id:
            # For agents, use agent_name; for users, use name
            display_name = None
            if hasattr(p, "agent_name") and p.agent_name:
                display_name = p.agent_name
            elif hasattr(p, "name") and p.name:
                display_name = p.name

            participant_map[p_id] = display_name or p_id

    messages_data = {
        "messages": [
            {
                "id": getattr(msg, "id", None),
                "content": getattr(msg, "content", None),
                "sender_id": getattr(msg, "sender_id", None),
                "sender_name": participant_map.get(
                    getattr(msg, "sender_id", None), "Unknown"
                ),
                "sender_type": getattr(msg, "sender_type", None),
                "message_type": getattr(msg, "message_type", None),
                "created_at": str(getattr(msg, "created_at", "")),
                "delivery_status": getattr(msg, "delivery_status", None),
                "mentions": getattr(msg, "mentions", None),
            }
            for msg in messages_list
        ]
    }
    if hasattr(result, "page"):
        messages_data["page"] = result.page
    if hasattr(result, "per_page"):
        messages_data["per_page"] = result.per_page
    if hasattr(result, "total"):
        messages_data["total"] = result.total

    logger.info(f"Retrieved {len(messages_list)} messages for chat: {chat_id}")
    return json.dumps(messages_data, indent=2)


@mcp.tool()
async def create_chat_message(
    chat_id: str,
    content: str,
    recipient_ids: Optional[str] = None,
    message_type: Optional[str] = None,
    participants: Optional[List[dict]] = None,
) -> str:
    """Send a message to a chat room.

    Args:
        chat_id: Chat room UUID.
        content: Message text. Use @name for mentions (e.g. "@John Hello"), never UUIDs.
        recipient_ids: Comma-separated UUIDs for mention tracking.
        message_type: Message type (default: 'text').
        participants: Array of {id, name} dicts. Skips API call if provided.

    Returns:
        Success message with created message ID.
    """
    logger.debug(f"Creating message in chat: {chat_id}")

    # Get the authenticated user's ID from the API key
    profile = client.my_profile.get_my_profile()
    sender_id = profile.data.id if hasattr(profile, "data") else profile.id
    logger.debug(f"Authenticated user ID: {sender_id}")

    # Build participant maps (by ID and by name)
    participant_by_id = {}
    participant_by_name = {}

    if participants:
        # Use provided participants (from caller's cache)
        for p in participants:
            p_id = p["id"]
            display_name = p["name"]
            participant_by_id[p_id] = display_name
            participant_by_name[display_name.lower()] = {
                "id": p_id,
                "name": display_name,
            }
        logger.debug(f"Using {len(participants)} cached participants")
    else:
        # Fallback: fetch from API
        participants_result = client.chat_participants.list_chat_participants(
            chat_id=chat_id
        )
        participants_data = (
            participants_result.data if hasattr(participants_result, "data") else []
        )
        participants_data = participants_data or []

        for p in participants_data:
            p_id = (
                p.participant_id
                if hasattr(p, "participant_id")
                else (p.id if hasattr(p, "id") else None)
            )
            if p_id:
                display_name = None
                if hasattr(p, "agent_name") and p.agent_name:
                    display_name = p.agent_name
                elif hasattr(p, "name") and p.name:
                    display_name = p.name
                elif hasattr(p, "first_name") and p.first_name:
                    display_name = p.first_name
                    if hasattr(p, "last_name") and p.last_name:
                        display_name = f"{p.first_name} {p.last_name}"
                display_name = display_name or p_id
                participant_by_id[p_id] = display_name
                participant_by_name[display_name.lower()] = {
                    "id": p_id,
                    "name": display_name,
                }
        logger.debug(f"Fetched {len(participants_data)} participants from API")

    # Build mentions list by checking if any participant name appears after @ in content
    mentions_list = []
    content_lower = content.lower()
    for name_lower, p in participant_by_name.items():
        if f"@{name_lower}" in content_lower:
            mentions_list.append({"id": p["id"], "username": p["name"]})

    # Also process recipient_ids if provided (add to mentions if not already present)
    if recipient_ids:
        recipient_list = [
            rid.strip() for rid in recipient_ids.split(",") if rid.strip()
        ]
        existing_ids = {m["id"] for m in mentions_list}
        for rid in recipient_list:
            if rid in participant_by_id and rid not in existing_ids:
                mentions_list.append({"id": rid, "username": participant_by_id[rid]})

    # Build request
    request_data = {
        "content": content,
        "sender_id": sender_id,
        "sender_type": "User",  # Always User since we're sending from authenticated user
    }
    if message_type is not None:
        request_data["message_type"] = message_type
    else:
        request_data["message_type"] = "text"  # Default to text

    if mentions_list:
        request_data["mentions"] = mentions_list

    # Send the message
    result = client.chat_messages.create_chat_message(
        chat_id=chat_id,
        message=request_data,  # type: ignore
    )
    message = result.data if hasattr(result, "data") else result  # type: ignore

    if message is None:
        logger.error("Message sent but response data is None")
        raise RuntimeError("Message sent but ID not available in response")

    message_id = getattr(message, "id", "unknown")
    logger.info(f"Message sent successfully: {message_id}")
    return f"Message sent successfully: {message_id}"


# TODO: check if neeeded
@mcp.tool()
async def delete_chat_message(chat_id: str, message_id: str) -> str:
    """Delete a message from a chat room.

    Permanently deletes a message from the specified chat room.
    This action cannot be undone.

    Args:
        chat_id: The unique identifier of the chat room (required).
        message_id: The unique identifier of the message to delete (required).

    Returns:
        Success message confirming deletion.
    """
    logger.debug(f"Deleting message {message_id} from chat {chat_id}")
    try:
        client.chat_messages.delete_chat_message(chat_id=chat_id, id=message_id)
        logger.info(f"Message deleted successfully: {message_id}")
        return f"Message deleted successfully: {message_id}"
    except ApiError as e:
        # HTTP 204 (No Content) is a successful delete response that some APIs treat as error
        error_str = str(e)
        if "status_code: 204" in error_str or "204" in error_str:
            logger.info(f"Message deleted successfully (204 response): {message_id}")
            return f"Message deleted successfully: {message_id}"
        # Re-raise the actual API error
        logger.error(f"Failed to delete message {message_id}: {e}")
        raise
