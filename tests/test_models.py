"""Tests for model serialization — verify APIObject, Memory, Chat, User, etc."""

import pytest

from memorykit._types import (
    APIObject,
    Chat,
    ChatList,
    ChatMessage,
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

# ---------------------------------------------------------------------------
# APIObject base class
# ---------------------------------------------------------------------------


class TestAPIObject:
    def test_attribute_access(self):
        obj = APIObject({"name": "test", "value": 42})
        assert obj.name == "test"
        assert obj.value == 42

    def test_dict_access(self):
        obj = APIObject({"name": "test"})
        assert obj["name"] == "test"

    def test_get_with_default(self):
        obj = APIObject({"name": "test"})
        assert obj.get("name") == "test"
        assert obj.get("missing") is None
        assert obj.get("missing", "default") == "default"

    def test_contains(self):
        obj = APIObject({"name": "test"})
        assert "name" in obj
        assert "missing" not in obj

    def test_len(self):
        obj = APIObject({"a": 1, "b": 2})
        assert len(obj) == 2

    def test_iter(self):
        obj = APIObject({"a": 1, "b": 2})
        keys = list(obj)
        assert set(keys) == {"a", "b"}

    def test_nested_dict_wrapped(self):
        obj = APIObject({"nested": {"key": "val"}})
        nested = obj.nested
        assert isinstance(nested, APIObject)
        assert nested.key == "val"

    def test_nested_list_of_dicts_wrapped(self):
        obj = APIObject({"results": [{"id": 1}, {"id": 2}]})
        results = obj.results
        assert isinstance(results, list)
        assert isinstance(results[0], APIObject)
        assert results[0].id == 1

    def test_set_attribute(self):
        obj = APIObject({})
        obj.name = "test"
        assert obj.name == "test"
        assert obj["name"] == "test"

    def test_to_dict(self):
        obj = APIObject({"a": 1, "b": 2})
        d = obj.to_dict()
        assert d == {"a": 1, "b": 2}
        assert isinstance(d, dict)

    def test_eq_with_dict(self):
        obj = APIObject({"a": 1})
        assert obj == {"a": 1}

    def test_eq_with_api_object(self):
        obj1 = APIObject({"a": 1})
        obj2 = APIObject({"a": 1})
        assert obj1 == obj2

    def test_repr(self):
        obj = APIObject({"name": "test"})
        assert repr(obj) == "APIObject(name='test')"

    def test_missing_attribute_raises(self):
        obj = APIObject({"name": "test"})
        with pytest.raises(AttributeError, match="no attribute 'missing'"):
            _ = obj.missing

    def test_kwargs_init(self):
        obj = APIObject(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42


# ---------------------------------------------------------------------------
# Memory / MemoryList
# ---------------------------------------------------------------------------


class TestMemory:
    def test_from_dict(self):
        data = {
            "id": "mem_123",
            "status": "completed",
            "title": "Test Memory",
            "type": "article",
            "tags": ["test"],
            "content": "Hello world",
            "metadata": {"key": "val"},
            "user_id": "u1",
            "language": "en",
            "format": "text",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        mem = Memory(data)
        assert mem.id == "mem_123"
        assert mem.status == "completed"
        assert mem.title == "Test Memory"
        assert mem.tags == ["test"]


class TestMemoryList:
    def test_wraps_items(self):
        data = {
            "data": [
                {"id": "mem_1", "status": "completed"},
                {"id": "mem_2", "status": "processing"},
            ],
            "has_more": True,
        }
        lst = MemoryList(data)
        assert len(lst) == 2
        assert isinstance(list(lst)[0], Memory)
        assert lst.has_more is True

    def test_empty_list(self):
        data = {"data": [], "has_more": False}
        lst = MemoryList(data)
        assert len(lst) == 0
        assert lst.has_more is False

    def test_iterable(self):
        data = {"data": [{"id": "mem_1"}, {"id": "mem_2"}], "has_more": False}
        lst = MemoryList(data)
        ids = [m.id for m in lst]
        assert ids == ["mem_1", "mem_2"]


# ---------------------------------------------------------------------------
# Chat / ChatList
# ---------------------------------------------------------------------------


class TestChat:
    def test_from_dict(self):
        data = {
            "id": "chat_123",
            "title": "Support Chat",
            "user_id": "u1",
            "created_at": "2024-01-01T00:00:00Z",
        }
        chat = Chat(data)
        assert chat.id == "chat_123"
        assert chat.title == "Support Chat"


class TestChatList:
    def test_wraps_items(self):
        data = {
            "data": [{"id": "chat_1"}, {"id": "chat_2"}],
            "has_more": False,
        }
        lst = ChatList(data)
        assert len(lst) == 2
        assert isinstance(list(lst)[0], Chat)


class TestChatMessageResponse:
    def test_wraps_message(self):
        data = {
            "message": {
                "id": "msg_1",
                "role": "assistant",
                "content": "Hello!",
                "sources": [],
            }
        }
        resp = ChatMessageResponse(data)
        assert isinstance(resp.message, ChatMessage)
        assert resp.message.role == "assistant"
        assert resp.message.content == "Hello!"


# ---------------------------------------------------------------------------
# User / Event
# ---------------------------------------------------------------------------


class TestUser:
    def test_from_dict(self):
        data = {
            "id": "u_123",
            "email": "alice@example.com",
            "name": "Alice",
            "metadata": {"role": "admin"},
        }
        user = User(data)
        assert user.id == "u_123"
        assert user.email == "alice@example.com"


class TestEventList:
    def test_wraps_events(self):
        data = {
            "data": [
                {"id": "evt_1", "type": "page_view", "data": {}},
                {"id": "evt_2", "type": "click", "data": {}},
            ]
        }
        lst = EventList(data)
        events = list(lst)
        assert len(events) == 2
        assert isinstance(events[0], Event)
        assert events[0].type == "page_view"


# ---------------------------------------------------------------------------
# Webhook / WebhookList
# ---------------------------------------------------------------------------


class TestWebhookList:
    def test_wraps_webhooks(self):
        data = {
            "data": [
                {"id": "wh_1", "url": "https://example.com/hook", "events": ["*"]},
            ]
        }
        lst = WebhookList(data)
        webhooks = list(lst)
        assert len(webhooks) == 1
        assert isinstance(webhooks[0], Webhook)
        assert webhooks[0].url == "https://example.com/hook"


class TestWebhookTestResponse:
    def test_from_dict(self):
        resp = WebhookTestResponse({"success": True, "status_code": 200})
        assert resp.success is True
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# QueryResponse / SearchResponse
# ---------------------------------------------------------------------------


class TestQueryResponse:
    def test_from_dict(self):
        data = {
            "answer": "The answer is 42.",
            "confidence": 0.95,
            "sources": [{"content": "src1", "score": 0.9}],
            "model": "gpt-5-nano",
            "request_id": "req_123",
            "usage": {"total_time_ms": 500},
        }
        resp = QueryResponse(data)
        assert resp.answer == "The answer is 42."
        assert resp.confidence == 0.95
        assert resp.model == "gpt-5-nano"
        assert resp.request_id == "req_123"


class TestSearchResponse:
    def test_from_dict(self):
        data = {
            "results": [{"content": "match", "score": 0.8}],
            "total_results": 1,
            "request_id": "req_456",
        }
        resp = SearchResponse(data)
        assert resp.total_results == 1
        assert len(resp.results) == 1


# ---------------------------------------------------------------------------
# Status / Feedback
# ---------------------------------------------------------------------------


class TestStatus:
    def test_from_dict(self):
        data = {"project": "My Project", "plan": "pro", "usage": {"memories_total": 100}}
        status = Status(data)
        assert status.project == "My Project"


class TestFeedback:
    def test_from_dict(self):
        data = {"id": "fb_1", "request_id": "req_1", "rating": 5, "comment": "Great!"}
        fb = Feedback(data)
        assert fb.id == "fb_1"
        assert fb.rating == 5
