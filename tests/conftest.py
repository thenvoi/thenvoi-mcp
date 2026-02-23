"""Pytest configuration for thenvoi-mcp tests.

Fixtures from thenvoi-testing-python are auto-loaded via pytest entry point.
We override mock_api_client to add v0.0.4 split namespace properties.
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from thenvoi_mcp.shared import AppContext


@dataclass
class MockRequestContext:
    """Mock request context for testing."""

    lifespan_context: AppContext


class MockContext:
    """Mock MCP Context for testing with mocked API client."""

    def __init__(self, client: Mock):
        self.request_context = MockRequestContext(
            lifespan_context=AppContext(client=client)
        )


@pytest.fixture
def mock_api_client(mock_agent_api: MagicMock, mock_human_api: MagicMock) -> AsyncMock:
    """Create a mocked RestClient with v0.0.4 split namespace properties.

    Maps all new namespace properties to the shared mock_agent_api / mock_human_api
    MagicMock objects. Since method names are unique across namespaces, all existing
    test assertions work unchanged.

    NOTE: This strategy assumes method names remain unique across namespaces.
    If two namespaces ever share a method name, tests could silently pass with
    wrong assertions. In that case, split into per-namespace mock objects.
    """
    client = AsyncMock()

    # Agent namespaces
    client.agent_api_chats = mock_agent_api
    client.agent_api_identity = mock_agent_api
    client.agent_api_messages = mock_agent_api
    client.agent_api_events = mock_agent_api
    client.agent_api_participants = mock_agent_api
    client.agent_api_peers = mock_agent_api
    client.agent_api_context = mock_agent_api
    client.agent_api_contacts = mock_agent_api

    # Human namespaces
    client.human_api_agents = mock_human_api
    client.human_api_chats = mock_human_api
    client.human_api_messages = mock_human_api
    client.human_api_participants = mock_human_api
    client.human_api_profile = mock_human_api
    client.human_api_peers = mock_human_api
    client.human_api_contacts = mock_human_api

    return client


@pytest.fixture
def mock_ctx(mock_api_client: Mock) -> MockContext:
    """Create a mock Context with a mocked API client for unit tests."""
    return MockContext(client=mock_api_client)
