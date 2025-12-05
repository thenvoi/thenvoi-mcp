import time


class TestMessageIntegration:
    """Test message management tools against real API."""

    def test_message_lifecycle(self, setup_test_client):
        """Test creating, listing, and deleting messages."""
        from thenvoi_mcp.tools.chats import create_chat, delete_chat
        from thenvoi_mcp.tools.messages import (
            create_chat_message,
            list_chat_messages,
        )

        client, ctx = setup_test_client

        # Use timestamp with milliseconds for unique names
        timestamp = int(time.time() * 1000)

        # Setup: Create agent using direct API call
        response = client.agents.create_agent(
            agent={
                "name": f"Message Test Agent {timestamp}",
                "model_type": "gpt-4o-mini",
                "description": "Agent for message tests",
            }
        )
        assert response.data is not None
        agent_id = response.data.id
        assert agent_id is not None

        try:
            create_chat_result = create_chat(
                ctx,
                title=f"Test Chat for Messages {timestamp}",
                chat_type="direct",
                owner_id=agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_chat_result
            chat_id = create_chat_result.split(": ")[1].strip()

            try:
                # 1. Create message (sender is determined by API from auth)
                create_msg_result = create_chat_message(
                    ctx,
                    chat_id=chat_id,
                    content="Test message from integration test",
                )

                assert "Message sent successfully" in create_msg_result
                message_id = create_msg_result.split(": ")[1].strip()

                # 2. List messages (should include our test message)
                list_result = list_chat_messages(ctx, chat_id=chat_id)
                assert message_id in list_result
                assert "Test message from integration test" in list_result

            finally:
                # Cleanup: Delete chat
                delete_chat(ctx, chat_id=chat_id)
        finally:
            # Cleanup: Delete agent
            try:
                client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
