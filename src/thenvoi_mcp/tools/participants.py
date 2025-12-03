import json
import logging
from typing import Optional

from mcp.server.fastmcp import Context
from thenvoi_api.chat_participants.types import AddChatParticipantRequestParticipant

from thenvoi_mcp.shared import mcp, get_app_context

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_chat_participants(
    ctx: Context,
    chat_id: str,
    participant_type: Optional[str] = None,
) -> str:
    """List participants in a chat room.

    Retrieves a list of all participants (users and/or agents) in a specific
    chat room with optional filtering by participant type.

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_type: Filter by participant type: 'User' or 'Agent' (optional).

    Returns:
        JSON string containing the list of participants.
    """
    logger.debug(f"Fetching participants for chat: {chat_id}")
    client = get_app_context(ctx).client
    result = client.chat_participants.list_chat_participants(
        chat_id=chat_id,
        participant_type=participant_type,
    )

    participants_list = result.data or []

    # ChatParticipantDetails has: id, agent_name, email, first_name, last_name, role, status, type
    participants_data = {
        "participants": [
            {
                "id": p.id,
                "type": p.type,
                "agent_name": p.agent_name,
                "email": p.email,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "role": p.role,
                "status": p.status,
            }
            for p in participants_list
        ]
    }

    logger.info(f"Retrieved {len(participants_list)} participants for chat: {chat_id}")
    return json.dumps(participants_data, indent=2)


@mcp.tool()
async def add_chat_participant(
    ctx: Context,
    chat_id: str,
    participant_id: str,
    role: str = "member",
) -> str:
    """Add a participant (agent or user) to a chat room.

    Adds a new participant to the specified chat room with the given role.
    Participants can be either users or agents.

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_id: The ID of the participant (user or agent) to add (required).
        role: The role to assign: 'owner', 'admin', or 'member' (default: 'member').

    Returns:
        Success message confirming the participant was added.
    """
    logger.debug(
        f"Adding participant {participant_id} to chat {chat_id} with role {role}"
    )
    client = get_app_context(ctx).client
    participant = AddChatParticipantRequestParticipant(
        participant_id=participant_id,
        role=role,
    )
    client.chat_participants.add_chat_participant(
        chat_id=chat_id, participant=participant
    )
    logger.info(f"Participant added successfully: {participant_id}")
    return f"Participant added successfully: {participant_id}"


@mcp.tool()
async def remove_chat_participant(ctx: Context, chat_id: str, participant_id: str) -> str:
    """Remove a participant from a chat room.

    Removes a participant (user or agent) from the specified chat room.

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_id: The unique identifier of the participant to remove (required).

    Returns:
        Success message confirming the participant was removed.
    """
    logger.debug(f"Removing participant {participant_id} from chat {chat_id}")
    client = get_app_context(ctx).client
    client.chat_participants.remove_chat_participant(chat_id=chat_id, id=participant_id)
    logger.info(f"Participant removed successfully: {participant_id}")
    return f"Participant removed successfully: {participant_id}"


@mcp.tool()
async def list_available_participants(
    ctx: Context,
    chat_id: str,
    participant_type: str,
) -> str:
    """List available participants that can be added to a chat room.

    Retrieves a list of users or agents that are available to be added to
    the specified chat room (i.e., not already participants).

    Args:
        chat_id: The unique identifier of the chat room (required).
        participant_type: Type of participants to list: 'User' or 'Agent' (required).

    Returns:
        JSON string containing the list of available participants.
    """
    logger.debug(
        f"Fetching available {participant_type} participants for chat: {chat_id}"
    )
    client = get_app_context(ctx).client
    result = client.chat_participants.get_available_chat_participants(
        chat_id=chat_id,
        participant_type=participant_type,
    )

    participants_list = result.data or []

    # AvailableParticipant has: id, name, type, agent_name, avatar_url, email, first_name, last_name
    participants_data = {
        "available_participants": [
            {
                "id": p.id,
                "name": p.name,
                "type": p.type,
                "agent_name": p.agent_name,
                "avatar_url": p.avatar_url,
                "email": p.email,
                "first_name": p.first_name,
                "last_name": p.last_name,
            }
            for p in participants_list
        ]
    }

    logger.info(
        f"Retrieved {len(participants_list)} available participants for chat: {chat_id}"
    )
    return json.dumps(participants_data, indent=2)
