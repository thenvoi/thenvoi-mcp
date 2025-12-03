"""Shared fixtures for integration tests.

These tests run against a real Thenvoi API (defaults to localhost:4000).
Run with: THENVOI_API_KEY=your_key pytest tests/
Or override base URL: THENVOI_API_KEY=your_key THENVOI_BASE_URL=your_url pytest tests/
"""

import os
import pytest


# Skip all tests if no API credentials
pytestmark = pytest.mark.skipif(
    not os.getenv("THENVOI_API_KEY"),
    reason="THENVOI_API_KEY not set - skipping integration tests",
)


@pytest.fixture(scope="function")
def setup_test_client():
    """Setup client with test API credentials.

    This fixture is used by integration tests (not autouse to allow unit tests).
    Integration tests should explicitly request this fixture.
    """
    api_key = os.getenv("THENVOI_API_KEY")
    base_url = os.getenv("THENVOI_BASE_URL", "http://localhost:4000")

    # Reinitialize client with test credentials
    from thenvoi.client.rest import RestClient
    from thenvoi_mcp import shared

    # Store original client
    original_client = shared.client

    # Replace with test client - api_key is guaranteed non-None by pytestmark skip
    assert api_key is not None, "API key should not be None in tests"
    shared.client = RestClient(api_key=api_key, base_url=base_url)

    yield

    # Restore original client
    shared.client = original_client
