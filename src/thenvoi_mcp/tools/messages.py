import json
import logging
from typing import Optional, Any, Dict

from mcp.server.fastmcp import Context

from thenvoi_mcp.shared import mcp, get_app_context

logger = logging.getLogger(__name__)


@mcp.tool()
def list_chat_messages(
    ctx: Context,
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

    messages_list = result.data or []

    # Fetch participants to get sender names
    participants_result = client.chat_participants.list_chat_participants(
        chat_id=chat_id
    )
    participants_data = participants_result.data or []

    # Build participant map with names
    # ChatParticipantDetails has: id, agent_name, email, first_name, last_name, role, status, type
    participant_map: Dict[str, str] = {}
    for p in participants_data:
        # Use agent_name for agents, otherwise construct name from first/last name or use id
        display_name: Optional[str] = None
        if p.agent_name:
            display_name = p.agent_name
        elif p.first_name or p.last_name:
            display_name = " ".join(filter(None, [p.first_name, p.last_name]))

        participant_map[p.id] = display_name or p.id

    messages_data: Dict[str, Any] = {
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "sender_name": participant_map.get(msg.sender_id, msg.sender_name or "Unknown"),
                "sender_type": msg.sender_type,
                "message_type": msg.message_type,
                "created_at": str(msg.inserted_at) if msg.inserted_at else "",
                "metadata": msg.metadata,
            }
            for msg in messages_list
        ]
    }
    # Pagination metadata is in result.metadata
    if result.metadata:
        messages_data["page"] = result.metadata.page
        messages_data["per_page"] = result.metadata.per_page
        messages_data["total"] = result.metadata.total_count

    logger.info(f"Retrieved {len(messages_list)} messages for chat: {chat_id}")
    return json.dumps(messages_data, indent=2)


@mcp.tool()
def create_chat_message(
    ctx: Context,
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
                      Must be verified chat participants.
        message_type: Optional message type (defaults to 'text').

    Returns:
        Success message with the created message's ID.

    REMINDER: Sender is ALWAYS authenticated user. Use list_chat_participants
    to get IDs of people you want to send TO.
    """
    logger.debug(f"Creating message in chat: {chat_id}")
    client = get_app_context(ctx).client

    # Get the authenticated user's ID from the API key
    # my_profile.get_my_profile() returns UserDetails directly (not wrapped in .data)
    profile = client.my_profile.get_my_profile()
    sender_id = profile.id
    logger.debug(f"Authenticated user ID: {sender_id}")

    # Process recipients if provided
    mentions_list: Optional[list[Dict[str, str]]] = None
    formatted_content = content

    if recipient_ids:
        # Parse recipient IDs
        recipient_list = [
            rid.strip() for rid in recipient_ids.split(",") if rid.strip()
        ]

        if recipient_list:
            # Get chat participants to verify recipients are in the chat
            participants_result = client.chat_participants.list_chat_participants(
                chat_id=chat_id
            )
            participants_data = participants_result.data or []

            # Extract participant IDs and their details
            # ChatParticipantDetails has: id, agent_name, first_name, last_name, type
            participant_map: Dict[str, Dict[str, Any]] = {}
            for p in participants_data:
                # Use agent_name for agents, otherwise construct from first/last name
                display_name: Optional[str] = None
                if p.agent_name:
                    display_name = p.agent_name
                elif p.first_name or p.last_name:
                    display_name = " ".join(filter(None, [p.first_name, p.last_name]))

                participant_map[p.id] = {
                    "display_name": display_name or p.id,
                    "type": p.type,
                }

            # Verify all recipients are in the chat
            invalid_recipients = [
                rid for rid in recipient_list if rid not in participant_map
            ]
            if invalid_recipients:
                error_msg = f"The following recipients are not participants in the chat room: {', '.join(invalid_recipients)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Build mentions list
            mentions_list = []
            mention_tags: list[str] = []
            for rid in recipient_list:
                participant = participant_map[rid]
                display_name = participant["display_name"]
                # Ensure types for mentions
                mentions_list.append({"id": str(rid), "username": str(display_name)})
                mention_tags.append(str(f"@{display_name}"))

            # Format message with @ mentions: @user1 @user2 @user3 message content
            formatted_content = f"{' '.join(mention_tags)} {content}"

    # Build request
    request_data: Dict[str, Any] = {
        "content": formatted_content,
        "sender_id": sender_id,
        "sender_type": "User",  # Always User since we're sending from authenticated user
    }
    if message_type is not None:
        request_data["message_type"] = message_type
    else:
        request_data["message_type"] = "text"  # Default to text

    if mentions_list is not None:
        request_data["mentions"] = mentions_list

    # Send the message
    result = client.chat_messages.create_chat_message(
        chat_id=chat_id,
        message=request_data,  # type: ignore
    )
    message = result.data

    if message is None:
        logger.error("Message sent but response data is None")
        raise RuntimeError("Message sent but ID not available in response")

    logger.info(f"Message sent successfully: {message.id}")
    return f"Message sent successfully: {message.id}"
