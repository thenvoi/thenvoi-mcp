"""Integration tests for error cases and edge cases.

Tests error handling for:
- Authentication errors (wrong API key)
- Chat access errors (non-existent chat)
- Participant errors (invalid UUID, non-existent participant)
- Participant role variations (add agent, add user as owner)

Run with: uv run pytest tests/integration/test_error_cases.py -v -s --no-cov
"""

import json
import uuid

import pytest
from thenvoi_rest import RestClient
from thenvoi_rest.errors import (
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
)

from tests.integration.conftest import get_base_url, requires_api
from thenvoi_mcp.tools.chats import get_agent_chat
from thenvoi_mcp.tools.identity import list_agent_peers
from thenvoi_mcp.tools.participants import (
    add_agent_chat_participant,
    list_agent_chat_participants,
    remove_agent_chat_participant,
)


def fetch_all_peers(
    ctx, not_in_chat: str | None = None, debug: bool = False
) -> list[dict]:
    """Fetch all peers across all pages.

    Args:
        ctx: Integration context
        not_in_chat: Optional chat ID to filter peers not in that chat
        debug: Print debug info about pages and peer types
    """
    all_peers = []
    page = 1
    while True:
        if not_in_chat:
            result = list_agent_peers(
                ctx, page=page, page_size=100, not_in_chat=not_in_chat
            )
        else:
            result = list_agent_peers(ctx, page=page, page_size=100)
        parsed = json.loads(result)
        peers = parsed.get("data", [])
        all_peers.extend(peers)
        metadata = parsed.get("metadata", {})
        total_pages = metadata.get("total_pages", 1)
        if debug:
            peer_types = {}
            for p in peers:
                t = p.get("type", "Unknown")
                peer_types[t] = peer_types.get(t, 0) + 1
            print(f"  Page {page}/{total_pages}: {len(peers)} peers - {peer_types}")
        if page >= total_pages:
            break
        page += 1
    if debug:
        total_types = {}
        for p in all_peers:
            t = p.get("type", "Unknown")
            total_types[t] = total_types.get(t, 0) + 1
        print(f"  Total: {len(all_peers)} peers - {total_types}")
    return all_peers


@requires_api
class TestAuthenticationErrors:
    """Tests for authentication error handling."""

    def test_wrong_api_key_raises_unauthorized(self):
        """Connect with invalid API key, expect UnauthorizedError (401)."""
        print("\n" + "=" * 60)
        print("Testing: Wrong API Key → UnauthorizedError")
        print("=" * 60)

        bad_client = RestClient(
            api_key="not-a-real-key",  # noqa: S106
            base_url=get_base_url(),
        )

        with pytest.raises(UnauthorizedError) as exc_info:
            bad_client.agent_api.get_agent_me()

        print(f"Got expected UnauthorizedError: {exc_info.value}")
        print("✓ Wrong API key correctly raises UnauthorizedError")


@requires_api
class TestChatAccessErrors:
    """Tests for chat access error handling."""

    def test_get_nonexistent_chat_raises_not_found(self, integration_ctx):
        """Access chat with random UUID, expect NotFoundError (404)."""
        print("\n" + "=" * 60)
        print("Testing: Non-existent Chat → NotFoundError")
        print("=" * 60)

        fake_chat_id = str(uuid.uuid4())
        print(f"Attempting to access fake chat: {fake_chat_id}")

        with pytest.raises(NotFoundError) as exc_info:
            get_agent_chat(integration_ctx, chat_id=fake_chat_id)

        print(f"Got expected NotFoundError: {exc_info.value}")
        print("✓ Non-existent chat correctly raises NotFoundError")

    def test_list_participants_nonexistent_chat(self, integration_ctx):
        """List participants for non-existent chat, expect NotFoundError."""
        print("\n" + "=" * 60)
        print("Testing: List Participants for Non-existent Chat → NotFoundError")
        print("=" * 60)

        fake_chat_id = str(uuid.uuid4())
        print(f"Attempting to list participants for fake chat: {fake_chat_id}")

        with pytest.raises(NotFoundError) as exc_info:
            list_agent_chat_participants(integration_ctx, chat_id=fake_chat_id)

        print(f"Got expected NotFoundError: {exc_info.value}")
        print(
            "✓ List participants for non-existent chat correctly raises NotFoundError"
        )

    def test_add_participant_to_nonexistent_chat(self, integration_ctx, test_peer_id):
        """Add participant to non-existent chat, expect NotFoundError."""
        print("\n" + "=" * 60)
        print("Testing: Add Participant to Non-existent Chat → NotFoundError")
        print("=" * 60)

        if not test_peer_id:
            pytest.skip("No peer available for testing")

        fake_chat_id = str(uuid.uuid4())
        print(f"Attempting to add participant to fake chat: {fake_chat_id}")

        with pytest.raises(NotFoundError) as exc_info:
            add_agent_chat_participant(
                integration_ctx,
                chat_id=fake_chat_id,
                participant_id=test_peer_id,
                role="member",
            )

        print(f"Got expected NotFoundError: {exc_info.value}")
        print("✓ Add participant to non-existent chat correctly raises NotFoundError")


@requires_api
class TestParticipantErrors:
    """Tests for participant error handling."""

    def test_add_nonexistent_participant(self, integration_ctx, test_chat):
        """Add participant with valid UUID that doesn't exist."""
        print("\n" + "=" * 60)
        print("Testing: Add Non-existent Participant")
        print("=" * 60)

        fake_participant_id = str(uuid.uuid4())
        print(f"Attempting to add non-existent participant: {fake_participant_id}")

        # Expect either NotFoundError or UnprocessableEntityError
        with pytest.raises((NotFoundError, UnprocessableEntityError)) as exc_info:
            add_agent_chat_participant(
                integration_ctx,
                chat_id=test_chat,
                participant_id=fake_participant_id,
                role="member",
            )

        print(f"Got expected error: {type(exc_info.value).__name__}: {exc_info.value}")
        print("✓ Adding non-existent participant raises appropriate error")

    def test_add_participant_invalid_uuid_format(self, integration_ctx, test_chat):
        """Add participant with malformed UUID string."""
        print("\n" + "=" * 60)
        print("Testing: Add Participant with Invalid UUID Format")
        print("=" * 60)

        invalid_uuid = "not-a-valid-uuid"
        print(f"Attempting to add participant with invalid UUID: {invalid_uuid}")

        # Expect UnprocessableEntityError for validation failure
        with pytest.raises(UnprocessableEntityError) as exc_info:
            add_agent_chat_participant(
                integration_ctx,
                chat_id=test_chat,
                participant_id=invalid_uuid,
                role="member",
            )

        print(f"Got expected UnprocessableEntityError: {exc_info.value}")
        print("✓ Invalid UUID format correctly raises UnprocessableEntityError")

    def test_remove_nonexistent_participant(self, integration_ctx, test_chat):
        """Remove participant that's not in the chat."""
        print("\n" + "=" * 60)
        print("Testing: Remove Non-existent Participant")
        print("=" * 60)

        fake_participant_id = str(uuid.uuid4())
        print(f"Attempting to remove non-existent participant: {fake_participant_id}")

        # Expect NotFoundError or similar
        with pytest.raises((NotFoundError, UnprocessableEntityError)) as exc_info:
            remove_agent_chat_participant(
                integration_ctx, chat_id=test_chat, participant_id=fake_participant_id
            )

        print(f"Got expected error: {type(exc_info.value).__name__}: {exc_info.value}")
        print("✓ Removing non-existent participant raises appropriate error")


@requires_api
class TestPeersFiltering:
    """Tests for peers endpoint filtering with notInChat parameter."""

    def test_peers_without_filter_returns_all(self, integration_ctx):
        """Test that peers without filter returns all available peers."""
        print("\n" + "=" * 60)
        print("Testing: List All Peers (no filter)")
        print("=" * 60)

        peers = fetch_all_peers(integration_ctx, debug=True)
        assert len(peers) > 0, "Should have at least one peer"
        print(f"✓ Found {len(peers)} total peers")

    def test_peers_filter_excludes_chat_participants(self, integration_ctx, test_chat):
        """Test that notInChat filter excludes participants already in the chat."""
        print("\n" + "=" * 60)
        print("Testing: notInChat Filter Excludes Participants")
        print("=" * 60)

        # Step 1: Get all peers (no filter)
        print("\nStep 1: Get all peers without filter:")
        all_peers = fetch_all_peers(integration_ctx, debug=True)
        initial_count = len(all_peers)
        assert initial_count > 0, "Need at least one peer for this test"

        # Step 2: Get peers not in our test chat (should be same as all since chat is empty)
        print(f"\nStep 2: Get peers not in chat {test_chat}:")
        peers_not_in_chat = fetch_all_peers(
            integration_ctx, not_in_chat=test_chat, debug=True
        )
        count_before_add = len(peers_not_in_chat)
        print(f"Peers not in chat (before adding): {count_before_add}")

        # Step 3: Add a peer to the chat
        peer_to_add = all_peers[0]
        peer_id = peer_to_add["id"]
        peer_name = peer_to_add["name"]
        print(f"\nStep 3: Adding peer '{peer_name}' (ID: {peer_id}) to chat")

        result = add_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=peer_id, role="member"
        )
        assert "successfully" in result.lower()
        print(f"Added: {result}")

        # Step 4: Get peers not in chat again - should be one less
        print("\nStep 4: Get peers not in chat (after adding one):")
        peers_after_add = fetch_all_peers(
            integration_ctx, not_in_chat=test_chat, debug=True
        )
        count_after_add = len(peers_after_add)

        # Verify the added peer is no longer in the filtered list
        peer_ids_after = [p["id"] for p in peers_after_add]
        assert peer_id not in peer_ids_after, (
            f"Added peer {peer_id} should not appear in filtered list"
        )
        assert count_after_add == count_before_add - 1, (
            f"Expected {count_before_add - 1} peers, got {count_after_add}"
        )
        print(
            f"✓ Filter correctly excludes added participant ({count_before_add} → {count_after_add})"
        )

        # Cleanup
        remove_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=peer_id
        )
        print("\nCleanup: Removed peer from chat")

    def test_agent_can_see_owner_in_peers(self, integration_ctx):
        """Test that an agent can see its owner (User) in the peers list."""
        print("\n" + "=" * 60)
        print("Testing: Agent Can See Owner (User) in Peers")
        print("=" * 60)

        # Get all peers and look for Users
        print("Fetching all peers to find Users:")
        peers = fetch_all_peers(integration_ctx, debug=True)

        # Count by type
        agents = [p for p in peers if p["type"] == "Agent"]
        users = [p for p in peers if p["type"] == "User"]

        print("\nPeer breakdown:")
        print(f"  - Agents: {len(agents)}")
        print(f"  - Users: {len(users)}")

        assert len(users) > 0, (
            f"Agent should be able to see at least one User peer (its owner). "
            f"Found {len(agents)} Agents but 0 Users in {len(peers)} total peers."
        )

        print(f"\nFound {len(users)} User peer(s):")
        for user in users:
            print(f"  - {user['name']} (ID: {user['id']})")
        print("✓ Agent can see User peers (including owner)")


@requires_api
class TestParticipantRoles:
    """Tests for different participant types and roles."""

    def test_add_agent_as_participant(self, integration_ctx, test_chat):
        """Add another agent to chat as member."""
        print("\n" + "=" * 60)
        print("Testing: Add Agent as Participant")
        print("=" * 60)

        # Find an agent peer not already in the chat
        peers = fetch_all_peers(integration_ctx, not_in_chat=test_chat)
        agent_peer = next((p for p in peers if p["type"] == "Agent"), None)

        if not agent_peer:
            pytest.skip("No agent peer available for testing")

        agent_id = agent_peer["id"]
        agent_name = agent_peer["name"]
        print(f"Found agent peer: {agent_name} (ID: {agent_id})")

        # Add agent as member
        result = add_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=agent_id, role="member"
        )
        print(f"Add result: {result}")
        assert "successfully" in result.lower()

        # Verify agent was added
        result = list_agent_chat_participants(integration_ctx, chat_id=test_chat)
        parsed = json.loads(result)
        participant_ids = [p["id"] for p in parsed["data"]]
        assert agent_id in participant_ids, "Agent should be in participant list"

        # Find the agent's role
        agent_participant = next(
            (p for p in parsed["data"] if p["id"] == agent_id), None
        )
        print(f"Agent participant: {agent_participant}")
        assert agent_participant is not None
        assert agent_participant["type"] == "Agent"

        # Cleanup: remove the agent
        remove_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=agent_id
        )
        print("✓ Successfully added and removed agent as participant")

    def test_add_user_as_owner(self, integration_ctx, test_chat):
        """Add user peer with owner role."""
        print("\n" + "=" * 60)
        print("Testing: Add User as Owner")
        print("=" * 60)

        # Find a user peer not already in the chat (with debug to see all pages)
        print(f"Fetching peers not in chat {test_chat}:")
        peers = fetch_all_peers(integration_ctx, not_in_chat=test_chat, debug=True)
        user_peer = next((p for p in peers if p["type"] == "User"), None)

        if not user_peer:
            pytest.skip("No user peer available for testing")

        user_id = user_peer["id"]
        user_name = user_peer["name"]
        print(f"Found user peer: {user_name} (ID: {user_id})")

        # Add user as owner
        result = add_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=user_id, role="owner"
        )
        print(f"Add result: {result}")
        assert "successfully" in result.lower()

        # Verify user was added with owner role
        result = list_agent_chat_participants(integration_ctx, chat_id=test_chat)
        parsed = json.loads(result)
        user_participant = next((p for p in parsed["data"] if p["id"] == user_id), None)
        print(f"User participant: {user_participant}")
        assert user_participant is not None
        assert user_participant["type"] == "User"
        assert user_participant.get("role") == "owner"

        # Cleanup: remove the user
        remove_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=user_id
        )
        print("✓ Successfully added user as owner and removed")

    def test_add_participant_then_remove(
        self, integration_ctx, test_chat, test_peer_id
    ):
        """Full add → verify → remove → verify cycle."""
        print("\n" + "=" * 60)
        print("Testing: Add → Verify → Remove → Verify Cycle")
        print("=" * 60)

        if not test_peer_id:
            pytest.skip("No peer available for testing")

        # Get peer info (filter by not in chat)
        peers = fetch_all_peers(integration_ctx, not_in_chat=test_chat)
        peer = next((p for p in peers if p["id"] == test_peer_id), None)
        if peer:
            print(f"Using peer: {peer['name']} ({peer['type']}, ID: {test_peer_id})")
        else:
            print(f"Using peer ID: {test_peer_id}")

        # Step 1: Add participant
        print("\nStep 1: Adding participant...")
        result = add_agent_chat_participant(
            integration_ctx,
            chat_id=test_chat,
            participant_id=test_peer_id,
            role="member",
        )
        print(f"Add result: {result}")
        assert "successfully" in result.lower()

        # Step 2: Verify participant is present
        print("\nStep 2: Verifying participant is present...")
        result = list_agent_chat_participants(integration_ctx, chat_id=test_chat)
        parsed = json.loads(result)
        participant_ids = [p["id"] for p in parsed["data"]]
        assert test_peer_id in participant_ids, "Peer should be in participant list"
        print(f"✓ Participant found in list (total: {len(parsed['data'])})")

        # Step 3: Remove participant
        print("\nStep 3: Removing participant...")
        result = remove_agent_chat_participant(
            integration_ctx, chat_id=test_chat, participant_id=test_peer_id
        )
        print(f"Remove result: {result}")
        assert "successfully" in result.lower()

        # Step 4: Verify participant is removed
        print("\nStep 4: Verifying participant is removed...")
        result = list_agent_chat_participants(integration_ctx, chat_id=test_chat)
        parsed = json.loads(result)
        participant_ids = [p["id"] for p in parsed["data"]]
        assert test_peer_id not in participant_ids, (
            "Peer should not be in participant list"
        )
        print(f"✓ Participant removed (remaining: {len(parsed['data'])})")

        print("\n✓ Full add/remove cycle completed successfully")
