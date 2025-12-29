"""Shared fixtures for unit tests.

These tests use mocked API responses and do not require a running API server.
"""

from dataclasses import dataclass
from unittest.mock import MagicMock, Mock

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
def mock_agent_api() -> MagicMock:
    """Create a mocked agent_api with all methods stubbed."""
    agent_api = MagicMock()
    return agent_api


@pytest.fixture
def mock_client(mock_agent_api: MagicMock) -> Mock:
    """Create a mocked RestClient with agent_api attached."""
    client = Mock()
    client.agent_api = mock_agent_api
    return client


@pytest.fixture
def mock_ctx(mock_client: Mock) -> MockContext:
    """Create a mock Context with a mocked API client for unit tests."""
    return MockContext(client=mock_client)
