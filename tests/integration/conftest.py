"""Pytest configuration for integration tests.

Re-exports fixtures from the parent module.
Credentials are loaded from .env.test automatically.
"""

from tests.conftest_integration import (
    api_client,
    get_api_key,
    get_base_url,
    get_test_agent_id,
    integration_ctx,
    requires_api,
    test_settings,
)

__all__ = [
    "api_client",
    "get_api_key",
    "get_base_url",
    "get_test_agent_id",
    "integration_ctx",
    "requires_api",
    "test_settings",
]
