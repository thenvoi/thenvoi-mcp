# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1](https://github.com/thenvoi/thenvoi-mcp/compare/thenvoi-mcp-v1.1.0...thenvoi-mcp-v1.1.1) (2026-01-07)


### Bug Fixes

* remove PyPI publishing from release workflow ([8ac41e4](https://github.com/thenvoi/thenvoi-mcp/commit/8ac41e43826d8801e41bc8543bda6f1efff3b3ae))
* remove PyPI publishing from release workflow ([2aa8296](https://github.com/thenvoi/thenvoi-mcp/commit/2aa8296ab72946329b22a8eba86a8ec440e28955))

## [1.1.0](https://github.com/thenvoi/thenvoi-mcp/compare/thenvoi-mcp-v1.0.0...thenvoi-mcp-v1.1.0) (2026-01-07)


### Features

* **ci:** add changelog generation with semantic versioning ([b5f2cfe](https://github.com/thenvoi/thenvoi-mcp/commit/b5f2cfe52b968d8742372a944d29d714289523f2))


### Bug Fixes

* **ci:** move checkout before token generation ([885da5d](https://github.com/thenvoi/thenvoi-mcp/commit/885da5da11c4907f20cbaa39ca76e912da7d69b9))

## [Unreleased]

## [1.0.0] - 2024-01-01

### Added

- Initial MCP server implementation for Thenvoi integration
- Tools for managing agents (`list_agents`, `get_agent`)
- Tools for managing chats (`list_chats`, `get_chat`, `create_chat`)
- Tools for managing messages (`list_messages`, `send_message`)
- Tools for managing participants (`list_participants`, `add_participant`)
- SSE server support for remote deployments
- Pre-commit hooks for code quality (ruff, gitleaks, pyrefly)
- Comprehensive test suite with pytest
- LangGraph and LangChain integration examples

[Unreleased]: https://github.com/thenvoi/thenvoi-mcp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thenvoi/thenvoi-mcp/releases/tag/v1.0.0
