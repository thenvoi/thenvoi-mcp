from __future__ import annotations

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response


@mcp.tool()
def list_user_memories(
    ctx: AppContextType,
    chat_room_id: str | None = None,
    scope: str | None = None,
    system: str | None = None,
    memory_type: str | None = None,
    segment: str | None = None,
    content_query: str | None = None,
    page_size: int | None = None,
    status: str | None = None,
) -> str:
    """List memories available to the authenticated user."""
    client = get_app_context(ctx).client
    result = client.human_api_memories.list_user_memories(
        chat_room_id=chat_room_id,
        scope=scope,
        system=system,
        type=memory_type,
        segment=segment,
        content_query=content_query,
        page_size=page_size,
        status=status,
    )
    return serialize_response(result)


@mcp.tool()
def get_user_memory(ctx: AppContextType, memory_id: str) -> str:
    """Get a single user memory by ID."""
    client = get_app_context(ctx).client
    result = client.human_api_memories.get_user_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def supersede_user_memory(ctx: AppContextType, memory_id: str) -> str:
    """Mark a user memory as superseded."""
    client = get_app_context(ctx).client
    result = client.human_api_memories.supersede_user_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def archive_user_memory(ctx: AppContextType, memory_id: str) -> str:
    """Archive a user memory."""
    client = get_app_context(ctx).client
    result = client.human_api_memories.archive_user_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def restore_user_memory(ctx: AppContextType, memory_id: str) -> str:
    """Restore an archived user memory."""
    client = get_app_context(ctx).client
    result = client.human_api_memories.restore_user_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def delete_user_memory(ctx: AppContextType, memory_id: str) -> str:
    """Delete a user memory permanently."""
    client = get_app_context(ctx).client
    client.human_api_memories.delete_user_memory(memory_id)
    return serialize_response({"deleted": True, "id": memory_id})
