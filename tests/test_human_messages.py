"""Unit tests for human message tools (list_my_chat_messages, send_my_chat_message)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from thenvoi_mcp.tools.human.human_messages import (
    list_my_chat_messages,
    send_my_chat_message,
)


class TestListMyChatMessages:
    """Tests for list_my_chat_messages tool."""

    def test_returns_messages(self, mock_ctx, mock_human_api):
        """Test successful retrieval of messages."""
        mock_human_api.list_my_chat_messages.return_value = MagicMock(
            model_dump=lambda **kw: {
                "data": [
                    {"id": "msg-1", "content": "Hello"},
                    {"id": "msg-2", "content": "World"},
                ]
            }
        )

        result = list_my_chat_messages(mock_ctx, chat_id="chat-123")

        mock_human_api.list_my_chat_messages.assert_called_once_with(
            chat_id="chat-123",
            page=None,
            page_size=None,
            message_type=None,
            since=None,
        )
        parsed = json.loads(result)
        assert len(parsed["data"]) == 2

    def test_pagination_parameters(self, mock_ctx, mock_human_api):
        """Test pagination parameters are passed through."""
        mock_human_api.list_my_chat_messages.return_value = MagicMock(
            model_dump=lambda **kw: {"data": []}
        )

        list_my_chat_messages(mock_ctx, chat_id="chat-123", page=2, page_size=10)

        mock_human_api.list_my_chat_messages.assert_called_once_with(
            chat_id="chat-123",
            page=2,
            page_size=10,
            message_type=None,
            since=None,
        )

    def test_message_type_filter(self, mock_ctx, mock_human_api):
        """Test filtering by message type."""
        mock_human_api.list_my_chat_messages.return_value = MagicMock(
            model_dump=lambda **kw: {"data": []}
        )

        list_my_chat_messages(mock_ctx, chat_id="chat-123", message_type="text")

        mock_human_api.list_my_chat_messages.assert_called_once_with(
            chat_id="chat-123",
            page=None,
            page_size=None,
            message_type="text",
            since=None,
        )

    def test_since_parameter(self, mock_ctx, mock_human_api):
        """Test since parameter is parsed and passed through."""
        mock_human_api.list_my_chat_messages.return_value = MagicMock(
            model_dump=lambda **kw: {"data": []}
        )

        list_my_chat_messages(
            mock_ctx, chat_id="chat-123", since="2026-01-01T00:00:00Z"
        )

        call_args = mock_human_api.list_my_chat_messages.call_args
        assert call_args.kwargs["since"] is not None


class TestSendMyChatMessage:
    """Tests for send_my_chat_message tool."""

    def test_sends_message_with_recipients(self, mock_ctx, mock_human_api):
        """Test sending a message with recipients."""
        participant = SimpleNamespace(id="agent-1", name="Weather Agent")
        mock_human_api.list_my_chat_participants.return_value = MagicMock(
            data=[participant]
        )
        mock_human_api.send_my_chat_message.return_value = MagicMock(
            model_dump=lambda **kw: {"data": {"id": "msg-new", "content": "Hello!"}}
        )

        result = send_my_chat_message(
            mock_ctx,
            chat_id="chat-123",
            content="Hello!",
            recipients="Weather Agent",
        )

        mock_human_api.list_my_chat_participants.assert_called_once_with(
            chat_id="chat-123"
        )
        mock_human_api.send_my_chat_message.assert_called_once()
        parsed = json.loads(result)
        assert parsed["data"]["id"] == "msg-new"

    def test_raises_when_no_recipients(self, mock_ctx):
        """Test error when recipients is not provided."""
        with pytest.raises(ValueError, match="recipients is required"):
            send_my_chat_message(mock_ctx, chat_id="chat-123", content="Hello!")

    def test_raises_when_recipient_not_found(self, mock_ctx, mock_human_api):
        """Test error when recipient name doesn't match any participant."""
        participant = SimpleNamespace(id="agent-1", name="Existing Agent")
        mock_human_api.list_my_chat_participants.return_value = MagicMock(
            data=[participant]
        )

        with pytest.raises(ValueError, match="Not found: unknown agent"):
            send_my_chat_message(
                mock_ctx,
                chat_id="chat-123",
                content="Hello!",
                recipients="unknown agent",
            )

    def test_multiple_recipients(self, mock_ctx, mock_human_api):
        """Test message with multiple comma-separated recipients."""
        p1 = SimpleNamespace(id="agent-1", name="Agent One")
        p2 = SimpleNamespace(id="agent-2", name="Agent Two")
        mock_human_api.list_my_chat_participants.return_value = MagicMock(data=[p1, p2])
        mock_human_api.send_my_chat_message.return_value = MagicMock(
            model_dump=lambda **kw: {"data": {"id": "msg-new"}}
        )

        send_my_chat_message(
            mock_ctx,
            chat_id="chat-123",
            content="Hello!",
            recipients="Agent One, Agent Two",
        )

        call_args = mock_human_api.send_my_chat_message.call_args
        mentions = call_args.kwargs["message"].mentions
        assert len(mentions) == 2

    def test_resolves_by_username(self, mock_ctx, mock_human_api):
        """Test that participants can be matched by username."""
        participant = SimpleNamespace(id="user-1", name=None, username="jdoe")
        mock_human_api.list_my_chat_participants.return_value = MagicMock(
            data=[participant]
        )
        mock_human_api.send_my_chat_message.return_value = MagicMock(
            model_dump=lambda **kw: {"data": {"id": "msg-new"}}
        )

        send_my_chat_message(
            mock_ctx,
            chat_id="chat-123",
            content="Hello!",
            recipients="jdoe",
        )

        mock_human_api.send_my_chat_message.assert_called_once()

    def test_resolves_by_first_name(self, mock_ctx, mock_human_api):
        """Test that participants can be matched by first_name."""
        participant = SimpleNamespace(id="user-1", name=None, first_name="Sarah")
        mock_human_api.list_my_chat_participants.return_value = MagicMock(
            data=[participant]
        )
        mock_human_api.send_my_chat_message.return_value = MagicMock(
            model_dump=lambda **kw: {"data": {"id": "msg-new"}}
        )

        send_my_chat_message(
            mock_ctx,
            chat_id="chat-123",
            content="Hello!",
            recipients="sarah",
        )

        mock_human_api.send_my_chat_message.assert_called_once()
