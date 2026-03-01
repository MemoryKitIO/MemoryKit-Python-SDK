"""MemoryKit response types.

All API responses are wrapped in typed objects that provide attribute access
while still allowing dict-style access for forward-compatibility.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class APIObject:
    """Lightweight wrapper around a dict that exposes keys as attributes.

    Unknown keys are still accessible via ``obj["key"]`` or ``obj.get("key")``.
    The underlying data is stored in ``_data`` and is always a plain dict.
    """

    _data: dict[str, Any]

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", {})
        if data:
            self._data.update(data)
        if kwargs:
            self._data.update(kwargs)

    # Attribute access -------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            ) from None
        # Recursively wrap nested dicts
        if isinstance(value, dict):
            return APIObject(value)
        if isinstance(value, list):
            return [APIObject(v) if isinstance(v, dict) else v for v in value]
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        self._data[name] = value

    # Dict-like access -------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self) -> Any:
        return self._data.keys()

    def values(self) -> Any:
        return self._data.values()

    def items(self) -> Any:
        return self._data.items()

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # Representation ---------------------------------------------------------

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in self._data.items())
        return f"{type(self).__name__}({fields})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, APIObject):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other
        return NotImplemented

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying data as a plain ``dict``."""
        return dict(self._data)


# ---------------------------------------------------------------------------
# Concrete types
# ---------------------------------------------------------------------------

class Memory(APIObject):
    """A single memory record."""

    id: str
    status: str
    title: str | None
    type: str | None
    tags: list[str]
    content: str | None
    metadata: dict[str, Any] | None
    user_id: str | None
    language: str | None
    format: str | None
    chunks_count: int | None
    created_at: str | None
    updated_at: str | None


class MemoryList(APIObject):
    """Paginated list of memories."""

    data: list[Memory]
    has_more: bool

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        # Wrap items in Memory objects
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Memory(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Memory]:  # type: ignore[override]
        return iter(self._data["data"])

    def __len__(self) -> int:
        return len(self._data["data"])


class BatchIngestResponse(APIObject):
    """Response from batch memory ingestion."""

    items: list[APIObject]
    total: int
    failed: int
    errors: list[dict[str, Any]] | None


class QueryResponse(APIObject):
    """Response from a RAG query."""

    answer: str
    confidence: float | None
    sources: list[APIObject]
    model: str | None
    request_id: str | None
    usage: dict[str, Any] | None


class SearchResponse(APIObject):
    """Response from a hybrid search."""

    results: list[APIObject]
    graph: Any | None
    request_id: str | None
    processing_time_ms: int | None
    total_results: int | None


class Chat(APIObject):
    """A chat session."""

    id: str
    title: str | None
    user_id: str | None
    message_count: int
    created_at: str | None
    updated_at: str | None


class ChatList(APIObject):
    """Paginated list of chats."""

    data: list[Chat]
    has_more: bool

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Chat(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Chat]:  # type: ignore[override]
        return iter(self._data["data"])

    def __len__(self) -> int:
        return len(self._data["data"])


class ChatMessage(APIObject):
    """A single chat message response."""

    id: str | None
    role: str
    content: str
    sources: list[APIObject] | None
    created_at: str | None


class ChatMessageList(APIObject):
    """Paginated list of chat messages."""

    data: list[ChatMessage]
    has_more: bool

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            ChatMessage(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[ChatMessage]:  # type: ignore[override]
        return iter(self._data["data"])

    def __len__(self) -> int:
        return len(self._data["data"])


class ChatHistory(APIObject):
    """Chat history with metadata and full message list."""

    id: str
    title: str | None
    messages: list[ChatMessage]

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_messages = self._data.get("messages", [])
        self._data["messages"] = [
            ChatMessage(item) if isinstance(item, dict) else item for item in raw_messages
        ]

    def __iter__(self) -> Iterator[ChatMessage]:  # type: ignore[override]
        return iter(self._data["messages"])

    def __len__(self) -> int:
        return len(self._data["messages"])


class ChatMessageResponse(APIObject):
    """Wrapper for chat message API response."""

    message: ChatMessage

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        msg = self._data.get("message")
        if isinstance(msg, dict):
            self._data["message"] = ChatMessage(msg)


class User(APIObject):
    """A user record."""

    id: str
    email: str | None
    name: str | None
    metadata: dict[str, Any] | None
    created_at: str | None
    updated_at: str | None


class Event(APIObject):
    """A user event."""

    id: str
    type: str
    data: dict[str, Any] | None
    user_id: str | None
    created_at: str | None


class EventList(APIObject):
    """Paginated list of user events."""

    data: list[Event]
    has_more: bool

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Event(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Event]:  # type: ignore[override]
        return iter(self._data["data"])

    def __len__(self) -> int:
        return len(self._data["data"])


class Webhook(APIObject):
    """A webhook registration."""

    id: str
    url: str
    events: list[str]
    secret: str | None
    is_active: bool
    failure_count: int
    created_at: str | None


class WebhookList(APIObject):
    """List of webhooks."""

    data: list[Webhook]

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Webhook(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Webhook]:  # type: ignore[override]
        return iter(self._data["data"])


class WebhookTestResponse(APIObject):
    """Response from testing a webhook."""

    success: bool
    status_code: int | None


class Status(APIObject):
    """Project status, usage, and plan information."""

    pass


class Feedback(APIObject):
    """Feedback submission response."""

    id: str | None
    request_id: str | None
    rating: Any | None
    comment: str | None
