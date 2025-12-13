"""Chat participant management tools.

This module provides tools for managing chat room participants
using the agent-centric API.
"""

import logging
from typing import Optional

from thenvoi_rest import ParticipantRequest, ParticipantRole

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)

# Valid roles for participants (matches ParticipantRole Literal type)
VALID_ROLES = frozenset(["owner", "admin", "member"])


@mcp.tool()
def listAgentChatParticipants(
    ctx: AppContextType,
    chatId: str,
) -> str:
    """List participants in a chat room.

    Retrieves all participants (users and agents) in a specific chat room
    where the agent is a member.

    Args:
        chatId: The unique identifier of the chat room (required).

    Returns:
        JSON string containing the list of participants.
    """
    logger.debug(f"Fetching participants for chat: {chatId}")
    client = get_app_context(ctx).client
    result = client.agent_api.list_agent_chat_participants(chat_id=chatId)
    participant_count = len(result.data or []) if hasattr(result, "data") else 0
    logger.info(f"Retrieved {participant_count} participants for chat: {chatId}")
    return serialize_response(result)


@mcp.tool()
def addAgentChatParticipant(
    ctx: AppContextType,
    chatId: str,
    participantId: str,
    role: Optional[str] = None,
) -> str:
    """Add a participant (agent or user) to a chat room.

    Adds a new participant to the specified chat room. The acting agent
    must be the owner or admin of the room.

    Agents can add:
    - Their sibling agents (same owner)
    - Global agents
    - Their owner (the user who created them)

    Use listAgentPeers(notInChat=chatId) to discover available participants.

    Args:
        chatId: The unique identifier of the chat room (required).
        participantId: The ID of the participant (user or agent) to add (required).
        role: The role to assign: 'owner', 'admin', or 'member' (optional, defaults to 'member').

    Returns:
        Success message confirming the participant was added.
    """
    logger.debug(
        f"Adding participant {participantId} to chat {chatId} with role {role or 'member'}"
    )
    client = get_app_context(ctx).client

    # Validate and normalize role
    role_value: Optional[ParticipantRole] = None
    if role:
        role_lower = role.lower()
        if role_lower not in VALID_ROLES:
            valid_roles = ", ".join(sorted(VALID_ROLES))
            raise ValueError(f"Invalid role: {role}. Must be one of: {valid_roles}")
        role_value = role_lower  # type: ignore[assignment]

    participant = ParticipantRequest(
        participant_id=participantId,
        role=role_value,
    )
    client.agent_api.add_agent_chat_participant(chat_id=chatId, participant=participant)
    logger.info(f"Participant added successfully: {participantId}")
    return f"Participant added successfully: {participantId}"


@mcp.tool()
def removeAgentChatParticipant(
    ctx: AppContextType,
    chatId: str,
    participantId: str,
) -> str:
    """Remove a participant from a chat room.

    Removes a participant (user or agent) from the specified chat room.
    The acting agent must be the owner or admin of the room.

    Args:
        chatId: The unique identifier of the chat room (required).
        participantId: The participant's ID to remove (required).

    Returns:
        Success message confirming the participant was removed.
    """
    logger.debug(f"Removing participant {participantId} from chat {chatId}")
    client = get_app_context(ctx).client
    client.agent_api.remove_agent_chat_participant(chat_id=chatId, id=participantId)
    logger.info(f"Participant removed successfully: {participantId}")
    return f"Participant removed successfully: {participantId}"
