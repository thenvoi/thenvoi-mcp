import json
import logging
from typing import Optional

from thenvoi_mcp.shared import mcp, client

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_tools(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """List available tools.

    Retrieves a list of tools with support for pagination.

    Args:
        page: Page number for pagination (optional).
        page_size: Number of items per page (optional).

    Returns:
        JSON string containing the list of tools.
    """
    logger.debug("Fetching list of tools")
    result = client.tools.thenvoi_com_web_api_v_1_tools_controller_index(
        page=page,
        page_size=page_size,
    )

    tools_list = result.data if hasattr(result, "data") else []
    tools_list = tools_list or []

    tools_data = {
        "tools": [
            {
                "id": getattr(t, "id", None),
                "name": getattr(t, "name", None),
                "description": getattr(t, "description", None),
                "json_schema": getattr(t, "json_schema", None),
                "connection_config": getattr(t, "connection_config", None),
            }
            for t in tools_list
        ]
    }
    if hasattr(result, "page"):
        tools_data["page"] = result.page
    if hasattr(result, "page_size"):
        tools_data["page_size"] = result.page_size
    if hasattr(result, "total"):
        tools_data["total"] = result.total

    logger.info(f"Retrieved {len(tools_list)} tools")
    return json.dumps(tools_data, indent=2)


@mcp.tool()
async def get_tool(tool_id: str) -> str:
    """Get a specific tool by ID.

    Retrieves detailed information about a single tool.

    Args:
        tool_id: The unique identifier of the tool to retrieve (required).

    Returns:
        JSON string containing the tool details.
    """
    logger.debug(f"Fetching tool with ID: {tool_id}")
    result = client.tools.thenvoi_com_web_api_v_1_tools_controller_show(id=tool_id)
    tool = result.data if hasattr(result, "data") else result

    tool_data = {
        "id": getattr(tool, "id", None),
        "name": getattr(tool, "name", None),
        "description": getattr(tool, "description", None),
        "json_schema": getattr(tool, "json_schema", None),
        "connection_config": getattr(tool, "connection_config", None),
    }
    logger.info(f"Retrieved tool: {tool_id}")
    return json.dumps(tool_data, indent=2)


@mcp.tool()
async def create_tool(
    name: str,
    description: str,
    json_schema: Optional[str] = None,
    connection_config: Optional[str] = None,
) -> str:
    """Create a new tool.

    Creates a new tool with the specified configuration. Tools define capabilities
    that agents can use to perform actions.

    Args:
        name: The name of the tool (required).
        description: Description of the tool's purpose and functionality (required).
        json_schema: Optional JSON schema defining the tool's parameters (as JSON string).
                     This is passed directly to the API without MCP validation.
        connection_config: Optional connection configuration (as JSON string).

    Returns:
        Success message with the created tool's ID.
    """
    logger.debug(f"Creating tool: {name}")

    # Parse JSON fields if provided
    schema_dict = None
    if json_schema is not None:
        try:
            schema_dict = json.loads(json_schema)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for json_schema: {e}")
            raise ValueError(f"Invalid JSON for json_schema: {str(e)}")

    config_dict = None
    if connection_config is not None:
        try:
            config_dict = json.loads(connection_config)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for connection_config: {e}")
            raise ValueError(f"Invalid JSON for connection_config: {str(e)}")

    # Build request with only non-None values
    request_data = {
        "name": name,
        "description": description,
    }
    if schema_dict is not None:
        request_data["json_schema"] = schema_dict
    if config_dict is not None:
        request_data["connection_config"] = config_dict

    result = client.tools.thenvoi_com_web_api_v_1_tools_controller_create(
        tool=request_data  # type: ignore
    )
    tool = result.data if hasattr(result, "data") else result  # type: ignore

    if tool is None:
        logger.error("Tool created but response data is None")
        raise RuntimeError("Tool created but ID not available in response")

    tool_id = getattr(tool, "id", "unknown")
    logger.info(f"Tool created successfully: {tool_id}")
    return f"Tool created successfully: {tool_id}"


@mcp.tool()
async def update_tool(
    tool_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    json_schema: Optional[str] = None,
    connection_config: Optional[str] = None,
) -> str:
    """Update an existing tool.

    Updates a tool's configuration. All fields are optional - only the fields
    provided will be updated.

    Args:
        tool_id: The unique identifier of the tool to update (required).
        name: New name for the tool.
        description: New description.
        json_schema: New JSON schema (as JSON string). Passed directly to API.
        connection_config: New connection configuration (as JSON string).

    Returns:
        Success message with the updated tool's ID.
    """
    logger.debug(f"Updating tool: {tool_id}")

    # Parse JSON fields if provided
    schema_dict = None
    if json_schema is not None:
        try:
            schema_dict = json.loads(json_schema)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for json_schema: {e}")
            raise ValueError(f"Invalid JSON for json_schema: {str(e)}")

    config_dict = None
    if connection_config is not None:
        try:
            config_dict = json.loads(connection_config)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for connection_config: {e}")
            raise ValueError(f"Invalid JSON for connection_config: {str(e)}")

    # Build request - only set fields that were provided
    request_data = {}
    if name is not None:
        request_data["name"] = name
    if description is not None:
        request_data["description"] = description
    if schema_dict is not None:
        request_data["json_schema"] = schema_dict
    if config_dict is not None:
        request_data["connection_config"] = config_dict

    result = client.tools.thenvoi_com_web_api_v_1_tools_controller_update(
        id=tool_id,
        tool=request_data,  # type: ignore
    )
    tool = result.data if hasattr(result, "data") else result  # type: ignore

    if tool is None:
        logger.error(f"Tool {tool_id} updated but response data is None")
        raise RuntimeError("Tool updated but ID not available in response")

    updated_tool_id = getattr(tool, "id", "unknown")
    logger.info(f"Tool updated successfully: {updated_tool_id}")
    return f"Tool updated successfully: {updated_tool_id}"


@mcp.tool()
async def delete_tool(tool_id: str) -> str:
    """Delete a tool.

    Permanently deletes a tool. This action cannot be undone.

    Args:
        tool_id: The unique identifier of the tool to delete (required).

    Returns:
        Success message confirming deletion.
    """
    logger.debug(f"Deleting tool: {tool_id}")
    client.tools.thenvoi_com_web_api_v_1_tools_controller_delete(id=tool_id)
    logger.info(f"Tool deleted successfully: {tool_id}")
    return f"Tool deleted successfully: {tool_id}"
