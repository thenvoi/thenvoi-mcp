import time

from thenvoi_client_rest import AgentRequest

from thenvoi_mcp.shared import get_app_context
from thenvoi_mcp.tools.chats import create_chat, delete_chat
from thenvoi_mcp.tools.participants import (
    add_chat_participant,
    list_available_participants,
    list_chat_participants,
    remove_chat_participant,
)


class TestParticipantIntegration:
    """Test participant management tools against real API."""

    def test_participant_lifecycle(self, ctx):
        """Test adding, listing, and removing participants."""
        client = get_app_context(ctx).client
        timestamp = int(time.time() * 1000)

        # Setup: Create agents (one for owner, one for participant)
        owner_response = client.agents.create_agent(
            agent=AgentRequest(
                name=f"Chat Owner Agent {timestamp}",
                model_type="gpt-4o-mini",
                description="Agent for chat ownership",
            )
        )
        assert owner_response.data is not None
        owner_agent_id = owner_response.data.id
        assert owner_agent_id is not None

        try:
            create_chat_result = create_chat(
                ctx=ctx,
                title=f"Test Chat for Participants {timestamp}",
                chat_type="group",
                owner_id=owner_agent_id,
                owner_type="Agent",
            )

            assert "Chat room created successfully" in create_chat_result
            chat_id = create_chat_result.split(": ")[1].strip()

            participant_response = client.agents.create_agent(
                agent=AgentRequest(
                    name=f"Test Participant Agent {timestamp}",
                    model_type="gpt-4o-mini",
                    description="Test agent for participant tests",
                )
            )
            assert participant_response.data is not None
            agent_id = participant_response.data.id
            assert agent_id is not None

            try:
                # 1. List available participants
                available_result = list_available_participants(
                    ctx=ctx, chat_id=chat_id, participant_type="Agent"
                )
                assert "participants" in available_result

                # 2. Add participant
                add_result = add_chat_participant(
                    ctx=ctx, chat_id=chat_id, participant_id=agent_id, role="member"
                )
                assert "Participant added successfully" in add_result

                # 3. List participants (should include our agent)
                list_result = list_chat_participants(ctx=ctx, chat_id=chat_id)
                assert agent_id in list_result

                # 4. Remove participant
                remove_result = remove_chat_participant(
                    ctx=ctx, chat_id=chat_id, participant_id=agent_id
                )
                assert "Participant removed successfully" in remove_result

            finally:
                try:
                    client.agents.delete_agent(id=agent_id)
                except Exception as e:
                    print(f"Warning: Failed to cleanup agent {agent_id}: {e}")
                delete_chat(ctx=ctx, chat_id=chat_id)
        finally:
            try:
                client.agents.delete_agent(id=owner_agent_id)
            except Exception as e:
                print(f"Warning: Failed to cleanup owner agent {owner_agent_id}: {e}")
