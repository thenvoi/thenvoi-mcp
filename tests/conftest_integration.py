"""Fixtures for integration tests against a real API server.

These tests require a running API server and valid credentials.
Credentials are loaded from .env.test file automatically.

Run integration tests:
    uv run pytest tests/integration/ -v

Skip integration tests (run only unit tests):
    uv run pytest tests/ --ignore=tests/integration/

To override .env.test values, set environment variables:
    THENVOI_API_KEY="your-key" uv run pytest tests/integration/ -v
"""

from dataclasses import dataclass
from pathlib import Path

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from thenvoi_rest import RestClient

from thenvoi_mcp.shared import AppContext


class TestSettings(BaseSettings):
    """Settings for integration tests, loaded from .env.test."""

    thenvoi_api_key: str = ""
    thenvoi_base_url: str = "http://localhost:4000"
    test_agent_id: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env.test",
        case_sensitive=False,
        extra="ignore",
    )


# Load settings from .env.test
test_settings = TestSettings()


def get_api_key() -> str | None:
    return test_settings.thenvoi_api_key or None


def get_base_url() -> str:
    return test_settings.thenvoi_base_url


def get_test_agent_id() -> str | None:
    return test_settings.test_agent_id or None


# Skip marker for integration tests
requires_api = pytest.mark.skipif(
    not get_api_key(), reason="THENVOI_API_KEY environment variable not set"
)


@dataclass
class IntegrationRequestContext:
    """Request context for integration tests."""

    lifespan_context: AppContext


class IntegrationContext:
    """Real MCP Context for integration testing with actual API client."""

    def __init__(self, client: RestClient):
        self.request_context = IntegrationRequestContext(
            lifespan_context=AppContext(client=client)
        )


@pytest.fixture(scope="session")
def api_client() -> RestClient | None:
    """Create a real API client for integration tests.

    Returns None if THENVOI_API_KEY is not set.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    return RestClient(
        api_key=api_key,
        base_url=get_base_url(),
    )


@pytest.fixture
def integration_ctx(api_client: RestClient | None) -> IntegrationContext:
    """Create a real Context for integration tests.

    Skips test if API client is not available.
    """
    if api_client is None:
        pytest.skip("THENVOI_API_KEY not set")

    return IntegrationContext(client=api_client)


@pytest.fixture
def test_chat(api_client: RestClient | None):
    """Create a temporary chat for testing and clean up after.

    Yields the chat ID for use in tests.
    Note: Cleanup may not be possible if delete is not supported.
    """
    if api_client is None:
        pytest.skip("THENVOI_API_KEY not set")

    from thenvoi_rest import ChatRequest

    # Create a test chat
    response = api_client.agent_api.create_agent_chat(
        chat=ChatRequest(title="Integration Test Chat")
    )
    chat_id = response.data.id

    yield chat_id

    # Cleanup: We can't delete chats via agent API, so just leave it
    # The chat will remain but won't affect other tests


@pytest.fixture
def test_peer_id(api_client: RestClient | None) -> str | None:
    """Get a peer ID that can be used for testing participant operations.

    Returns the first available peer (agent or user) that can be added to chats.
    """
    if api_client is None:
        pytest.skip("THENVOI_API_KEY not set")

    response = api_client.agent_api.list_agent_peers()
    if response.data:
        return response.data[0].id
    return None
