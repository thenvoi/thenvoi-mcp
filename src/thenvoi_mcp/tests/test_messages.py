import time
import pytest


class TestMessageIntegration:
    """Test message management tools against real API."""

    @pytest.mark.asyncio
    async def test_message_lifecycle(self, setup_test_client):
        """Test creating, listing, and deleting messages."""
        from thenvoi_mcp.tools.agents import create_agent
        from thenvoi_mcp.tools.chats import create_chat, delete_chat
        from thenvoi_mcp.tools.messages import (
            create_chat_message,
            list_chat_messages,
            delete_chat_message,
        )
        from thenvoi_mcp import shared

        # Use timestamp with milliseconds for unique names
        timestamp = int(time.time() * 1000)

        # Setup: Create agent and chat
        agent_result = await create_agent(
            name=f"Message Test Agent {timestamp}",
            model_type="gpt-4o-mini",
            description="Agent for message tests",
        )

        assert "Agent created successfully" in agent_result
        agent_id = agent_result.split(": ")[1].strip()

        try:
            create_chat_result = await create_chat(
                title=f"Test Chat for Messages {timestamp}",
                chat_type="direct",
                owner_id=agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_chat_result
            chat_id = create_chat_result.split(": ")[1].strip()

            try:
                # 1. Create message
                create_msg_result = await create_chat_message(
                    chat_id=chat_id,
                    content="Test message from integration test",
                    sender_id=agent_id,
                    sender_type="Agent",
                )

                assert "Message created successfully" in create_msg_result
                message_id = create_msg_result.split(": ")[1].strip()

                # 2. List messages (should include our test message)
                list_result = await list_chat_messages(chat_id=chat_id)
                assert message_id in list_result
                assert "Test message from integration test" in list_result

                # 3. Delete message
                delete_msg_result = await delete_chat_message(
                    chat_id=chat_id, message_id=message_id
                )
                assert "Message deleted successfully" in delete_msg_result

            finally:
                # Cleanup: Delete chat
                await delete_chat(chat_id=chat_id)
        finally:
            # Cleanup: Delete agent
            try:
                shared.client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
