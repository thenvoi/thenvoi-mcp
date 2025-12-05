import time

from thenvoi_client_rest import AgentRequest

from thenvoi_mcp.shared import get_app_context
from thenvoi_mcp.tools.agents import get_agent, list_agents, update_agent


class TestAgentIntegration:
    """Test agent management tools against real API."""

    def test_agent_lifecycle(self, ctx):
        """Test creating, reading, updating, and deleting an agent."""
        client = get_app_context(ctx).client
        timestamp = int(time.time() * 1000)

        # 1. Create agent using direct API call
        response = client.agents.create_agent(
            agent=AgentRequest(
                name=f"Test Agent Integration {timestamp}",
                model_type="gpt-4o-mini",
                description="Integration test agent",
            )
        )
        assert response.data is not None
        agent_id = response.data.id
        assert agent_id is not None

        try:
            # 2. Get agent
            get_result = get_agent(ctx=ctx, agent_id=agent_id)
            assert f"Test Agent Integration {timestamp}" in get_result
            assert agent_id in get_result

            # 3. Update agent
            update_result = update_agent(
                ctx=ctx, agent_id=agent_id, name=f"Updated Test Agent {timestamp}"
            )
            assert "Agent updated successfully" in update_result

            # 4. Verify update
            get_updated = get_agent(ctx=ctx, agent_id=agent_id)
            assert f"Updated Test Agent {timestamp}" in get_updated

            # 5. List agents (should include our test agent)
            list_result = list_agents(ctx=ctx)
            assert agent_id in list_result

        finally:
            # Cleanup
            try:
                client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")

    def test_agent_with_structured_output(self, ctx):
        """Test creating agent with structured output schema."""
        client = get_app_context(ctx).client
        timestamp = int(time.time() * 1000)

        schema = {
            "type": "object",
            "properties": {
                "response": {"type": "string"},
                "confidence": {"type": "number"},
            },
            "required": ["response"],
        }

        response = client.agents.create_agent(
            agent=AgentRequest(
                name=f"Test Agent with Schema {timestamp}",
                model_type="gpt-4o-mini",
                description="Test agent with structured output",
                structured_output_schema=schema,
            )
        )
        assert response.data is not None
        agent_id = response.data.id
        assert agent_id is not None

        try:
            get_result = get_agent(ctx=ctx, agent_id=agent_id)
            assert agent_id in get_result
        finally:
            try:
                client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
