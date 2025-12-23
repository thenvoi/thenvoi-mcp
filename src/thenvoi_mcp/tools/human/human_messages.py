from datetime import datetime
from typing import Any, Optional

from thenvoi_rest import ChatMessageRequest, ChatMessageRequestMentionsItem

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response


@mcp.tool()
def list_user_chat_messages(
    ctx: AppContextType,
    chat_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    message_type: Optional[str] = None,
    since: Optional[str] = None,
) -> str:
    """List messages in a chat room.

    Args:
        chat_id: The chat room ID (required).
        page: Page number (optional).
        page_size: Items per page (optional).
        message_type: Filter by type: 'text', 'tool_call', etc. (optional).
        since: ISO 8601 timestamp to filter messages after (optional).
    """
    client = get_app_context(ctx).client

    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))

    result = client.human_api.list_my_chat_messages(
        chat_id=chat_id,
        page=page,
        page_size=page_size,
        message_type=message_type,
        since=since_dt,
    )
    return serialize_response(result)


@mcp.tool()
def send_user_chat_message(
    ctx: AppContextType,
    chat_id: str,
    content: str,
    recipients: Optional[str] = None,
) -> str:
    """Send a message in a chat room.

    Args:
        chat_id: The chat room ID (required).
        content: Message text (required).
        recipients: Comma-separated participant names to @mention (required).
    """
    client = get_app_context(ctx).client

    if not recipients:
        raise ValueError("recipients is required - specify who to @mention")

    recipient_names = [
        name.strip().lower() for name in recipients.split(",") if name.strip()
    ]

    # Fetch participants to resolve names to IDs
    participants_response = client.human_api.list_my_chat_participants(chat_id=chat_id)
    participants = participants_response.data or []

    # Build name -> participant mapping
    name_to_participant: dict[str, Any] = {}
    for p in participants:
        if hasattr(p, "name") and p.name:
            name_to_participant[p.name.lower()] = p
        if hasattr(p, "username") and p.username:
            name_to_participant[p.username.lower()] = p
        if hasattr(p, "first_name") and p.first_name:
            name_to_participant[p.first_name.lower()] = p

    # Resolve names to mentions
    mentions_list: list[ChatMessageRequestMentionsItem] = []
    not_found: list[str] = []

    for name in recipient_names:
        participant = name_to_participant.get(name)
        if participant:
            display_name = getattr(participant, "name", None) or getattr(
                participant, "username", "Unknown"
            )
            mentions_list.append(
                ChatMessageRequestMentionsItem(id=participant.id, name=display_name)
            )
        else:
            not_found.append(name)

    if not_found:
        available = list(name_to_participant.keys())
        raise ValueError(
            f"Not found: {', '.join(not_found)}. Available: {', '.join(available)}"
        )

    message_request = ChatMessageRequest(content=content, mentions=mentions_list)
    result = client.human_api.send_my_chat_message(
        chat_id=chat_id, message=message_request
    )
    return serialize_response(result)
