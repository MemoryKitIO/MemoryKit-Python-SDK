"""Tests for AsyncMemoryKit client initialization and async resource access.

Verifies that the async client:
  1. Initializes correctly with valid API key
  2. Exposes all expected async resource attributes
  3. Has the correct repr
  4. Supports async context manager protocol
"""

import pytest

from memorykit import AsyncMemoryKit, MemoryKitError
from memorykit._client import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT


class TestAsyncMemoryKitInit:
    def test_creates_with_valid_key(self):
        mk = AsyncMemoryKit(api_key="ctx_test_key")
        assert mk._client._api_key == "ctx_test_key"
        assert mk._client._base_url == DEFAULT_BASE_URL
        assert mk._client._timeout == DEFAULT_TIMEOUT
        assert mk._client._max_retries == DEFAULT_MAX_RETRIES

    def test_empty_api_key_raises(self):
        with pytest.raises(MemoryKitError, match="api_key is required"):
            AsyncMemoryKit(api_key="")

    def test_custom_options(self):
        mk = AsyncMemoryKit(
            api_key="ctx_test",
            base_url="https://custom.io/v1",
            timeout=60.0,
            max_retries=5,
        )
        assert mk._client._base_url == "https://custom.io/v1"
        assert mk._client._timeout == 60.0
        assert mk._client._max_retries == 5

    def test_repr(self):
        mk = AsyncMemoryKit(api_key="ctx_test")
        assert "AsyncMemoryKit(base_url=" in repr(mk)


class TestAsyncResourceAccess:
    def test_all_resources_present(self):
        mk = AsyncMemoryKit(api_key="ctx_test")
        assert mk.memories is not None
        assert mk.chats is not None
        assert mk.users is not None
        assert mk.webhooks is not None
        assert mk.status is not None
        assert mk.feedback is not None

    def test_resource_types(self):
        from memorykit.chats import AsyncChats
        from memorykit.feedback import AsyncFeedbackResource
        from memorykit.memories import AsyncMemories
        from memorykit.status import AsyncStatusResource
        from memorykit.users import AsyncUsers
        from memorykit.webhooks import AsyncWebhooks

        mk = AsyncMemoryKit(api_key="ctx_test")
        assert isinstance(mk.memories, AsyncMemories)
        assert isinstance(mk.chats, AsyncChats)
        assert isinstance(mk.users, AsyncUsers)
        assert isinstance(mk.webhooks, AsyncWebhooks)
        assert isinstance(mk.status, AsyncStatusResource)
        assert isinstance(mk.feedback, AsyncFeedbackResource)


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with AsyncMemoryKit(api_key="ctx_test") as mk:
            assert mk._client is not None
