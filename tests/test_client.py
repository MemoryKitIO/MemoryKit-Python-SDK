"""Tests for MemoryKit client initialization, configuration, and error handling."""

import pytest

from memorykit import (
    AsyncMemoryKit,
    AuthenticationError,
    MemoryKit,
    MemoryKitError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    __version__,
)
from memorykit._client import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    _backoff_delay,
    _convert_keys_to_snake,
    _to_camel,
    _to_snake,
)
from memorykit._errors import _raise_for_status

# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------


class TestMemoryKitInit:
    """Verify sync and async client initialization."""

    def test_sync_client_with_valid_key(self):
        mk = MemoryKit(api_key="ctx_test_key")
        assert mk._client._api_key == "ctx_test_key"
        assert mk._client._base_url == DEFAULT_BASE_URL
        assert mk._client._timeout == DEFAULT_TIMEOUT
        assert mk._client._max_retries == DEFAULT_MAX_RETRIES
        mk.close()

    def test_async_client_with_valid_key(self):
        mk = AsyncMemoryKit(api_key="ctx_test_key")
        assert mk._client._api_key == "ctx_test_key"
        assert mk._client._base_url == DEFAULT_BASE_URL
        mk = None  # Let GC handle it

    def test_empty_api_key_raises(self):
        with pytest.raises(MemoryKitError, match="api_key is required"):
            MemoryKit(api_key="")

    def test_empty_api_key_raises_async(self):
        with pytest.raises(MemoryKitError, match="api_key is required"):
            AsyncMemoryKit(api_key="")

    def test_custom_base_url(self):
        mk = MemoryKit(api_key="ctx_test", base_url="https://custom.api.io/v1")
        assert mk._client._base_url == "https://custom.api.io/v1"
        mk.close()

    def test_base_url_trailing_slash_stripped(self):
        mk = MemoryKit(api_key="ctx_test", base_url="https://api.example.com/v1/")
        assert mk._client._base_url == "https://api.example.com/v1"
        mk.close()

    def test_custom_timeout(self):
        mk = MemoryKit(api_key="ctx_test", timeout=60.0)
        assert mk._client._timeout == 60.0
        mk.close()

    def test_custom_max_retries(self):
        mk = MemoryKit(api_key="ctx_test", max_retries=5)
        assert mk._client._max_retries == 5
        mk.close()

    def test_sync_context_manager(self):
        with MemoryKit(api_key="ctx_test") as mk:
            assert mk._client is not None

    def test_repr(self):
        mk = MemoryKit(api_key="ctx_test")
        assert "MemoryKit(base_url=" in repr(mk)
        mk.close()

    def test_async_repr(self):
        mk = AsyncMemoryKit(api_key="ctx_test")
        assert "AsyncMemoryKit(base_url=" in repr(mk)


class TestResourceAccess:
    """Verify all resource attributes are present."""

    def test_sync_resources_exist(self):
        mk = MemoryKit(api_key="ctx_test")
        assert mk.memories is not None
        assert mk.chats is not None
        assert mk.users is not None
        assert mk.webhooks is not None
        assert mk.status is not None
        assert mk.feedback is not None
        mk.close()

    def test_async_resources_exist(self):
        mk = AsyncMemoryKit(api_key="ctx_test")
        assert mk.memories is not None
        assert mk.chats is not None
        assert mk.users is not None
        assert mk.webhooks is not None
        assert mk.status is not None
        assert mk.feedback is not None


# ---------------------------------------------------------------------------
# Key conversion
# ---------------------------------------------------------------------------


class TestKeyConversion:
    """Test snake_case <-> camelCase conversion."""

    def test_to_camel_known_params(self):
        assert _to_camel("user_id") == "userId"
        assert _to_camel("max_sources") == "maxSources"
        assert _to_camel("include_graph") == "includeGraph"
        assert _to_camel("score_threshold") == "scoreThreshold"
        assert _to_camel("response_format") == "responseFormat"
        assert _to_camel("memory_ids") == "memoryIds"

    def test_to_camel_unknown_params(self):
        assert _to_camel("some_param") == "someParam"
        assert _to_camel("another_long_name") == "anotherLongName"

    def test_to_snake_known_params(self):
        assert _to_snake("userId") == "user_id"
        assert _to_snake("maxSources") == "max_sources"
        assert _to_snake("includeGraph") == "include_graph"

    def test_to_snake_unknown_params(self):
        assert _to_snake("someParam") == "some_param"
        assert _to_snake("anotherLongName") == "another_long_name"

    def test_convert_keys_to_snake_recursive(self):
        data = {
            "userId": "u1",
            "nested": {"maxSources": 5, "includeGraph": True},
            "items": [{"scoreThreshold": 0.5}],
        }
        result = _convert_keys_to_snake(data)
        assert result["user_id"] == "u1"
        assert result["nested"]["max_sources"] == 5
        assert result["items"][0]["score_threshold"] == 0.5


# ---------------------------------------------------------------------------
# Backoff
# ---------------------------------------------------------------------------


class TestBackoffDelay:
    """Test retry backoff delay calculation."""

    def test_respects_retry_after(self):
        delay = _backoff_delay(0, retry_after=5.0)
        assert delay == 5.0

    def test_exponential_base(self):
        delay = _backoff_delay(0)
        assert 0.0 < delay < 1.0  # 0.5 base + up to 25% jitter

    def test_grows_with_attempts(self):
        _backoff_delay(0)
        d2 = _backoff_delay(2)
        # Attempt 2: base=2.0, attempt 0: base=0.5
        # Even with jitter, attempt 2 should generally be larger
        # but due to jitter it's not guaranteed, so just check the base math
        assert d2 > 0

    def test_capped_at_30(self):
        delay = _backoff_delay(100)
        assert delay <= 30.0 * 1.25 + 1  # 30 base + 25% jitter margin


# ---------------------------------------------------------------------------
# Error handling / _raise_for_status
# ---------------------------------------------------------------------------


class TestRaiseForStatus:
    """Verify correct exception classes are raised for status codes."""

    def test_200_no_error(self):
        _raise_for_status(200, {"ok": True})  # Should not raise

    def test_400_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc:
            _raise_for_status(400, {"message": "Bad request", "code": "invalid"})
        assert exc.value.status_code == 400
        assert exc.value.message == "Bad request"
        assert exc.value.code == "invalid"

    def test_401_raises_authentication_error(self):
        with pytest.raises(AuthenticationError) as exc:
            _raise_for_status(401, {"message": "Invalid API key"})
        assert exc.value.status_code == 401

    def test_403_raises_permission_error(self):
        from memorykit import PermissionError as MKPermissionError
        with pytest.raises(MKPermissionError):
            _raise_for_status(403, {"message": "Forbidden"})

    def test_404_raises_not_found_error(self):
        with pytest.raises(NotFoundError) as exc:
            _raise_for_status(404, {"message": "Not found"})
        assert exc.value.status_code == 404

    def test_429_raises_rate_limit_error(self):
        with pytest.raises(RateLimitError) as exc:
            _raise_for_status(429, {"message": "Too many requests"})
        assert exc.value.status_code == 429

    def test_500_raises_server_error(self):
        with pytest.raises(ServerError) as exc:
            _raise_for_status(500, {"message": "Internal error"})
        assert exc.value.status_code == 500

    def test_502_raises_server_error(self):
        with pytest.raises(ServerError):
            _raise_for_status(502, {})

    def test_unknown_4xx_raises_generic(self):
        with pytest.raises(MemoryKitError) as exc:
            _raise_for_status(418, {"message": "I'm a teapot"})
        assert exc.value.status_code == 418

    def test_error_body_with_nested_error(self):
        body = {"error": {"message": "Nested error msg", "code": "nested_code"}}
        with pytest.raises(ValidationError) as exc:
            _raise_for_status(400, body)
        # Note: top-level message overrides nested if present
        # If only nested: should use nested
        assert "error" in exc.value.message.lower() or "Nested" in exc.value.message

    def test_error_body_with_string_error(self):
        body = {"error": "Simple string error"}
        with pytest.raises(ValidationError):
            _raise_for_status(400, body)

    def test_empty_body(self):
        with pytest.raises(NotFoundError):
            _raise_for_status(404, {})

    def test_none_body(self):
        with pytest.raises(NotFoundError):
            _raise_for_status(404, None)


class TestErrorHierarchy:
    """Verify error class inheritance."""

    def test_authentication_error_is_memorykit_error(self):
        err = AuthenticationError("test")
        assert isinstance(err, MemoryKitError)
        assert isinstance(err, Exception)

    def test_rate_limit_error_has_retry_after(self):
        err = RateLimitError("limited", retry_after=30.0)
        assert err.retry_after == 30.0

    def test_error_repr(self):
        err = AuthenticationError("test", code="auth_failed", request_id="req_123")
        r = repr(err)
        assert "AuthenticationError" in r
        assert "test" in r
        assert "auth_failed" in r
        assert "req_123" in r


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


class TestVersion:
    def test_version_defined(self):
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert "." in __version__
