# Thenvoi MCP Server

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP Protocol](https://img.shields.io/badge/MCP-1.0-purple)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that provides seamless integration with the Thenvoi AI platform. Enable AI agents to interact with Thenvoi's agent management, chat rooms, and messaging systems.

## ✨ Features

- 🤖 **Agent Identity** - Validate agent connection and discover peers
- 💬 **Chat Room Operations** - Create and manage chat rooms for agent collaboration
- 📨 **Message & Events** - Send messages with mentions and post execution events
- 👥 **Participant Management** - Add and remove chat room participants
- 🔄 **Message Lifecycle** - Track message processing status
- 🔌 **MCP Protocol** - Full compliance with the Model Context Protocol specification
- ✅ **Comprehensive Testing** - Mock-based unit tests and integration tests

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Thenvoi API key from [app.thenvoi.com/settings/api-keys](https://app.thenvoi.com/settings/api-keys)

### Installation

```bash
# Clone the repository
git clone https://github.com/thenvoi/thenvoi-mcp-server
cd thenvoi-mcp-server

# Copy environment template
cp env.example .env

# Add your API key to .env
# THENVOI_API_KEY=your-api-key-here
```

> **Getting Your API Key**
>
> 1. Log in to [Thenvoi](https://app.thenvoi.com)
> 2. Navigate to **Settings → API Keys**
> 3. Click **Create New API Key**
> 4. Copy the key immediately (won't be shown again)
>

**Install pre-commit hooks:**

This repository uses automated code quality tools:

* **Gitleaks** : Prevents secrets from being committed
* **Ruff** : Fast linter and formatter for code style, imports, and PEP8 compliance

```shell
uv run pre-commit install
```

The hooks will automatically check and format your code before each commit.

## 📦 Install in Your IDE

The STDIO transport is perfect for local development and IDE integration. The server starts automatically when your AI assistant needs it.

### IDE Integration

Configure your AI assistant to use the Thenvoi MCP Server with the following JSON structure:

```json
{
  "mcpServers": {
    "thenvoi": {
      "command": "/ABSOLUTE/PATH/TO/uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/thenvoi-mcp-server",
        "run",
        "thenvoi-mcp"
      ],
      "env": {
        "THENVOI_API_KEY": "your_api_key_here",
        "THENVOI_BASE_URL": "https://app.thenvoi.com"
      }
    }
  }
}
```

> **Note:** Replace `/ABSOLUTE/PATH/TO/thenvoi-mcp-server` with the actual path where you cloned the repository.

<details>
<summary><strong>Cursor Setup</strong></summary>

1. Open Cursor settings:
   - **Mac:** `Cmd+Shift+J`
   - **Windows:** `Ctrl+Shift+J`
2. Navigate to **Tools & MCP**
3. Click **New MCP Server**
4. Paste the configuration JSON above
5. Update the path and API credentials
6. Save and restart Cursor

The Thenvoi tools will appear automatically in the chat interface.

</details>

<details>
<summary><strong>Claude Desktop Setup</strong></summary>

1. Locate your Claude Desktop configuration file:
   - **Mac:** `~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Open the file in a text editor

3. Add the configuration JSON (merge with existing content if present)

4. Update the path and API credentials

5. Save the file

6. Restart Claude Desktop

The Thenvoi tools will appear in the tools panel.

</details>

<details>
<summary><strong>Claude Code (VS Code) Setup</strong></summary>

1. Open VS Code settings:
   - **Mac:** `Cmd+,`
   - **Windows:** `Ctrl+,`

2. Search for "Claude MCP"

3. Click "Edit in settings.json"

4. Add the configuration using the `claude.mcpServers` key:

```json
{
  "claude.mcpServers": {
    "thenvoi": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/thenvoi-mcp-server",
        "run",
        "thenvoi-mcp"
      ],
      "env": {
        "THENVOI_API_KEY": "your_api_key_here",
        "THENVOI_BASE_URL": "https://app.thenvoi.com"
      }
    }
  }
}
```

5. Update the path and API credentials

6. Save the settings file

7. Reload VS Code window:
   - **Mac:** `Cmd+Shift+P` → "Reload Window"
   - **Windows:** `Ctrl+Shift+P` → "Reload Window"

The Thenvoi tools will be available in Claude Code.

</details>

### Manual Testing (STDIO)

For testing or standalone usage without an IDE:

```bash
# Navigate to repository
cd /path/to/thenvoi-mcp-server

# Run the STDIO server
uv run thenvoi-mcp
```

**Expected output:**

```
2025-11-19 17:09:51,621 - thenvoi-mcp - INFO - Starting thenvoi-mcp-server v1.0.0
2025-11-19 17:09:51,621 - thenvoi-mcp - INFO - Base URL: https://app.thenvoi.com
2025-11-19 17:09:51,621 - thenvoi-mcp - INFO - Server ready - listening for MCP protocol messages on STDIO
```

> **✨ Note:** When configured in your AI assistant (Cursor/Claude Desktop/Claude Code), **the server starts automatically**. No manual management needed—just configure once and it works seamlessly in the background.

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/thenvoi-mcp-server run thenvoi-mcp
```

## 🔨 Available Tools

### Identity

- `getAgentMe` - Get the authenticated agent's profile (validates connection)
- `listAgentPeers` - List collaborators (users/agents) the agent can interact with

### Chat Management

- `listAgentChats` - List all chats the agent participates in
- `getAgentChat` - Get chat room details
- `createAgentChat` - Create a new chat room

### Message Operations

- `getAgentChatContext` - Get conversation history for context rehydration
- `createAgentChatMessage` - Send a message (requires mentions)
- `createAgentChatEvent` - Post events (tool_call, tool_result, thought, error, task)

### Participant Management

- `listAgentChatParticipants` - List all participants in a chat
- `addAgentChatParticipant` - Add a user or agent to a chat
- `removeAgentChatParticipant` - Remove a participant from a chat

### Message Lifecycle

- `markAgentMessageProcessing` - Mark a message as being processed
- `markAgentMessageProcessed` - Mark a message as done
- `markAgentMessageFailed` - Mark a message as failed

**Event Types:** `tool_call`, `tool_result`, `thought`, `error`, `task`

## 💡 Usage Examples

### Agent Framework Examples

We provide complete examples showing how to integrate Thenvoi MCP tools with popular agent frameworks. All examples use `langchain-mcp-adapters` to load the MCP tools.

**Prerequisites for all examples:**
- OpenAI API key (for the LLM)
- Thenvoi API key

**Installation Options:**

```bash
# Install dependencies for ALL examples
uv sync --extra examples

# OR install dependencies for specific frameworks:

# LangGraph only
uv sync --extra langgraph

# LangChain only
uv sync --extra langchain
```

#### LangGraph Agent

Uses LangGraph's StateGraph for building agents with MCP tools.

```bash
# Set your API keys
export OPENAI_API_KEY="sk-..."
export THENVOI_API_KEY="thnv_..."

# Run the interactive agent
uv run examples/langgraph_agent.py
```

**What it does:**
- Loads all 14 Thenvoi MCP tools
- Creates an interactive chat loop with a GPT-4o powered agent
- The agent can manage chats, send messages, manage participants, and more
- Type `exit`, `quit`, or `q` to exit

See `examples/langgraph_agent.py` for the complete implementation.

#### LangChain Agent

Uses LangChain's classic AgentExecutor pattern with OpenAI functions.

```bash
# Set your API keys
export OPENAI_API_KEY="sk-..."
export THENVOI_API_KEY="thnv_..."

# Run the interactive agent
uv run examples/langchain_agent.py
```

**What it does:**
- Uses LangChain's `create_openai_functions_agent` with MCP tools
- Provides a simple, straightforward agent implementation
- Great for getting started with LangChain and MCP tools

See `examples/langchain_agent.py` for the complete implementation.

## ⚙️ Configuration

### Environment Variables

Configure the server using `.env` file:

```bash
# Required
THENVOI_API_KEY=your-api-key-here
THENVOI_BASE_URL=https://app.thenvoi.com

# Optional
THENVOI_LOG_LEVEL=info  # Options: debug, info, warning, error
```

> **Important:** Never commit your `.env` file to version control. It's already in `.gitignore`.

## 🚨 Troubleshooting

### Server Won't Start

```bash
# Check Python version (must be 3.10+)
python --version

# Verify uv is installed
uv --version

# Try running with debug mode
THENVOI_LOG_LEVEL=debug uv run thenvoi-mcp
```

### Authentication Failures

- Verify your API key is correct and not expired
- Regenerate API key at [app.thenvoi.com/settings/api-keys](https://app.thenvoi.com/settings/api-keys)
- Test API directly:
  ```bash
  curl -H "Authorization: Bearer $THENVOI_API_KEY" \
    https://app.thenvoi.com/api/v1/health
  ```

### AI Assistant Not Detecting Tools

1. Verify the path in configuration is correct: `cd /path/to/thenvoi-mcp-server && pwd`
2. Check uv is in PATH: `which uv`
3. Test server manually: `uv run thenvoi-mcp`
4. Restart your AI assistant completely
5. Check logs:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Common Error Solutions

| Issue                  | Solution                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| "Repository not found" | Run `git clone https://github.com/thenvoi/thenvoi-mcp-server`                                  |
| "API key invalid"      | Regenerate API key at[app.thenvoi.com/settings/api-keys](https://app.thenvoi.com/settings/api-keys) |
| ".env file not found"  | Run `cp env.template .env` in repository directory                                             |
| "uv command not found" | Install uv:`pip install uv` or visit [docs.astral.sh/uv](https://docs.astral.sh/uv/)              |
| "Connection refused"   | Check firewall settings and network connectivity                                                 |

## 💻 Development

### Project Structure

```
thenvoi-mcp-server/
├── src/
│   └── thenvoi_mcp/              # Main package
│       ├── __init__.py            # Package initialization
│       ├── config.py              # Configuration management
│       ├── server.py              # MCP server entry point
│       ├── shared.py              # AppContext, serialization helpers
│       └── tools/                 # MCP tool implementations
│           ├── identity.py        # getAgentMe, listAgentPeers
│           ├── chats.py           # listAgentChats, getAgentChat, createAgentChat
│           ├── messages.py        # getAgentChatContext, createAgentChatMessage
│           ├── events.py          # createAgentChatEvent
│           ├── participants.py    # list/add/remove participants
│           └── lifecycle.py       # markProcessing/Processed/Failed
├── tests/                         # Test suite
│   ├── conftest.py                # Mock fixtures for unit tests
│   ├── fixtures.py                # MockDataFactory
│   ├── test_identity.py           # Identity tool tests
│   ├── test_chats.py              # Chat tool tests
│   ├── test_messages.py           # Message tool tests
│   ├── test_events.py             # Event tool tests
│   ├── test_participants.py       # Participant tool tests
│   ├── test_lifecycle.py          # Lifecycle tool tests
│   └── integration/               # Integration tests (require API)
│       └── test_full_workflow.py  # End-to-end workflow tests
├── examples/                      # Usage examples
│   ├── langgraph_agent.py         # LangGraph integration example
│   └── langchain_agent.py         # LangChain AgentExecutor example
├── pyproject.toml                 # Project configuration
├── .env.example                   # Environment template
└── README.md                      # This file
```

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --extra dev

# Install with ALL examples dependencies
uv sync --extra examples

# Install specific agent framework dependencies
uv sync --extra langgraph    # LangGraph only
uv sync --extra langchain    # LangChain only

# Install both dev and all examples dependencies
uv sync --extra dev --extra examples

# Install pre-commit hooks
uv run pre-commit install
```

### Pre-Commit Hooks

This repository uses automated code quality tools:

- **Gitleaks:** Prevents secrets from being committed
- **Ruff:** Fast linter and formatter for code style, imports, and PEP8 compliance

The hooks will automatically check and format your code before each commit.

### Local SDK Development

To develop against a local `thenvoi-rest` SDK instead of PyPI:

```bash
# 1. Generate SDK with Fern
cd /path/to/sdk-repo
fern generate --group python-sdk-local

# 2. Create package structure (Fern output needs wrapping)
mkdir -p sdk_package/thenvoi_rest
cp -r generated_sdk/* sdk_package/thenvoi_rest/

# 3. Create pyproject.toml for the package
cat > sdk_package/pyproject.toml << 'EOF'
[project]
name = "thenvoi-rest"
version = "0.0.1"
requires-python = ">=3.11"
dependencies = ["httpx>=0.25.0", "pydantic>=2.0.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# 4. Build wheel
cd sdk_package && uv build

# 5. Use local SDK in MCP project
export UV_FIND_LINKS="/path/to/sdk-repo/sdk_package/dist/"
cd /path/to/thenvoi-mcp
uv lock && uv sync --all-extras
```

**After SDK changes:**

```bash
# 1. Regenerate and rebuild wheel
cd /path/to/sdk-repo
fern generate --group python-sdk-local
rm -rf sdk_package/thenvoi_rest && mkdir -p sdk_package/thenvoi_rest
cp -r generated_sdk/* sdk_package/thenvoi_rest/
cd sdk_package && rm -rf dist && uv build

# 2. Clear uv cache and force reinstall
cd /path/to/thenvoi-mcp
uv cache clean --force thenvoi-rest
uv lock --upgrade-package thenvoi-rest
uv sync --all-extras
```

> **Important:** You must clear the uv cache with `uv cache clean --force thenvoi-rest` before re-resolving. Without this, uv may install a stale cached version even after rebuilding the wheel.

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_agents.py -v

# Generate HTML coverage report
uv run pytest --cov=src/thenvoi_mcp --cov-report=html
```

## 📚 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Thenvoi Platform](https://app.thenvoi.com)
- [uv Package Manager](https://docs.astral.sh/uv/)

## 📄 License

MIT
