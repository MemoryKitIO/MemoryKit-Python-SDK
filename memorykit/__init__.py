"""MemoryKit — Official Python SDK for the MemoryKit API.

Usage::

    from memorykit import MemoryKit

    mk = MemoryKit(api_key="ctx_...")
    memory = mk.memories.create(content="Hello, world!")

For async usage::

    from memorykit import AsyncMemoryKit

    mk = AsyncMemoryKit(api_key="ctx_...")
    memory = await mk.memories.create(content="Hello, world!")
"""

from __future__ import annotations

from typing import Optional

from ._client import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncHTTPClient,
    SyncHTTPClient,
    __version__,
)
from ._errors import (
    AuthenticationError,
    ConnectionError,
    MemoryKitError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from ._types import (
    APIObject,
    BatchIngestResponse,
    Chat,
    ChatHistory,
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
from .chats import AsyncChats, Chats
from .feedback import AsyncFeedbackResource, FeedbackResource
from .memories import AsyncMemories, Memories
from .status import AsyncStatusResource, StatusResource
from .users import AsyncUsers, Users
from .webhooks import AsyncWebhooks, Webhooks


class MemoryKit:
    """Synchronous MemoryKit client.

    Args:
        api_key: Your MemoryKit API key (starts with ``ctx_``).
        base_url: API base URL. Defaults to ``https://api.memorykit.io/v1``.
        timeout: Request timeout in seconds (default 30).
        max_retries: Maximum automatic retries on 429/5xx (default 3).

    Example::

        from memorykit import MemoryKit

        mk = MemoryKit(api_key="ctx_...")
        memories = mk.memories.list()
    """

    memories: Memories
    chats: Chats
    users: Users
    webhooks: Webhooks
    status: StatusResource
    feedback: FeedbackResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._client = SyncHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.memories = Memories(self._client)
        self.chats = Chats(self._client)
        self.users = Users(self._client)
        self.webhooks = Webhooks(self._client)
        self.status = StatusResource(self._client)
        self.feedback = FeedbackResource(self._client)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> "MemoryKit":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"MemoryKit(base_url={self._client.base_url!r})"


class AsyncMemoryKit:
    """Asynchronous MemoryKit client.

    Args:
        api_key: Your MemoryKit API key (starts with ``ctx_``).
        base_url: API base URL. Defaults to ``https://api.memorykit.io/v1``.
        timeout: Request timeout in seconds (default 30).
        max_retries: Maximum automatic retries on 429/5xx (default 3).

    Example::

        from memorykit import AsyncMemoryKit

        mk = AsyncMemoryKit(api_key="ctx_...")
        memories = await mk.memories.list()
    """

    memories: AsyncMemories
    chats: AsyncChats
    users: AsyncUsers
    webhooks: AsyncWebhooks
    status: AsyncStatusResource
    feedback: AsyncFeedbackResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._client = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.memories = AsyncMemories(self._client)
        self.chats = AsyncChats(self._client)
        self.users = AsyncUsers(self._client)
        self.webhooks = AsyncWebhooks(self._client)
        self.status = AsyncStatusResource(self._client)
        self.feedback = AsyncFeedbackResource(self._client)

    async def close(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._client.close()

    async def __aenter__(self) -> "AsyncMemoryKit":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncMemoryKit(base_url={self._client.base_url!r})"


__all__ = [
    # Clients
    "MemoryKit",
    "AsyncMemoryKit",
    # Errors
    "MemoryKitError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "ConnectionError",
    "TimeoutError",
    # Types
    "APIObject",
    "Memory",
    "MemoryList",
    "BatchIngestResponse",
    "QueryResponse",
    "SearchResponse",
    "Chat",
    "ChatList",
    "ChatHistory",
    "ChatMessage",
    "ChatMessageResponse",
    "User",
    "Event",
    "EventList",
    "Webhook",
    "WebhookList",
    "WebhookTestResponse",
    "Status",
    "Feedback",
    # Version
    "__version__",
]
