"""Test that all SDK resource methods call correct API endpoint paths.

Uses unittest.mock to intercept the low-level client.request() method
and verify each resource method calls the right (method, path) pair.
No external test dependencies required beyond pytest.
"""

from unittest.mock import MagicMock

import pytest

from memorykit import MemoryKit


@pytest.fixture
def mk():
    """Create a MemoryKit client with mocked HTTP layer."""
    client = MemoryKit(api_key="ctx_test_key")
    # Mock the internal request method to capture calls
    client.chats._client.request = MagicMock(return_value={})
    client.memories._client.request = MagicMock(return_value={})
    client.users._client.request = MagicMock(return_value={})
    return client


# ---------------------------------------------------------------------------
# Memories
# ---------------------------------------------------------------------------


class TestMemoriesEndpoints:
    def test_create_path(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1", "status": "pending"}
        mk.memories.create(content="hello")
        mk.memories._client.request.assert_called_once()
        args = mk.memories._client.request.call_args
        assert args[0] == ("POST", "/memories")

    def test_list_path(self, mk):
        mk.memories._client.request.return_value = {"data": [], "hasMore": False, "cursor": None}
        mk.memories.list()
        args = mk.memories._client.request.call_args
        assert args[0] == ("GET", "/memories")

    def test_get_path(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1"}
        mk.memories.get("mem_1")
        args = mk.memories._client.request.call_args
        assert args[0] == ("GET", "/memories/mem_1")

    def test_update_path(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1"}
        mk.memories.update("mem_1", title="New")
        args = mk.memories._client.request.call_args
        assert args[0] == ("PUT", "/memories/mem_1")

    def test_delete_path(self, mk):
        mk.memories._client.request.return_value = {}
        mk.memories.delete("mem_1")
        args = mk.memories._client.request.call_args
        assert args[0] == ("DELETE", "/memories/mem_1")

    def test_batch_create_path(self, mk):
        mk.memories._client.request.return_value = {"accepted": 1, "rejected": 0, "errors": []}
        mk.memories.batch_create(items=[{"content": "hello"}])
        args = mk.memories._client.request.call_args
        assert args[0] == ("POST", "/memories/batch")

    def test_search_path(self, mk):
        mk.memories._client.request.return_value = {"results": [], "totalResults": 0}
        mk.memories.search(query="test")
        args = mk.memories._client.request.call_args
        assert args[0] == ("POST", "/memories/search")

    def test_query_path(self, mk):
        mk.memories._client.request.return_value = {"answer": "test", "confidence": 0.9, "sources": []}
        mk.memories.query(query="test")
        args = mk.memories._client.request.call_args
        assert args[0] == ("POST", "/memories/query")


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------


class TestChatsEndpoints:
    def test_create_path(self, mk):
        mk.chats._client.request.return_value = {"id": "chat_1"}
        mk.chats.create()
        args = mk.chats._client.request.call_args
        assert args[0] == ("POST", "/chats")

    def test_list_path(self, mk):
        mk.chats._client.request.return_value = {"data": [], "hasMore": False, "cursor": None}
        mk.chats.list()
        args = mk.chats._client.request.call_args
        assert args[0] == ("GET", "/chats")

    def test_get_history_path(self, mk):
        """Critical: must be /chats/{id}/messages, NOT /chats/{id}."""
        mk.chats._client.request.return_value = {"id": "chat_1", "messages": []}
        mk.chats.get_history("chat_1")
        args = mk.chats._client.request.call_args
        assert args[0] == ("GET", "/chats/chat_1/messages")

    def test_send_message_path(self, mk):
        mk.chats._client.request.return_value = {"message": {"id": "msg_1", "role": "assistant", "content": "hi"}}
        mk.chats.send_message("chat_1", message="hello")
        args = mk.chats._client.request.call_args
        assert args[0] == ("POST", "/chats/chat_1/messages")

    def test_delete_path(self, mk):
        mk.chats._client.request.return_value = {}
        mk.chats.delete("chat_1")
        args = mk.chats._client.request.call_args
        assert args[0] == ("DELETE", "/chats/chat_1")


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class TestUsersEndpoints:
    def test_upsert_path(self, mk):
        mk.users._client.request.return_value = {"id": "user_1"}
        mk.users.upsert(id="user_1")
        args = mk.users._client.request.call_args
        assert args[0] == ("POST", "/users")

    def test_get_path(self, mk):
        mk.users._client.request.return_value = {"id": "user_1"}
        mk.users.get("user_1")
        args = mk.users._client.request.call_args
        assert args[0] == ("GET", "/users/user_1")

    def test_delete_path(self, mk):
        mk.users._client.request.return_value = {}
        mk.users.delete("user_1")
        args = mk.users._client.request.call_args
        assert args[0] == ("DELETE", "/users/user_1")

    def test_create_event_path(self, mk):
        mk.users._client.request.return_value = {"id": "evt_1"}
        mk.users.create_event("user_1", type="page_view")
        args = mk.users._client.request.call_args
        assert args[0] == ("POST", "/users/user_1/events")

    def test_list_events_path(self, mk):
        mk.users._client.request.return_value = []
        mk.users.list_events("user_1")
        args = mk.users._client.request.call_args
        assert args[0] == ("GET", "/users/user_1/events")
