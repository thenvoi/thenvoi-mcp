import time

from thenvoi_client_rest import AgentRequest

from thenvoi_mcp.shared import get_app_context
from thenvoi_mcp.tools.chats import create_chat, delete_chat
from thenvoi_mcp.tools.messages import (
    create_chat_message,
    delete_chat_message,
    list_chat_messages,
)


class TestMessageIntegration:
    """Test message management tools against real API."""

    def test_message_lifecycle(self, ctx):
        """Test creating, listing, and deleting messages."""
        client = get_app_context(ctx).client
        timestamp = int(time.time() * 1000)

        # Setup: Create agent
        response = client.agents.create_agent(
            agent=AgentRequest(
                name=f"Message Test Agent {timestamp}",
                model_type="gpt-4o-mini",
                description="Agent for message tests",
            )
        )
        assert response.data is not None
        agent_id = response.data.id
        assert agent_id is not None

        try:
            create_chat_result = create_chat(
                ctx=ctx,
                title=f"Test Chat for Messages {timestamp}",
                chat_type="direct",
                owner_id=agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_chat_result
            chat_id = create_chat_result.split(": ")[1].strip()

            try:
                # 1. Create message
                create_msg_result = create_chat_message(
                    ctx=ctx,
                    chat_id=chat_id,
                    content="Test message from integration test",
                )

                assert "Message sent successfully" in create_msg_result
                message_id = create_msg_result.split(": ")[1].strip()

                # 2. List messages (should include our test message)
                list_result = list_chat_messages(ctx=ctx, chat_id=chat_id)
                assert message_id in list_result
                assert "Test message from integration test" in list_result

                # 3. Delete message
                delete_msg_result = delete_chat_message(
                    ctx=ctx, chat_id=chat_id, message_id=message_id
                )
                assert "Message deleted successfully" in delete_msg_result

            finally:
                delete_chat(ctx=ctx, chat_id=chat_id)
        finally:
            try:
                client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
