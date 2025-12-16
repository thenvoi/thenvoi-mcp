import logging
from typing import Optional

from thenvoi_rest.human_api import CreateMyChatRoomRequestChat

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def list_user_chats(
    ctx: AppContextType,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """List chat rooms where the user is a participant.

    Args:
        page: Page number (optional).
        page_size: Items per page (optional).
    """
    client = get_app_context(ctx).client
    result = client.human_api.list_my_chats(page=page, page_size=page_size)
    return serialize_response(result)


@mcp.tool()
def get_user_chat(ctx: AppContextType, chat_id: str) -> str:
    """Get a specific chat room by ID.

    Args:
        chat_id: The chat room ID (required).
    """
    client = get_app_context(ctx).client
    result = client.human_api.get_my_chat_room(id=chat_id)
    return serialize_response(result)


@mcp.tool()
def create_user_chat(ctx: AppContextType, task_id: Optional[str] = None) -> str:
    """Create a new chat room with the user as owner.

    Args:
        task_id: Optional task ID to associate with the chat.
    """
    client = get_app_context(ctx).client
    chat_request = (
        CreateMyChatRoomRequestChat(task_id=task_id)
        if task_id
        else CreateMyChatRoomRequestChat()
    )
    result = client.human_api.create_my_chat_room(chat=chat_request)
    return serialize_response(result)
