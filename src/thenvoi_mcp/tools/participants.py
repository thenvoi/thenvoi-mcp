"""Chat participant management tools.

This module provides tools for managing chat room participants
using the agent-centric API.
"""

import logging
from typing import Literal, Optional

from thenvoi_rest import ParticipantRequest, ParticipantRole

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)

# Valid roles for participants (matches ParticipantRole Literal type)
VALID_ROLES = frozenset(["owner", "admin", "member"])


@mcp.tool()
def list_agent_chat_participants(
    ctx: AppContextType,
    chat_id: str,
) -> str:
    """List participants in a chat room.

    Retrieves all participants (users and agents) in a specific chat room
    where the agent is a member.

    Args:
        chat_id: The unique identifier of the chat room (required).

    Returns:
        JSON string containing the list of participants.
    """
    logger.debug(f"Fetching participants for chat: {chat_id}")
    client = get_app_context(ctx).client
    result = client.agent_api.list_agent_chat_participants(chat_id=chat_id)
    participant_count = len(result.data)
    logger.info(f"Retrieved {participant_count} participants for chat: {chat_id}")
    return serialize_response(result)


@mcp.tool()
def add_agent_chat_participant(
    ctx: AppContextType,
    chat_id: str,
    participant_id: str,
    role: Optional[Literal["owner", "admin", "member"]] = None,
) -> str:
    """Add a participant (agent or user) to a chat room.

    Adds a new participant to the specified chat room. The acting agent
    must be the owner or admin of the room.

    Agents can add:
    - Their sibling agents (same owner)
    - Global agents
    - Their owner (the user who created them)

    Use list_agent_peers(not_in_chat=chat_id) to discover available participants.

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_id: The ID of the participant (user or agent) to add (required).
        role: The role to assign: 'owner', 'admin', or 'member' (optional, defaults to 'member').

    Returns:
        Success message confirming the participant was added.
    """
    logger.debug(
        f"Adding participant {participant_id} to chat {chat_id} with role {role or 'member'}"
    )
    client = get_app_context(ctx).client

    # Validate and normalize role (default to "member" if not provided)
    role_value: ParticipantRole = "member"
    if role:
        role_lower = role.lower()
        if role_lower not in VALID_ROLES:
            valid_roles = ", ".join(sorted(VALID_ROLES))
            raise ValueError(f"Invalid role: {role}. Must be one of: {valid_roles}")
        role_value = role_lower  # type: ignore[assignment]

    participant = ParticipantRequest(
        participant_id=participant_id,
        role=role_value,
    )
    client.agent_api.add_agent_chat_participant(
        chat_id=chat_id, participant=participant
    )
    logger.info(f"Participant added successfully: {participant_id}")
    return f"Participant added successfully: {participant_id}"


@mcp.tool()
def remove_agent_chat_participant(
    ctx: AppContextType,
    chat_id: str,
    participant_id: str,
) -> str:
    """Remove a participant from a chat room.

    Removes a participant (user or agent) from the specified chat room.
    The acting agent must be the owner or admin of the room.

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_id: The participant's ID to remove (required).

    Returns:
        Success message confirming the participant was removed.
    """
    logger.debug(f"Removing participant {participant_id} from chat {chat_id}")
    client = get_app_context(ctx).client
    client.agent_api.remove_agent_chat_participant(chat_id=chat_id, id=participant_id)
    logger.info(f"Participant removed successfully: {participant_id}")
    return f"Participant removed successfully: {participant_id}"
