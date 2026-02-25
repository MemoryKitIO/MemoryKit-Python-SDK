"""MemoryKit response types.

All API responses are wrapped in typed objects that provide attribute access
while still allowing dict-style access for forward-compatibility.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class APIObject:
    """Lightweight wrapper around a dict that exposes keys as attributes.

    Unknown keys are still accessible via ``obj["key"]`` or ``obj.get("key")``.
    The underlying data is stored in ``_data`` and is always a plain dict.
    """

    _data: Dict[str, Any]

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
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

    def to_dict(self) -> Dict[str, Any]:
        """Return the underlying data as a plain ``dict``."""
        return dict(self._data)


# ---------------------------------------------------------------------------
# Concrete types
# ---------------------------------------------------------------------------

class Memory(APIObject):
    """A single memory record."""

    id: str
    status: str
    title: Optional[str]
    type: Optional[str]
    tags: List[str]
    content: Optional[str]
    metadata: Optional[Dict[str, Any]]
    user_id: Optional[str]
    language: Optional[str]
    format: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class MemoryList(APIObject):
    """Paginated list of memories."""

    data: List[Memory]
    has_more: bool
    cursor: Optional[str]

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
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

    accepted: int
    rejected: int
    items: List[APIObject]


class QueryResponse(APIObject):
    """Response from a RAG query."""

    answer: str
    confidence: Optional[float]
    sources: List[APIObject]
    model: Optional[str]
    request_id: Optional[str]
    usage: Optional[Dict[str, Any]]


class SearchResponse(APIObject):
    """Response from a hybrid search."""

    results: List[APIObject]
    graph: Optional[Any]
    request_id: Optional[str]
    total_results: Optional[int]


class Chat(APIObject):
    """A chat session."""

    id: str
    title: Optional[str]
    user_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


class ChatList(APIObject):
    """Paginated list of chats."""

    data: List[Chat]
    has_more: bool

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Chat(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Chat]:  # type: ignore[override]
        return iter(self._data["data"])

    def __len__(self) -> int:
        return len(self._data["data"])


class ChatHistory(APIObject):
    """Chat with its message history."""

    id: str
    title: Optional[str]
    messages: List[APIObject]


class ChatMessage(APIObject):
    """A single chat message response."""

    id: Optional[str]
    role: str
    content: str
    sources: Optional[List[APIObject]]
    created_at: Optional[str]


class ChatMessageResponse(APIObject):
    """Wrapper for chat message API response."""

    message: ChatMessage

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        msg = self._data.get("message")
        if isinstance(msg, dict):
            self._data["message"] = ChatMessage(msg)


class User(APIObject):
    """A user record."""

    id: str
    email: Optional[str]
    name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: Optional[str]
    updated_at: Optional[str]


class Event(APIObject):
    """A user event."""

    id: str
    type: str
    data: Optional[Dict[str, Any]]
    user_id: Optional[str]
    created_at: Optional[str]


class EventList(APIObject):
    """List of user events."""

    data: List[Event]

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        super().__init__(data, **kwargs)
        raw_items = self._data.get("data", [])
        self._data["data"] = [
            Event(item) if isinstance(item, dict) else item for item in raw_items
        ]

    def __iter__(self) -> Iterator[Event]:  # type: ignore[override]
        return iter(self._data["data"])


class Webhook(APIObject):
    """A webhook registration."""

    id: str
    url: str
    events: List[str]
    secret: Optional[str]
    created_at: Optional[str]


class WebhookList(APIObject):
    """List of webhooks."""

    data: List[Webhook]

    def __init__(self, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
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
    status_code: Optional[int]


class Status(APIObject):
    """Project status, usage, and plan information."""

    pass


class Feedback(APIObject):
    """Feedback submission response."""

    id: Optional[str]
    request_id: Optional[str]
    rating: Optional[Any]
    comment: Optional[str]
