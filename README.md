# Thenvoi MCP Server

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP Protocol](https://img.shields.io/badge/MCP-1.0-purple)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that provides seamless integration with the Thenvoi AI platform. Enable AI assistants like Claude and Cursor to interact with Thenvoi's agent management, chat rooms, and messaging systems.

## ✨ Features

- 🤖 **Agent Management** - Create, read, update, and manage AI agents with custom configurations
- 💬 **Chat Room Operations** - Full lifecycle management of chat rooms for agent-user interactions
- 📨 **Message Handling** - Send and manage messages with support for multiple message types
- 👥 **Participant Management** - Control chat room participants and roles
- 🔌 **MCP Protocol** - Full compliance with the Model Context Protocol specification
- 🔒 **Secure Configuration** - Environment-based configuration with validation
- ✅ **Comprehensive Testing** - Integration tests for end-to-end workflows

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

### Agent Management

- `list_agents` - List all accessible agents
- `get_agent` - Get detailed agent information
- `create_agent` - Create a new AI agent
- `update_agent` - Update agent properties
- `list_agent_chats` - List chats for a specific agent

### Chat Management

- `list_chats` - List all chat rooms
- `get_chat` - Get chat room details
- `create_chat` - Create a new chat room
- `update_chat` - Update chat properties
- `delete_chat` - Delete a chat room

### Message Operations

- `list_chat_messages` - List messages in a chat with sender names for easy tagging
- `create_chat_message` - Send a message (always from authenticated user)
- `delete_chat_message` - Delete a message

### Participant Management

- `list_chat_participants` - List all participants in a chat
- `add_chat_participant` - Add a user or agent to a chat
- `remove_chat_participant` - Remove a participant from a chat
- `list_available_participants` - List users/agents available to add

### System

- `health_check` - Verify server and API connectivity

**Supported Message Types:** `text`, `system`, `action`, `thought`, `guidelines`, `error`, `task`

**Chat Types:** `direct`, `group`, `task`

**Chat Statuses:** `active`, `archived`, `closed`

## 💡 Usage Examples

### Natural Language in AI Assistants

Once connected, interact with Thenvoi through natural language:

```
Create a new agent named "Research Assistant" using model gpt-4o
```

```
Show me all my agents and their active chats
```

```
Send a message to the team saying "Project update meeting at 3pm"
```

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
- Loads all 17 Thenvoi MCP tools
- Creates an interactive chat loop with a GPT-4o powered agent
- The agent can list agents, create chats, send messages, manage participants, and more
- Type `exit`, `quit`, or `q` to exit

**Example interaction:**

```
You: list all the agents in the platform
Agent: Here are the agents available on the platform:
1. **Executive Assistant**
   - ID: aeae3cf4-c127-45d5-ac4c-57fbceb19f61
   - Model Type: gpt-4o
   - Description: Handles any task-like request from a user.
[...]
```

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
│       ├── server.py              # MCP server
│       ├── shared.py              # Shared instances
│       ├── tools/                 # MCP tool implementations
│       │   ├── agents.py          # Agent management tools
│       │   ├── chats.py           # Chat room tools
│       │   ├── messages.py        # Message operation tools
│       │   └── participants.py    # Participant management tools
│       └── tests/                 # Test suite
│           ├── conftest.py        # Test fixtures
│           ├── test_agents.py     # Agent tests
│           ├── test_chats.py      # Chat tests
│           ├── test_messages.py   # Message tests
│           └── test_participants.py # Participant tests
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
