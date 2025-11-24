import time
import pytest


class TestParticipantIntegration:
    """Test participant management tools against real API."""

    @pytest.mark.asyncio
    async def test_participant_lifecycle(self, setup_test_client):
        """Test adding, listing, and removing participants."""
        from thenvoi_mcp.tools.chats import create_chat, delete_chat
        from thenvoi_mcp.tools.agents import create_agent
        from thenvoi_mcp.tools.participants import (
            add_chat_participant,
            list_chat_participants,
            remove_chat_participant,
            list_available_participants,
        )
        from thenvoi_mcp import shared

        # Use timestamp with milliseconds for unique names
        timestamp = int(time.time() * 1000)

        # Setup: Create agents (one for owner, one for participant)
        owner_agent_result = await create_agent(
            name=f"Chat Owner Agent {timestamp}",
            model_type="gpt-4o-mini",
            description="Agent for chat ownership",
        )

        assert "Agent created successfully" in owner_agent_result
        owner_agent_id = owner_agent_result.split(": ")[1].strip()

        try:
            create_chat_result = await create_chat(
                title=f"Test Chat for Participants {timestamp}",
                chat_type="group",
                owner_id=owner_agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_chat_result
            chat_id = create_chat_result.split(": ")[1].strip()

            create_agent_result = await create_agent(
                name=f"Test Participant Agent {timestamp}",
                model_type="gpt-4o-mini",
                description="Test agent for participant tests",
            )

            assert "Agent created successfully" in create_agent_result
            agent_id = create_agent_result.split(": ")[1].strip()

            try:
                # 1. List available participants
                available_result = await list_available_participants(
                    chat_id=chat_id, participant_type="Agent"
                )
                assert "participants" in available_result

                # 2. Add participant
                add_result = await add_chat_participant(
                    chat_id=chat_id, participant_id=agent_id, role="member"
                )
                assert "Participant added successfully" in add_result

                # 3. List participants (should include our agent)
                list_result = await list_chat_participants(chat_id=chat_id)
                assert agent_id in list_result

                # 4. Remove participant
                remove_result = await remove_chat_participant(
                    chat_id=chat_id, participant_id=agent_id
                )
                assert "Participant removed successfully" in remove_result

            finally:
                # Cleanup: Delete participant agent and chat
                try:
                    shared.client.agents.delete_agent(id=agent_id)
                except Exception as e:
                    print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
                await delete_chat(chat_id=chat_id)
        finally:
            # Cleanup: Delete owner agent
            try:
                shared.client.agents.delete_agent(id=owner_agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup owner agent {owner_agent_id}: {e}")
