"""Message lifecycle management tools.

This module provides tools for managing message processing lifecycle
(processing, processed, failed) using the agent-centric API.
"""

import logging

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def markAgentMessageProcessing(
    ctx: AppContextType,
    chatId: str,
    messageId: str,
) -> str:
    """Mark a message as being processed by the agent.

    Creates a new processing attempt with a system-managed timestamp.
    Call this when the agent starts working on a message.

    This endpoint automatically:
    - Creates a new attempt with auto-incremented attempt_number
    - Sets the attempt status to "processing"
    - Records the started_at timestamp (system-managed)
    - Updates the agent's delivery status to "processing"

    Args:
        chatId: The unique identifier of the chat room (required).
        messageId: The ID of the message to mark as processing (required).

    Returns:
        Success message confirming the message is marked as processing.
    """
    logger.debug(f"Marking message {messageId} as processing in chat {chatId}")
    client = get_app_context(ctx).client

    result = client.agent_api.mark_agent_message_processing(
        chats_id=chatId,
        id=messageId,
    )

    logger.info(f"Message marked as processing: {messageId}")
    return serialize_response(result)


@mcp.tool()
def markAgentMessageProcessed(
    ctx: AppContextType,
    chatId: str,
    messageId: str,
) -> str:
    """Mark a message as successfully processed by the agent.

    Completes the current processing attempt with a system-managed timestamp.
    Call this when the agent finishes processing a message successfully.

    This endpoint automatically:
    - Sets the current attempt's completed_at timestamp (system-managed)
    - Sets the current attempt status to "success"
    - Sets the agent's processed_at timestamp (system-managed)
    - Updates the agent's delivery status to "processed"

    Note: Requires an active processing attempt. If no processing attempt exists,
    returns a 422 error. Call markAgentMessageProcessing first.

    Args:
        chatId: The unique identifier of the chat room (required).
        messageId: The ID of the message to mark as processed (required).

    Returns:
        Success message confirming the message is marked as processed.
    """
    logger.debug(f"Marking message {messageId} as processed in chat {chatId}")
    client = get_app_context(ctx).client

    result = client.agent_api.mark_agent_message_processed(
        chats_id=chatId,
        id=messageId,
    )

    logger.info(f"Message marked as processed: {messageId}")
    return serialize_response(result)


@mcp.tool()
def markAgentMessageFailed(
    ctx: AppContextType,
    chatId: str,
    messageId: str,
    error: str,
) -> str:
    """Mark a message processing as failed by the agent.

    Completes the current processing attempt with an error message.
    Call this when the agent cannot process a message.

    This endpoint automatically:
    - Sets the current attempt's completed_at timestamp (system-managed)
    - Sets the current attempt status to "failed"
    - Records the error message in the current attempt
    - Updates the agent's delivery status to "failed"

    Note: Requires an active processing attempt. If no processing attempt exists,
    returns a 422 error. Call markAgentMessageProcessing first.

    Args:
        chatId: The unique identifier of the chat room (required).
        messageId: The ID of the message to mark as failed (required).
        error: Error message describing why processing failed (required).

    Returns:
        Success message confirming the message is marked as failed.
    """
    logger.debug(f"Marking message {messageId} as failed in chat {chatId}: {error}")
    client = get_app_context(ctx).client

    result = client.agent_api.mark_agent_message_failed(
        chats_id=chatId,
        id=messageId,
        error=error,
    )

    logger.info(f"Message marked as failed: {messageId}")
    return serialize_response(result)
