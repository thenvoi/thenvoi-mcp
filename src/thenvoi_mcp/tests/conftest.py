import os
from dataclasses import dataclass

import pytest

from thenvoi._vendor.thenvoi_client_rest import RestClient as ThenvoiClient

from thenvoi_mcp.shared import AppContext


# Skip all tests if no API credentials
pytestmark = pytest.mark.skipif(
    not os.getenv("THENVOI_API_KEY"),
    reason="THENVOI_API_KEY not set - skipping integration tests",
)


@dataclass
class MockRequestContext:
    """Mock request context for testing."""

    lifespan_context: dict


class MockContext:
    """Mock MCP Context for testing with real API client."""

    def __init__(self, client: ThenvoiClient):
        self.request_context = MockRequestContext(
            lifespan_context={"app_context": AppContext(client=client)}
        )


@pytest.fixture(scope="function")
def test_client() -> ThenvoiClient:
    """Create a test client with API credentials."""
    api_key = os.getenv("THENVOI_API_KEY")
    base_url = os.getenv("THENVOI_BASE_URL")

    assert api_key is not None, "API key should not be None in tests"
    return ThenvoiClient(api_key=api_key, base_url=base_url)


@pytest.fixture(scope="function")
def mock_ctx(test_client: ThenvoiClient) -> MockContext:
    """Create a mock Context with a real API client for integration tests."""
    return MockContext(client=test_client)


# Legacy fixture for backwards compatibility during migration
@pytest.fixture(scope="function")
def setup_test_client(test_client: ThenvoiClient, mock_ctx: MockContext):
    yield test_client, mock_ctx
