"""Pytest configuration for thenvoi-mcp tests.

Fixtures from thenvoi-testing-python are auto-loaded via pytest entry point.
"""

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
