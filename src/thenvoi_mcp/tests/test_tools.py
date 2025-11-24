import pytest


class TestToolIntegration:
    """Test tool management tools against real API."""

    @pytest.mark.asyncio
    async def test_tool_lifecycle(self, setup_test_client):
        """Test creating, reading, updating, and deleting a tool."""
        from thenvoi_mcp.tools.tools import (
            create_tool,
            get_tool,
            update_tool,
            delete_tool,
            list_tools,
        )

        # 1. Create tool
        create_result = await create_tool(
            name="test_integration_tool", description="Integration test tool"
        )

        assert "Tool created successfully" in create_result
        tool_id = create_result.split(": ")[1].strip()

        try:
            # 2. Get tool
            get_result = await get_tool(tool_id=tool_id)
            assert "test_integration_tool" in get_result
            assert tool_id in get_result

            # 3. Update tool
            update_result = await update_tool(
                tool_id=tool_id,
                name="test_integration_tool",  # API requires name even when updating
                description="Updated integration test tool",
            )
            assert "Tool updated successfully" in update_result

            # 4. List tools (should include our test tool)
            list_result = await list_tools()
            assert tool_id in list_result

        finally:
            # 5. Cleanup: Delete tool
            delete_result = await delete_tool(tool_id=tool_id)
            assert "Tool deleted successfully" in delete_result
