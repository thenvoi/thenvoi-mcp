"""Shared fixtures for integration tests.

These tests run against a real Thenvoi API (defaults to localhost:4000).

Configuration:
    Create a .env.test file with your test credentials:
        THENVOI_API_KEY=your_api_key
        THENVOI_BASE_URL=http://localhost:4000
        TEST_AGENT_ID=your_agent_uuid

    Or set environment variables directly before running tests.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock

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


@pytest.fixture(scope="function")
def ctx():
    """Create a mock Context with the test client.

    Tools require a Context parameter for dependency injection.
    This fixture creates a mock that provides access to the client
    via get_app_context(ctx).client.
    """
    api_key = os.getenv("THENVOI_API_KEY")
    base_url = os.getenv("THENVOI_BASE_URL", "http://localhost:4000")
    assert api_key is not None, "API key should not be None in tests"

    client = RestClient(api_key=api_key, base_url=base_url)
    app_context = AppContext(client=client)

    # Mock the request_context.lifespan_context chain
    mock_request_context = MagicMock()
    mock_request_context.lifespan_context = app_context

    mock_ctx = MagicMock()
    mock_ctx.request_context = mock_request_context

    return mock_ctx


@pytest.fixture(scope="function")
def test_agent_id():
    """Get the test agent ID from environment."""
    agent_id = os.getenv("TEST_AGENT_ID")
    if not agent_id:
        pytest.skip("TEST_AGENT_ID not set - skipping test")
    return agent_id
