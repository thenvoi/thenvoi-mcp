import logging
from typing import Dict, List, Optional

from thenvoi.client.rest import ChatMessageRequest

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
    recipient_ids: Optional[str] = None,
    message_type: Optional[str] = None,
) -> str:
    """Send a message in a chat room FROM the authenticated user.

    CRITICAL: This tool ALWAYS sends FROM the authenticated user. You CANNOT send
    FROM agents or other users. There is NO sender_id or sender_type parameter.

    HOW TO INTERPRET USER REQUESTS:

    When user says: "send message TO [person]"
    - Use recipient_ids parameter with that person's ID
    - Message is sent FROM authenticated user TO that person (with @mention)
    - DO NOT try to send FROM that person!

    When user says: "send message saying [text]"
    - Just use content parameter
    - Message broadcasts to everyone FROM authenticated user

    WRONG INTERPRETATION:
    User: "Send message to dan_agent"
    Wrong: Try to send FROM dan_agent
    Correct: Send FROM authenticated user TO dan_agent using recipient_ids

    EXAMPLES:

    User Request: "Send message TO dan_agent saying hello"
    Correct Usage:
        create_chat_message(
            chat_id="123",
            content="hello",
            recipient_ids="dan-agent-id"
        )
        Result: "@dan_agent hello" sent FROM authenticated user

    User Request: "Send message TO sarah and mike"
    Correct Usage:
        create_chat_message(
            chat_id="123",
            content="Can you help?",
            recipient_ids="sarah-id,mike-id"
        )
        Result: "@sarah @mike Can you help?" sent FROM authenticated user

    User Request: "Broadcast 'meeting in 5 minutes'"
    Correct Usage:
        create_chat_message(
            chat_id="123",
            content="meeting in 5 minutes"
            # No recipient_ids = broadcast to everyone
        )
        Result: "meeting in 5 minutes" sent FROM authenticated user

    Args:
        chat_id: The unique identifier of the chat room (required).
        content: The message content/text (required).
        recipient_ids: Comma-separated participant IDs to send TO (optional).
                      These people will be @mentioned in the message.
                      Example: "user-123,agent-456,user-789"
        message_type: Optional message type (defaults to 'text').

    Returns:
        Success message with the created message's ID.

    REMINDER: Sender is ALWAYS authenticated user. Use list_chat_participants
    to get IDs of people you want to send TO.
    """
    logger.debug(f"Creating message in chat: {chat_id}")
    client = get_app_context(ctx).client

    profile = client.my_profile.get_my_profile()
    sender_id = profile.id
    logger.debug(f"Authenticated user ID: {sender_id}")

    mentions_list: Optional[List[Dict[str, str]]] = None
    if recipient_ids:
        recipient_list = [
            rid.strip() for rid in recipient_ids.split(",") if rid.strip()
        ]
        if recipient_list:
            mentions_list = [{"id": rid, "username": rid} for rid in recipient_list]

    request = ChatMessageRequest(
        content=content,
        sender_id=sender_id,
        sender_type="User",
        message_type=message_type or "text",
        mentions=mentions_list,
    )

    try:
        result = client.chat_messages.create_chat_message(
            chat_id=chat_id,
            message=request,
        )
    except Exception as e:
        error_str = str(e)
        logger.error(f"Failed to send message: {error_str}")
        raise RuntimeError(f"Failed to send message: {error_str}") from e

    message = result.data

    if message is None:
        logger.error("Message sent but response data is None")
        raise RuntimeError("Message sent but ID not available in response")

    logger.info(f"Message sent successfully: {message.id}")
    return f"Message sent successfully: {message.id}"
