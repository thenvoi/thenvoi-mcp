"""Pytest configuration for integration tests.

Re-exports fixtures from the parent module.
Credentials are loaded from .env.test automatically.
"""

from tests.conftest_integration import (
    IntegrationContext,
    api_client,
    get_api_key,
    get_base_url,
    get_test_agent_id,
    integration_ctx,
    requires_api,
    test_chat,
    test_peer_id,
    test_settings,
)

__all__ = [
    "IntegrationContext",
    "api_client",
    "get_api_key",
    "get_base_url",
    "get_test_agent_id",
    "integration_ctx",
    "requires_api",
    "test_chat",
    "test_peer_id",
    "test_settings",
]
