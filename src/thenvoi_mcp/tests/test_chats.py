import time


class TestChatIntegration:
    """Test chat management tools against real API."""

    def test_chat_lifecycle(self, setup_test_client):
        """Test creating, reading, updating, and deleting a chat."""
        from thenvoi_mcp.tools.chats import (
            create_chat,
            get_chat,
            update_chat,
            delete_chat,
            list_chats,
        )

        client, ctx = setup_test_client

        # Use timestamp with milliseconds for unique names
        timestamp = int(time.time() * 1000)

        # Setup: Create an agent to be the chat owner using direct API call
        response = client.agents.create_agent(
            agent={
                "name": f"Chat Owner Agent {timestamp}",
                "model_type": "gpt-4o-mini",
                "description": "Agent for chat ownership",
            }
        )
        assert response.data is not None
        agent_id = response.data.id
        assert agent_id is not None

        try:
            # 1. Create chat
            create_result = create_chat(
                ctx,
                title=f"Test Chat Integration {timestamp}",
                chat_type="direct",
                owner_id=agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_result
            chat_id = create_result.split(": ")[1].strip()

            try:
                # 2. Get chat
                get_result = get_chat(ctx, chat_id=chat_id)
                assert f"Test Chat Integration {timestamp}" in get_result
                assert chat_id in get_result

                # 3. Update chat
                update_result = update_chat(
                    ctx, chat_id=chat_id, title=f"Updated Test Chat {timestamp}"
                )
                assert "Chat room updated successfully" in update_result

                # 4. List chats (should include our test chat)
                list_result = list_chats(ctx)
                assert chat_id in list_result

            finally:
                # Cleanup: Delete chat
                delete_chat(ctx, chat_id=chat_id)
        finally:
            # Cleanup: Delete agent
            try:
                client.agents.delete_agent(id=agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
