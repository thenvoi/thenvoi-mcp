from __future__ import annotations

import json
from typing import Any, cast

from thenvoi_rest import MemoryCreateRequest

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response


@mcp.tool()
def list_agent_memories(
    ctx: AppContextType,
    subject_id: str | None = None,
    scope: str | None = None,
    system: str | None = None,
    memory_type: str | None = None,
    segment: str | None = None,
    content_query: str | None = None,
    page_size: int | None = None,
    status: str | None = None,
) -> str:
    """List memories visible to the authenticated agent."""
    client = get_app_context(ctx).client
    result = client.agent_api_memories.list_agent_memories(
        subject_id=subject_id,
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
def get_agent_memory(ctx: AppContextType, memory_id: str) -> str:
    """Get a single agent memory by ID."""
    client = get_app_context(ctx).client
    result = client.agent_api_memories.get_agent_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def create_agent_memory(
    ctx: AppContextType,
    content: str,
    thought: str,
    system: str,
    segment: str,
    memory_type: str,
    scope: str | None = None,
    subject_id: str | None = None,
    metadata: str | None = None,
) -> str:
    """Create a new memory for the authenticated agent."""
    client = get_app_context(ctx).client

    parsed_metadata: dict[str, Any] | None = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON for metadata: {exc}") from exc

    memory_request = MemoryCreateRequest(
        content=content,
        thought=thought,
        system=system,
        segment=segment,
        type=memory_type,
        scope=scope,
        subject_id=subject_id,
        metadata=cast(Any, parsed_metadata),
    )
    result = client.agent_api_memories.create_agent_memory(memory=memory_request)
    return serialize_response(result)


@mcp.tool()
def supersede_agent_memory(ctx: AppContextType, memory_id: str) -> str:
    """Mark an agent memory as superseded."""
    client = get_app_context(ctx).client
    result = client.agent_api_memories.supersede_agent_memory(memory_id)
    return serialize_response(result)


@mcp.tool()
def archive_agent_memory(ctx: AppContextType, memory_id: str) -> str:
    """Archive an agent memory."""
    client = get_app_context(ctx).client
    result = client.agent_api_memories.archive_agent_memory(memory_id)
    return serialize_response(result)
