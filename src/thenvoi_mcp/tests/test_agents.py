import time
import pytest


class TestAgentIntegration:
    """Test agent management tools against real API."""

    @pytest.mark.asyncio
    async def test_agent_lifecycle(self, setup_test_client):
        """Test creating, reading, updating, and deleting an agent."""
        from thenvoi_mcp.tools.agents import (
            create_agent,
            get_agent,
            update_agent,
            list_agents,
        )
        from thenvoi_mcp import shared

        # Use timestamp with milliseconds to ensure unique names
        timestamp = int(time.time() * 1000)

        # 1. Create agent
        create_result = await create_agent(
            name=f"Test Agent Integration {timestamp}",
            model_type="gpt-4o-mini",
            description="Integration test agent",
        )

        assert "Agent created successfully" in create_result
        # Extract agent ID from result
        agent_id = create_result.split(": ")[1].strip()

        try:
            # 2. Get agent
            get_result = await get_agent(agent_id=agent_id)
            assert f"Test Agent Integration {timestamp}" in get_result
            assert agent_id in get_result

            # 3. Update agent (use unique name for update too)
            update_result = await update_agent(
                agent_id=agent_id, name=f"Updated Test Agent {timestamp}"
            )
            assert "Agent updated successfully" in update_result

            # 4. Verify update
            get_updated = await get_agent(agent_id=agent_id)
            assert f"Updated Test Agent {timestamp}" in get_updated

            # 5. List agents (should include our test agent)
            list_result = await list_agents()
            assert agent_id in list_result

        finally:
            # Cleanup: Delete agent
            try:
                shared.client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")

    @pytest.mark.asyncio
    async def test_agent_with_structured_output(self, setup_test_client):
        """Test creating agent with structured output schema."""
        from thenvoi_mcp.tools.agents import create_agent, get_agent
        from thenvoi_mcp import shared

        # Use timestamp with milliseconds for unique name
        timestamp = int(time.time() * 1000)

        schema = """{
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["response"]
        }"""

        create_result = await create_agent(
            name=f"Test Agent with Schema {timestamp}",
            model_type="gpt-4o-mini",
            description="Test agent with structured output",
            structured_output_schema=schema,
        )

        assert "Agent created successfully" in create_result
        agent_id = create_result.split(": ")[1].strip()

        try:
            # Verify agent was created
            get_result = await get_agent(agent_id=agent_id)
            assert agent_id in get_result
        finally:
            # Cleanup: Delete agent
            try:
                shared.client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
