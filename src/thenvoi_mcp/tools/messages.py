"""Chat message tools.

This module provides tools for retrieving conversation context and
sending text messages using the agent-centric API.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from thenvoi_rest import (
    ChatMessageRequest,
    ChatMessageRequestMentionsItem,
)

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def get_agent_chat_context(
    ctx: AppContextType,
    chat_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """Get conversation context for agent rehydration.

    Returns all messages relevant to the agent for execution context/rehydration.
    This includes:
    - All messages the agent sent (any type: text, tool_call, tool_result, thought, etc.)
    - All text messages that @mention the agent

    Use this to load the complete context an external agent needs to resume execution.
    Messages are returned in chronological order (oldest first).

    Args:
        chat_id: The unique identifier of the chat room (required).
        page: Page number for pagination (optional, default: 1).
        page_size: Items per page (optional, default: 50, max: 100).

    Returns:
        JSON string containing the agent's conversation context with messages.
    """
    logger.debug(f"Fetching agent context for chat: {chat_id}")
    client = get_app_context(ctx).client
    result = client.agent_api.get_agent_chat_context(
        chat_id=chat_id,
        page=page,
        page_size=page_size,
    )
    message_count = len(result.data)
    logger.info(f"Retrieved {message_count} context messages for chat: {chat_id}")
    return serialize_response(result)


@mcp.tool()
def create_agent_chat_message(
    ctx: AppContextType,
    chat_id: str,
    content: str,
    recipients: Optional[str] = None,
    mentions: Optional[str] = None,
) -> str:
    """Send a text message in a chat room.

    Creates a new text message in a chat room. Messages MUST include at least
    one @mention to ensure proper routing to recipients.

    TWO WAYS TO SPECIFY RECIPIENTS:

    Option 1 - Use `recipients` (recommended for LLMs):
        Provide comma-separated names. The tool resolves names to IDs automatically.
        Example: recipients="weather agent,sarah"

    Option 2 - Use `mentions` (for libraries with caching):
        Provide a JSON array with pre-resolved IDs.
        Example: mentions='[{"id": "uuid-123", "name": "weather agent"}]'

    If both are provided, `mentions` takes precedence (no API call needed).

    For event-type messages (tool_call, tool_result, thought, error, etc.),
    use create_agent_chat_event instead.

    Args:
        chat_id: The unique identifier of the chat room (required).
        content: The message content/text (required).
        recipients: Comma-separated participant names to tag (LLM-friendly).
                   Example: "weather agent,sarah,mike"
                   Names are resolved to IDs via list_agent_chat_participants.
        mentions: JSON array of mentions with pre-resolved IDs (for libraries).
                 Format: [{"id": "uuid", "name": "display_name"}, ...]
                 When provided, skips name resolution (more efficient).

    Returns:
        JSON string containing the created message details.

    Examples:
        # LLM usage (names):
        create_agent_chat_message(chat_id="123", content="Hello!", recipients="weather agent")

        # Library usage (pre-resolved IDs):
        create_agent_chat_message(
            chat_id="123",
            content="Hello!",
            mentions='[{"id": "uuid-456", "name": "weather agent"}]'
        )
    """
    logger.debug(f"Creating message in chat: {chat_id}")
    client = get_app_context(ctx).client

    mentions_list: List[ChatMessageRequestMentionsItem] = []

    # Option 1: Pre-resolved mentions provided (efficient path for libraries)
    if mentions:
        try:
            parsed_mentions = json.loads(mentions)
            mentions_list = [
                ChatMessageRequestMentionsItem(id=m["id"], name=m["name"])
                for m in parsed_mentions
            ]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for mentions: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Missing required field in mentions: {str(e)}")

    # Option 2: Resolve names to IDs (LLM-friendly path)
    elif recipients:
        recipient_names = [
            name.strip().lower() for name in recipients.split(",") if name.strip()
        ]

        if not recipient_names:
            raise ValueError("recipients cannot be empty")

        # Fetch participants to map names to IDs
        participants_response = client.agent_api.list_agent_chat_participants(
            chat_id=chat_id
        )
        participants = participants_response.data

        # Build name -> participant mapping (case-insensitive)
        name_to_participant: Dict[str, Any] = {}
        for p in participants:
            # Agent participants have 'name' field
            if hasattr(p, "name") and p.name:
                name_to_participant[p.name.lower()] = p
            # User participants may have 'username' or 'display_name'
            if hasattr(p, "username") and p.username:
                name_to_participant[p.username.lower()] = p
            if hasattr(p, "display_name") and p.display_name:
                name_to_participant[p.display_name.lower()] = p

        # Resolve names to mentions
        not_found: List[str] = []
        for name in recipient_names:
            participant = name_to_participant.get(name)
            if participant:
                display_name = (
                    getattr(participant, "name", None)
                    or getattr(participant, "username", None)
                    or getattr(participant, "display_name", "Unknown")
                )
                mentions_list.append(
                    ChatMessageRequestMentionsItem(id=participant.id, name=display_name)
                )
            else:
                not_found.append(name)

        if not_found:
            available_names = list(name_to_participant.keys())
            raise ValueError(
                f"Could not find participants: {', '.join(not_found)}. "
                f"Available participants: {', '.join(available_names)}"
            )

    # Neither provided - error with helpful guidance
    else:
        raise ValueError(
            f"Missing recipients or mentions. To send a message, specify who to tag. "
            f'Use recipients=\'name1,name2\' (names) or mentions=\'[{{"id":"uuid","name":"display_name"}}]\' (IDs). '
            f"Call list_agent_chat_participants(chat_id='{chat_id}') to see available participants."
        )

    # Build and send message
    message_request = ChatMessageRequest(
        content=content,
        mentions=mentions_list,
    )

    result = client.agent_api.create_agent_chat_message(
        chat_id=chat_id,
        message=message_request,
    )

    logger.info(f"Message sent successfully: {result.data.id}")
    return serialize_response(result)
