"""Shared fixtures for integration tests.

These tests run against a real Thenvoi API (defaults to localhost:4000).

Configuration:
    Create a .env.test file with your test credentials:
        THENVOI_API_KEY=your_api_key
        THENVOI_BASE_URL=http://localhost:4000

    Or set environment variables directly before running tests.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import pytest
from dotenv import load_dotenv

from thenvoi_client_rest import RestClient

from thenvoi_mcp.shared import AppContext

# Load test environment from .env.test if it exists
env_test_path = Path(__file__).parents[3] / ".env.test"
if env_test_path.exists():
    load_dotenv(env_test_path)

# Skip all tests if no API credentials
pytestmark = pytest.mark.skipif(
    not os.getenv("THENVOI_API_KEY"),
    reason="THENVOI_API_KEY not set - skipping integration tests",
)


@dataclass
class MockRequestContext:
    """Mock request context for testing."""

    lifespan_context: AppContext


class MockContext:
    """Mock MCP Context for testing with real API client."""

    def __init__(self, client: RestClient):
        self.request_context = MockRequestContext(
            lifespan_context=AppContext(client=client)
        )


@pytest.fixture(scope="function")
def test_client() -> RestClient:
    """Create a test client with API credentials."""
    api_key = os.getenv("THENVOI_API_KEY")
    base_url = os.getenv("THENVOI_BASE_URL", "http://localhost:4000")

    assert api_key is not None, "API key should not be None in tests"
    return RestClient(api_key=api_key, base_url=base_url)


@pytest.fixture(scope="function")
def mock_ctx(test_client: RestClient) -> MockContext:
    """Create a mock Context with a real API client for integration tests."""
    return MockContext(client=test_client)


@pytest.fixture(scope="function")
def setup_test_client(test_client: RestClient, mock_ctx: MockContext):
    """Fixture that yields (client, ctx) tuple for tests."""
    yield test_client, mock_ctx
