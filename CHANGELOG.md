# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2](https://github.com/thenvoi/thenvoi-mcp/compare/thenvoi-mcp-v1.1.1...thenvoi-mcp-v1.1.2) (2026-01-27)


### Bug Fixes

* **ci:** add ci scope to allowed PR title scopes ([4ed73c3](https://github.com/thenvoi/thenvoi-mcp/commit/4ed73c30fefe8a349b2cf5ec1072bd39a17b3e26))
* **ci:** skip PR title validation for dependabot ([4cf3c17](https://github.com/thenvoi/thenvoi-mcp/commit/4cf3c175c2a79390a05805a9cadcf159a581f54a))
* **ci:** skip PR title validation for dependabot ([54c5aec](https://github.com/thenvoi/thenvoi-mcp/commit/54c5aecfad58f276b631b26af5be2aff5ad53fc0))


### Documentation

* add naming conventions and PR title validation ([9437687](https://github.com/thenvoi/thenvoi-mcp/commit/94376879114d4f7d419a64479b2d1716f96863b4))
* add naming conventions and PR title validation ([f212529](https://github.com/thenvoi/thenvoi-mcp/commit/f212529600c0197d6c7b1aebd3a95e0c6b30f7b7))
* Add shared Claude rules via git submodule ([296cbe4](https://github.com/thenvoi/thenvoi-mcp/commit/296cbe498e088dcd10489a665571bf38fdede5ca))
* Add shared Claude rules via git submodule ([8f6f5a6](https://github.com/thenvoi/thenvoi-mcp/commit/8f6f5a6accbc55e73041aaab7d7509bf72fc6b42))
* Clean up CLAUDE.md to remove duplicated shared rules ([a7eaa1b](https://github.com/thenvoi/thenvoi-mcp/commit/a7eaa1bb16e97ea324e6ce938eecb529da76573e))
* Update Python version requirement to 3.11 ([#64](https://github.com/thenvoi/thenvoi-mcp/issues/64)) ([d28da44](https://github.com/thenvoi/thenvoi-mcp/commit/d28da448cdc2eee5cf9880ca3354c56b5df95f8c))

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
