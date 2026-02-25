"""Feedback resource — submit feedback on query/search results."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._types import Feedback


class FeedbackResource:
    """Synchronous interface for the Feedback API.

    Access via ``mk.feedback``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        request_id: str,
        rating: Any,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Submit feedback for a previous query or search request.

        Args:
            request_id: The ``request_id`` from a query or search response.
            rating: Rating value (e.g. 1-5, thumbs up/down).
            comment: Optional text comment.

        Returns:
            The created :class:`Feedback` object.
        """
        body: Dict[str, Any] = {
            "request_id": request_id,
            "rating": rating,
            "comment": comment,
        }
        data = self._client.request("POST", "/feedback", json=body)
        return Feedback(data)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncFeedbackResource:
    """Asynchronous interface for the Feedback API.

    Access via ``mk.feedback`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        request_id: str,
        rating: Any,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Submit feedback. See :meth:`FeedbackResource.create`."""
        body: Dict[str, Any] = {
            "request_id": request_id,
            "rating": rating,
            "comment": comment,
        }
        data = await self._client.request("POST", "/feedback", json=body)
        return Feedback(data)
