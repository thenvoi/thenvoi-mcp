import logging
from typing import Any, Dict, List, Optional, cast

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
    recipients: Optional[str] = None,
    message_type: Optional[str] = None,
) -> str:
    """Send a message in a chat room FROM the authenticated user.

    CRITICAL: This tool ALWAYS sends FROM the authenticated user. You CANNOT send
    FROM agents or other users. There is NO sender_id or sender_type parameter.

    HOW TO INTERPRET USER REQUESTS:

    When user says: "send message TO [person]"
    - Use recipients parameter with that person's NAME
    - Message is sent FROM authenticated user TO that person (with @mention)
    - DO NOT try to send FROM that person!

    When user says: "send message saying [text]"
    - Just use content parameter
    - Message broadcasts to everyone FROM authenticated user

    EXAMPLES:

    User Request: "Send message TO chen saying hello"
    Correct Usage:
        create_chat_message(
            chat_id="123",
            content="hello",
            recipients="chen"
        )
        Result: "@chen hello" sent FROM authenticated user

    User Request: "Send message TO sarah and mike"
    Correct Usage:
        create_chat_message(
            chat_id="123",
            content="Can you help?",
            recipients="sarah,mike"
        )
        Result: "@sarah @mike Can you help?" sent FROM authenticated user

    Args:
        chat_id: The unique identifier of the chat room (required).
        content: The message content/text (required).
        recipients: Comma-separated names/usernames to tag (REQUIRED).
                   The API requires at least one recipient to be mentioned.
                   Use the participant's name (e.g., "chen", "sarah").
                   Example: "chen,sarah,mike"
        message_type: Optional message type (defaults to 'text').

    Returns:
        Success message with the created message's ID.

    REMINDER: Sender is ALWAYS authenticated user. Use participant names to tag them.
    """
    logger.debug(f"Creating message in chat: {chat_id}")
    client = get_app_context(ctx).client

    if not recipients:
        # API requires at least one recipient - provide actionable error for LLM
        raise ValueError(
            f"Missing recipients. To send a message, you must tag at least one participant. "
            f"Step 1: Call list_chat_participants(chat_id='{chat_id}') to see participant names. "
            f"Step 2: Call create_chat_message with those names in recipients parameter."
        )

    recipient_names = [
        name.strip().lower() for name in recipients.split(",") if name.strip()
    ]

    if not recipient_names:
        raise ValueError("recipients cannot be empty")

    # Fetch participants to map names to IDs
    participants_response = client.chat_participants.list_chat_participants(
        chat_id=chat_id
    )
    participants = participants_response.data or []

    # Build name -> participant mapping (case-insensitive)
    name_to_participant: Dict[str, Any] = {}
    for p in participants:
        # Get the participant's display name
        if hasattr(p, "agent_name") and p.agent_name:
            name_to_participant[p.agent_name.lower()] = p
        if hasattr(p, "first_name") and p.first_name:
            name_to_participant[p.first_name.lower()] = p
            # Also add full name
            if hasattr(p, "last_name") and p.last_name:
                full_name = f"{p.first_name} {p.last_name}"
                name_to_participant[full_name.lower()] = p

    # Build mentions list by looking up names
    mentions_list: List[Dict[str, str]] = []
    not_found: List[str] = []

    for name in recipient_names:
        participant = name_to_participant.get(name)
        if participant:
            display_name = (
                participant.agent_name
                if hasattr(participant, "agent_name") and participant.agent_name
                else participant.first_name
            )
            mentions_list.append({"id": participant.id, "username": display_name})
        else:
            not_found.append(name)

    if not_found:
        available_names = list(name_to_participant.keys())
        raise ValueError(
            f"Could not find participants: {', '.join(not_found)}. "
            f"Available participants: {', '.join(available_names)}"
        )

    # Get sender info from authenticated user
    profile = client.my_profile.get_my_profile()
    sender_id = profile.id

    # Use raw dict - API may require sender_id/sender_type even if not in SDK model
    request_data: Dict[str, Any] = {
        "content": content,
        "sender_id": sender_id,
        "sender_type": "User",
        "message_type": message_type or "text",
        "mentions": mentions_list,
    }

    try:
        result = client.chat_messages.create_chat_message(
            chat_id=chat_id,
            message=cast(Any, request_data),
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
