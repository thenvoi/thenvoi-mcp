"""Full workflow integration tests for all MCP tools.

Tests the complete agent workflow from identity to message lifecycle.
Run with: uv run pytest tests/integration/test_full_workflow.py -v -s --no-cov
"""

import json
from typing import Any, Callable


from tests.integration.conftest import get_test_agent_id, requires_api
from thenvoi_mcp.tools.identity import get_agent_me, list_agent_peers
from thenvoi_mcp.tools.chats import create_agent_chat, get_agent_chat, list_agent_chats
from thenvoi_mcp.tools.participants import (
    add_agent_chat_participant,
    list_agent_chat_participants,
)
from thenvoi_mcp.tools.messages import create_agent_chat_message, get_agent_chat_context
from thenvoi_mcp.tools.events import create_agent_chat_event
from thenvoi_mcp.tools.lifecycle import (
    mark_agent_message_processing,
    mark_agent_message_processed,
    mark_agent_message_failed,
)


# ============================================================
# Pagination Helpers
# ============================================================


def fetch_all_pages(
    ctx,
    list_func: Callable,
    page_size: int = 50,
    **kwargs,
) -> list[dict[str, Any]]:
    """Fetch all pages of results from a paginated endpoint.

    Args:
        ctx: Integration context
        list_func: The MCP tool function to call (e.g., list_agent_peers)
        page_size: Number of items per page
        **kwargs: Additional arguments to pass to the list function

    Returns:
        List of all items across all pages
    """
    all_items = []
    page = 1

    while True:
        result = list_func(ctx, page=page, page_size=page_size, **kwargs)
        parsed = json.loads(result)

        items = parsed.get("data", [])
        all_items.extend(items)

        # Check if there are more pages
        metadata = parsed.get("metadata", {})
        total_pages = metadata.get("total_pages", 1)

        if page >= total_pages:
            break
        page += 1

    return all_items


def find_item_in_pages(
    ctx,
    list_func: Callable,
    predicate: Callable[[dict], bool],
    page_size: int = 50,
    **kwargs,
) -> dict[str, Any] | None:
    """Search through paginated results to find an item matching a predicate.

    Args:
        ctx: Integration context
        list_func: The MCP tool function to call
        predicate: Function that returns True for the desired item
        page_size: Number of items per page
        **kwargs: Additional arguments to pass to the list function

    Returns:
        The matching item or None if not found
    """
    page = 1

    while True:
        result = list_func(ctx, page=page, page_size=page_size, **kwargs)
        parsed = json.loads(result)

        items = parsed.get("data", [])
        for item in items:
            if predicate(item):
                return item

        metadata = parsed.get("metadata", {})
        total_pages = metadata.get("total_pages", 1)

        if page >= total_pages:
            break
        page += 1

    return None


def item_exists_in_pages(
    ctx,
    list_func: Callable,
    item_id: str,
    page_size: int = 50,
    **kwargs,
) -> bool:
    """Check if an item with given ID exists in paginated results.

    Args:
        ctx: Integration context
        list_func: The MCP tool function to call
        item_id: The ID to search for
        page_size: Number of items per page
        **kwargs: Additional arguments to pass to the list function

    Returns:
        True if item exists, False otherwise
    """
    return (
        find_item_in_pages(
            ctx, list_func, lambda item: item.get("id") == item_id, page_size, **kwargs
        )
        is not None
    )


def fetch_all_context(
    ctx,
    chat_id: str,
    page_size: int = 50,
) -> list[dict[str, Any]]:
    """Fetch all pages of chat context.

    Args:
        ctx: Integration context
        chat_id: The chat ID to get context for
        page_size: Number of items per page

    Returns:
        List of all context items across all pages
    """
    all_items = []
    page = 1

    while True:
        result = get_agent_chat_context(
            ctx, chat_id=chat_id, page=page, page_size=page_size
        )
        parsed = json.loads(result)

        items = parsed.get("data", [])
        all_items.extend(items)

        metadata = parsed.get("metadata", {})
        total_pages = metadata.get("total_pages", 1)

        if page >= total_pages:
            break
        page += 1

    return all_items


@requires_api
class TestFullWorkflow:
    """End-to-end integration test covering all MCP tools in a realistic workflow."""

    def test_complete_agent_workflow(self, integration_ctx):
        """Test complete workflow: identity → chat → participants → messages → events → lifecycle."""

        # ============================================================
        # STEP 1: Identity - Get agent profile
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 1: Get Agent Identity")
        print("=" * 60)

        result = get_agent_me(integration_ctx)
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Agent profile should not be None"

        agent = parsed["data"]
        agent_id = agent["id"]
        agent_name = agent["name"]
        print(f"Agent: {agent_name} (ID: {agent_id})")

        # Verify against expected test agent if configured
        expected_agent_id = get_test_agent_id()
        if expected_agent_id:
            assert agent_id == expected_agent_id, f"Expected agent {expected_agent_id}"

        # ============================================================
        # STEP 2: Identity - List available peers (with pagination)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 2: List Available Peers (all pages)")
        print("=" * 60)

        peers = fetch_all_pages(integration_ctx, list_agent_peers)
        assert isinstance(peers, list), "Peers should be a list"
        print(f"Found {len(peers)} available peers across all pages")

        # We need at least one User peer to test human participant operations
        assert len(peers) > 0, "Need at least one peer for participant tests"

        # Find a User peer (human) - this is the key test: agent communicating with human
        user_peer = next((p for p in peers if p["type"] == "User"), None)
        assert user_peer is not None, (
            "Need at least one User peer to test agent-human communication"
        )

        peer = user_peer
        peer_id = peer["id"]
        peer_name = peer["name"]
        peer_type = peer["type"]
        print(f"Will use User peer: {peer_name} ({peer_type}, ID: {peer_id})")

        # ============================================================
        # STEP 3: Chats - Create a new chat
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 3: Create New Chat")
        print("=" * 60)

        result = create_agent_chat(integration_ctx)
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Created chat should not be None"

        chat = parsed["data"]
        chat_id = chat["id"]
        print(f"Created chat (ID: {chat_id}, title: {chat.get('title')})")

        # ============================================================
        # STEP 4: Chats - Get the created chat
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 4: Get Chat Details")
        print("=" * 60)

        result = get_agent_chat(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Chat should exist"
        assert parsed["data"]["id"] == chat_id, "Chat ID should match"
        print(f"Retrieved chat: {parsed['data'].get('title')}")

        # ============================================================
        # STEP 5: Chats - Verify chat appears in list (with pagination)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 5: List Chats (verify new chat appears, checking all pages)")
        print("=" * 60)

        chat_exists = item_exists_in_pages(integration_ctx, list_agent_chats, chat_id)
        assert chat_exists, "New chat should appear in chat list"
        all_chats = fetch_all_pages(integration_ctx, list_agent_chats)
        print(
            f"Chat list contains {len(all_chats)} chats across all pages, including our test chat"
        )

        # ============================================================
        # STEP 6: Participants - List initial participants
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 6: List Initial Participants")
        print("=" * 60)

        result = list_agent_chat_participants(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        initial_participants = parsed["data"]
        print(f"Initial participants: {len(initial_participants)}")
        for p in initial_participants:
            print(f"  - {p['name']} ({p['type']}, role: {p.get('role', 'N/A')})")

        # ============================================================
        # STEP 7: Participants - Add peer to chat
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 7: Add Participant to Chat")
        print("=" * 60)

        result = add_agent_chat_participant(
            integration_ctx, chat_id=chat_id, participant_id=peer_id, role="member"
        )
        print(f"Result: {result}")
        assert "successfully" in result.lower(), "Should indicate success"

        # ============================================================
        # STEP 8: Participants - Verify participant was added
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 8: Verify Participant Added")
        print("=" * 60)

        result = list_agent_chat_participants(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        participants = parsed["data"]
        participant_ids = [p["id"] for p in participants]
        assert peer_id in participant_ids, "Peer should now be a participant"
        print(f"Participants after adding: {len(participants)}")
        for p in participants:
            print(f"  - {p['name']} ({p['type']}, role: {p.get('role', 'N/A')})")

        # ============================================================
        # STEP 9: Messages - Send a message with mention
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 9: Send Message with Mention")
        print("=" * 60)

        # Find the peer's name for mention
        peer_participant = next((p for p in participants if p["id"] == peer_id), None)
        mention_name = peer_participant.get("name") or peer_name

        message_content = f"Hello @{mention_name}, this is an integration test message!"
        mentions = json.dumps([{"id": peer_id, "name": mention_name}])

        result = create_agent_chat_message(
            integration_ctx,
            chat_id=chat_id,
            content=message_content,
            mentions=mentions,
        )
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Message should be created"

        message = parsed["data"]
        message_id = message["id"]
        print(f"Sent message: '{message_content[:50]}...' (ID: {message_id})")

        # ============================================================
        # STEP 10: Messages - Get chat context (verify message, with pagination)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 10: Get Chat Context (all pages)")
        print("=" * 60)

        context = fetch_all_context(integration_ctx, chat_id)
        assert isinstance(context, list), "Context should be a list"
        message_ids = [m["id"] for m in context if "id" in m]
        assert message_id in message_ids, "Our message should appear in context"
        print(f"Chat context contains {len(context)} items across all pages")

        # ============================================================
        # STEP 11: Events - Create a thought event
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 11: Create Thought Event")
        print("=" * 60)

        event_content = "Processing the user's request about integration testing..."
        result = create_agent_chat_event(
            integration_ctx,
            chat_id=chat_id,
            content=event_content,
            message_type="thought",
        )
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Event should be created"

        event = parsed["data"]
        event_id = event["id"]
        print(f"Created thought event (ID: {event_id})")

        # ============================================================
        # STEP 12: Events - Create a tool_call event
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 12: Create Tool Call Event")
        print("=" * 60)

        tool_metadata = json.dumps(
            {
                "function": {
                    "name": "search_database",
                    "arguments": {"query": "integration test"},
                }
            }
        )
        result = create_agent_chat_event(
            integration_ctx,
            chat_id=chat_id,
            content="Calling search_database",
            message_type="tool_call",
            metadata=tool_metadata,
        )
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Tool call event should be created"
        print(f"Created tool_call event (ID: {parsed['data']['id']})")

        # ============================================================
        # STEP 13: Events - Create a tool_result event
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 13: Create Tool Result Event")
        print("=" * 60)

        result_metadata = json.dumps(
            {"result": {"found": 5, "items": ["item1", "item2"]}}
        )
        result = create_agent_chat_event(
            integration_ctx,
            chat_id=chat_id,
            content="Search completed successfully",
            message_type="tool_result",
            metadata=result_metadata,
        )
        parsed = json.loads(result)
        assert parsed["data"] is not None, "Tool result event should be created"
        print(f"Created tool_result event (ID: {parsed['data']['id']})")

        # ============================================================
        # STEP 14: Lifecycle - Mark message as processing
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 14: Mark Message Processing")
        print("=" * 60)

        result = mark_agent_message_processing(
            integration_ctx, chat_id=chat_id, message_id=message_id
        )
        parsed = json.loads(result)
        print(f"Marked message {message_id} as processing")

        # ============================================================
        # STEP 15: Lifecycle - Mark message as processed
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 15: Mark Message Processed")
        print("=" * 60)

        result = mark_agent_message_processed(
            integration_ctx, chat_id=chat_id, message_id=message_id
        )
        parsed = json.loads(result)
        print(f"Marked message {message_id} as processed")

        # ============================================================
        # STEP 16: Verify User still in chat after all operations
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 16: Verify User Still in Chat")
        print("=" * 60)

        result = list_agent_chat_participants(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        participant_ids = [p["id"] for p in parsed["data"]]
        assert peer_id in participant_ids, "User should still be a participant"
        print(f"Verified: User '{peer_name}' is still in chat")
        print(f"Total participants: {len(parsed['data'])}")
        for p in parsed["data"]:
            print(f"  - {p['name']} ({p['type']}, role: {p.get('role', 'N/A')})")

        # ============================================================
        # COMPLETE
        # ============================================================
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE - All 16 steps passed!")
        print("=" * 60)
        print(f"Test chat ID: {chat_id}")
        print(f"User '{peer_name}' remains in chat as expected")


@requires_api
class TestAddParticipantWithoutRole:
    """Test adding a participant without specifying a role (should default to member)."""

    def test_add_participant_without_role_defaults_to_member(self, integration_ctx):
        """Test that adding a participant without role defaults to 'member'.

        This test verifies the bug fix: the docstring says role 'defaults to member'
        but the code was sending None, causing a 422 error from the API.
        """
        print("\n" + "=" * 60)
        print("Testing Add Participant Without Role")
        print("=" * 60)

        # Create a chat for this test
        result = create_agent_chat(integration_ctx)
        parsed = json.loads(result)
        chat_id = parsed["data"]["id"]
        print(f"Created test chat: {chat_id}")

        # Get peers and find a User peer to add to the chat
        result = list_agent_peers(integration_ctx)
        parsed = json.loads(result)
        assert len(parsed["data"]) > 0, "Need at least one peer"

        # Find a User peer (human) for this test
        user_peer = next((p for p in parsed["data"] if p["type"] == "User"), None)
        assert user_peer is not None, "Need at least one User peer"

        peer_id = user_peer["id"]
        peer_name = user_peer["name"]
        print(f"Found User peer: {peer_name} (ID: {peer_id})")

        # Add participant WITHOUT specifying role - this should default to "member"
        print("Adding participant without role parameter...")
        result = add_agent_chat_participant(
            integration_ctx, chat_id=chat_id, participant_id=peer_id
        )
        print(f"Result: {result}")
        assert "successfully" in result.lower(), "Should indicate success"

        # Verify participant was added with member role
        result = list_agent_chat_participants(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        participants = parsed["data"]

        added_participant = next((p for p in participants if p["id"] == peer_id), None)
        assert added_participant is not None, "Participant should be in the chat"
        assert added_participant.get("role") == "member", (
            f"Role should default to 'member', got: {added_participant.get('role')}"
        )

        print(
            f"Verified: {peer_name} added with role '{added_participant.get('role')}'"
        )
        print("\nTest complete - default role works correctly!")


@requires_api
class TestMessageFailureLifecycle:
    """Test the message failure lifecycle separately."""

    def test_mark_message_failed(self, integration_ctx):
        """Test marking a message as failed with error message."""
        print("\n" + "=" * 60)
        print("Testing Message Failure Lifecycle")
        print("=" * 60)

        # Create a chat for this test
        result = create_agent_chat(integration_ctx)
        parsed = json.loads(result)
        chat_id = parsed["data"]["id"]
        print(f"Created test chat: {chat_id}")

        # Get peers and find a User peer to add to the chat
        result = list_agent_peers(integration_ctx)
        parsed = json.loads(result)
        assert len(parsed["data"]) > 0, "Need at least one peer"

        # Find a User peer (human) for this test
        user_peer = next((p for p in parsed["data"] if p["type"] == "User"), None)
        assert user_peer is not None, "Need at least one User peer"

        peer_id = user_peer["id"]
        peer_name = user_peer["name"]

        add_agent_chat_participant(
            integration_ctx, chat_id=chat_id, participant_id=peer_id, role="member"
        )
        print(f"Added User peer: {peer_name}")

        # Send a message
        mentions = json.dumps([{"id": peer_id, "name": peer_name}])
        result = create_agent_chat_message(
            integration_ctx,
            chat_id=chat_id,
            content=f"Test message for @{peer_name}",
            mentions=mentions,
        )
        parsed = json.loads(result)
        message_id = parsed["data"]["id"]
        print(f"Created message: {message_id}")

        # Mark as processing
        mark_agent_message_processing(
            integration_ctx, chat_id=chat_id, message_id=message_id
        )
        print("Marked as processing")

        # Mark as failed
        error_message = "Integration test simulated failure"
        result = mark_agent_message_failed(
            integration_ctx,
            chat_id=chat_id,
            message_id=message_id,
            error=error_message,
        )
        parsed = json.loads(result)
        print(f"Marked as failed with error: {error_message}")

        # Verify User is still in the chat
        result = list_agent_chat_participants(integration_ctx, chat_id=chat_id)
        parsed = json.loads(result)
        participant_ids = [p["id"] for p in parsed["data"]]
        assert peer_id in participant_ids, "User should still be a participant"
        print(f"Verified: User '{peer_name}' is still in chat")

        print("\nFailure lifecycle test complete!")
