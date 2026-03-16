from __future__ import annotations

from thenvoi_rest import CreateContactRequestRequestContactRequest

from thenvoi_mcp.shared import AppContextType, get_app_context, mcp, serialize_response


def _require_contact_lookup(
    contact_id: str | None = None, handle: str | None = None
) -> None:
    if not contact_id and not handle:
        raise ValueError("Provide either contact_id or handle")


@mcp.tool()
def resolve_handle(ctx: AppContextType, handle: str) -> str:
    """Resolve a Thenvoi handle before sending a contact request."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.resolve_handle(handle=handle)
    return serialize_response(result)


@mcp.tool()
def list_my_contacts(
    ctx: AppContextType,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """List contacts for the authenticated user."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.list_my_contacts(
        page=page,
        page_size=page_size,
    )
    return serialize_response(result)


@mcp.tool()
def list_received_contact_requests(
    ctx: AppContextType,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """List contact requests sent to the authenticated user."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.list_received_contact_requests(
        page=page,
        page_size=page_size,
    )
    return serialize_response(result)


@mcp.tool()
def list_sent_contact_requests(
    ctx: AppContextType,
    status: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """List contact requests sent by the authenticated user."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.list_sent_contact_requests(
        status=status,
        page=page,
        page_size=page_size,
    )
    return serialize_response(result)


@mcp.tool()
def create_contact_request(
    ctx: AppContextType,
    recipient_handle: str,
    message: str | None = None,
) -> str:
    """Send a new contact request from the authenticated user."""
    client = get_app_context(ctx).client
    request = CreateContactRequestRequestContactRequest(
        recipient_handle=recipient_handle,
        message=message,
    )
    result = client.human_api_contacts.create_contact_request(contact_request=request)
    return serialize_response(result)


@mcp.tool()
def approve_contact_request(ctx: AppContextType, request_id: str) -> str:
    """Approve a received contact request."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.approve_contact_request(request_id)
    return serialize_response(result)


@mcp.tool()
def reject_contact_request(ctx: AppContextType, request_id: str) -> str:
    """Reject a received contact request."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.reject_contact_request(request_id)
    return serialize_response(result)


@mcp.tool()
def cancel_contact_request(ctx: AppContextType, request_id: str) -> str:
    """Cancel a sent contact request."""
    client = get_app_context(ctx).client
    result = client.human_api_contacts.cancel_contact_request(request_id)
    return serialize_response(result)


@mcp.tool()
def remove_my_contact(
    ctx: AppContextType,
    contact_id: str | None = None,
    handle: str | None = None,
) -> str:
    """Remove one of the authenticated user's contacts."""
    _require_contact_lookup(contact_id=contact_id, handle=handle)

    client = get_app_context(ctx).client
    result = client.human_api_contacts.remove_my_contact(
        contact_id=contact_id,
        handle=handle,
    )
    return serialize_response(result)
