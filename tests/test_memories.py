"""Unit tests for memory tools."""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from thenvoi_mcp.tools.agent.agent_memories import (
    archive_agent_memory,
    create_agent_memory,
    list_agent_memories,
)
from thenvoi_mcp.tools.human.human_memories import (
    delete_user_memory,
    list_user_memories,
    restore_user_memory,
)


def make_response(payload: dict[str, object]) -> Mock:
    """Create a mock SDK response."""
    response = Mock()
    response.model_dump.return_value = payload
    return response


class TestAgentMemories:
    """Tests for agent memory tools."""

    def test_lists_agent_memories(
        self, mock_ctx: Mock, mock_agent_api_memories: Mock
    ) -> None:
        mock_agent_api_memories.list_agent_memories.return_value = make_response(
            {"data": [{"id": "mem-1"}]}
        )

        result = list_agent_memories(
            mock_ctx,
            subject_id="subject-1",
            scope="subject",
            system="long_term",
            memory_type="semantic",
            segment="agent",
            content_query="fern",
            page_size=25,
            status="active",
        )

        mock_agent_api_memories.list_agent_memories.assert_called_once_with(
            subject_id="subject-1",
            scope="subject",
            system="long_term",
            type="semantic",
            segment="agent",
            content_query="fern",
            page_size=25,
            status="active",
        )
        assert json.loads(result)["data"][0]["id"] == "mem-1"

    def test_creates_agent_memory(
        self, mock_ctx: Mock, mock_agent_api_memories: Mock
    ) -> None:
        mock_agent_api_memories.create_agent_memory.return_value = make_response(
            {"data": {"id": "mem-2"}}
        )

        result = create_agent_memory(
            mock_ctx,
            content="Remember this",
            thought="This helps later",
            system="long_term",
            segment="agent",
            memory_type="semantic",
            scope="subject",
            subject_id="subject-1",
            metadata='{"topic":"mcp"}',
        )

        call = mock_agent_api_memories.create_agent_memory.call_args
        memory = call.kwargs["memory"]
        assert memory.content == "Remember this"
        assert memory.metadata.topic == "mcp"
        assert json.loads(result)["data"]["id"] == "mem-2"

    def test_rejects_invalid_memory_metadata(self, mock_ctx: Mock) -> None:
        with pytest.raises(ValueError, match="Invalid JSON for metadata"):
            create_agent_memory(
                mock_ctx,
                content="Remember this",
                thought="This helps later",
                system="long_term",
                segment="agent",
                memory_type="semantic",
                metadata="{bad json}",
            )

    def test_archives_agent_memory(
        self, mock_ctx: Mock, mock_agent_api_memories: Mock
    ) -> None:
        mock_agent_api_memories.archive_agent_memory.return_value = make_response(
            {"data": {"id": "mem-3"}}
        )

        result = archive_agent_memory(mock_ctx, memory_id="mem-3")

        mock_agent_api_memories.archive_agent_memory.assert_called_once_with("mem-3")
        assert json.loads(result)["data"]["id"] == "mem-3"


class TestHumanMemories:
    """Tests for human memory tools."""

    def test_lists_user_memories(
        self, mock_ctx: Mock, mock_human_api_memories: Mock
    ) -> None:
        mock_human_api_memories.list_user_memories.return_value = make_response(
            {"data": [{"id": "mem-4"}]}
        )

        result = list_user_memories(
            mock_ctx,
            chat_room_id="chat-1",
            scope="subject",
            system="working",
            memory_type="episodic",
            segment="user",
            content_query="fern",
            page_size=10,
            status="active",
        )

        mock_human_api_memories.list_user_memories.assert_called_once_with(
            chat_room_id="chat-1",
            scope="subject",
            system="working",
            type="episodic",
            segment="user",
            content_query="fern",
            page_size=10,
            status="active",
        )
        assert json.loads(result)["data"][0]["id"] == "mem-4"

    def test_restores_user_memory(
        self, mock_ctx: Mock, mock_human_api_memories: Mock
    ) -> None:
        mock_human_api_memories.restore_user_memory.return_value = make_response(
            {"data": {"id": "mem-5"}}
        )

        result = restore_user_memory(mock_ctx, memory_id="mem-5")

        mock_human_api_memories.restore_user_memory.assert_called_once_with("mem-5")
        assert json.loads(result)["data"]["id"] == "mem-5"

    def test_deletes_user_memory(
        self, mock_ctx: Mock, mock_human_api_memories: Mock
    ) -> None:
        result = delete_user_memory(mock_ctx, memory_id="mem-6")

        mock_human_api_memories.delete_user_memory.assert_called_once_with("mem-6")
        assert json.loads(result) == {"deleted": True, "id": "mem-6"}
