import json
import logging
from typing import Optional, Any, Dict

from mcp.server.fastmcp import Context

from thenvoi_mcp.shared import get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def list_agents(ctx: Context) -> str:
    """List all accessible agents.

    Returns a list of agents that the authenticated user has access to.
    Each agent includes its ID, name, model type, description, and other metadata.

    Returns:
        JSON string containing the list of agents.
    """
    logger.debug("Fetching list of agents")
    client = get_app_context(ctx).client
    result = client.agents.list_agents()
    logger.info(f"Retrieved {len(result.data)} agents")
    return serialize_response(result)


@mcp.tool()
def get_agent(ctx: Context, agent_id: str) -> str:
    """Get a specific agent by ID.

    Retrieves detailed information about a single agent.

    Args:
        agent_id: The unique identifier of the agent to retrieve.

    Returns:
        JSON string containing the agent details.
    """
    logger.debug(f"Fetching agent with ID: {agent_id}")
    client = get_app_context(ctx).client
    result = client.agents.get_agent(id=agent_id)
    logger.info(f"Retrieved agent: {agent_id}")
    return serialize_response(result)
    

@mcp.tool()
def update_agent(
    ctx: Context,
    agent_id: str,
    name: Optional[str] = None,
    model_type: Optional[str] = None,
    description: Optional[str] = None,
    system_prompt_id: Optional[str] = None,
    is_external: Optional[bool] = None,
    is_global: Optional[bool] = None,
    organization_id: Optional[str] = None,
    structured_output_schema: Optional[str] = None,
) -> str:
    """Update an existing agent.

    Updates an agent's configuration. Only the fields provided will be updated
    (partial updates are supported). Fields not provided will remain unchanged.

    Args:
        agent_id: The unique identifier of the agent to update (required).
        name: New name for the agent.
        model_type: New AI model type to use.
        description: New description.
        system_prompt_id: New system prompt ID.
        is_external: Update external flag.
        is_global: Update global flag.
        organization_id: New organization ID.
        structured_output_schema: New JSON string for structured outputs (will be parsed as JSON).

    Returns:
        Success message with the updated agent's ID.
    """
    logger.debug(f"Updating agent: {agent_id}")
    client = get_app_context(ctx).client

    # Build update request with only provided fields
    update_data: Dict[str, Any] = {}
    if name is not None:
        update_data["name"] = name
    if model_type is not None:
        update_data["model_type"] = model_type
    if description is not None:
        update_data["description"] = description
    if system_prompt_id is not None:
        update_data["system_prompt_id"] = system_prompt_id
    if is_external is not None:
        update_data["is_external"] = is_external
    if is_global is not None:
        update_data["is_global"] = is_global
    if organization_id is not None:
        update_data["organization_id"] = organization_id
    if structured_output_schema is not None:
        try:
            update_data["structured_output_schema"] = json.loads(
                structured_output_schema
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for structured_output_schema: {e}")
            raise ValueError(f"Invalid JSON for structured_output_schema: {str(e)}")

    result = client.agents.update_agent(id=agent_id, agent=update_data)  # type: ignore
    agent = result.data

    if agent is None:
        logger.error(f"Agent {agent_id} updated but response data is None")
        raise RuntimeError("Agent updated but ID not available in response")

    logger.info(f"Agent updated successfully: {agent.id}")
    return f"Agent updated successfully: {agent.id}"


@mcp.tool()
def list_agent_chats(
    ctx: Context,
    agent_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None,
    chat_type: Optional[str] = None,
) -> str:
    """List all chat rooms where an agent participates.

    Retrieves a list of chat rooms that include the specified agent.
    Supports filtering by status and type, as well as pagination.

    Args:
        agent_id: The unique identifier of the agent (required).
        page: Page number for pagination (optional).
        page_size: Number of items per page (optional).
        status: Filter by chat status: 'active', 'archived', or 'closed' (optional).
        chat_type: Filter by chat type: 'direct', 'group', or 'task' (optional).

    Returns:
        JSON string containing the list of chats.
    """
    logger.debug(f"Fetching chats for agent: {agent_id}")
    client = get_app_context(ctx).client
    result = client.agents.list_agent_chats(
        agents_id=agent_id,
        page=page,
        page_size=page_size,
        status=status,
        type=chat_type,
    )
    logger.info(f"Retrieved {len(result.data)} chats for agent: {agent_id}")
    return serialize_response(result)
