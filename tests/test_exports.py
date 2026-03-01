"""Tests that all expected public symbols are exported from the memorykit package.

This catches accidental removal of exports from __init__.py during refactoring.
"""

import memorykit


class TestPublicExports:
    def test_client_classes_exported(self):
        assert hasattr(memorykit, "MemoryKit")
        assert hasattr(memorykit, "AsyncMemoryKit")

    def test_error_classes_exported(self):
        assert hasattr(memorykit, "MemoryKitError")
        assert hasattr(memorykit, "AuthenticationError")
        assert hasattr(memorykit, "PermissionError")
        assert hasattr(memorykit, "NotFoundError")
        assert hasattr(memorykit, "ValidationError")
        assert hasattr(memorykit, "RateLimitError")
        assert hasattr(memorykit, "ServerError")
        assert hasattr(memorykit, "ConnectionError")
        assert hasattr(memorykit, "TimeoutError")

    def test_type_classes_exported(self):
        assert hasattr(memorykit, "APIObject")
        assert hasattr(memorykit, "Memory")
        assert hasattr(memorykit, "MemoryList")
        assert hasattr(memorykit, "BatchIngestResponse")
        assert hasattr(memorykit, "QueryResponse")
        assert hasattr(memorykit, "SearchResponse")
        assert hasattr(memorykit, "Chat")
        assert hasattr(memorykit, "ChatList")
        assert hasattr(memorykit, "ChatMessage")
        assert hasattr(memorykit, "ChatMessageList")
        assert hasattr(memorykit, "ChatMessageResponse")
        assert hasattr(memorykit, "User")
        assert hasattr(memorykit, "Event")
        assert hasattr(memorykit, "EventList")
        assert hasattr(memorykit, "Webhook")
        assert hasattr(memorykit, "WebhookList")
        assert hasattr(memorykit, "WebhookTestResponse")
        assert hasattr(memorykit, "Status")
        assert hasattr(memorykit, "Feedback")

    def test_version_exported(self):
        assert hasattr(memorykit, "__version__")
        assert isinstance(memorykit.__version__, str)
        assert "." in memorykit.__version__

    def test_all_list_complete(self):
        """Verify that __all__ contains all the expected exports."""
        expected = {
            "MemoryKit",
            "AsyncMemoryKit",
            "MemoryKitError",
            "AuthenticationError",
            "PermissionError",
            "NotFoundError",
            "ValidationError",
            "RateLimitError",
            "ServerError",
            "ConnectionError",
            "TimeoutError",
            "APIObject",
            "Memory",
            "MemoryList",
            "BatchIngestResponse",
            "QueryResponse",
            "SearchResponse",
            "Chat",
            "ChatList",
            "ChatMessage",
            "ChatMessageList",
            "ChatMessageResponse",
            "User",
            "Event",
            "EventList",
            "Webhook",
            "WebhookList",
            "WebhookTestResponse",
            "Status",
            "Feedback",
            "__version__",
        }
        actual = set(memorykit.__all__)
        assert expected == actual, f"Missing: {expected - actual}, Extra: {actual - expected}"
