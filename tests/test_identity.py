"""Unit tests for identity tools (getAgentMe, listAgentPeers)."""

import json


from tests.fixtures import factory
from thenvoi_mcp.tools.identity import getAgentMe, listAgentPeers


class TestGetAgentMe:
    """Tests for getAgentMe tool."""

    def test_returns_agent_profile(self, mock_ctx, mock_agent_api):
        """Test successful retrieval of agent profile."""
        agent = factory.agent_me(
            name="Weather Agent", description="Provides weather info"
        )
        mock_agent_api.get_agent_me.return_value = factory.response(agent)

        result = getAgentMe(mock_ctx)

        mock_agent_api.get_agent_me.assert_called_once()
        parsed = json.loads(result)
        assert parsed["data"]["name"] == "Weather Agent"
        assert parsed["data"]["description"] == "Provides weather info"

    def test_includes_agent_id_and_timestamps(self, mock_ctx, mock_agent_api):
        """Test that response includes id and timestamps."""
        agent = factory.agent_me()
        mock_agent_api.get_agent_me.return_value = factory.response(agent)

        result = getAgentMe(mock_ctx)

        parsed = json.loads(result)
        assert "id" in parsed["data"]
        assert "inserted_at" in parsed["data"]
        assert "updated_at" in parsed["data"]


class TestListAgentPeers:
    """Tests for listAgentPeers tool."""

    def test_returns_list_of_peers(self, mock_ctx, mock_agent_api):
        """Test successful retrieval of peer list."""
        peers = [
            factory.peer(name="Assistant Agent", type="Agent"),
            factory.peer(name="Research Agent", type="Agent"),
        ]
        mock_agent_api.list_agent_peers.return_value = factory.list_response(peers)

        result = listAgentPeers(mock_ctx)

        mock_agent_api.list_agent_peers.assert_called_once_with(
            not_in_chat=None,
            page=None,
            page_size=None,
        )
        parsed = json.loads(result)
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["name"] == "Assistant Agent"

    def test_filters_by_not_in_chat(self, mock_ctx, mock_agent_api):
        """Test filtering peers not in a specific chat."""
        chat_id = "chat-123"
        peers = [factory.peer(name="Available Agent")]
        mock_agent_api.list_agent_peers.return_value = factory.list_response(peers)

        listAgentPeers(mock_ctx, notInChat=chat_id)

        mock_agent_api.list_agent_peers.assert_called_once_with(
            not_in_chat=chat_id,
            page=None,
            page_size=None,
        )

    def test_pagination_parameters(self, mock_ctx, mock_agent_api):
        """Test pagination parameters are passed through."""
        mock_agent_api.list_agent_peers.return_value = factory.list_response([])

        listAgentPeers(mock_ctx, page=2, pageSize=10)

        mock_agent_api.list_agent_peers.assert_called_once_with(
            not_in_chat=None,
            page=2,
            page_size=10,
        )

    def test_empty_peer_list(self, mock_ctx, mock_agent_api):
        """Test handling of empty peer list."""
        mock_agent_api.list_agent_peers.return_value = factory.list_response([])

        result = listAgentPeers(mock_ctx)

        parsed = json.loads(result)
        assert parsed["data"] == []
