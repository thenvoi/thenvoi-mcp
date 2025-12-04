#!/usr/bin/env python3
"""
LangChain agent that uses Thenvoi MCP tools with langchain-mcp-adapters.

This example shows how to use the Thenvoi MCP server with a LangChain
agent using the newer create_agent pattern (built on LangGraph).

Usage:
    export OPENAI_API_KEY="sk-..."
    export THENVOI_API_KEY="thnv_..."
    uv run examples/langchain_agent.py
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run LangChain agent with Thenvoi MCP tools."""
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("THENVOI_API_KEY"):
        logger.error("Error: Set OPENAI_API_KEY and THENVOI_API_KEY")
        return

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Create MCP client that connects to Thenvoi server
    client = MultiServerMCPClient(
        {
            "thenvoi": {
                "command": "uv",
                "args": ["--directory", project_root, "run", "thenvoi-mcp"],
                "transport": "stdio",
                "env": {
                    "THENVOI_API_KEY": os.getenv("THENVOI_API_KEY", ""),
                    "THENVOI_BASE_URL": os.getenv(
                        "THENVOI_BASE_URL", "https://app.thenvoi.com"
                    ),
                },
            },
        }
    )

    logger.info("Loading tools from Thenvoi MCP server...")
    tools = await client.get_tools()
    logger.info(f"Loaded {len(tools)} tools!")

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Create the agent using LangChain's create_agent
    # (This is the modern approach that uses LangGraph under the hood)
    agent_executor = create_agent(llm, tools)

    logger.info("\n" + "=" * 50)
    logger.info("LangChain Agent Ready!")
    logger.info("=" * 50)
    logger.info("Type 'exit' to quit\n")

    # Interactive loop
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        try:
            result = await agent_executor.ainvoke({"messages": [("user", user_input)]})
            # Get the last message from the agent
            last_message = result["messages"][-1]
            logger.info(f"\nAgent: {last_message.content}\n")
        except Exception as e:
            logger.error(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    asyncio.run(main())
