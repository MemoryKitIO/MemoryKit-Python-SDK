"""Base HTTP client logic for sync and async MemoryKit clients.

Handles authentication, request building, retries with exponential backoff,
error parsing, and the snake_case <-> camelCase parameter conversion.
"""

from __future__ import annotations

import re
import time
import random
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import httpx

from ._errors import (
    ConnectionError as MKConnectionError,
    MemoryKitError,
    RateLimitError,
    TimeoutError as MKTimeoutError,
    _raise_for_status,
)

__version__ = "0.1.1"

DEFAULT_BASE_URL = "https://api.memorykit.io/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)
USER_AGENT = f"memorykit-python/{__version__}"

# ---------------------------------------------------------------------------
# camelCase <-> snake_case conversion
# ---------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")
_SNAKE_RE = re.compile(r"_([a-z0-9])")

# Known camelCase API parameter names and their snake_case equivalents.
# The SDK accepts BOTH forms; conversion is always to camelCase before sending.
_PARAM_MAP: Dict[str, str] = {
    "user_id": "userId",
    "max_sources": "maxSources",
    "include_graph": "includeGraph",
    "score_threshold": "scoreThreshold",
    "response_format": "responseFormat",
    "memory_ids": "memoryIds",
    "request_id": "requestId",
    "has_more": "hasMore",
    "total_results": "totalResults",
    "status_code": "statusCode",
}

# Reverse map for converting API responses back to snake_case
_REVERSE_PARAM_MAP: Dict[str, str] = {v: k for k, v in _PARAM_MAP.items()}


def _to_camel(name: str) -> str:
    """Convert a snake_case name to camelCase."""
    if name in _PARAM_MAP:
        return _PARAM_MAP[name]
    return _SNAKE_RE.sub(lambda m: m.group(1).upper(), name)


def _to_snake(name: str) -> str:
    """Convert a camelCase name to snake_case."""
    if name in _REVERSE_PARAM_MAP:
        return _REVERSE_PARAM_MAP[name]
    return _CAMEL_RE.sub(r"\1_\2", name).lower()


def _is_camel_case(name: str) -> bool:
    """Check if a name is already in camelCase."""
    return bool(re.search(r"[a-z][A-Z]", name))


def _convert_keys_to_camel(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all top-level dict keys from snake_case to camelCase.

    Keys that are already camelCase are left unchanged. Only converts
    keys that contain underscores (look like snake_case).
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if "_" in key:
            result[_to_camel(key)] = value
        else:
            result[key] = value
    return result


def _convert_keys_to_snake(data: Any) -> Any:
    """Recursively convert all dict keys from camelCase to snake_case.

    This is applied to API response bodies so users get Python-style attributes.
    """
    if isinstance(data, dict):
        return {_to_snake(k): _convert_keys_to_snake(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_convert_keys_to_snake(item) for item in data]
    return data


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------


def _backoff_delay(attempt: int, retry_after: Optional[float] = None) -> float:
    """Calculate exponential backoff delay with jitter."""
    if retry_after is not None and retry_after > 0:
        return retry_after
    delay = min(2 ** attempt * 0.5, 30.0)
    jitter = random.uniform(0, delay * 0.25)
    return delay + jitter


# ---------------------------------------------------------------------------
# Sync HTTP client
# ---------------------------------------------------------------------------


class SyncHTTPClient:
    """Synchronous HTTP client wrapping :class:`httpx.Client`.

    Args:
        api_key: MemoryKit API key (must start with ``ctx_``).
        base_url: API base URL. Defaults to ``https://api.memorykit.io/v1``.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of automatic retries on retriable errors.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise MemoryKitError("api_key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(timeout),
        )

    # -- public helpers ------------------------------------------------------

    @property
    def base_url(self) -> str:
        return self._base_url

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "SyncHTTPClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # -- core request methods ------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a request and return the parsed JSON response body.

        Handles retries, error parsing, and key conversion.
        """
        # Convert outgoing keys to camelCase
        if json is not None:
            json = _convert_keys_to_camel(json)
        if params is not None:
            params = _convert_keys_to_camel(params)
        if data is not None:
            data = _convert_keys_to_camel(data)

        # Filter out None values
        if json is not None:
            json = {k: v for k, v in json.items() if v is not None}
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}

        last_err: Optional[Exception] = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    files=files,
                    data=data,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                last_err = MKTimeoutError(f"Request timed out: {exc}")
                if attempt < self._max_retries:
                    time.sleep(_backoff_delay(attempt))
                    continue
                raise last_err from exc
            except httpx.ConnectError as exc:
                last_err = MKConnectionError(f"Connection failed: {exc}")
                if attempt < self._max_retries:
                    time.sleep(_backoff_delay(attempt))
                    continue
                raise last_err from exc

            # Successful response (no body expected)
            if response.status_code == 204:
                return {}
            if response.status_code == 202:
                # May or may not have a body
                try:
                    body = response.json()
                except Exception:
                    return {}
                return _convert_keys_to_snake(body)

            # Parse response body
            try:
                body = response.json()
            except Exception:
                body = {}

            # Check for retriable status codes
            if response.status_code in DEFAULT_RETRY_STATUSES and attempt < self._max_retries:
                retry_after: Optional[float] = None
                ra_header = response.headers.get("Retry-After")
                if ra_header:
                    try:
                        retry_after = float(ra_header)
                    except ValueError:
                        pass
                time.sleep(_backoff_delay(attempt, retry_after))
                continue

            # Raise on error
            _raise_for_status(response.status_code, body)

            # Success -- convert response keys to snake_case
            return _convert_keys_to_snake(body)

        # Should not reach here, but just in case
        if last_err is not None:
            raise last_err
        raise MemoryKitError("Request failed after retries")

    def request_stream(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Send a streaming request and return the raw ``httpx.Response``.

        The caller is responsible for iterating and closing the response.
        """
        if json is not None:
            json = _convert_keys_to_camel(json)
            json = {k: v for k, v in json.items() if v is not None}

        stream_headers = dict(headers or {})
        stream_headers["Accept"] = "text/event-stream"

        return self._client.stream(
            method,
            path,
            json=json,
            headers=stream_headers,
        )


# ---------------------------------------------------------------------------
# Async HTTP client
# ---------------------------------------------------------------------------


class AsyncHTTPClient:
    """Asynchronous HTTP client wrapping :class:`httpx.AsyncClient`.

    Args:
        api_key: MemoryKit API key (must start with ``ctx_``).
        base_url: API base URL. Defaults to ``https://api.memorykit.io/v1``.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of automatic retries on retriable errors.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise MemoryKitError("api_key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(timeout),
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncHTTPClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send an async request and return the parsed JSON response body."""
        if json is not None:
            json = _convert_keys_to_camel(json)
        if params is not None:
            params = _convert_keys_to_camel(params)
        if data is not None:
            data = _convert_keys_to_camel(data)

        if json is not None:
            json = {k: v for k, v in json.items() if v is not None}
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}

        last_err: Optional[Exception] = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    files=files,
                    data=data,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                last_err = MKTimeoutError(f"Request timed out: {exc}")
                if attempt < self._max_retries:
                    import asyncio
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise last_err from exc
            except httpx.ConnectError as exc:
                last_err = MKConnectionError(f"Connection failed: {exc}")
                if attempt < self._max_retries:
                    import asyncio
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise last_err from exc

            if response.status_code == 204:
                return {}
            if response.status_code == 202:
                try:
                    body = response.json()
                except Exception:
                    return {}
                return _convert_keys_to_snake(body)

            try:
                body = response.json()
            except Exception:
                body = {}

            if response.status_code in DEFAULT_RETRY_STATUSES and attempt < self._max_retries:
                retry_after: Optional[float] = None
                ra_header = response.headers.get("Retry-After")
                if ra_header:
                    try:
                        retry_after = float(ra_header)
                    except ValueError:
                        pass
                import asyncio
                await asyncio.sleep(_backoff_delay(attempt, retry_after))
                continue

            _raise_for_status(response.status_code, body)
            return _convert_keys_to_snake(body)

        if last_err is not None:
            raise last_err
        raise MemoryKitError("Request failed after retries")

    async def request_stream(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Send an async streaming request and return the raw response."""
        if json is not None:
            json = _convert_keys_to_camel(json)
            json = {k: v for k, v in json.items() if v is not None}

        stream_headers = dict(headers or {})
        stream_headers["Accept"] = "text/event-stream"

        # Use the client's stream context manager -- we return the response
        # and the caller is responsible for iterating/closing.
        req = self._client.build_request(
            method,
            path,
            json=json,
            headers=stream_headers,
        )
        response = await self._client.send(req, stream=True)
        return response
