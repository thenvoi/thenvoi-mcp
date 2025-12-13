"""Chat event tools.

This module provides tools for posting events (tool_call, tool_result,
thought, error, task) using the agent-centric API.
"""

import json
import logging
from typing import Any, Dict, Optional

from thenvoi_rest import (
    ChatEventMessageType,
    ChatEventRequest,
)

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


# Valid event types for createAgentChatEvent (matches ChatEventMessageType enum)
VALID_EVENT_TYPES = frozenset(
    [
        "tool_call",
        "tool_result",
        "thought",
        "error",
        "task",
    ]
)


@mcp.tool()
def createAgentChatEvent(
    ctx: AppContextType,
    chatId: str,
    content: str,
    messageType: str,
    metadata: Optional[str] = None,
) -> str:
    """Post an event in a chat room (tool_call, tool_result, thought, error, task).

    Creates a new event in a chat room. Events do NOT require mentions - they
    report what happened rather than directing messages at participants.

    Event types and their content/metadata structure:

    - **tool_call**: Agent invokes a tool
      - content: Human-readable description (e.g., "Calling send_direct_message_service")
      - metadata: {"function": {"name": "fn_name", "arguments": {...}}, "id": "call_id", "type": "function"}

    - **tool_result**: Result from tool execution
      - content: Human-readable summary (e.g., "Message sent successfully")
      - metadata: {"success": true, "message": "...", ...result data}

    - **thought**: Agent's internal reasoning
      - content: The reasoning text
      - metadata: Optional

    - **error**: Error or failure notification
      - content: Error message
      - metadata: {"error_code": "...", "details": {...}}

    - **task**: Task-related message
      - content: Task message
      - metadata: Optional

    For text messages with mentions, use createAgentChatMessage instead.

    Args:
        chatId: The unique identifier of the chat room (required).
        content: Human-readable event content (required).
        messageType: Event type (required). One of: 'tool_call', 'tool_result',
                    'thought', 'error', 'task'.
        metadata: Optional JSON object with structured event data. Structure varies by messageType.

    Returns:
        JSON string containing the created event details.

    Examples:
        # Tool call event
        createAgentChatEvent(
            chatId="123",
            content="Calling weather_service",
            messageType="tool_call",
            metadata='{"function": {"name": "get_weather", "arguments": {"city": "NYC"}}, "id": "call_1", "type": "function"}'
        )

        # Tool result event
        createAgentChatEvent(
            chatId="123",
            content="Weather retrieved successfully",
            messageType="tool_result",
            metadata='{"success": true, "temperature": 72, "conditions": "sunny"}'
        )

        # Thought event
        createAgentChatEvent(
            chatId="123",
            content="I should check the weather before suggesting outdoor activities",
            messageType="thought"
        )
    """
    logger.debug(f"Creating event in chat: {chatId}, type: {messageType}")
    client = get_app_context(ctx).client

    # Validate message type
    message_type_lower = messageType.lower()
    if message_type_lower not in VALID_EVENT_TYPES:
        valid_types = ", ".join(sorted(VALID_EVENT_TYPES))
        raise ValueError(
            f"Invalid messageType: {messageType}. Must be one of: {valid_types}"
        )

    # Parse optional metadata
    metadata_dict: Optional[Dict[str, Any]] = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for metadata: {str(e)}")

    # Cast to ChatEventMessageType for type safety
    event_type: ChatEventMessageType = message_type_lower  # type: ignore[assignment]

    event_request = ChatEventRequest(
        content=content,
        message_type=event_type,
        metadata=metadata_dict,
    )

    try:
        result = client.agent_api.create_agent_chat_event(
            chats_id=chatId,
            event=event_request,
        )
    except Exception as e:
        error_str = str(e)
        logger.error(f"Failed to create event: {error_str}")
        raise RuntimeError(f"Failed to create event: {error_str}") from e

    if result.data is None:
        raise RuntimeError("Event created but data not available in response")

    logger.info(f"Event created successfully: {result.data.id}")
    return serialize_response(result)
