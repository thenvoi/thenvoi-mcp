import logging
from typing import Optional

from thenvoi_rest import AgentRegisterRequest

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response

logger = logging.getLogger(__name__)


@mcp.tool()
def list_user_agents(
    ctx: AppContextType,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """List agents owned by the user.

    Args:
        page: Page number (optional).
        page_size: Items per page (optional).
    """
    client = get_app_context(ctx).client
    result = client.human_api.list_my_agents(page=page, page_size=page_size)
    return serialize_response(result)


@mcp.tool()
def register_user_agent(
    ctx: AppContextType,
    name: str,
    description: Optional[str] = None,
    model_type: Optional[str] = None,
) -> str:
    """Register a new external agent.

    Returns the agent details including API key. Save the API key - it's only shown once!

    Args:
        name: Agent name (required).
        description: Agent description (optional).
        model_type: AI model type (optional).
    """
    client = get_app_context(ctx).client
    agent_request = AgentRegisterRequest(name=name, description=description, model_type=model_type)
    result = client.human_api.register_my_agent(agent=agent_request)
    return serialize_response(result)

