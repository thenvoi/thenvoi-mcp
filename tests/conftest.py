"""Pytest configuration for thenvoi-mcp tests.

Fixtures from thenvoi-testing-python are auto-loaded via pytest entry point.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

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
def mock_ctx(mock_api_client: Mock) -> MockContext:
    """Create a mock Context with a mocked API client for unit tests."""
    return MockContext(client=mock_api_client)


@pytest.fixture
def mock_api_client() -> Mock:
    """Create a mock RestClient with Fern SDK namespaces."""
    client = Mock()

    for namespace in (
        "agent_api_chats",
        "agent_api_contacts",
        "agent_api_context",
        "agent_api_events",
        "agent_api_identity",
        "agent_api_memories",
        "agent_api_messages",
        "agent_api_participants",
        "agent_api_peers",
        "human_api_agents",
        "human_api_chats",
        "human_api_contacts",
        "human_api_memories",
        "human_api_messages",
        "human_api_participants",
        "human_api_peers",
        "human_api_profile",
    ):
        setattr(client, namespace, Mock(name=namespace))

    return client


@pytest.fixture
def mock_agent_api_chats(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_chats


@pytest.fixture
def mock_agent_api_contacts(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_contacts


@pytest.fixture
def mock_agent_api_context(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_context


@pytest.fixture
def mock_agent_api_events(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_events


@pytest.fixture
def mock_agent_api_identity(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_identity


@pytest.fixture
def mock_agent_api_memories(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_memories


@pytest.fixture
def mock_agent_api_messages(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_messages


@pytest.fixture
def mock_agent_api_participants(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_participants


@pytest.fixture
def mock_agent_api_peers(mock_api_client: Mock) -> Mock:
    return mock_api_client.agent_api_peers


@pytest.fixture
def mock_human_api_agents(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_agents


@pytest.fixture
def mock_human_api_chats(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_chats


@pytest.fixture
def mock_human_api_contacts(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_contacts


@pytest.fixture
def mock_human_api_memories(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_memories


@pytest.fixture
def mock_human_api_messages(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_messages


@pytest.fixture
def mock_human_api_participants(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_participants


@pytest.fixture
def mock_human_api_peers(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_peers


@pytest.fixture
def mock_human_api_profile(mock_api_client: Mock) -> Mock:
    return mock_api_client.human_api_profile
