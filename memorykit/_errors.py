"""MemoryKit error classes.

Provides a structured exception hierarchy for all API errors.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class MemoryKitError(Exception):
    """Base exception for all MemoryKit API errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code from the API response.
        code: Machine-readable error code from the API (e.g. ``"validation_error"``).
        request_id: Request ID returned by the API, useful for support.
        body: Raw response body, if available.
    """

    message: str
    status_code: Optional[int]
    code: Optional[str]
    request_id: Optional[str]
    body: Optional[Dict[str, Any]]

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.body = body

    def __repr__(self) -> str:
        attrs = [f"message={self.message!r}"]
        if self.status_code is not None:
            attrs.append(f"status_code={self.status_code}")
        if self.code is not None:
            attrs.append(f"code={self.code!r}")
        if self.request_id is not None:
            attrs.append(f"request_id={self.request_id!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class AuthenticationError(MemoryKitError):
    """Raised when the API key is missing, invalid, or expired (HTTP 401)."""

    def __init__(
        self,
        message: str = "Invalid or missing API key",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class PermissionError(MemoryKitError):
    """Raised when the API key lacks permission for the requested action (HTTP 403)."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(MemoryKitError):
    """Raised when the requested resource does not exist (HTTP 404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=404, **kwargs)


class ValidationError(MemoryKitError):
    """Raised when the request body or parameters fail validation (HTTP 400)."""

    def __init__(
        self,
        message: str = "Validation error",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=400, **kwargs)


class RateLimitError(MemoryKitError):
    """Raised when the API rate limit has been exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying, if provided by the API.
    """

    retry_after: Optional[float]

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ServerError(MemoryKitError):
    """Raised when the API returns a 5xx server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class ConnectionError(MemoryKitError):
    """Raised when a network-level connection error occurs."""

    def __init__(
        self,
        message: str = "Connection error",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class TimeoutError(MemoryKitError):
    """Raised when a request exceeds the configured timeout."""

    def __init__(
        self,
        message: str = "Request timed out",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

_STATUS_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    429: RateLimitError,
}


def _raise_for_status(status_code: int, body: Optional[Dict[str, Any]]) -> None:
    """Raise the appropriate :class:`MemoryKitError` subclass for *status_code*."""
    if status_code < 400:
        return

    message = "API error"
    code: Optional[str] = None
    request_id: Optional[str] = None
    retry_after: Optional[float] = None

    if body:
        err = body.get("error", {})
        if isinstance(err, dict):
            message = err.get("message", message)
            code = err.get("code", code)
        elif isinstance(err, str):
            message = err
        # Top-level fields
        message = body.get("message", message)
        code = body.get("code", code)
        request_id = body.get("request_id", request_id)

    cls = _STATUS_MAP.get(status_code)

    if cls is RateLimitError:
        raise RateLimitError(
            message=message,
            code=code,
            request_id=request_id,
            body=body,
            retry_after=retry_after,
        )

    if cls is not None:
        raise cls(message=message, code=code, request_id=request_id, body=body)

    if status_code >= 500:
        raise ServerError(
            message=message,
            status_code=status_code,
            code=code,
            request_id=request_id,
            body=body,
        )

    raise MemoryKitError(
        message=message,
        status_code=status_code,
        code=code,
        request_id=request_id,
        body=body,
    )
