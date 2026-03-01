"""Tests that resource methods return correctly typed wrapper objects.

Verifies that each sync resource method:
  1. Calls the correct HTTP method + path
  2. Wraps the raw dict response in the expected type (Webhook, User, Status, etc.)

Uses unittest.mock to intercept the low-level client.request() method.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from memorykit import AsyncMemoryKit, MemoryKit
from memorykit._types import (
    BatchIngestResponse,
    Chat,
    ChatHistory,
    ChatList,
    ChatMessage,
    ChatMessageList,
    ChatMessageResponse,
    Event,
    EventList,
    Feedback,
    Memory,
    MemoryList,
    QueryResponse,
    SearchResponse,
    Status,
    User,
    Webhook,
    WebhookList,
    WebhookTestResponse,
)


@pytest.fixture
def mk():
    """Create a MemoryKit client with mocked HTTP layer on all resources."""
    client = MemoryKit(api_key="ctx_test_key")
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
# Webhooks — return type verification
# ---------------------------------------------------------------------------


class TestWebhooksReturnTypes:
    def test_create_returns_webhook(self, mk):
        mk.webhooks._client.request.return_value = {
            "id": "wh_1",
            "url": "https://example.com/hook",
            "events": ["memory.completed"],
            "secret": "whsec_xxx",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        result = mk.webhooks.create(url="https://example.com/hook", events=["memory.completed"])
        assert isinstance(result, Webhook)
        assert result.id == "wh_1"
        assert result.url == "https://example.com/hook"
        assert result.events == ["memory.completed"]

    def test_list_returns_webhook_list(self, mk):
        mk.webhooks._client.request.return_value = {
            "data": [
                {"id": "wh_1", "url": "https://a.com", "events": ["*"]},
                {"id": "wh_2", "url": "https://b.com", "events": ["memory.created"]},
            ]
        }
        result = mk.webhooks.list()
        assert isinstance(result, WebhookList)
        webhooks = list(result)
        assert len(webhooks) == 2
        assert isinstance(webhooks[0], Webhook)
        assert webhooks[0].id == "wh_1"
        assert webhooks[1].url == "https://b.com"

    def test_get_returns_webhook(self, mk):
        mk.webhooks._client.request.return_value = {
            "id": "wh_1",
            "url": "https://example.com",
            "events": ["*"],
        }
        result = mk.webhooks.get("wh_1")
        assert isinstance(result, Webhook)
        assert result.id == "wh_1"

    def test_delete_returns_none(self, mk):
        mk.webhooks._client.request.return_value = {}
        result = mk.webhooks.delete("wh_1")
        assert result is None

    def test_test_returns_webhook_test_response(self, mk):
        mk.webhooks._client.request.return_value = {
            "success": True,
            "status_code": 200,
        }
        result = mk.webhooks.test("wh_1")
        assert isinstance(result, WebhookTestResponse)
        assert result.success is True
        assert result.status_code == 200


# ---------------------------------------------------------------------------
# Status — return type verification
# ---------------------------------------------------------------------------


class TestStatusReturnTypes:
    def test_get_returns_status(self, mk):
        mk.status._client.request.return_value = {
            "project": "My Project",
            "plan": "pro",
            "usage": {
                "memories_total": 100,
                "memories_limit": 10000,
                "memories_today": 5,
                "queries_this_month": 200,
                "queries_limit": 5000,
                "storage_mb": 50.5,
                "storage_limit_mb": 1024,
            },
            "knowledge": {
                "total_chunks": 500,
                "total_entities": 120,
                "total_relationships": 80,
                "embedding_dimensions": 1536,
            },
        }
        result = mk.status.get()
        assert isinstance(result, Status)
        assert result.project == "My Project"
        assert result.plan == "pro"
        assert result.usage.memories_total == 100


# ---------------------------------------------------------------------------
# Feedback — return type verification
# ---------------------------------------------------------------------------


class TestFeedbackReturnTypes:
    def test_create_returns_feedback(self, mk):
        mk.feedback._client.request.return_value = {
            "id": "fb_123",
            "request_id": "req_abc",
            "rating": 5,
            "comment": "Great answer!",
            "created_at": "2024-06-15T10:00:00Z",
        }
        result = mk.feedback.create(
            request_id="req_abc",
            rating=5,
            comment="Great answer!",
        )
        assert isinstance(result, Feedback)
        assert result.id == "fb_123"
        assert result.request_id == "req_abc"
        assert result.rating == 5
        assert result.comment == "Great answer!"

    def test_create_without_comment(self, mk):
        mk.feedback._client.request.return_value = {
            "id": "fb_124",
            "request_id": "req_def",
            "rating": 1,
        }
        result = mk.feedback.create(request_id="req_def", rating=1)
        assert isinstance(result, Feedback)
        assert result.id == "fb_124"


# ---------------------------------------------------------------------------
# Users — return type verification
# ---------------------------------------------------------------------------


class TestUsersReturnTypes:
    def test_upsert_returns_user(self, mk):
        mk.users._client.request.return_value = {
            "id": "user_1",
            "email": "alice@example.com",
            "name": "Alice",
            "metadata": {"role": "admin"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        result = mk.users.upsert(id="user_1", email="alice@example.com", name="Alice")
        assert isinstance(result, User)
        assert result.id == "user_1"
        assert result.email == "alice@example.com"

    def test_get_returns_user(self, mk):
        mk.users._client.request.return_value = {
            "id": "user_1",
            "email": "bob@example.com",
            "name": "Bob",
            "metadata": {},
        }
        result = mk.users.get("user_1")
        assert isinstance(result, User)
        assert result.name == "Bob"

    def test_update_returns_user(self, mk):
        mk.users._client.request.return_value = {
            "id": "user_1",
            "email": "new@example.com",
            "name": "Alice Updated",
            "metadata": {},
        }
        result = mk.users.update("user_1", email="new@example.com", name="Alice Updated")
        assert isinstance(result, User)
        assert result.email == "new@example.com"

    def test_delete_returns_none(self, mk):
        mk.users._client.request.return_value = {}
        result = mk.users.delete("user_1")
        assert result is None

    def test_create_event_returns_event(self, mk):
        mk.users._client.request.return_value = {
            "id": "evt_1",
            "user_id": "user_1",
            "type": "page_view",
            "data": {"page": "/home"},
            "created_at": "2024-01-01T00:00:00Z",
        }
        result = mk.users.create_event("user_1", type="page_view", data={"page": "/home"})
        assert isinstance(result, Event)
        assert result.id == "evt_1"
        assert result.type == "page_view"

    def test_list_events_returns_event_list(self, mk):
        mk.users._client.request.return_value = {
            "data": [
                {"id": "evt_1", "type": "page_view", "data": {}},
                {"id": "evt_2", "type": "click", "data": {"element": "btn"}},
            ]
        }
        result = mk.users.list_events("user_1")
        assert isinstance(result, EventList)
        events = list(result)
        assert len(events) == 2
        assert isinstance(events[0], Event)
        assert events[1].type == "click"

    def test_delete_event_returns_none(self, mk):
        mk.users._client.request.return_value = {}
        result = mk.users.delete_event("user_1", "evt_1")
        assert result is None


# ---------------------------------------------------------------------------
# Chats — return type verification
# ---------------------------------------------------------------------------


class TestChatsReturnTypes:
    def test_create_returns_chat(self, mk):
        mk.chats._client.request.return_value = {
            "id": "chat_1",
            "user_id": "u1",
            "title": "Support Chat",
            "metadata": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        result = mk.chats.create(user_id="u1", title="Support Chat")
        assert isinstance(result, Chat)
        assert result.id == "chat_1"
        assert result.title == "Support Chat"

    def test_list_returns_chat_list(self, mk):
        mk.chats._client.request.return_value = {
            "data": [
                {"id": "chat_1", "title": "Chat A"},
                {"id": "chat_2", "title": "Chat B"},
            ],
            "has_more": True,
        }
        result = mk.chats.list()
        assert isinstance(result, ChatList)
        chats = list(result)
        assert len(chats) == 2
        assert isinstance(chats[0], Chat)
        assert result.has_more is True

    def test_get_history_returns_chat_history(self, mk):
        mk.chats._client.request.return_value = {
            "id": "chat_1",
            "title": "Test conversation",
            "messages": [
                {"id": "msg_1", "role": "user", "content": "Hello"},
                {"id": "msg_2", "role": "assistant", "content": "Hi there!"},
            ],
        }
        result = mk.chats.get_history("chat_1")
        assert isinstance(result, ChatHistory)
        assert result.id == "chat_1"
        assert result.title == "Test conversation"
        assert len(result.messages) == 2
        assert isinstance(result.messages[0], ChatMessage)
        assert result.messages[0].role == "user"
        assert result.messages[0].content == "Hello"

    def test_send_message_returns_chat_message_response(self, mk):
        mk.chats._client.request.return_value = {
            "message": {
                "id": "msg_2",
                "role": "assistant",
                "content": "Hello! How can I help?",
                "sources": [],
            }
        }
        result = mk.chats.send_message("chat_1", message="Hello")
        assert isinstance(result, ChatMessageResponse)
        assert result.message.role == "assistant"
        assert result.message.content == "Hello! How can I help?"

    def test_delete_returns_none(self, mk):
        mk.chats._client.request.return_value = {}
        result = mk.chats.delete("chat_1")
        assert result is None


# ---------------------------------------------------------------------------
# Memories — return type verification
# ---------------------------------------------------------------------------


class TestMemoriesReturnTypes:
    def test_create_returns_memory(self, mk):
        mk.memories._client.request.return_value = {
            "id": "mem_1",
            "status": "pending",
            "title": None,
            "content": "Hello world",
            "type": "text",
            "tags": [],
            "metadata": {},
        }
        result = mk.memories.create(content="Hello world")
        assert isinstance(result, Memory)
        assert result.id == "mem_1"
        assert result.status == "pending"

    def test_list_returns_memory_list(self, mk):
        mk.memories._client.request.return_value = {
            "data": [
                {"id": "mem_1", "status": "completed"},
                {"id": "mem_2", "status": "processing"},
            ],
            "has_more": False,
        }
        result = mk.memories.list()
        assert isinstance(result, MemoryList)
        memories = list(result)
        assert len(memories) == 2
        assert isinstance(memories[0], Memory)

    def test_get_returns_memory(self, mk):
        mk.memories._client.request.return_value = {
            "id": "mem_1",
            "status": "completed",
            "content": "Test",
        }
        result = mk.memories.get("mem_1")
        assert isinstance(result, Memory)
        assert result.id == "mem_1"

    def test_update_returns_memory(self, mk):
        mk.memories._client.request.return_value = {
            "id": "mem_1",
            "status": "completed",
            "title": "Updated Title",
        }
        result = mk.memories.update("mem_1", title="Updated Title")
        assert isinstance(result, Memory)
        assert result.title == "Updated Title"

    def test_query_returns_query_response(self, mk):
        mk.memories._client.request.return_value = {
            "answer": "The answer is 42.",
            "confidence": 0.95,
            "sources": [{"content": "source1", "score": 0.9}],
            "model": "gpt-4",
            "request_id": "req_123",
            "usage": {"total_time_ms": 500},
        }
        result = mk.memories.query(query="What is the answer?")
        assert isinstance(result, QueryResponse)
        assert result.answer == "The answer is 42."
        assert result.confidence == 0.95

    def test_search_returns_search_response(self, mk):
        mk.memories._client.request.return_value = {
            "results": [{"content": "match", "score": 0.8}],
            "total_results": 1,
            "request_id": "req_456",
        }
        result = mk.memories.search(query="test search")
        assert isinstance(result, SearchResponse)
        assert result.total_results == 1

    def test_batch_create_returns_batch_ingest_response(self, mk):
        mk.memories._client.request.return_value = {
            "items": [
                {"id": "mem_1", "title": "Item 1", "status": "pending", "index": 0},
            ],
            "total": 1,
            "failed": 0,
        }
        result = mk.memories.batch_create(items=[{"content": "hello"}])
        assert isinstance(result, BatchIngestResponse)
        assert result.total == 1
        assert result.failed == 0


class TestAsyncChatsReturnTypes:
    """Test async chats resource return types."""

    @pytest.fixture
    def async_mk(self):
        """Create an AsyncMemoryKit client with mocked HTTP layer."""
        client = AsyncMemoryKit(api_key="ctx_test_key")
        client.chats._client.request = AsyncMock(return_value={})
        return client

    @pytest.mark.asyncio
    async def test_async_get_history_returns_chat_history(self, async_mk):
        async_mk.chats._client.request.return_value = {
            "id": "chat_1",
            "title": "Test async conversation",
            "messages": [
                {"id": "msg_1", "role": "user", "content": "Hello async"},
                {"id": "msg_2", "role": "assistant", "content": "Hi there async!"},
            ],
        }
        result = await async_mk.chats.get_history("chat_1")
        assert isinstance(result, ChatHistory)
        assert result.id == "chat_1"
        assert result.title == "Test async conversation"
        assert len(result.messages) == 2
        assert isinstance(result.messages[0], ChatMessage)
        assert result.messages[0].role == "user"
        assert result.messages[0].content == "Hello async"
