"""Status resource — retrieve project usage, plan, and knowledge information."""

from __future__ import annotations

from typing import Any, Dict

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._types import Status


class StatusResource:
    """Synchronous interface for the Status API.

    Access via ``mk.status``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def get(self) -> Status:
        """Get project status including usage, plan, and knowledge stats.

        Returns:
            A :class:`Status` object with project details.
        """
        data = self._client.request("GET", "/status")
        return Status(data)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncStatusResource:
    """Asynchronous interface for the Status API.

    Access via ``mk.status`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def get(self) -> Status:
        """Get project status. See :meth:`StatusResource.get`."""
        data = await self._client.request("GET", "/status")
        return Status(data)
