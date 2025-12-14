"""Unit tests for message tools (get_agent_chat_context, create_agent_chat_message)."""

import json

import pytest

from tests.fixtures import factory
from thenvoi_mcp.tools.messages import create_agent_chat_message, get_agent_chat_context


class TestGetAgentChatContext:
    """Tests for get_agent_chat_context tool."""

    def test_returns_context_messages(self, mock_ctx, mock_agent_api):
        """Test successful retrieval of context messages."""
        chat_id = "chat-123"
        messages = [
            factory.chat_message(content="Hello", message_type="text"),
            factory.chat_message(content="Thinking...", message_type="thought"),
        ]
        mock_agent_api.get_agent_chat_context.return_value = factory.list_response(
            messages
        )

        result = get_agent_chat_context(mock_ctx, chat_id=chat_id)

        mock_agent_api.get_agent_chat_context.assert_called_once_with(
            chat_id=chat_id,
            page=None,
            page_size=None,
        )
        parsed = json.loads(result)
        assert len(parsed["data"]) == 2

    def test_pagination_parameters(self, mock_ctx, mock_agent_api):
        """Test pagination parameters are passed through."""
        mock_agent_api.get_agent_chat_context.return_value = factory.list_response([])

        get_agent_chat_context(mock_ctx, chat_id="chat-123", page=2, page_size=25)

        mock_agent_api.get_agent_chat_context.assert_called_once_with(
            chat_id="chat-123",
            page=2,
            page_size=25,
        )

    def test_empty_context(self, mock_ctx, mock_agent_api):
        """Test handling of empty context."""
        mock_agent_api.get_agent_chat_context.return_value = factory.list_response([])

        result = get_agent_chat_context(mock_ctx, chat_id="empty-chat")

        parsed = json.loads(result)
        assert parsed["data"] == []


class TestCreateAgentChatMessage:
    """Tests for create_agent_chat_message tool."""

    def test_creates_message_with_recipients(self, mock_ctx, mock_agent_api):
        """Test creating a message using recipients parameter."""
        chat_id = "chat-123"
        content = "Hello everyone!"
        participant = factory.chat_participant(id="agent-456", name="Weather Agent")
        mock_agent_api.list_agent_chat_participants.return_value = (
            factory.list_response([participant])
        )
        message = factory.chat_message(id="msg-789", content=content)
        mock_agent_api.create_agent_chat_message.return_value = factory.response(
            message
        )

        result = create_agent_chat_message(
            mock_ctx, chat_id=chat_id, content=content, recipients="Weather Agent"
        )

        mock_agent_api.list_agent_chat_participants.assert_called_once_with(
            chat_id=chat_id
        )
        mock_agent_api.create_agent_chat_message.assert_called_once()
        parsed = json.loads(result)
        assert parsed["data"]["id"] == "msg-789"

    def test_creates_message_with_mentions(self, mock_ctx, mock_agent_api):
        """Test creating a message using pre-resolved mentions."""
        chat_id = "chat-123"
        content = "Hello!"
        mentions = '[{"id": "agent-456", "name": "Weather Agent"}]'
        message = factory.chat_message(id="msg-789", content=content)
        mock_agent_api.create_agent_chat_message.return_value = factory.response(
            message
        )

        result = create_agent_chat_message(
            mock_ctx, chat_id=chat_id, content=content, mentions=mentions
        )

        # Should NOT call list_agent_chat_participants when mentions is provided
        mock_agent_api.list_agent_chat_participants.assert_not_called()
        mock_agent_api.create_agent_chat_message.assert_called_once()
        parsed = json.loads(result)
        assert parsed["data"]["id"] == "msg-789"

    def test_mentions_takes_precedence_over_recipients(self, mock_ctx, mock_agent_api):
        """Test that mentions takes precedence when both are provided."""
        chat_id = "chat-123"
        mentions = '[{"id": "agent-456", "name": "Weather Agent"}]'
        message = factory.chat_message(id="msg-789")
        mock_agent_api.create_agent_chat_message.return_value = factory.response(
            message
        )

        create_agent_chat_message(
            mock_ctx,
            chat_id=chat_id,
            content="Hello!",
            recipients="Other Agent",  # Should be ignored
            mentions=mentions,
        )

        # Should NOT call list_agent_chat_participants when mentions is provided
        mock_agent_api.list_agent_chat_participants.assert_not_called()

    def test_raises_when_no_recipients_or_mentions(self, mock_ctx, mock_agent_api):
        """Test error when neither recipients nor mentions is provided."""
        with pytest.raises(ValueError, match="Missing recipients or mentions"):
            create_agent_chat_message(mock_ctx, chat_id="chat-123", content="Hello!")

    def test_raises_on_invalid_mentions_json(self, mock_ctx, mock_agent_api):
        """Test error handling for invalid JSON in mentions."""
        with pytest.raises(ValueError, match="Invalid JSON for mentions"):
            create_agent_chat_message(
                mock_ctx,
                chat_id="chat-123",
                content="Hello!",
                mentions="not valid json",
            )

    def test_raises_when_recipient_not_found(self, mock_ctx, mock_agent_api):
        """Test error when recipient name doesn't match any participant."""
        participant = factory.chat_participant(name="Existing Agent")
        mock_agent_api.list_agent_chat_participants.return_value = (
            factory.list_response([participant])
        )

        with pytest.raises(
            ValueError, match="Could not find participants: unknown agent"
        ):
            create_agent_chat_message(
                mock_ctx,
                chat_id="chat-123",
                content="Hello!",
                recipients="unknown agent",
            )

    def test_multiple_recipients(self, mock_ctx, mock_agent_api):
        """Test message with multiple comma-separated recipients."""
        participants = [
            factory.chat_participant(id="agent-1", name="Agent One"),
            factory.chat_participant(id="agent-2", name="Agent Two"),
        ]
        mock_agent_api.list_agent_chat_participants.return_value = (
            factory.list_response(participants)
        )
        message = factory.chat_message(id="msg-789")
        mock_agent_api.create_agent_chat_message.return_value = factory.response(
            message
        )

        create_agent_chat_message(
            mock_ctx,
            chat_id="chat-123",
            content="Hello!",
            recipients="Agent One, Agent Two",
        )

        call_args = mock_agent_api.create_agent_chat_message.call_args
        mentions = call_args.kwargs["message"].mentions
        assert len(mentions) == 2

    def test_recipient_matching_is_case_insensitive(self, mock_ctx, mock_agent_api):
        """Test that recipient name matching is case insensitive."""
        participant = factory.chat_participant(id="agent-456", name="Weather Agent")
        mock_agent_api.list_agent_chat_participants.return_value = (
            factory.list_response([participant])
        )
        message = factory.chat_message(id="msg-789")
        mock_agent_api.create_agent_chat_message.return_value = factory.response(
            message
        )

        create_agent_chat_message(
            mock_ctx, chat_id="chat-123", content="Hello!", recipients="WEATHER AGENT"
        )

        mock_agent_api.create_agent_chat_message.assert_called_once()
