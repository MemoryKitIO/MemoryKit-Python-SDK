"""Tests for request building — verify correct URL construction, headers, params, and payloads."""

from unittest.mock import MagicMock

import pytest

from memorykit import MemoryKit


@pytest.fixture
def mk():
    """Create a MemoryKit client with mocked HTTP layer."""
    client = MemoryKit(api_key="ctx_test_key")
    # Mock all resource clients' request methods
    for resource in [
        client.memories,
        client.chats,
        client.users,
        client.webhooks,
        client.status,
        client.feedback,
    ]:
        resource._client.request = MagicMock(return_value={})
    return client


# ---------------------------------------------------------------------------
# Memories — request payload verification
# ---------------------------------------------------------------------------


class TestMemoriesRequestBuilding:
    def test_create_sends_all_params(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1", "status": "pending"}
        mk.memories.create(
            content="hello",
            title="My Title",
            type="article",
            tags=["a", "b"],
            metadata={"key": "val"},
            user_id="user_1",
            language="en",
            format="text",
        )
        args = mk.memories._client.request.call_args
        body = args[1]["json"]
        assert body["content"] == "hello"
        assert body["title"] == "My Title"
        assert body["type"] == "article"
        assert body["tags"] == ["a", "b"]
        assert body["metadata"] == {"key": "val"}
        assert body["user_id"] == "user_1"
        assert body["language"] == "en"
        assert body["format"] == "text"

    def test_create_minimal(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1", "status": "pending"}
        mk.memories.create(content="just content")
        args = mk.memories._client.request.call_args
        body = args[1]["json"]
        assert body["content"] == "just content"

    def test_list_sends_params(self, mk):
        mk.memories._client.request.return_value = {"data": [], "has_more": False}
        mk.memories.list(limit=10, status="completed", type="article", user_id="u1")
        args = mk.memories._client.request.call_args
        params = args[1]["params"]
        assert params["limit"] == 10
        assert params["status"] == "completed"
        assert params["type"] == "article"
        assert params["user_id"] == "u1"

    def test_update_sends_only_provided_fields(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1"}
        mk.memories.update("mem_1", title="New Title")
        args = mk.memories._client.request.call_args
        body = args[1]["json"]
        assert body["title"] == "New Title"

    def test_query_sends_all_params(self, mk):
        mk.memories._client.request.return_value = {"answer": "", "confidence": 0.0, "sources": []}
        mk.memories.query(
            query="test query",
            max_sources=5,
            temperature=0.5,
            mode="precise",
            user_id="u1",
            instructions="Be concise",
            response_format="markdown",
            include_graph=True,
            filters={"tags": ["important"]},
        )
        args = mk.memories._client.request.call_args
        body = args[1]["json"]
        assert body["query"] == "test query"
        assert body["max_sources"] == 5
        assert body["temperature"] == 0.5
        assert body["mode"] == "precise"
        assert body["user_id"] == "u1"
        assert body["instructions"] == "Be concise"
        assert body["response_format"] == "markdown"
        assert body["include_graph"] is True
        assert body["filters"] == {"tags": ["important"]}

    def test_search_sends_all_params(self, mk):
        mk.memories._client.request.return_value = {"results": [], "total_results": 0}
        mk.memories.search(
            query="search term",
            precision="high",
            limit=20,
            include_graph=True,
            user_id="u1",
            type="article",
            tags=["python", "sdk"],
            created_after="2025-01-01T00:00:00Z",
            created_before="2025-12-31T23:59:59Z",
        )
        args = mk.memories._client.request.call_args
        params = args[1]["params"]
        assert params["query"] == "search term"
        assert params["precision"] == "high"
        assert params["limit"] == 20
        assert params["include_graph"] is True
        assert params["user_id"] == "u1"
        assert params["type"] == "article"
        assert params["tags"] == "python,sdk"
        assert params["created_after"] == "2025-01-01T00:00:00Z"
        assert params["created_before"] == "2025-12-31T23:59:59Z"

    def test_search_handles_datetime_objects(self, mk):
        from datetime import datetime, timezone

        mk.memories._client.request.return_value = {"results": []}
        dt_after = datetime(2025, 1, 1, tzinfo=timezone.utc)
        dt_before = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        mk.memories.search(
            query="test",
            created_after=dt_after,
            created_before=dt_before,
        )
        args = mk.memories._client.request.call_args
        params = args[1]["params"]
        assert params["created_after"] == dt_after.isoformat()
        assert params["created_before"] == dt_before.isoformat()

    def test_search_tags_as_string(self, mk):
        mk.memories._client.request.return_value = {"results": []}
        mk.memories.search(query="test", tags="a,b,c")
        args = mk.memories._client.request.call_args
        params = args[1]["params"]
        assert params["tags"] == "a,b,c"

    def test_batch_create_sends_items(self, mk):
        mk.memories._client.request.return_value = {"accepted": 2, "rejected": 0, "items": []}
        items = [{"content": "item1"}, {"content": "item2"}]
        mk.memories.batch_create(items=items, defaults={"type": "note"})
        args = mk.memories._client.request.call_args
        body = args[1]["json"]
        assert body["items"] == items
        assert body["defaults"] == {"type": "note"}

    def test_reprocess_path_and_method(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1", "status": "processing"}
        mk.memories.reprocess("mem_1")
        args = mk.memories._client.request.call_args
        assert args[0] == ("POST", "/memories/mem_1/reprocess")


# ---------------------------------------------------------------------------
# Chats — request payload verification
# ---------------------------------------------------------------------------


class TestChatsRequestBuilding:
    def test_create_sends_all_params(self, mk):
        mk.chats._client.request.return_value = {"id": "chat_1"}
        mk.chats.create(
            user_id="u1",
            title="Support Chat",
            metadata={"priority": "high"},
        )
        args = mk.chats._client.request.call_args
        body = args[1]["json"]
        assert body["user_id"] == "u1"
        assert body["title"] == "Support Chat"
        assert body["metadata"] == {"priority": "high"}

    def test_list_sends_params(self, mk):
        mk.chats._client.request.return_value = {"data": [], "has_more": False}
        mk.chats.list(user_id="u1", limit=5, starting_after="cur_abc")
        args = mk.chats._client.request.call_args
        params = args[1]["params"]
        assert params["user_id"] == "u1"
        assert params["limit"] == 5
        assert params["starting_after"] == "cur_abc"

    def test_send_message_sends_all_params(self, mk):
        mk.chats._client.request.return_value = {
            "message": {"id": "msg_1", "role": "assistant", "content": "hi"}
        }
        mk.chats.send_message(
            "chat_1",
            message="hello",
            mode="fast",
            max_sources=3,
            temperature=0.3,
            user_id="u1",
            instructions="Short answers",
            response_format="text",
            filters={"tags": ["faq"]},
        )
        args = mk.chats._client.request.call_args
        assert args[0] == ("POST", "/chats/chat_1/messages")
        body = args[1]["json"]
        assert body["message"] == "hello"
        assert body["mode"] == "fast"
        assert body["max_sources"] == 3
        assert body["temperature"] == 0.3
        assert body["user_id"] == "u1"
        assert body["instructions"] == "Short answers"

    def test_get_history_path(self, mk):
        mk.chats._client.request.return_value = {"id": "chat_1", "messages": []}
        mk.chats.get_history("chat_1")
        args = mk.chats._client.request.call_args
        assert args[0] == ("GET", "/chats/chat_1/messages")


# ---------------------------------------------------------------------------
# Users — request payload verification
# ---------------------------------------------------------------------------


class TestUsersRequestBuilding:
    def test_upsert_sends_all_params(self, mk):
        mk.users._client.request.return_value = {"id": "u1"}
        mk.users.upsert(
            id="u1",
            email="alice@example.com",
            name="Alice",
            metadata={"role": "admin"},
        )
        args = mk.users._client.request.call_args
        body = args[1]["json"]
        assert body["id"] == "u1"
        assert body["email"] == "alice@example.com"
        assert body["name"] == "Alice"
        assert body["metadata"] == {"role": "admin"}

    def test_update_sends_params(self, mk):
        mk.users._client.request.return_value = {"id": "u1"}
        mk.users.update("u1", email="new@example.com", name="Bob")
        args = mk.users._client.request.call_args
        assert args[0] == ("PUT", "/users/u1")
        body = args[1]["json"]
        assert body["email"] == "new@example.com"
        assert body["name"] == "Bob"

    def test_delete_user(self, mk):
        mk.users._client.request.return_value = {}
        mk.users.delete("u1")
        args = mk.users._client.request.call_args
        assert args[0] == ("DELETE", "/users/u1")

    def test_create_event_sends_params(self, mk):
        mk.users._client.request.return_value = {"id": "evt_1"}
        mk.users.create_event(
            "u1",
            type="page_view",
            data={"page": "/home", "duration": 30},
        )
        args = mk.users._client.request.call_args
        assert args[0] == ("POST", "/users/u1/events")
        body = args[1]["json"]
        assert body["type"] == "page_view"
        assert body["data"] == {"page": "/home", "duration": 30}

    def test_list_events_sends_params(self, mk):
        mk.users._client.request.return_value = {"data": []}
        mk.users.list_events("u1", limit=5, type="click")
        args = mk.users._client.request.call_args
        assert args[0] == ("GET", "/users/u1/events")
        params = args[1]["params"]
        assert params["limit"] == 5
        assert params["type"] == "click"

    def test_delete_event_path(self, mk):
        mk.users._client.request.return_value = {}
        mk.users.delete_event("u1", "evt_123")
        args = mk.users._client.request.call_args
        assert args[0] == ("DELETE", "/users/u1/events/evt_123")


# ---------------------------------------------------------------------------
# Webhooks — request payload verification
# ---------------------------------------------------------------------------


class TestWebhooksRequestBuilding:
    def test_create_sends_params(self, mk):
        mk.webhooks._client.request.return_value = {"id": "wh_1"}
        mk.webhooks.create(url="https://example.com/hook", events=["memory.completed"])
        args = mk.webhooks._client.request.call_args
        assert args[0] == ("POST", "/webhooks")
        body = args[1]["json"]
        assert body["url"] == "https://example.com/hook"
        assert body["events"] == ["memory.completed"]

    def test_list_path(self, mk):
        mk.webhooks._client.request.return_value = {"data": []}
        mk.webhooks.list()
        args = mk.webhooks._client.request.call_args
        assert args[0] == ("GET", "/webhooks")

    def test_get_path(self, mk):
        mk.webhooks._client.request.return_value = {"id": "wh_1"}
        mk.webhooks.get("wh_1")
        args = mk.webhooks._client.request.call_args
        assert args[0] == ("GET", "/webhooks/wh_1")

    def test_delete_path(self, mk):
        mk.webhooks._client.request.return_value = {}
        mk.webhooks.delete("wh_1")
        args = mk.webhooks._client.request.call_args
        assert args[0] == ("DELETE", "/webhooks/wh_1")

    def test_test_path(self, mk):
        mk.webhooks._client.request.return_value = {"success": True}
        mk.webhooks.test("wh_1")
        args = mk.webhooks._client.request.call_args
        assert args[0] == ("POST", "/webhooks/wh_1/test")


# ---------------------------------------------------------------------------
# Status + Feedback
# ---------------------------------------------------------------------------


class TestStatusRequestBuilding:
    def test_get_path(self, mk):
        mk.status._client.request.return_value = {"project": "test"}
        mk.status.get()
        args = mk.status._client.request.call_args
        assert args[0] == ("GET", "/status")


class TestFeedbackRequestBuilding:
    def test_create_sends_params(self, mk):
        mk.feedback._client.request.return_value = {"id": "fb_1"}
        mk.feedback.create(
            request_id="req_abc",
            rating=5,
            comment="Great answer!",
        )
        args = mk.feedback._client.request.call_args
        assert args[0] == ("POST", "/feedback")
        body = args[1]["json"]
        assert body["request_id"] == "req_abc"
        assert body["rating"] == 5
        assert body["comment"] == "Great answer!"


# ---------------------------------------------------------------------------
# Dual camelCase/snake_case parameter acceptance
# ---------------------------------------------------------------------------


class TestDualCaseParams:
    """Verify SDK accepts both camelCase and snake_case params."""

    def test_memories_create_user_id_camel(self, mk):
        mk.memories._client.request.return_value = {"id": "mem_1", "status": "pending"}
        mk.memories.create(content="test", userId="u1")
        body = mk.memories._client.request.call_args[1]["json"]
        assert body["user_id"] == "u1"

    def test_memories_query_max_sources_camel(self, mk):
        mk.memories._client.request.return_value = {"answer": "", "confidence": 0, "sources": []}
        mk.memories.query(query="test", maxSources=5)
        body = mk.memories._client.request.call_args[1]["json"]
        assert body["max_sources"] == 5

    def test_memories_search_user_id_camel(self, mk):
        mk.memories._client.request.return_value = {"results": []}
        mk.memories.search(query="test", userId="u1")
        params = mk.memories._client.request.call_args[1]["params"]
        assert params["user_id"] == "u1"

    def test_memories_search_include_graph_camel(self, mk):
        mk.memories._client.request.return_value = {"results": []}
        mk.memories.search(query="test", includeGraph=True)
        params = mk.memories._client.request.call_args[1]["params"]
        assert params["include_graph"] is True

    def test_memories_query_include_graph_camel(self, mk):
        mk.memories._client.request.return_value = {"answer": "", "confidence": 0, "sources": []}
        mk.memories.query(query="test", includeGraph=True)
        body = mk.memories._client.request.call_args[1]["json"]
        assert body["include_graph"] is True

    def test_chats_send_message_max_sources_camel(self, mk):
        mk.chats._client.request.return_value = {
            "message": {"role": "assistant", "content": "hi"}
        }
        mk.chats.send_message("chat_1", message="hi", maxSources=3)
        body = mk.chats._client.request.call_args[1]["json"]
        assert body["max_sources"] == 3
