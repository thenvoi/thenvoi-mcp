from __future__ import annotations

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response


def _require_contact_identifier(contact_id: str | None, handle: str | None) -> None:
    if not contact_id and not handle:
        raise ValueError("Provide a contact_id or handle")


def _require_contact_request_target(handle: str | None, request_id: str | None) -> None:
    if not handle and not request_id:
        raise ValueError("Provide a handle or request_id")


@mcp.tool()
def list_agent_contacts(
    ctx: AppContextType,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """List contacts for the authenticated agent."""
    client = get_app_context(ctx).client
    result = client.agent_api_contacts.list_agent_contacts(
        page=page,
        page_size=page_size,
    )
    return serialize_response(result)


@mcp.tool()
def list_agent_contact_requests(
    ctx: AppContextType,
    page: int | None = None,
    page_size: int | None = None,
    sent_status: str | None = None,
) -> str:
    """List incoming and outgoing contact requests for the authenticated agent."""
    client = get_app_context(ctx).client
    result = client.agent_api_contacts.list_agent_contact_requests(
        page=page,
        page_size=page_size,
        sent_status=sent_status,
    )
    return serialize_response(result)


@mcp.tool()
def add_agent_contact(
    ctx: AppContextType,
    handle: str,
    message: str | None = None,
) -> str:
    """Send a contact request from the authenticated agent."""
    client = get_app_context(ctx).client
    result = client.agent_api_contacts.add_agent_contact(
        handle=handle,
        message=message,
    )
    return serialize_response(result)


@mcp.tool()
def respond_to_agent_contact_request(
    ctx: AppContextType,
    action: str,
    handle: str | None = None,
    request_id: str | None = None,
) -> str:
    """Approve, reject, or cancel an agent contact request."""
    _require_contact_request_target(handle=handle, request_id=request_id)

    client = get_app_context(ctx).client
    result = client.agent_api_contacts.respond_to_agent_contact_request(
        action=action,
        handle=handle,
        request_id=request_id,
    )
    return serialize_response(result)


@mcp.tool()
def remove_agent_contact(
    ctx: AppContextType,
    contact_id: str | None = None,
    handle: str | None = None,
) -> str:
    """Remove an existing contact from the authenticated agent."""
    _require_contact_identifier(contact_id=contact_id, handle=handle)

    client = get_app_context(ctx).client
    result = client.agent_api_contacts.remove_agent_contact(
        contact_id=contact_id,
        handle=handle,
    )
    return serialize_response(result)
