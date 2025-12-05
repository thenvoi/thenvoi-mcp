import json
import logging
from typing import Optional

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def list_chat_messages(
    ctx: AppContextType,
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
    client = get_app_context(ctx).client

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
    logger.info(f"Retrieved {len(result.data or [])} messages for chat: {chat_id}")
    return serialize_response(result)


@mcp.tool()
def create_chat_message(
    ctx: AppContextType,
    chat_id: str,
    content: str,
    mentions: Optional[str] = None,
    message_type: Optional[str] = None,
) -> str:
    """Send a message in a chat room.

    The sender is automatically determined from the API key (authenticated user or agent).

    Args:
        chat_id: The unique identifier of the chat room (required).
        content: The message content/text (required). Include @username in content
                 for each mentioned user.
        mentions: JSON array of mentions (optional). Each mention requires both fields:
                  [{"id": "user-uuid", "username": "display_name"}, ...]
                  Get IDs and usernames from list_chat_participants.
        message_type: Message type (optional, defaults to 'text').
                      Options: 'text', 'system', 'action', 'thought', 'error'.

    Returns:
        Success message with the created message's ID.

    Example:
        create_chat_message(
            chat_id="chat-123",
            content="@dan_agent hello there!",
            mentions='[{"id": "agent-uuid", "username": "dan_agent"}]'
        )
    """
    logger.debug(f"Creating message in chat: {chat_id}")
    client = get_app_context(ctx).client

    # Parse mentions if provided
    mentions_list = None
    if mentions:
        mentions_list = json.loads(mentions)

    # Build request - sender is determined by API from API key
    request_data = {
        "content": content,
        "message_type": message_type or "text",
    }

    if mentions_list:
        request_data["mentions"] = mentions_list

    # Send the message
    result = client.chat_messages.create_chat_message(
        chat_id=chat_id,
        message=request_data,  # type: ignore
    )
    message = result.data

    if message is None:
        raise RuntimeError("Message sent but ID not available in response")

    logger.info(f"Message sent successfully: {message.id}")
    return f"Message sent successfully: {message.id}"


@mcp.tool()
def delete_chat_message(
    ctx: AppContextType,
    chat_id: str,
    message_id: str,
) -> str:
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
    client = get_app_context(ctx).client
    client.chat_messages.delete_chat_message(chat_id=chat_id, id=message_id)
    logger.info(f"Message deleted successfully: {message_id}")
    return f"Message deleted successfully: {message_id}"
